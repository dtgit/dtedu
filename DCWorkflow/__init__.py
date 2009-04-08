##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Web-configurable workflow.

$Id: __init__.py 68513 2006-06-07 16:45:25Z yuppie $
"""

from Products.CMFCore.utils import registerIcon

import DCWorkflow, States, Transitions, Variables, Worklists, Scripts


def initialize(context):

    context.registerHelp(directory='help')
    context.registerHelpTitle('DCWorkflow')

    registerIcon(DCWorkflow.DCWorkflowDefinition,
                 'images/workflow.gif', globals())
    registerIcon(States.States,
                 'images/state.gif', globals())
    States.StateDefinition.icon = States.States.icon
    registerIcon(Transitions.Transitions,
                 'images/transition.gif', globals())
    Transitions.TransitionDefinition.icon = Transitions.Transitions.icon
    registerIcon(Variables.Variables,
                 'images/variable.gif', globals())
    Variables.VariableDefinition.icon = Variables.Variables.icon
    registerIcon(Worklists.Worklists,
                 'images/worklist.gif', globals())
    Worklists.WorklistDefinition.icon = Worklists.Worklists.icon
    registerIcon(Scripts.Scripts,
                 'images/script.gif', globals())
