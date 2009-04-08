from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.CMFCore.permissions import AccessContentsInformation, \
        ListFolderContents, ModifyPortalContent, View
from Products.CMFPlone.FolderWorkflow import setupFolderWorkflow

from config import *
from permissions import *


def setupTestWorkflow(wf):
    setupFolderWorkflow(wf)

    # Fix titles for default workflow states (from
    # Products/CMFPlone/migrations/v2_1/betas.py)
    state_titles = { 'private'  : 'Private',
                     'visible'  : 'Public Draft',
                     'pending'  : 'Pending',
                     'published': 'Published',
                    }
    for state, title in state_titles.items():
        wf_state = getattr(wf.states, state, None)
        if (wf_state is not None) and (wf_state.title != title):
            wf_state.title = title

    wf.permissions+=(PERMISSION_STUDENT,)
    wf.states.setInitialState(id='visible')

    for state in ('private', 'visible', 'published'):
        sdef = wf.states[state]
        student_roles = ('Owner',
                         'Reviewer',
                         'Manager',
                         ROLE_RESULT_GRADER,
                         )
#         modify_roles  = ('Manager',
#                          'Owner',
#                          )
        if state != 'private':
            student_roles += ('Authenticated',)
#             modify_roles  += (ROLE_RESULT_GRADER,)
        sdef.setPermission(PERMISSION_STUDENT,  0, student_roles)
#         sdef.setPermission(ModifyPortalContent, 0, modify_roles)
    
    roles = ('Owner',
             'Reviewer',
             'Manager',
             ROLE_RESULT_GRADER,
             )
    for perm in (ListFolderContents,
                 View,
                 ):
        wf.states.private.permission_roles[perm] = roles
        wf.states.visible.permission_roles[perm] = roles


def setupElementWorkflow(wf):
    setupTestWorkflow(wf)

    # Deny 'Authenticated' permission to [ListFolderContents] and
    # [View] elements of an ECQuiz /even if/ they are published.
    roles = ('Owner',
             'Reviewer',
             'Manager',
             ROLE_RESULT_GRADER,
             )
    for perm in (ListFolderContents,
                 View,
                 ):
        wf.states.published.permission_roles[perm] = roles


def createTestWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupTestWorkflow(ob)
    ob.setProperties(title=ECMCT_WORKFLOW_TITLE)
    return ob


def createElementWorkflow(id):
    ob=DCWorkflowDefinition(id)
    setupElementWorkflow(ob)
    ob.setProperties(title=ECMCE_WORKFLOW_TITLE)
    return ob


addWorkflowFactory(createTestWorkflow,
                   id=ECMCT_WORKFLOW_ID,
                   title=ECMCT_WORKFLOW_TITLE)

addWorkflowFactory(createElementWorkflow,
                   id=ECMCE_WORKFLOW_ID,
                   title=ECMCE_WORKFLOW_TITLE)
