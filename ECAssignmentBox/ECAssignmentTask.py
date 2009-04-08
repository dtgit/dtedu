# -*- coding: utf-8 -*-
# Copyright (c) 2007 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
#
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.base import registerATCT#, updateActions, \
#     updateAliases
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolderSchema,ATFolder

from Products.ECAssignmentBox import permissions
from Products.ECAssignmentBox.config import *
from Products.ECAssignmentBox.PlainTextField import PlainTextField

ECAssignmentTaskSchema = ATFolderSchema.copy() + Schema((
#	TextField(
#		'directions',
#		default_content_type = 'text/structured',
#		default_output_type = 'text/html',
#		allowable_content_types = TEXT_TYPES,
#		widget = RichWidget(
#			label = 'Directions',
#			label_msgid = 'label_directions',
#			description = 'Instructions/directions for that assignment task',
#			description_msgid = 'help_directions',
#			i18n_domain = I18N_DOMAIN,
#			rows = 10,
#			cols = 20,
#		),
#	),
	TextField(
		'assignment_text',
		required = True,
		searchable = True,
		default_output_type = 'text/html',
		default_content_type = 'text/structured',
		allowable_content_types = TEXT_TYPES,
		widget = RichWidget(
			label = 'Assignment text',
			label_msgid = 'label_assignment_text',
			description = 'Enter text and hints for the assignment',
			description_msgid = 'help_assignment_text',
			i18n_domain = I18N_DOMAIN,
			rows=10,
		),
	),
	PlainTextField(
		'answerTemplate',
		widget = RichWidget(
			label = 'Answer template',
			label_msgid = 'label_answer_template',
			description = 'You can provide a template for the students\' answers',
			description_msgid = 'help_answer_template',
			i18n_domain = I18N_DOMAIN,
			rows = 12,
			format = 0,
		),
	),
))

finalizeATCTSchema(ECAssignmentTaskSchema)

class ECAssignmentTask(ATFolder):
	"""Defines the task for an assignment box"""

	portal_type = meta_type = ECAT_META
	archetype_name = ECAT_NAME
	content_icon = 'ecat.png'
	schema = ECAssignmentTaskSchema
	typeDescription = 'Defines the task for an assignment box.'
	typeDescMsgID = 'description_edit_ecat'

	_at_rename_after_creation = True
	__implements__ = ATFolder.__implements__

	# Attach views
	default_view = 'ecat_view'
	immediate_view = 'ecat_view'
	suppl_views = None

#	actions = updateActions(ATFolder, (
#                {'action':      'string:$object_url/ecat_backlinks',
#                 'category':    'object',
#                 'id':          'ecat_backlinks',
#                 'name':        'Backlinks',
#                 'permissions': (permissions.ManageProperties,),},
#                ))
#
#	aliases = updateAliases(ATFolder, {
#		'view'		: 'ecat_view',
#	})


registerATCT(ECAssignmentTask,PROJECTNAME)
