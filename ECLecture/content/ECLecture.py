# -*- coding: utf-8 -*-
# $Id: ECLecture.py,v 1.22 2008/01/06 14:36:49 peilicke Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
# ECLecture is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECLecture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECLecture; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re
from types import StringType, IntType

from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.utils import log

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import LinesWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import CalendarWidget
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import TextAreaWidget

from Products.ATContentTypes.configuration import zconf

from Products.ATContentTypes.content.base import registerATCT
#from Products.ATContentTypes.content.base import updateActions, updateAliases

#from Products.ATContentTypes.content.folder import ATFolderSchema
#from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.interfaces import IATEvent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
#from Products.DataGridField.Column import Column
#from Products.DataGridField.LinkColumn import LinkColumn

from DateTime import DateTime
import urllib

# local imports
try:
    from Products.ECAssignmentBox.ECFolder import ECFolder as SuperClass
    from Products.ECAssignmentBox.ECFolder import ECFolderSchema as SuperSchema
except:
    from Products.ATContentTypes.content.folder import ATFolder as SuperClass
    from Products.ATContentTypes.content.folder import ATFolderSchema as SuperSchema

from Products.ECLecture.config import PRODUCT_NAME, ECL_NAME, ECL_TITLE, \
     ECL_META, ECL_ICON, I18N_DOMAIN, edit_permission
from TimePeriodField import TimePeriodField

NO_RECURRENCE = 0
DAILY = 1
WEEKLY = 2
MONTHLY = 3
YEARLY = 4

NO_GROUP = ''

