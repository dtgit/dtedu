##############################################################################
#
# TemplateFields - DTML and ZPT fields for Archetypes
# Copyright (C) 2005 Klein & Partner KEG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: test_field.py 9616 2008-04-27 19:41:14Z smcmahon $
"""


# Load fixture
import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import doctest
from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()

from Products.TemplateFields import DTMLField, ZPTField

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('TemplateFields')

class DTMLFieldTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.field = DTMLField('aField')
        self.folder.validate_field = lambda *args, **kw: None
        self.folder.setTitle("My Folder")

    def validate(self, value):
        errors = {}
        res = self.field.validate(value, self.folder, errors)
        return res, errors

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), "My Folder")

    def test_getRaw(self):
        raw = self.field.getRaw(self.folder)
        self.assertEquals(raw, '<dtml-var title_or_id>')

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), "My Folder")
        self.field.set(self.folder,
                       """<dtml-if expr="1 + 1 == 2">
                       True
                       <dtml-else>
                       False
                       </dtml-if>
                       """)
        self.assertEquals(self.field.get(self.folder).strip(), "True")

    def test_set_dtmlmethod(self):
        # Just make sure setting DTMLMethod works too.
        default_dtml = self.field.getDefault(self.folder)
        self.field.set(self.folder, default_dtml)
        self.assertEquals(
            self.field.getRaw(self.folder), default_dtml.read())


class ZPTFieldTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.field = ZPTField('aField')
        self.folder.validate_field = lambda *args, **kw: None
        self.folder.setTitle("My Folder")

    def validate(self, value):
        errors = {}
        res = self.field.validate(value, self.folder, errors)
        return res, errors

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), "My Folder\n")

    def test_getRaw(self):
        raw = self.field.getRaw(self.folder)
        self.assertEquals(raw, '<span tal:replace="here/title_or_id" />')

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), "My Folder\n")
        self.field.set(self.folder,
                       '<span tal:replace="here/aq_parent/title_or_id" />')
        if PloneTestCase.PLONE30:
            self.assertEquals(self.field.get(self.folder), "Users\n")
        else:
            self.assertEquals(self.field.get(self.folder), "Members\n")

    def test_set_zpt(self):
        # Just make sure setting PageTemplate works too.
        default_zpt = self.field.getDefault(self.folder)
        self.field.set(self.folder, default_zpt)
        self.assertEquals(
            self.field.getRaw(self.folder), default_zpt.read())
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DTMLFieldTest))
    suite.addTest(unittest.makeSuite(ZPTFieldTest))
    doctests = (
        'Products.TemplateFields.validators',
        )
    for module in doctests:
        suite.addTest(doctest.DocTestSuite(module))
    return suite

