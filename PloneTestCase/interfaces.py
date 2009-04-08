#
# PloneTestCase interfaces
#

# $Id: interfaces.py 33456 2006-11-12 13:55:14Z shh42 $

from Testing.ZopeTestCase.interfaces import *


class IPloneSecurity(IPortalSecurity):

    def setGroups(groups, name=None):
        '''Changes the groups assigned to a user.
           If the 'name' argument is omitted, changes the
           groups of the default user.
        '''

    def loginAsPortalOwner():
        '''Logs in as the user owning the portal object.
           Use this when you need to manipulate the portal
           itself.
        '''


class IPloneTestCase(IPortalTestCase):

    def addProfile(name):
        '''Imports an extension profile into the Plone site.
           This is an alternative to passing the 'extension_profiles'
           argument to 'setupPloneSite'.
        '''

    def addProduct(name):
        '''Quickinstalls a product into the Plone site.
           This is an alternative to passing the 'products'
           argument to 'setupPloneSite'.
        '''

