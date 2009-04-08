# -*- coding: iso-8859-1 -*-
#
# $Id: config.py,v 1.1 2006/08/10 13:16:06 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" This script contains the global constants for the
'ECQuiz' Product."""

import os
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName


def makeTypeList(relativeDir):
    """ Returns a sequence of all the python files in a directory 
        specified by "relativeDir".
    """
    ret = os.listdir(os.path.dirname(__file__)+'/'+ relativeDir)
    ret = [type[:-3] for type in ret
           if type.endswith('.py') and (not type.startswith('__'))]
    return ret

GLOBALS = globals()

# define dependencies
DEPENDENCIES = ['DataGridField']

# The name of the Product
PROJECTNAME = 'ECQuiz'
ECMCR_WORKFLOW_ID    = 'ecq_result_workflow'
ECMCR_WORKFLOW_TITLE = 'Result Workflow [ECQ]'

ECMCT_WORKFLOW_ID    = 'ecq_quiz_workflow'
ECMCT_WORKFLOW_TITLE = 'Test Workflow [ECQ]'

ECMCE_WORKFLOW_ID    = 'ecq_element_workflow'
ECMCE_WORKFLOW_TITLE = 'Element Workflow [ECQ]'

SKINS_DIR = 'skins'

QUESTION_DIR = 'QuestionTypes'
QUESTION_TYPES = makeTypeList(QUESTION_DIR)
                
ANSWER_DIR = 'AnswerTypes'
ANSWER_TYPES = makeTypeList(ANSWER_DIR)

I18N_DOMAIN = 'ECQuiz'

# The name of custom evaluation functions.
CUSTOM_EVALUATION_FUNCTION_NAME = 'getCandidatePointsCustom'

# Types which support custom evaluation functions
CUSTOM_EVALUATION_TYPES = ['ECQuiz', 'ECQGroup', 'ECQMCQuestion']

def addSiteProperties(portal):
    """adds site_properties in portal_properties"""
    id = PROJECTNAME.lower()+'_properties'
    title = 'Site wide properties'
    p=PropertyManager('id')
    if id not in portal.portal_properties.objectIds():
        portal.portal_properties.addPropertySheet(id, title, p)
    p=getattr(portal.portal_properties, id)

##    if not hasattr(p,'allowAnonymousViewAbout'):
##        safeEditProperty(p, 'allowAnonymousViewAbout', 1, 'boolean')
##    if not hasattr(p,'localTimeFormat'):
##        safeEditProperty(p, 'localTimeFormat', '%Y-%m-%d', 'string')
##    if not hasattr(p,'localLongTimeFormat'):
##        safeEditProperty(p, 'localLongTimeFormat', '%Y-%m-%d %H:%M', 'string')
##    if not hasattr(p,'default_language'):
##        safeEditProperty(p, 'default_language', 'en', 'string')
##    if not hasattr(p,'default_charset'):
##        safeEditProperty(p, 'default_charset', 'utf-8', 'string')
##    if not hasattr(p,'use_folder_tabs'):
##        safeEditProperty(p, 'use_folder_tabs',('Folder',), 'lines')
##    if not hasattr(p,'use_folder_contents'):
##        safeEditProperty(p, 'use_folder_contents',[], 'lines')
##    if not hasattr(p,'ext_editor'):
##        safeEditProperty(p, 'ext_editor', 0, 'boolean')
##    if not hasattr(p, 'available_editors'):
##        safeEditProperty(p, 'available_editors', ('None', ), 'lines')
##    if not hasattr(p, 'allowRolesToAddKeywords'):
##        safeEditProperty(p, 'allowRolesToAddKeywords', ['Manager', 'Reviewer'], 'lines')
##    if not hasattr(p, 'auth_cookie_length'):
##        safeEditProperty(p, 'auth_cookie_length', 0, 'int')
##    if not hasattr(p, 'calendar_starting_year'):
##        safeEditProperty(p, 'calendar_starting_year', 1999, 'int')
##    if not hasattr(p, 'calendar_future_years_available'):
##        safeEditProperty(p, 'calendar_future_years_available', 5, 'int'
