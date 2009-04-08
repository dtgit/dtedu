#
# CMFTestCase setup
#

# $Id: setup.py 49972 2007-09-23 14:41:30Z shh42 $

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFUid', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('ZCTextIndex', quiet=1)

# Check for CMF 1.5 or above
try:
    from Products.CMFCore import permissions
except ImportError:
    CMF15 = 0
else:
    CMF15 = 1

# Check for CMF 1.6 or above
try:
    from Products.CMFDefault import factory
except ImportError:
    CMF16 = 0
else:
    CMF16 = 1
    CMF15 = 1

# Check for CMF 2.0 or above
try:
    from Products.CMFDefault.utils import translate
except ImportError:
    CMF20 = 0
else:
    CMF20 = 1
    CMF16 = 1
    CMF15 = 1

# Check for CMF 2.1 or above
try:
    from Products.CMFDefault.utils import getBrowserCharset
except ImportError:
    CMF21 = 0
else:
    CMF21 = 1
    CMF20 = 1
    CMF16 = 1
    CMF15 = 1

# Check for layer support
try:
    import zope.testing.testrunner
except ImportError:
    USELAYER = 0
else:
    USELAYER = 1

# Check for Zope3 interfaces
try:
    from zope.interface.interfaces import IInterface
except ImportError:
    Z3INTERFACES = 0
else:
    from interfaces import ICMFTestCase
    Z3INTERFACES = IInterface.providedBy(ICMFTestCase)

# BBB: Zope 2.8
if CMF16 and not USELAYER:
    ZopeTestCase.installProduct('Five')

from Testing.ZopeTestCase import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
from time import time
from Globals import PersistentMapping

portal_name = 'cmf'
portal_owner = 'portal_owner'
default_products = ()
default_user = ZopeTestCase.user_name
default_password = ZopeTestCase.user_password

default_base_profile = 'CMFDefault:default'
default_extension_profiles = ()

if CMF21:
    default_base_profile = 'Products.CMFDefault:default'


def setupCMFSite(id=portal_name,
                 products=default_products,
                 quiet=0,
                 base_profile=default_base_profile,
                 extension_profiles=default_extension_profiles):
    '''Creates a CMF site and/or installs products into it.'''
    if USELAYER:
        quiet = 1
        cleanupCMFSite(id)
    SiteSetup(id, products, quiet, base_profile, extension_profiles).run()

if USELAYER:
    import layer
    setupCMFSite = layer.onsetup(setupCMFSite)


def cleanupCMFSite(id):
    '''Removes a site.'''
    SiteCleanup(id).run()

if USELAYER:
    import layer
    cleanupCMFSite = layer.onteardown(cleanupCMFSite)


