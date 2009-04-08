#
# PloneTestCase
#

# $Id: PloneTestCase.py 18203 2007-11-28 14:22:06Z witsch $

from Products.PloneTestCase.ptc import *

# Make the test fixture extension profile active
from zope.interface import classImplements
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.interfaces import ITestCasePloneSiteRoot
classImplements(PloneSite, ITestCasePloneSiteRoot)

setupPloneSite(extension_profiles=['Products.CMFPlone:testfixture'])


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

    def setRequestMethod(self, method):
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method


class FunctionalTestCase(Functional, PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """
