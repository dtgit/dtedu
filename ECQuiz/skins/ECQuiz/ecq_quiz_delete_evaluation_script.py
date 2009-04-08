## Script (Python) "deleteEvaluationScript"
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=archetype_name=''
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_quiz_delete_evaluation_script.py,v 1.2 2007/07/04 01:09:26 wfenske Exp $
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

""" Handle deletion of custom scoring scripts. """

REQUEST  = container.REQUEST

I18N_DOMAIN = context.i18n_domain

if not REQUEST.has_key('deleteCustomEvaluationScripts'):
    msg = context.translate(
        msgid   = 'select_item_delete',
        domain  = I18N_DOMAIN,
        default = 'Please select one or more items to delete first.')
else:
    msg = context.translate(
        msgid   = 'scoring_scripts_deleted',
        domain  = I18N_DOMAIN,
        default = 'Deleted custom scoring scripts for types: ')
    #msg = REQUEST.get('deleteCustomEvaluationScripts')
    deleted = []
    scriptsToBeDeleted = []
    evaluationScripts = context.getEvaluationScripts()

    if same_type(REQUEST['deleteCustomEvaluationScripts'], []):
        scriptsToBeDeleted += REQUEST['deleteCustomEvaluationScripts']
    else:
        scriptsToBeDeleted.append(REQUEST['deleteCustomEvaluationScripts'])
    
    for script in scriptsToBeDeleted:
        if(evaluationScripts.has_key(script)):
            evaluationScripts.pop(script)
            deleted.append(script)
    
    context.setEvaluationScripts(evaluationScripts)

    msg += ", ".join(deleted)
        
target = context.getActionInfo('object/import_export')['url']
context.redirect('%s?portal_status_message=%s' % (target, msg))
