# -*- coding: utf-8 -*-
# $Id: ECAssignment.py,v 1.60 2007/07/02 14:40:14 peilicke Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#from urllib import quote
from StringIO import StringIO
from textwrap import TextWrapper
import re

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import registerATCT, ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.interfaces import IATDocument


from Products.PortalTransforms.utils import TransformException

# local imports
from Products.ECAssignmentBox.config import *
from Products.ECAssignmentBox import permissions

# PlagDetector imports
from PlagDetector.PlagChecker import PlagChecker
from PlagDetector.PlagVisualizer import PlagVisualizer

# alter default fields -> hide title and description
ECAssignmentSchema = ATContentTypeSchema.copy()
ECAssignmentSchema['title'].default_method = '_generateTitle'
ECAssignmentSchema['title'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}
ECAssignmentSchema['description'].widget.visible = {
    'view' : 'invisible',
    'edit' : 'invisible'
}

# define schema
ECAssignmentSchema = ECAssignmentSchema + Schema((
    TextField(
        'answer',
        default_content_type = 'text/html',
        default_output_type = 'text/structured',
        allowable_content_types = TEXT_TYPES,
        widget = RichWidget (
            label = "Answer",
            label_msgid = "label_answer",
            description = "The submission for this assignment",
            description_msgid = "help_answer",
            i18n_domain = I18N_DOMAIN,
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload,
        ),
    ),

    TextField(
        'remarks',
        default_content_type = 'text/structured',
        default_output_type = 'text/html',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Remarks",
            label_msgid = "label_remarks",
            description = "Your remarks for this assignment (they will not be shown to the student)",
            description_msgid = "help_remarks",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
        read_permission = permissions.ModifyPortalContent,
    ),

    TextField(
        'feedback',
        searchable = True,
        default_content_type = 'text/html',
        default_output_type = 'text/structured',
        allowable_content_types = TEXT_TYPES,
        widget = TextAreaWidget(
            label = "Feedback",
            label_msgid = "label_feedback",
            description = "The grader's feedback for this assignment",
            description_msgid = "help_feedback",
            i18n_domain = I18N_DOMAIN,
            rows = 8,
        ),
    ),

    StringField(
        'mark',
        vocabulary=[(1, '1 - Pass'), (0, '0 - No Pass'),],
        accessor = 'getGradeIfAllowed',
        edit_accessor = 'getGradeForEdit',
        mutator = 'setGrade',
        widget=SelectionWidget(
            label = 'Grade',
            label_msgid = 'label_grade',
            description = "The grade awarded for this assignment",
            description_msgid = "help_grade",
            i18n_domain = I18N_DOMAIN,
            format='select',
        ),
    ),
  ) # , marshall = PrimaryFieldMarshaller()
)

finalizeATCTSchema(ECAssignmentSchema)