# -- schema definition --------------------------------------------------------
ECLectureSchema = SuperSchema.copy() + Schema((

    StringField('courseType',
        required = False,
        widget = StringWidget(
            label = "Course type",
            description = "Enter the type of this course (e.g., Lecture or Lab Exercise)",
            label_msgid = 'label_course_type',
            description_msgid = 'help_course_type',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    LinesField('instructors',
        #TWB Change
        #required = True,
        required = False,
        languageIndependent = True,
        searchable = True,
        widget = LinesWidget(
            label = "Instructors",
            description = "User names or names of instructors, one per line",
            label_msgid = 'label_instructors',
            description_msgid = 'help_instructors',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TimePeriodField('timePeriod',
        accessor = 'getTimePeriod',
        edit_accessor = 'getTimePeriodForEdit',

        #TWB Change
        #required = True,
        required = False,

        default = ['11:00', '13:00'],
        widget = StringWidget(
            macro = 'time_period',
            size = 5,
            maxlength = 5,
            label = "Time period",
            description = "Start and end times of this course",
            label_msgid = 'label_time_period',
            description_msgid = 'help_time_period',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    DateTimeField('startDate',

        #TWB Change
        #required = True,
        required = False,

        widget = CalendarWidget(
            label = "Start date",
            description = "First regular date",
            label_msgid = 'label_start_date',
            description_msgid = 'help_start_date',
            show_hm = False, 
            #show_ymd = True,
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    
    DateTimeField('endDate',

        #TWB Change
        #required = True,
        required = False,


        widget = CalendarWidget(
            label = "End date",
            description = "Last regular date",
            label_msgid = 'label_end_date',
            description_msgid = 'help_end_date',
            show_hm = False, 
            #show_ymd = True,
            i18n_domain = I18N_DOMAIN,
        ),
    ),
                                                   
    IntegerField('recurrence',
        #TWB Change
        #required = True,
        required = False,

        vocabulary = 'getRecurrenceDisplayList',
        default = WEEKLY,
        widget = SelectionWidget(
            format = "radio", # possible values: flex, select, radio
            label = "Recurrence",
            description = "How often this course takes place",
            label_msgid = 'label_recurrence',
            description_msgid = 'help_recurrence',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
                                                   
    DateTimeField('firstSession',
        widget = CalendarWidget(
            label = "First session",
            description = "Date for the first session for this course",
            label_msgid = 'label_first_session',
            description_msgid = 'help_first_session',
            #show_hm = False, 
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('location',
        #TWB Change
        #required = True,
        required = False,

        widget = StringWidget(
            label = "Location",
            description = "Location for this course",
            label_msgid = 'label_location',
            description_msgid = 'help_location',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('courseLanguage',
        vocabulary = 'getLanguagesDL',
        widget = SelectionWidget(
            label = 'Language of instruction',
            description = 'The language used for teaching this course',
            label_msgid = 'label_course_language',
            description_msgid = 'help_course_language',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('credits',
        required = False,
        widget = StringWidget(
            label = "Credits",
            description = "Credits which can be gained in this course",
            label_msgid = 'label_credits',
            description_msgid = 'help_credits',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TextField('prereq',
        required = False,
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = TextAreaWidget(
            label = "Prerequisites",
            description = "Describe which prerequisites are required for this course",
            label_msgid = 'label_prereq',
            description_msgid = 'help_prereq',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TextField('target',
        required = False,
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = TextAreaWidget(
            label = "Target group",
            description = "Describe for which audience this course is intended",
            label_msgid = 'label_target',
            description_msgid = 'help_target',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField('maxParticipants',
        required = False,
        widget = StringWidget(
            label = "Maximum number of participants",
            size = 4,
            description = "If there is an enrollment limit, specify the maximum number of participants",
            label_msgid = 'label_max_participants',
            description_msgid = 'help_max_participants',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('joinURL',
        required = False,
        #default value for TWB
        default = 'ecl_register',
        widget = StringWidget(
            label = "Registration link",
            description = "Link to the registration for this course",
            label_msgid = 'label_join_url',
            description_msgid = 'help_join_url',
            size = 65,
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('directoryEntry',
        required = False,
        widget = StringWidget(
            label = "Directory entry",
            description = "Link to the directory entry for this course",
            label_msgid = 'label_directory_entry',
            description_msgid = 'help_directory_entry',
            size = 65,
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    StringField('associatedGroup',
        required = False,
        vocabulary = 'getGroupsDisplayList',
        #default = NO_GROUP,
        #Adding default value for TWB
        default = 'CTMParticipant',
        widget = StringWidget(
            label = "Associated group",
            description = "You can associate a group with this course to represent its participants",
            label_msgid = 'label_associated_group',
            description_msgid = 'help_associated_group',
            size = 65,
            i18n_domain = I18N_DOMAIN,
        ),

        #widget = SelectionWidget(
        #    format = "select", # possible values: flex, select, radio
        #    label = "Associated group",
        #    description = "You can associate a group with this course to represent its participants",
        #    label_msgid = 'label_associated_group',
        #    description_msgid = 'help_associated_group',
        #    i18n_domain = I18N_DOMAIN,
    ),

    DataGridField('availableResources',
        searchable = True,
        #default_method = 'getDefaultResources',
        #required = True,
        columns = ('title', 'url'),
        allow_empty_rows = False,
        widget = DataGridWidget(
            label_msgid = 'label_available_resourcess',
            label = "Available resources",
            description_msgid = 'help_available_resources',
            description = """Enter available resources for this course. Title 
is the name of a resource as shown to the user, URL must be a path inside
this site or an URL to an external source. Please remember that published 
items inside this course are added by default.""",
            column_names = ('Title', 'URL',),
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    TextField('text',
        #required=True,
        searchable=True,
        primary=True,
        #storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = RichWidget(
            label = "Body Text",
            label_msgid = "label_body_text",
            description = "Enter course information",
            description_msgid = "help_body_text",
            rows = 18,
            i18n_domain = I18N_DOMAIN,
            allow_file_upload = zconf.ATDocument.allow_document_upload, 

        )
    ),

),)

if 'directions' in ECLectureSchema:
    # hide directions field if inheriting from ECFolder
    ECLectureSchema['directions'].widget.visible = {'view' : 'invisible',
                                                    'edit' : 'invisible' }
    # move inherited fields to separate edit page
    ECLectureSchema['completedStates'].schemata = 'ecfolder'
    ECLectureSchema['projectedAssignments'].schemata = 'ecfolder'


finalizeATCTSchema(ECLectureSchema, folderish=True, moveDiscussion=False)


class ECLecture(SuperClass):
    """A folder which contains lecture information."""

    __implements__ = (SuperClass.__implements__, IATEvent)

    security       = ClassSecurityInfo()

    schema         =  ECLectureSchema


    content_icon   = ECL_ICON
    meta_type      = ECL_META
    portal_type    = ECL_META
    archetype_name = ECL_TITLE

    default_view   = 'ecl_view'
    immediate_view = 'ecl_view'

    #suppl_views    = ()
    _at_rename_after_creation = True

    typeDescription = "A folder containing details about a lecture or a course."
    typeDescMsgId = 'description_edit_eclecture'

    # -- actions --------------------------------------------------------------
    """actions = updateActions(SuperClass, (
        {
        'action':      'string:$object_url/ecl_participants',
        'category':    'object',
        'id':          'ecl_participants',
        'name':        'Participants',
        'permissions': (edit_permission,),
        'condition'  : 'python: here.associatedGroup'
        },
    ))

    aliases = updateAliases(SuperClass, {
        'view': 'ecl_view',
        })"""

    # -- methods --------------------------------------------------------------
    security.declarePublic('getRecurrenceDisplayList')
    def getRecurrenceDisplayList(self):
        """
        Returns a display list of recurrence types.
        """
        dl = DisplayList(())
        
        dl.add(NO_RECURRENCE, self.translate(msgid='once', domain=I18N_DOMAIN,
                                             default='once'))
        dl.add(DAILY, self.translate(msgid='daily', domain=I18N_DOMAIN,
                                     default='daily'))
        dl.add(WEEKLY, self.translate(msgid='weekly', domain=I18N_DOMAIN,
                                      default='weekly'))
        dl.add(MONTHLY, self.translate(msgid='monthly', domain=I18N_DOMAIN,
                                       default='monthly'))
        # dl.add(YEARLY, self.translate(msgid='yearly', domain=I18N_DOMAIN,
        #                               default='yearly'))

        return dl

    security.declarePublic('getGroupsDisplayList')
    def getGroupsDisplayList(self):
        """
        Return all available groups as a display list.
        """
        dl = DisplayList(())
        dl.add(NO_GROUP, '----')

        #groups_tool = getToolByName(self, 'portal_groups')
        #groups = groups_tool.searchForGroups(REQUEST=None)
        # HINT: There is a problem with searchForGroups in Plone 2.5
        #groups = groups_tool.listGroups()
        
        #Plone-3.5 Deprecation warning fix:
        groups = self.acl_users.getGroups()

        for group_data in groups:
            # The following line causes an error under Plone-3:
            #dl.add(group.getGroupId(), group.getGroupName())
            # A workaround (does nearly the same as the above functions):
            dl.add(group_data.getId(), group_data.getName())
        
        return dl


    security.declareProtected(permissions.View, 'getLanguagesDL')
    def getLanguagesDL(self):
        """
        Vocabulary method for the courseLanguage field.

        This method is based on languages() in ExtensibleMetadata.py. 
        availableLanguages() is defined in a Script (Python)
        (CMFPlone/skins/plone_scripts/availableLanguages.py)
        """
        available_langs = getattr(self, 'availableLanguages', None)
        if available_langs is None:
            return DisplayList(
                (('en','English'), ('de','German'), ('fr','French'),
                 ('es','Spanish'), ('pt','Portuguese'), ('ru','Russian')))
        if callable(available_langs):
            available_langs = available_langs()
        return DisplayList(available_langs)


    def getGroupMembers(self, groupname):
        """
        This is a horrible workaround for the silly and totally
        unnecessary (the code is already there!) limitation that you
        can't retrieve the group members for groups stored in LDAP.

        Returns a list of member objects.
        """
        mtool = self.portal_membership
        #groups = self.portal_groups.listGroupIds()
        #Plone-3.5 Deprecation warning fix:
        groups = self.acl_users.getGroupIds()

        members = []

        if groupname:
            for userid in mtool.listMemberIds():
                if userid:
                    member = mtool.getMemberById(userid)
                    if 'group_' + groupname in member.getGroups():
                        members.append(member)
            # end for
        # end if

        return members


    def getGroupMembersMailto(self, groupMembers, type=None):
        """
        Return a mailto: link with the e-mail addresses of the users
        given in groupMembers (a list of user names). If type is
        'bcc', create a link that contains the user in the To: header
        and the participants in the Bcc: header.
        """
        currentUser = self.portal_membership.getAuthenticatedMember()
        currentEmail = currentUser.getProperty('email')
        addresses = []

        for user in groupMembers:
            email = user.getProperty('email')
            if email != currentEmail and email not in addresses:
                addresses.append(email)

        if type == 'bcc':
            return 'mailto:?to=%s&bcc=%s' % (currentEmail, ','.join(addresses))
        else:
            return 'mailto:%s' % ','.join(addresses)

        #return 'mailto:' + ','.join([urllib.quote(user.getProperty('email'))
        #                      for user in groupMembers])


    security.declarePublic('isParticipant')
    def isParticipant(self, user_id):
        """ """
        group = self.associatedGroup
        member = self.portal_membership.getMemberById(str(user_id))
        if hasattr(member, 'getGroups'):
            return group in member.getGroups()
            #return group in member.getGroupsWithoutPrefix()
        else:
            # This can happen for users who are not members of the
            # Plone site (admin)
            return False


    security.declarePublic('hasEnrollmentLimitReached')
    def hasEnrollmentLimitReached(self):
        """
        Returns wether or not a user can enroll in this course due to the
        enrollment limit (maxParticipants).
        """
        max = self.getMaxParticipants();
        current = len(self.getGroupMembers(self.getAssociatedGroup()))
        
        if max: 
            result = not (current < max)
        else:
            result = False
              
        return result
    

    security.declarePublic('addParticipant')
    def addParticipant(self, user_id):
        """
        Add a user to the group associated with this lecture.
        """
        #groups_tool = getToolByName(self, 'portal_groups')
        #group = groups_tool.getGroupById(self.associatedGroup)


        #group = self.acl_users.getGroupByName(self.associatedGroup)
        group = self.acl_users.getGroupById(str(self.associatedGroup))


        #log('xxx: %s' % self.associatedGroup)
        #log('xxx: %s' % group)

        # FIXME: There is a problem in Plone 2.5: acl_users.getGroupByName 
        #        returns None
        if group:
            try:

                #group.addMember(user_id)
                self.portal_groups._getGroupManagers()[0][1].addPrincipalToGroup(user_id, group.id)
            except ValueError, ve:
                # This can happen for users who are not members of the
                # Plone site (admin)
                log('addParticipant: %s' % ve)
                return False
        else:
            raise Exception('%s is not a valid group.' % self.associatedGroup)
            
        return True
            

    security.declarePublic('removeParticipant')
    def removeParticipant(self, user_id):
        """
        Remove a user from the group associated with this lecture.
        """
        group = self.associatedGroup

        if group:
            try:
                #self.acl_users.getGroupByName(group).removeMember(user_id)
                self.acl_users.getGroupByName(str(group)).removeMember(user_id)
            except ValueError, ve:
                # This can happen for users who are not members of the
                # Plone site (admin)
                log('removeParticipant: %s', ve)
                return False
            return True


    security.declarePublic('getTimePeriod')
    def getTimePeriod(self):
        """
        @return a string representing a time period
        """
        value = self.getTimePeriodForEdit()
        return '–'.join(value)


    security.declarePublic('getStartDateWeekday')
    def getStartDateWeekday(self):
        """
        """
        if self.recurrence in [NO_RECURRENCE, WEEKLY]:
            date = self.getField('startDate').get(self)
            if date:
                return date.Day()


    security.declarePrivate('getTimePeriodForEdit')
    def getTimePeriodForEdit(self):
        """
        @return a list with two values representing start and end time of a 
                time period
        """
        value = self.getField('timePeriod').get(self)
        result = []

        try:
            for item in value:
                if type(item) is IntType:
                    result.append('%02d:%02d' % (item/60, item%60))
                elif type(item) is StringType:
                    # When the object is created, this can be the
                    # default value (a string)
                    result.append(item)
        except:
            raise Exception(repr(item))
            
        return result
    
    
#    def getDefaultResources(self):
#        """
#        """
#        slidesTitle = self.translate(domain=I18N_DOMAIN,
#                                     msgid='default_slides_title',
#                                     default='Slides')
#        
#        assignmentsTitle = self.translate(domain=I18N_DOMAIN,
#                                          msgid='default_assignments_title',
#                                          default='Assignments')
#
#        return ({'title':slidesTitle, 'url':'slides', 
#                'icon':'book_icon.gif'},                    
#               {'title':assignmentsTitle, 'url':'assignments', 
#                'icon':'topic_icon.gif'},
#        )

    security.declarePublic('start')
    def start(self):
        """
        Method providing an Event-like interface (works with
        CalendarX, for example).
        """
        date = getattr(self, 'startDate', None)
        return date is None and self.created() or date

    security.declarePublic('end')
    def end(self):
        """
        Method providing an Event-like interface (works with
        CalendarX, for example).
        """
        date = getattr(self, 'endDate', None)
        return date is None and self.start() or date    

    security.declarePublic('lectureTakesPlace')
    def lectureTakesPlace(self, datetime=None):
        """
        Return True if the lecture takes place on the given date. If
        no date is specified, the current date will be used.

        TODO: Currently not implemented for monthly and yearly recurrence.
        """
        
        result = False
        if not datetime:
            datetime = DateTime()

        if datetime >= self.startDate.earliestTime() \
               and datetime <= self.endDate.latestTime():
            if self.recurrence == NO_RECURRENCE:
                result = self.startDate.isCurrentDay()
            elif self.recurrence == DAILY:
                result = True
            elif self.recurrence == WEEKLY:
                result = datetime.dow() == self.startDate.dow()
            elif self.recurrence == MONTHLY:
                # TODO
                result = False
            elif self.recurrence == YEARLY:
                # TODO
                result = False
        return result

    

registerATCT(ECLecture, PRODUCT_NAME)
