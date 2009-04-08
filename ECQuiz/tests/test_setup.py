# -*- coding: utf-8 -*-
#
# $Id: test_setup.py,v 1.1 2006/10/27 17:45:01 wfenske Exp $
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

from base import ECQTestCase
from Products.ECQuiz.config import *

class TestProductInstall(ECQTestCase):

    def afterSetUp(self):
        ECQTestCase.afterSetUp(self)
        self.typeReference = 'ECQReference'
        self.typeResult = 'ECQResult'
        self.typeQuiz = 'ECQuiz'
        self.typeGroup = 'ECQGroup'
        self.typeQuestions = (#'ECQBaseQuestion',
                              'ECQExtendedTextQuestion',
                              'ECQMCQuestion',
                              #'ECQPointsQuestion',
                              #'ECQRatingQuestion',
                              'ECQScaleQuestion',
                              #'ECQSelectionQuestion',
                              )
        self.typeAnswers = (#'ECQBaseAnswer',
                            #'ECQCorrectAnswer',
                            'ECQMCAnswer',
                            'ECQScaleAnswer',
                            #'ECQSelectionAnswer',
                            )

    def testTypesInstalled(self):
        for t in (self.typeReference,
                  self.typeResult,
                  self.typeQuiz,
                  self.typeGroup,) + \
                  self.typeQuestions + \
                  self.typeAnswers:
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)
    
    def testPortalFactoryEnabled(self):
        pfTypes = self.portal.portal_factory.getFactoryTypes()
        for t in (self.typeReference,
                  self.typeQuiz,
                  self.typeGroup,) + \
                  self.typeQuestions + \
                  self.typeAnswers:
            self.failUnless(pfTypes.has_key(t), '%s content type does not '
                            'use the Portal Factory' % t)

    def testWorkflowsInstalled(self):
        workflowIds = self.portal.portal_workflow.objectIds()
        self.failUnless(ECMCR_WORKFLOW_ID in workflowIds)
        self.failUnless(ECMCT_WORKFLOW_ID in workflowIds)
        self.failUnless(ECMCE_WORKFLOW_ID in workflowIds)
        
    def testWorkflowsMapped(self):
        wf = self.portal.portal_workflow
        gcfpt = wf.getChainForPortalType
        self.assertEquals((ECMCR_WORKFLOW_ID,), gcfpt(self.typeResult))
        self.assertEquals((ECMCT_WORKFLOW_ID,), gcfpt(self.typeQuiz))
        for t in (self.typeGroup,) + self.typeQuestions + self.typeAnswers:
            self.assertEquals((ECMCE_WORKFLOW_ID,), gcfpt(t))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