class ECAssignment(ATCTContent, HistoryAwareMixin):
    """A submission to an assignment box"""

    __implements__ = (ATCTContent.__implements__,
                      IATDocument,
                      HistoryAwareMixin.__implements__,
                     )

    security = ClassSecurityInfo()

    #_at_rename_after_creation = True
    schema = ECAssignmentSchema
    meta_type = ECA_META
    archetype_name = ECA_NAME

    content_icon = "eca.png"
    global_allow = False

    default_view   = 'eca_view'
    immediate_view = 'eca_view'

    typeDescription = "A submission to an assignment box."
    typeDescMsgId = 'description_edit_eca'

    # work-around for indexing in a corret way
    isAssignmentBoxType = False
    isAssignmentType = True


    # -- methods --------------------------------------------------------------
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """
        """
        #turning off for demo
        return
        BaseContent.manage_afterAdd(self, item, container)
        
        wtool = self.portal_workflow
        assignments = self.contentValues(filter = {'Creator': item.Creator()})
        if assignments:
            for a in assignments:
                if a != self:
                    wf = wtool.getWorkflowsFor(a)[0]
                    if wf.isActionSupported(a, 'supersede'):
                        wtool.doActionFor(a, 'supersede',
                                          comment='Superseded by %s'
                                          % self.getId())

        self.sendNotificationEmail()
    
    
    def sendNotificationEmail(self):
        """
        When this assignment is created, send a notification email to
        the owner of the assignment box, unless emailing is turned off.
        """
        box = self.aq_parent
        if not box.getSendNotificationEmail():
            return

        #portal_url = getToolByName(self, 'portal_url')
        #portal = portal_url.getPortalObject()

        site_properties = self.portal_properties.site_properties
        # 'en' is used as fallback language if default_language is not
        # set; this shouldn't normally happen

        portal_language = getattr(site_properties, 'default_language', 'en')
        portal_qi = getToolByName(self, 'portal_quickinstaller')
        productVersion = portal_qi.getProductVersion(PROJECTNAME)
        
        submitterId   = self.Creator()
        submitterName = self.ecab_utils.getFullNameById(submitterId)
        submissionURL = self.ecab_utils.normalizeURL(self.absolute_url())

        addresses = box.getNotificationEmailAddresses()
        prefLang = self.ecab_utils.getUserPropertyById(box.Creator(),
                                                       'language')
        if not prefLang:
            prefLang = portal_language
        
        default_subject = '[${id}] Submission to "${box_title}" by ${student}'
        subject = self.translate(domain=I18N_DOMAIN,
                                 msgid='email_new_submission_subject',
                                 target_language=prefLang,
                                 mapping={'id': 'Teachers Without Borders',
                                          'box_title': box.Title(),
                                          'student': submitterName},
                                 default=default_subject)

        default_mailText = '${student} has made a submission to ' \
                           'the assignment "${box_title}".\n\n' \
                           '<${url}>\n\n' \
                           '-- \n' \
                           'Teachers Without Borders :: Certificate for Teaching Mastery'
        mailText = self.translate(domain=I18N_DOMAIN,
                                  msgid='email_new_submission_content',
                                  target_language=prefLang,
                                  mapping={'box_title': box.Title(),
                                           'student': submitterName,
                                           'url': submissionURL,
                                           'product': PROJECTNAME,
                                           'version': productVersion},
                                  default=default_mailText)

        #revert to plone3 secureSend
        #self.ecab_utils.sendEmail(addresses, subject, mailText)
        self.MailHost.secureSend(mailText, mto=addresses, mfrom=self.email_from_address, subject=subject, charset='utf8')


    def sendGradingNotificationEmail(self):
        """
        When this assignment is graded, send a notification email to
        the submitter of the assignment, unless grading notification
        is turned off in the assignment box.
        """
        #turning off for demo
        return

        box = self.aq_parent
        if not box.getSendGradingNotificationEmail():
            return

        site_properties = self.portal_properties.site_properties
        # 'en' is used as fallback language if default_language is not
        # set; this shouldn't normally happen
        portal_language = getattr(site_properties, 'default_language', 'en')
        portal_qi = getToolByName(self, 'portal_quickinstaller')
        productVersion = portal_qi.getProductVersion(PROJECTNAME)
        
        submitterId   = self.Creator()
        submitterName = self.ecab_utils.getFullNameById(submitterId)
        submissionURL = self.ecab_utils.normalizeURL(self.absolute_url())

        addresses = []
        addresses.append(self.ecab_utils.getUserPropertyById(submitterId,
                                                             'email'))
        
        prefLang = self.ecab_utils.getUserPropertyById(submitterId,
                                                       'language')
        if not prefLang:
            prefLang = portal_language

        default_subject = 'Your submission to "${box_title}" has been graded'
        subject = self.translate(domain=I18N_DOMAIN,
                                 msgid='email_submission_graded_subject',
                                 target_language=prefLang,
                                 mapping={'box_title': box.Title(),},
                                 default=default_subject)

        default_mailText = 'Your submission to the assignment box ' \
                           '"${box_title}" has been graded.\n\n' \
                           'Visit the following URL to view your ' \
                           'submission:\n\n' \
                           '<${url}>\n\n' \
                           '-- \n' \
                           '${product} ${version}'
        mailText = self.translate(domain=I18N_DOMAIN,
                                  msgid='email_submission_graded_content',
                                  target_language=prefLang,
                                  mapping={'box_title': box.Title(),
                                           'grade': self.mark,
                                           'feedback': self.feedback,
                                           'url': submissionURL,
                                           'product': PROJECTNAME,
                                           'version': productVersion},
                                  default=default_mailText)

        #revert to plone3 secureSend
        #self.ecab_utils.sendEmail(addresses, subject, mailText)
        self.MailHost.secureSend(mailText, mto=addresses, mfrom=self.email_from_address, subject=subject, charset='utf8')



    # FIXME: deprecated, set security
    def setField(self, name, value, **kw):
        """Sets value of a field"""
        field = self.getField(name)
        field.set(self, value, **kw)


    security.declarePrivate('_generateTitle')
    def _generateTitle(self):
        #log("Title changed from '%s' to '%s'" % \
        #        (self.title, self.getCreatorFullName(),), severity=DEBUG)
        return self.getCreatorFullName()


    # FIXME: set security
    def getCreatorFullName(self):
        #return util.getFullNameById(self, self.Creator())
        return self.ecab_utils.getFullNameById(self.Creator())

    # EXPERIMENTAL
    def get_data(self):
        """
        If wrapAnswer is set for the box, plain text entered in the
        text area is stored as one line per paragraph. For display
        inside a <pre> element it should be wrapped.

        @return file content
        """
        mt = self.getContentType('file')
        
        if re.match("(text/.+)|(application/(.+\+)?xml)", mt):
        
            box = self.aq_parent
            
            if ((mt == 'text/plain') or
                (mt == 'text/x-web-intelligent')) and box.getWrapAnswer():
                file = StringIO(self.getField('file').get(self))
                wrap = TextWrapper()
                result = ''
    
                for line in file:
                    result += wrap.fill(line) + '\n'
    
                return result
            else:
                return self.getField('file').get(self)
        else:
            return None
        
    
    # FIXME: deprecated, use get_data or data in page templates
    def getAsPlainText(self):
        """
        Return the file contents as plain text.
        Cf. <http://www.bozzi.it/plone/>,
        <http://plone.org/Members/syt/PortalTransforms/user_manual>;
        see also portal_transforms in the ZMI for available
        transformations.
        
        @return file content as plain text or None
        """
        ptTool = getToolByName(self, 'portal_transforms')
        f = self.getField('file')
        #source = ''

        mt = self.getContentType('file')
        
        if re.match('text/|application/(.+\+)?xml', mt):
            return str(f.get(self))
        else:
            return None
        
        # FIXME: cut this for the moment because result of Word or PDF files 
        #        looks realy ugly

        try:
            result = ptTool.convertTo('text/plain-pre', str(f.get(self)),
                                      mimetype=mt)
        except TransformException:
            result = None
            
        if result:
            return result.getData()
        else:
            return None
    
    
    security.declarePublic('evaluate')
    def evaluate(self, parent, recheck=False):
        """
        Will be called if a new assignment is added to this assignment box to
        evaluate it. Please do not confuse this with the validation of the
        input values.
        For ECAssignment this mehtod returns nothing but it can be 
        overwritten in subclasses, e.g. ECAutoAssignmentBox.
        
        @return (1, '')
        """
        return (1, '')

    
    #security.declarePublic('getGradeIfAllowed')
    def getGradeIfAllowed(self):
        """
        The accessor for field grade. Returns the grade if this assigment is in
        state graded or current user has reviewer permissions.
        
        @return string value of the given grade or nothing
        """
        wtool = self.portal_workflow
        state = wtool.getInfoFor(self, 'review_state', '')
        
        currentUser = self.portal_membership.getAuthenticatedMember()
        #isReviewer = currentUser.checkPermission(permissions.ReviewPortalContent, self)
        #isOwner = currentUser.has_role(['Owner', 'Reviewer', 'Manager'], self)
        #isGrader = currentUser.has_role(['ECAssignment Grader', 'Manager'], self)
        #isGrader = currentUser.checkPermission(permissions.GradeAssignments,
        #                                       self)

        if self.mark and not currentUser.has_role('Anonymous'):
            try:
                value = self.mark
                prec = len(value) - value.find('.') - 1
                result = self.ecab_utils.localizeNumber("%.*f",
                                                        (prec, float(value)))
            except ValueError:
                result = self.mark

            if state == 'graded':
                return result
            #elif isGrader:
                #return '(' + result + ')'

        

    security.declarePublic('getGradeDisplayValue')
    def getGradeDisplayValue(self):
        """
        Formats and returns the grade if given .
        
        @return string value of the given grade or nothing
        """
        wtool = self.portal_workflow
        state = wtool.getInfoFor(self, 'review_state', '')
        
        if self.mark:
            try:
                value = self.mark
                prec = len(value) - value.find('.') - 1
                result = self.ecab_utils.localizeNumber("%.*f",
                                                        (prec, float(value)))
            except ValueError:
                result = self.mark

            if state == 'graded':
                return result
            else:
                return '(%s)' % result


    #security.declarePublic('getGradeForEdit')
    def getGradeForEdit(self):
        """
        The edit_accessor for field grade. Returns the grade for this
        assignment.
        
        @return string value of the given grade or nothing
        """
        try:
            value = self.mark
            prec = len(value) - value.find('.') - 1
            return self.ecab_utils.localizeNumber("%.*f", (prec, float(value)))
        except ValueError:
            return self.mark


    security.declarePrivate('setGrade')
    def setGrade(self, value):
        """
        Mutator for the `mark' field.  Allows the input of localized numbers.
        """
        decimalSeparator = self.translate(msgid = 'decimal_separator',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        value = value.strip()
        
        match = re.match('^[0-9]+' + decimalSeparator + '?[0-9]*$', value)
        if match:
            value = value.replace(decimalSeparator, '.')
        
        self.getField('mark').set(self, value)
    

    security.declarePublic('getViewerNames')
    def getViewerNames(self):
        """
        Get the names of the users and/or groups which have the local
        role `ECAssignment Viewer'.  This allows reviewers to quickly
        check who may view an assignment.
        
        @return list of user and/or group names
        """
        principalIds = self.users_with_local_role('ECAssignment Viewer')
        names = []
        
        for id in principalIds:
            if self.portal_groups.getGroupById(id):
                names.append(self.portal_groups.getGroupById(id).getGroupName())
            else:
                names.append(self.ecab_utils.getFullNameById(id))

        return names


    security.declarePublic('getRSSModeReadFieldNames')
    def getRSSModeReadFieldNames(self):
        """
        Returns the names of the fields which are shown in view mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        return ['answer']


    
    security.declarePublic('getGradeModeReadFieldNames')
    def getViewModeReadFieldNames(self):
        """
        Returns the names of the fields which are shown in view mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        return ['answer', 'remarks', 'feedback', 'mark']


    security.declarePublic('getGradeModeReadFieldNames')
    def getAnonRSSModeReadFieldNames(self):
        """
        Returns the names of the fields which are shown in RSS view mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        return ['answer', 'mark']



    security.declarePublic('getGradeModeReadFieldNames')
    def getGradeModeReadFieldNames(self):
        """
        Returns the names of the fields which are read only in grade mode.
        This method should be overridden in subclasses which need more fields.

        @return list of field names
        """
        
        return ['answer']


    security.declarePublic('getGradeModeEditFieldNames')
    def getGradeModeEditFieldNames(self):
        """
        Returns the names of the fields which are editable in grade mode.
        This method should be overridden in subclasses which need more fields.
        
        @return list of field names
        """
        return ['remarks', 'feedback', 'mark']


    security.declarePublic('getIndicators')
    def getIndicators(self):
        """
        Returns a list of dictionaries which contain information necessary
        to display the indicator icons.
        """
        result = []

        user = self.portal_membership.getAuthenticatedMember()
        isOwner = user.has_role(['Owner', 'Reviewer', 'Manager'], self);
        isGrader = self.portal_membership.checkPermission(
                                          permissions.GradeAssignments, self)        

        viewers = self.getViewerNames()
        
        if viewers:
            if isOwner:
                result.append({'icon':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'; '.join(viewers),
                               })
            elif user.has_role('ECAssignment Viewer', object=self):
                result.append({'icon':'ec_shared.png', 
                               'alt':'Released',
                               'alt_msgid':'label_released',
                               'title':'This assignment has been released for viewing',
                               'title_msgid':'tooltip_released_icon',
                               })
        
        if hasattr(self, 'feedback') and self.feedback:
            feedback = str(self.feedback)
            title = re.sub('[\r\n]+', ' ', feedback)

            result.append({'icon':'ec_comment.png', 
                           'alt':'Feedback',
                           'alt_msgid':'label_feedback',
                           'title':title,
                           })

        if isGrader and hasattr(self, 'remarks') and self.remarks:
            remarks = str(self.remarks)
            title = re.sub('[\r\n]+', ' ', remarks)

            result.append({'icon':'ecab_remarks.png', 
                           'alt':'Remarks',
                           'alt_msgid':'label_remarks',
                           'title':title,
                           })

        return result
        

    security.declarePublic('diff')
    def diff(self, other):
        """Compare this assignment to another one.
        """
        checker = PlagChecker()
        result = checker.compare(str(self.getFile()),
                        str(other.getFile()),
                        self.pretty_title_or_id(),
                        other.pretty_title_or_id())
        vis = PlagVisualizer()
        strList = vis.resultToHtml(result, 
                   str(self.getFile()),
                   str(other.getFile()))
        return strList


    security.declarePublic('diff2')
    def diff2(self, other):
        """Compare this assignment to another one.
        """
        checker = PlagChecker()
        result = checker.compare(str(self.getFile()),
                        str(other.getFile()),
                        self.pretty_title_or_id(),
                        other.pretty_title_or_id())
        vis = PlagVisualizer()
        strList = vis.resultToHtml(result, 
                   str(self.getFile()),
                   str(other.getFile()))
        return strList


    security.declarePublic('dotplot')
    def dotplot(self, other):#, REQUEST=None):
        """Compare this assignment to another one. Using a dotplot.
        """
        vis = PlagVisualizer()
        image = vis.stringsToDotplot(str(self.getFile()),
                             str(other.getFile()),
                             id1=self.pretty_title_or_id(),
                             id2=other.pretty_title_or_id(),
                             showIdNums=True)
        return image


registerATCT(ECAssignment, PROJECTNAME)
