from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField, TextAreaWidget, RichWidget
from Products.Archetypes.atapi import StringField, StringWidget, LinesField
from Products.Archetypes.atapi import BooleanField, BooleanWidget
from Products.Archetypes.atapi import SelectionWidget, MultiSelectionWidget
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from Products.eduCommons.interfaces import ICourse
from Products.eduCommons.config import PROJECTNAME

from Products.eduCommons import eduCommonsMessageFactory as _





CourseSchema = ATFolderSchema.copy() + Schema((
        
    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'Body Text'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload),
             ),

    StringField('courseId',
                required=False,
                widget=StringWidget(label=_(u'Course ID'),
                                    label_msgid='label_course_id',
                        	    description=_(u'The course identifier or catalog number. Also can be used to sequence courses (1.0, 2.0, etc).'),
                                    description_msgid='help_course_id',
                                    ),
                ),

    StringField('term',
                required=False,
                widget=StringWidget(label=_(u'Term'),
                                    label_msgid='label_course_term',
                                    description=_(u'The term the course was taught in.'),
                                    description_msgid='help_course_term',
                                    ),
                ),
        

    TextField('structure',
              required=False,
              default_content_type='text/plain',
              allowable_content_types = ('text/plain',),
              widget=TextAreaWidget(label=_(u'Structure'),
                                    label_msgid='label_course_structure',
                                    description=_(u'The structure of the course.'),
                                    description_msgid='help_course_structure',
                                    rows=3,
                                    cols=40,
                                    ),
              ),

    StringField('level',
                required=False,
                vocabulary=[_(u'Undergraduate'), _(u'Graduate'),],
                widget=SelectionWidget(label=_(u'Level'),
                                       label_msgid='label_course_structure',
                                       description=_(u'The level at which the course is taught.'),
                                       description_msgid='help_course_level',
                                       format='select',
                                       ),
                ),

    StringField('instructorName',
                required=False,
                widget=StringWidget(label=_(u'Instructor Name'),
                                    label_msgid='label_course_instructor_name',
                                    description=_(u'The name of the primary instructor teaching this course.'),
                                    description_msgid='help_course_instructor_name',
                                    ),
                ),
    
    StringField('instructorEmail',
                required=False,
                widget=StringWidget(label=_(u'Instructor Email'),
                                    label_msgid='label_course_instructor_email',
                                    description=_(u'The email address of the primary instructor teaching this course.'),
                                    description_msgid='help_course_instructor_email',
                                    ),
                ),

    BooleanField('displayInstEmail',
                 widget=BooleanWidget(label=_(u'Display Instructor Email Address'),
                                      label_msgid='label_course_display_inst_email',
                                      description=_(u'Should the primary instructor\'s Email address be publically displayed?'),
                                      description_msgid='help_course_display_inst_email',
                                      ),
                 ),

    BooleanField('instructorAsCreator',
                 widget=BooleanWidget(label=_(u'Instructor is Primary Author'),
                                      label_msgid='label_course_inst_primary_author',
                                      description=_(u'Is the primary instructor also the primary author of the course materials?'),
                                      description_msgid='help_course_inst_primary_author',
                                      ),
                 ),
    

    LinesField('crosslisting',
                required=False,
                vocabulary='getDivisionsVocab',
                widget=MultiSelectionWidget(label=_(u'Cross Listing(s)'),
                                       label_msgid='label_course_crosslisting',
                                       description=_(u'Other Divisions that this Course should be listed in. To select multiple options, SHIFT click for adjacent items, or CTRL/CMD click for non-adjacent items.'),
                                       description_msgid='help_course_crosslisting',
                                       format='select',
                                       ),
                ),


    ),
    marshall=RFC822Marshaller()
    )

finalizeATCTSchema(CourseSchema)


class Course(ATFolder):
    """ A course content object """

    implements(ICourse)
    security = ClassSecurityInfo()
    schema = CourseSchema
    portal_type = 'Course'

    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        deftext = self.restrictedTraverse('@@course_view')
        self.setText(deftext())

    def getECParent(self):
        """ Determine by acquisition if an object is a child of a course. """
        return self

    def getDivisionsVocab(self):
        """ Get the list of current divisions and return it as a vocabulary. """
        path = {'query':('/'), }
        brains = self.portal_catalog.searchResults(path=path, Type='Division', sort_on='sortable_title')
        dl = DisplayList()
        dl.add('None', 'None')
        for brain in brains:
            if brain.getId != self.aq_parent.id:
                dl.add(brain.getId, brain.Title)
        return dl

        

registerATCT(Course, PROJECTNAME)
