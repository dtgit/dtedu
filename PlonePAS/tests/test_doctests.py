##############################################################################
#
# PlonePAS - Adapt PluggableAuthService for use in Plone
# Copyright (C) 2005 Enfold Systems, Kapil Thangavelu, et al
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""

# Load fixture
import unittest
from Testing import ZopeTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from Products.CMFCore.utils import getToolByName

from zExceptions.ExceptionFormatter import format_exception
from ZPublisher.HTTPResponse import HTTPResponse

setupPloneSite()

# Silence Plone's handling of exceptions
orig_exception = HTTPResponse.exception
def exception(self, **kw):
    def tag_search(*args):
        return False
    kw['tag_search'] = tag_search
    return orig_exception(self, **kw)

orig_setBody = HTTPResponse.setBody
def setBody(self, *args, **kw):
    kw['is_error'] = 0
    if len(args[0]) == 2:
        title, body = args[0]
        args = (body,) + args[1:]
    return orig_setBody(self, *args, **kw)

def _traceback(self, t, v, tb, as_html=1):
    return ''.join(format_exception(t, v, tb, as_html=as_html))

HTTPResponse._error_format = 'text/plain'
HTTPResponse._traceback = _traceback
HTTPResponse.exception = exception
HTTPResponse.setBody = setBody

def test_suite():
    suite = unittest.TestSuite()
    DocFileSuite = ZopeTestCase.FunctionalDocFileSuite
    tests = (
        ('cookie_auth.txt', FunctionalTestCase),
        )

    for fname, klass in tests:
        t = DocFileSuite(fname,
                         test_class=klass,
                         package='Products.PlonePAS.tests')
        suite.addTest(t)
    return suite

