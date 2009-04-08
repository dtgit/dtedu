##############################################################################
#
# TALESField - Field with TALES support for Archetypes
# Copyright (C) 2005 Sidnei da Silva, Daniel Nouri and contributors
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
$Id: __init__.py,v 1.2 2005/02/26 17:56:10 sidnei Exp $
"""


# Load fixture
import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import doctest
#from Products.CMFPlone.tests import PloneTestCase
from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()

from Products.TALESField import TALESString, TALESLines

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('TALESField')



class TALESStringTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.field = TALESString('tales')
        self.folder.validate_field = lambda *args, **kw: None

    def validate(self, value):
        errors = {}
        res = self.field.validate(value, self.folder, errors)
        return res, errors

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), True)

    def test_getRaw(self):
        self.assertEquals(self.field.getRaw(self.folder), 'python: True')

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), True)
        self.folder.setTitle('bar')
        self.field.set(self.folder, "python: object.Title() == 'foo'")
        self.assertEquals(self.field.get(self.folder), False)
        self.field.set(self.folder, "python: object.Title() == 'bar'")
        self.assertEquals(self.field.get(self.folder), True)

    def test_set_expr(self):
        # Just make sure setting Expression works too.
        default_expr = self.field.getDefault(self.folder)
        self.field.set(self.folder, default_expr)
        self.assertEquals(self.field.getRaw(self.folder), default_expr.text)

    def test_validate(self):
        self.assertEquals(self.validate('python: True'), (None, {}))
        self.assertEquals(
            self.validate('python: 1 + (2 * 3'),
            ('TALES expression "python: 1 + (2 * 3" has errors.', {}))

    def test_valueIsEmptyString(self):
        self.field.set(self.folder, "")
        self.assertEquals(self.field.get(self.folder), None)


class TALESLinesTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.field = TALESLines('tales')
        self.folder.validate_field = lambda *args, **kw: None

    def validate(self, value):
        errors = {}
        res = self.field.validate(value, self.folder, errors)
        return res, errors

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), [True])

    def test_getRaw(self):
        self.assertEquals(self.field.getRaw(self.folder), ['python: True'])

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), [True])
        self.folder.setTitle('bar')
        self.field.set(
            self.folder,
            ["python: object.Title() == 'foo'",
             "python: object.Title() == 'bar'"])
        self.assertEquals(self.field.get(self.folder), [False, True])

    def test_set_expr(self):
        [default_expr] = self.field.getDefault(self.folder)
        self.field.set(self.folder, [default_expr])
        self.assertEquals(self.field.getRaw(self.folder), [default_expr.text])

    def test_validate(self):
        self.assertEquals(self.validate(['python: True']), (None, {}))
        self.assertEquals(
            self.validate(['python: True', 'python: 1 + (2 * 3']),
            ('TALES expression "python: 1 + (2 * 3" has errors.', {}))

    def test_valueIsEmptyStrings(self):
        self.field.set(self.folder, [""])
        self.assertEquals(self.field.get(self.folder), [None])


def test_suite():
    suite = unittest.TestSuite()
    tests = [
        unittest.makeSuite(TALESStringTest),
        unittest.makeSuite(TALESLinesTest),
        ]
    for t in tests:
        suite.addTest(t)
    doctests = (
        'Products.TALESField.validators',
        )
    for module in doctests:
        suite.addTest(doctest.DocTestSuite(module))
    return suite

