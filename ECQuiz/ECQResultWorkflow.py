# -*- coding: iso-8859-1 -*-
#
# $Id: ECQResultWorkflow.py,v 1.2 2006/08/14 11:39:09 wfenske Exp $
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

"""
Workflow for ECQResult objects
"""

__author__    = 'wfenske <wfenske@cs.uni-magdeburg.de>'
__docformat__ = 'plaintext'
__version__   = '$Revision: 1.2 $'

from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, \
     TRIGGER_USER_ACTION, TRIGGER_WORKFLOW_METHOD

from Products.CMFCore.permissions import ManageProperties

from config import *
from permissions import *

def setupWorkflow(wf):
    """Result Workflow Definition"""

    isTestOwner = ('python: user.has_permission("Review portal content", '
                   '        here.aq_parent) or '
                   '        user.has_role("Owner", here.aq_parent)')
    

    ###########################################################################
    #                     Declare States, Transitions, etc.                   #
    ###########################################################################

    wf.setProperties(title=ECMCR_WORKFLOW_TITLE)
    
    for s in ['unsubmitted',
              'pending',
              'graded',
              'superseded',
              'invalid',
              ]:
        wf.states.addState(s)

    for t in ['submit_pending',  # unsubmitted       -> pending
              'submit_graded',   # unsubmitted       -> graded
#             'unsubmit',        # {pending, graded} -> unsubmitted
              'grade',           # pending           -> graded
              'retract_pending', # graded            -> pending
              #'retract_graded',  # superseded        -> graded
              'supersede',       # {pending, graded} -> superseded
              'invalidate',      # *                 -> invalid
              ]:
        wf.transitions.addTransition(t)

    for v in ['review_history',
              'comments',
              'time',
              'actor',
              'action',
              ]:
        wf.variables.addVariable(v)

    for p in ['Access contents information',
              ManageProperties,
              'Modify portal content',
              'View',
              'List folder contents',
              PERMISSION_RESULT_READ,
              PERMISSION_RESULT_WRITE,
              ]:
        wf.addManagedPermission(p)

    wf.states.setInitialState('unsubmitted')
    

    ###########################################################################
    #                             Define States                               #
    ###########################################################################

    sdef = wf.states['unsubmitted']
    sdef.setProperties(title='Not Submitted',
                       transitions=('submit_pending',
                                    'submit_graded',
                                    'invalidate'))
    sdef.setPermission('Access contents information',
                       0,
                       [#'Owner',
#                         'Reviewer',
#                         'Manager',
#                         ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission('Modify portal content',
                       0,
                       [#'Owner',
#                         'Reviewer',
#                         'Manager',
#                         ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission(ManageProperties,
                       0,
                       [#'Owner',
#                         'Reviewer',
#                         'Manager',
#                         ROLE_RESULT_GRADER
                        ])
    sdef.setPermission('View',
                       0,
                       [#'Owner',
                         'Reviewer',
                         'Manager',
#                         ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_READ,
                       0,
                       ['Owner',
                        ])
    sdef.setPermission(PERMISSION_RESULT_WRITE,
                       0,
                       ['Owner',
                        ])
    sdef.setPermission('List folder contents',
                       0,
                       [# 'Reviewer',
#                         'Manager',
#                         ROLE_RESULT_GRADER,
                        ])

    sdef = wf.states['pending']
    sdef.setProperties(title='Pending',
                       transitions=('grade', 'supersede', 'invalidate'))
    sdef.setPermission('Access contents information',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission(ManageProperties,
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_READ,
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_WRITE,
                       0,
                       [])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])

    sdef = wf.states['graded']
    sdef.setProperties(title='Graded',
                       transitions=('supersede', 'retract_pending',
                                    'invalidate'))
    sdef.setPermission('Access contents information',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission(ManageProperties,
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_READ,
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_WRITE,
                       0,
                       [])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])

    sdef = wf.states['superseded']
    sdef.setProperties(title='Superseded',
                       transitions=('invalidate',))
    sdef.setPermission('Access contents information',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission(ManageProperties,
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_READ,
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])
    sdef.setPermission(PERMISSION_RESULT_WRITE,
                       0,
                       [])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        ROLE_RESULT_GRADER,
                        ROLE_RESULT_VIEWER,
                        ])

    sdef = wf.states['invalid']
    sdef.setProperties(title='Invalid',
                       transitions=())
    sdef.setPermission('Access contents information',
                       0,
                       ['Reviewer',
                        'Manager',
                        ])
    sdef.setPermission('Modify portal content',
                       0,
                       ['Reviewer',
                        'Manager',
                        ])
    sdef.setPermission(ManageProperties,
                       0,
                       ['Reviewer',
                        'Manager',
                        ])
    sdef.setPermission('View',
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager'])
    sdef.setPermission(PERMISSION_RESULT_READ,
                       0,
                       ['Owner',
                        'Reviewer',
                        'Manager',
                        ])
    sdef.setPermission(PERMISSION_RESULT_WRITE,
                       0,
                       [])
    sdef.setPermission('List folder contents',
                       0,
                       ['Reviewer',
                        'Manager',
                        ])
    

    ###########################################################################
    #                             Define Transitions                          #
    ###########################################################################

    tdef = wf.transitions['submit_pending']
    tdef.setProperties(
        title='Submit a result and wait for tutor to grade it',
        new_state_id='pending',
        trigger_type=1,
        script_name='',
        after_script_name='',
        # actbox_name='Submit',
        actbox_url='',
        actbox_category='workflow',
        props={
            'guard_roles': 'Owner',
            'guard_expr' : 'python:here.aq_parent.isTutorGraded(here)',
            },
        )

    tdef = wf.transitions['submit_graded']
    tdef.setProperties(
        title='Submit a result and automatically grade it',
        new_state_id='graded',
        trigger_type=1,
        script_name='',
        after_script_name='',
        # actbox_name='Submit',
        actbox_url='',
        actbox_category='workflow',
        props={
            'guard_roles': 'Owner',
            'guard_expr' : 'python:not here.aq_parent.isTutorGraded(here)',
            },
        )

    tdef = wf.transitions['grade']
    tdef.setProperties(
        title='Grade a result',
        new_state_id='graded',
        trigger_type=1,
        script_name='',
        after_script_name='',
        actbox_name='Grade',
        actbox_url='',
        actbox_category='workflow',
        props={
            'guard_roles': ';'.join((ROLE_RESULT_GRADER,
                                     'Manager',
                                     )),
            'guard_expr' : 'python:here.aq_parent.getCandidatePoints(here) is not None',
            },
        )

    tdef = wf.transitions['retract_pending']
    tdef.setProperties(
        title='Result is reset to pending state',
        new_state_id='pending',
        trigger_type=1,
        script_name='',
        after_script_name='',
        actbox_name='Retract',
        actbox_url='',
        actbox_category='workflow',
        props={
            'guard_roles': ';'.join((ROLE_RESULT_GRADER,
                                     'Manager',
                                     )),
            'guard_expr' : 'python:here.aq_parent.isTutorGraded(here)',
            },
        )

#     tdef = wf.transitions['retract_graded']
#     tdef.setProperties(
#         title='Result is reset to graded state',
#         new_state_id='graded',
#         trigger_type=1,
#         script_name='',
#         after_script_name='',
#         actbox_name='Retract',
#         actbox_url='',
#         actbox_category='workflow',
#         props={
#             'guard_roles': ';'.join((ROLE_RESULT_GRADER,
#                                      'Manager',
#                                      )),
#             'guard_expr' : 'python:not here.aq_parent.isTutorGraded(here)',
#             },
#         )

    tdef = wf.transitions['supersede']
    tdef.setProperties(
        title='Replace a submission with a newer one',
        new_state_id='superseded',
        trigger_type=1,
        script_name='',
        after_script_name='',
        # actbox_name='Supersede',
        actbox_url='',
        actbox_category='workflow',
        props={
            'guard_roles': 'Owner',
            'guard_expr' : 'python:here.aq_parent.isAllowRepetition()',
            },
        )

    tdef = wf.transitions['invalidate']
    tdef.setProperties(
        title='Invalidate a result because the quiz has changed.',
        new_state_id='invalid',
        trigger_type=1,
        script_name='',
        after_script_name='',
        # actbox_name='',
        actbox_url='',
        actbox_category='workflow',
        props={'guard_expr': isTestOwner},
        )
    

    ###########################################################################
    #                             History stuff                               #
    ###########################################################################
    
    wf.variables.setStateVar('review_state')

    vdef = wf.variables['review_history']
    vdef.setProperties(description='Provides access to workflow history',
                       default_value='',
                       default_expr='state_change/getHistory',
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions':
                              'Request review; Review portal content'})
    vdef = wf.variables['comments']
    vdef.setProperties(description='Comments about the last transition',
                       default_value='',
                       default_expr="python:state_change.kwargs.get('comment', '')",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['time']
    vdef.setProperties(description='Time of the last transition',
                       default_value='',
                       default_expr='state_change/getDateTime',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['actor']
    vdef.setProperties(description='The ID of the user who performed the '
                       'last transition',
                       default_value='',
                       default_expr='user/getUserName',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
    vdef = wf.variables['action']
    vdef.setProperties(description='The last transition',
                       default_value='',
                       default_expr='transition/getId|nothing',
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)


def createWorkflow(id):
    """workflow creation"""
    ob = DCWorkflowDefinition(id)
    setupWorkflow(ob)
    return ob

addWorkflowFactory(createWorkflow,
                   id=ECMCR_WORKFLOW_ID,
                   title=ECMCR_WORKFLOW_TITLE)