class SiteSetup:
    '''Creates a CMF site and/or installs products into it.'''

    def __init__(self, id, products, quiet, base_profile, extension_profiles):
        self.id = id
        self.products = products
        self.quiet = quiet
        self.base_profile = base_profile
        self.extension_profiles = tuple(extension_profiles)

    def run(self):
        self.app = self._app()
        try:
            uf = self.app.acl_users
            if uf.getUserById(portal_owner) is None:
                # Add portal owner
                uf.userFolderAddUser(portal_owner, default_password, ['Manager'], [])
            if not hasattr(aq_base(self.app), self.id):
                # Add site
                self._login(uf, portal_owner)
                self._optimize()
                self._setupCMFSite()
                self._setupRegistries()
            if hasattr(aq_base(self.app), self.id):
                # Configure site
                self._login(uf, portal_owner)
                self._placefulSetUp()
                self._setupProfiles()
                self._setupProducts()
        finally:
            self._abort()
            self._close()
            self._logout()
            self._placefulTearDown()

    def _setupCMFSite(self):
        '''Creates the CMF site.'''
        if CMF16:
            self._setupCMFSite_with_genericsetup()
        else:
            self._setupCMFSite_with_portalgenerator()

    def _setupCMFSite_with_genericsetup(self):
        '''Creates the site using GenericSetup.'''
        start = time()
        if self.base_profile != default_base_profile:
            self._print('Adding CMF Site (%s) ... ' % (self.base_profile,))
        else:
            self._print('Adding CMF Site ... ')
        factory.addConfiguredSite(self.app, self.id, snapshot=0,
                                  profile_id=self.base_profile)
        self._commit()
        self._print('done (%.3fs)\n' % (time()-start,))

    def _setupCMFSite_with_portalgenerator(self):
        '''Creates the site using PortalGenerator.'''
        start = time()
        self._print('Adding CMF Site ... ')
        from Products.CMFDefault.Portal import manage_addCMFSite
        manage_addCMFSite(self.app, self.id, create_userfolder=1)
        self._commit()
        self._print('done (%.3fs)\n' % (time()-start,))

    def _setupRegistries(self):
        '''Installs persistent registries.'''
        portal = getattr(self.app, self.id)
        if not hasattr(portal, '_installed_profiles'):
            portal._installed_profiles = PersistentMapping()
            self._commit()
        if not hasattr(portal, '_installed_products'):
            portal._installed_products = PersistentMapping()
            self._commit()

    def _setupProfiles(self):
        '''Imports extension profiles into the site.'''
        portal = getattr(self.app, self.id)
        setup = getattr(portal, 'portal_setup', None)
        if setup is not None:
            for profile in self.extension_profiles:
                if not portal._installed_profiles.has_key(profile):
                    start = time()
                    self._print('Adding %s ... ' % (profile,))
                    profile_id = 'profile-%s' % (profile,)
                    if CMF21:
                        setup.runAllImportStepsFromProfile(profile_id)
                    else:
                        saved = setup.getImportContextID()
                        try:
                            setup.setImportContext(profile_id)
                            setup.runAllImportSteps()
                        finally:
                            setup.setImportContext(saved)
                    portal._installed_profiles[profile] = 1
                    self._commit()
                    self._print('done (%.3fs)\n' % (time()-start,))

    def _setupProducts(self):
        '''Installs products into the site.'''
        portal = getattr(self.app, self.id)
        for product in self.products:
            if not portal._installed_products.has_key(product):
                start = time()
                self._print('Adding %s ... ' % (product,))
                exec 'from Products.%s.Extensions.Install import install' % (product,)
                install(portal)
                portal._installed_products[product] = 1
                self._commit()
                self._print('done (%.3fs)\n' % (time()-start,))

    def _placefulSetUp(self):
        '''Sets the local site/manager.'''
        if CMF21:
            portal = getattr(self.app, self.id)
            _placefulSetUp(portal)

    def _placefulTearDown(self):
        '''Resets the local site/manager.'''
        if CMF21:
            _placefulTearDown()

    def _optimize(self):
        '''Applies optimizations to the PortalGenerator.'''
        _optimize()

    def _app(self):
        '''Opens a ZODB connection and returns the app object.'''
        return ZopeTestCase.app()

    def _close(self):
        '''Closes the ZODB connection.'''
        ZopeTestCase.close(self.app)

    def _login(self, uf, name):
        '''Logs in as user 'name' from user folder 'uf'.'''
        user = uf.getUserById(name).__of__(uf)
        newSecurityManager(None, user)

    def _logout(self):
        '''Logs out.'''
        noSecurityManager()

    def _commit(self):
        '''Commits the transaction.'''
        transaction.commit()

    def _abort(self):
        '''Aborts the transaction.'''
        transaction.abort()

    def _print(self, msg):
        '''Prints msg to stderr.'''
        if not self.quiet:
            ZopeTestCase._print(msg)


class SiteCleanup(SiteSetup):
    '''Removes a site.'''

    def __init__(self, id):
        self.id = id

    def run(self):
        self.app = self._app()
        try:
            if hasattr(aq_base(self.app), self.id):
                self._placefulSetUp()
                self.app._delObject(self.id)
                self._commit()
        finally:
            self._abort()
            self._close()
            self._placefulTearDown()


def _placefulSetUp(portal):
    '''Sets the local site/manager.'''
    from zope.app.component.hooks import setHooks, setSite
    from zope.component.interfaces import ComponentLookupError
    setHooks()
    try:
        setSite(portal)
    except ComponentLookupError:
        pass


def _placefulTearDown():
    '''Resets the local site/manager.'''
    from zope.app.component.hooks import resetHooks, setSite
    resetHooks()
    setSite()


def _optimize():
    '''Reduces portal creation time.'''
    # Don't compile expressions on creation
    def __init__(self, text):
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    # Don't clone actions but convert to list only
    def _cloneActions(self):
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions
    # The site creation code is not needed anymore in CMF >= 1.6
    # as it is now based on GenericSetup
    if not CMF16:
        # Don't setup 'index_html' in Members folder
        def setupMembersFolder(self, p):
            p.manage_addPortalFolder('Members')
        from Products.CMFDefault.Portal import PortalGenerator
        PortalGenerator.setupMembersFolder = setupMembersFolder

