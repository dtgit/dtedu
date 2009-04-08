##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFTopic product:  unit test utilities.

$Id: common.py 77369 2007-07-03 16:17:37Z yuppie $
"""

from unittest import TestCase


class CriterionTestCase(TestCase):

    def _makeOne(self, id, *args, **kw):
        return self._getTargetClass()(id, *args, **kw)

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFTopic.interfaces import Criterion as ICriterion

        verifyClass( ICriterion, self._getTargetClass() )

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFTopic.interfaces import ICriterion

        verifyClass(ICriterion, self._getTargetClass())
