##############################################################################
#
# PythonField - Field with Python support for Archetypes
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
$Id: test_field.py 9606 2008-04-27 17:33:40Z smcmahon $
"""


# Load fixture
import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import doctest
from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()

from Products.PythonField import PythonField

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PythonField')

class PythonFieldTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.field = PythonField('python')
        self.folder.validate_field = lambda *args, **kw: None

    def validate(self, value):
        errors = {}
        res = self.field.validate(value, self.folder, errors)
        return res, errors

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), None)

    def test_getRaw(self):
        raw = self.field.getRaw(self.folder)
        self.assertEquals(raw, 'pass\n')

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), None)
        self.folder.setTitle('bar')
        self.field.set(self.folder, "return context.Title() == 'foo'")
        self.assertEquals(self.field.get(self.folder), False)
        self.field.set(self.folder, "return context.Title() == 'bar'")
        self.assertEquals(self.field.get(self.folder), True)

    def test_set_pythonscript(self):
        # Just make sure setting PythonScript works too.
        default_script = self.field.getDefault(self.folder)
        self.field.set(self.folder, default_script)
        self.assertEquals(
            self.field.getRaw(self.folder), default_script.body())

    def test_validate(self):
        self.assertEquals(self.validate('True'), (None, {}))
        self.assertEquals(
            self.validate('1 + (2 * 3'),
            ('unexpected EOF while parsing (Script (Python), line 1)', {}))

    def test_header_footer(self):
        self.field.header = "foo = 'bar'"
        self.field.footer = "return foo"
        self.field.set(self.folder, "pass")
        self.assertEquals(self.field.get(self.folder), 'bar')
        self.field.set(self.folder, "foo = 'baz'")
        self.assertEquals(self.field.get(self.folder), 'baz')
        self.assertEquals(self.field.getRaw(self.folder), "foo = 'baz'\n")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PythonFieldTest))
    doctests = (
        'Products.PythonField.validators',
        )
    for module in doctests:
        suite.addTest(doctest.DocTestSuite(module))
    return suite
