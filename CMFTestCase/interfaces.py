#
# CMFTestCase interfaces
#

# $Id: interfaces.py 33455 2006-11-12 13:52:45Z shh42 $

from Testing.ZopeTestCase.interfaces import *


class ICMFSecurity(IPortalSecurity):

    def loginAsPortalOwner():
        '''Logs in as the user owning the portal object.
           Use this when you need to manipulate the portal
           itself.
        '''


class ICMFTestCase(IPortalTestCase):

    def addProfile(name):
        '''Imports an extension profile into the CMF site.
           This is an alternative to passing the 'extension_profiles'
           argument to 'setupCMFSite'.
        '''

    def addProduct(name):
        '''Installs a product into the CMF site by executing
           its 'Extensions.Install.install' function.
           This is an alternative to passing the 'products'
           argument to 'setupCMFSite'.
        '''

