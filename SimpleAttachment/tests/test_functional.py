"""
    SimpleAttachment functional doctests.  This module collects all *.txt
    files in the tests directory and runs them.

    Based partly on test_functional.py from CMFPlone and the test tutorial:
    http://plone.org/documentation/tutorial/testing/doctests 

"""
import os
import glob
import doctest
import unittest
from Globals import package_home
from Testing import ZopeTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.SimpleAttachment.tests import GLOBALS
from Products.CMFPlone.tests import PloneTestCase

# RichDocument is required to be installed since the SimpleAttachment is tested
# in combination with a Rich document which is added in the functional doc test, UploadAttachment.txt
ZopeTestCase.installProduct('RichDocument')
PRODUCTS = ['SimpleAttachment','RichDocument']
PloneTestCase.setupPloneSite(products=PRODUCTS)

OPTIONFLAGS = (
    #doctest.REPORT_ONLY_FIRST_FAILURE |
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE
)

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
          glob.glob(os.path.sep.join([home, '*.txt']))]

def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.SimpleAttachment.tests',
               test_class=PloneTestCase.FunctionalTestCase)
              for filename in filenames]

    return unittest.TestSuite(suites)