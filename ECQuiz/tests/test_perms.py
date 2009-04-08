# -*- coding: utf-8 -*-
#
# $Id: test_perms.py,v 1.1 2006/10/27 17:45:01 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from AccessControl import Unauthorized

from base import ECQTestCase
from Products.ECQuiz.config import *
from Products.ECQuiz.tools import createObject

def getAccessor(obj, prop_name, getter_p):
    if getter_p:
        prefix = 'get'
    else:
        prefix = 'set'
    name = prefix + prop_name[0].upper() + prop_name[1:]
    return getattr(obj, name)

def setProp(obj, prop_name, value):
    f = getAccessor(obj, prop_name, False)
    f(value)

def getProp(obj, prop_name):
    f = getAccessor(obj, prop_name, True)
    return f()

def setProps(obj, props_values):
    for p, v in props_values:
        setProp(obj, p, v)

class TestPermissions(ECQTestCase):

    def createDummy(self):
        self.login('manager')
        portal = self.portal
        # dummy = ECQuiz(oid='dummy')
        # # put dummy in context of portal
        # dummy = dummy.__of__(portal)
        # portal.dummy = dummy
        # dummy.initializeArchetype()
        # return dummy
        dummy = createObject(self.portal, 'ECQuiz', 'dummy')
        portal.dummy = dummy
        # Set up the test's properties
        setProps(dummy, (('instantFeedback', False),
                         ('allowRepetition', False),
                         ('onePerPage', False),
                         ('onePerPageNav', False),
                         ('scoringFunction', 'cruel'),
                         #('gradingScale', ()),
                         ('directions', 'Please answer these questions!'),
                         ('randomOrder', False),
                         ('numberOfRandomQuestions', 0),))
        # Create an MC question
        mcq = createObject(dummy, 'ECQMCQuestion', 'mcq')
        # Set up the question's properties
        setProps(mcq, (('allowMultipleSelection', False),
                       ('randomOrder', False),
                       ('numberOfRandomAnswers', 0),
                       ('points', 666),
                       ('tutorGraded', False),
                       ))
        # Create MC answers
        for uid, comm, corr, answ in (('mca1', 'Correct comment', True,  'This is correct.'),
                                      ('mca2', 'Wrong comment',   False, 'This is wrong.'  ),
                                      ):
            mca = createObject(mcq, 'ECQMCAnswer', uid)
            # Set up the answer's properties
            setProps(mca, (('comment', comm),
                           ('correct', corr),
                           ('answer',  answ),
                           ))
        # publish the thing
        wtool = portal.portal_workflow
        wtool.doActionFor(dummy, 'publish')
        
        return dummy
    

    def afterSetUp(self):
        ECQTestCase.afterSetUp(self)
        self.membership = self.portal.portal_membership
        self.membership.addMember('member', 'secret', ['Member'], [])
        self.membership.addMember('manager', 'secret', ['Manager'], [])
        self.login('manager')
        self._dummy = self.createDummy()

    
    def testQuizPerms(self):
        t = self._dummy
        self.login('member')
        
        self.assertRaises(Unauthorized, t.maybeMakeNewTest)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPermissions))
    return suite
