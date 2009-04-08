#
# CMFTestCase
#

# $Id: CMFTestCase.py 44961 2007-07-01 19:36:36Z shh42 $

from Testing.ZopeTestCase import hasProduct
from Testing.ZopeTestCase import installProduct

try:
    from Testing.ZopeTestCase import hasPackage
    from Testing.ZopeTestCase import installPackage
except ImportError:
    pass

from Testing.ZopeTestCase import Sandboxed
from Testing.ZopeTestCase import Functional
from Testing.ZopeTestCase import PortalTestCase

from setup import CMF15
from setup import CMF16
from setup import CMF20
from setup import CMF21
from setup import USELAYER
from setup import Z3INTERFACES
from setup import portal_name
from setup import portal_owner
from setup import default_products
from setup import default_base_profile
from setup import default_extension_profiles
from setup import default_user
from setup import default_password
from setup import _placefulSetUp
from setup import _placefulTearDown

from setup import setupCMFSite

from interfaces import ICMFTestCase
from interfaces import ICMFSecurity

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from warnings import warn

import utils
import setup


class CMFTestCase(PortalTestCase):
    '''Base test case for CMF testing'''

    if Z3INTERFACES:
        from zope.interface import implements
        implements(ICMFTestCase, ICMFSecurity)
    else:
        __implements__ = (ICMFTestCase, ICMFSecurity,
                          PortalTestCase.__implements__)

    if USELAYER:
        import layer
        layer = layer.CMFSite

    def _portal(self):
        '''Returns the portal object for a test.'''
        portal = self.getPortal()
        if CMF21:
            _placefulSetUp(portal)
        return portal

    def _setup(self):
        '''Configures the portal.'''
        PortalTestCase._setup(self)
        if CMF21 and self.portal is not None:
            self._refreshSkinData()

    def _clear(self, call_close_hook=0):
        '''Clears the fixture.'''
        PortalTestCase._clear(self, call_close_hook)
        if CMF21:
            _placefulTearDown()

    # Portal interface

    def getPortal(self):
        '''Returns the portal object.

           Do not call this method! Use the self.portal
           attribute to access the portal object from tests.
        '''
        return getattr(self.app, portal_name)

    def createMemberarea(self, name):
        '''Creates a minimal memberarea.'''
        uf = self.portal.acl_users
        user = uf.getUserById(name)
        if user is None:
            raise ValueError, 'Member %s does not exist' % name
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        pm = self.portal.portal_membership
        members = pm.getMembersFolder()
        members.manage_addPortalFolder(name)
        folder = pm.getHomeFolder(name)
        folder.changeOwnership(user)
        folder.__ac_local_roles__ = None
        folder.manage_setLocalRoles(name, ['Owner'])

    # Security interface

    def loginAsPortalOwner(self):
        '''Use if - AND ONLY IF - you need to manipulate the
           portal object itself.
        '''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    # CMF interface

    def addProfile(self, name):
        '''Imports an extension profile into the site.'''
        sm = getSecurityManager()
        self.loginAsPortalOwner()
        try:
            installed = getattr(self.portal, '_installed_profiles', {})
            if not installed.has_key(name):
                setup = self.portal.portal_setup
                profile_id = 'profile-%s' % (name,)
                if CMF21:
                    setup.runAllImportStepsFromProfile(profile_id)
                else:
                    saved = setup.getImportContextID()
                    try:
                        setup.setImportContext(profile_id)
                        setup.runAllImportSteps()
                    finally:
                        setup.setImportContext(saved)
                self._refreshSkinData()
        finally:
            setSecurityManager(sm)

    def addProduct(self, name):
        '''Installs a product into the site.'''
        sm = getSecurityManager()
        self.loginAsPortalOwner()
        try:
            installed = getattr(self.portal, '_installed_products', {})
            if not installed.has_key(name):
                exec 'from Products.%s.Extensions.Install import install' % (name,)
                install(self.portal)
                self._refreshSkinData()
        finally:
            setSecurityManager(sm)


class FunctionalTestCase(Functional, CMFTestCase):
    '''Base class for functional CMF tests'''

    if not Z3INTERFACES:
        __implements__ = (Functional.__implements__,
                          CMFTestCase.__implements__)

