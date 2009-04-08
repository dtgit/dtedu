""" 
    
    An adapter for PloneFormGen that saves submitted form data
    to Salesforce.com
    
"""

__author__  = ''
__docformat__ = 'plaintext'

# Python imorts
import logging

# Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from zope.interface import classImplements, providedBy
from DateTime import DateTime

# Plone imports
from Products.Archetypes.public import StringField, SelectionWidget, \
    DisplayList, Schema, ManagedSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

# DataGridField
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.DataGridField import FixedRow

# Interfaces
from Products.PloneFormGen.interfaces import IPloneFormGenField

# PloneFormGen imports
from Products.PloneFormGen import HAS_PLONE30
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

# Local imports
from Products.salesforcepfgadapter.config import PROJECTNAME, REQUIRED_MARKER
from Products.salesforcepfgadapter import SalesforcePFGAdapterMessageFactory as _
from Products.salesforcepfgadapter import HAS_PLONE25, HAS_PLONE30

if HAS_PLONE25:
    import zope.i18n

logger = logging.getLogger("PloneFormGen")    

schema = FormAdapterSchema.copy() + Schema((
    StringField('SFObjectType',
        searchable=0,
        required=1,
        default=u'Contact',
        mutator='setSFObjectType',
        widget=SelectionWidget(
            label='Salesforce Object Type',
            i18n_domain = "salesforcepfgadapter",
            label_msgid = "label_salesforce_type_text",
            ),
        vocabulary='displaySFObjectTypes',
        ),
    DataGridField('fieldMap',
         searchable=0,
         required=1,
         schemata='field mapping',
         columns=('form_field', 'sf_field'),
         fixed_rows = "generateFormFieldRows",
         allow_delete = False,
         allow_insert = False,
         allow_reorder = False,
         widget = DataGridWidget(
             label='Form fields to Salesforce fields mapping',
             label_msgid = "label_salesforce_field_map",
             description="""The following Form Fields are available\
                 with your Form Folder. Choose the appropriate \
                 Salesforce Field for each Form Field.""",
             description_msgid = 'help_salesforce_field_map',
             columns= {
                 "form_field" : FixedColumn("Form Fields"),
                 "sf_field" : SelectColumn("Salesforce Fields", 
                                           vocabulary="buildSFFieldOptionList")
             },
             i18n_domain = "salesforcepfgadapter",
         ),
    )    
))

# move 'field mapping' schemata before the inherited overrides schemata
schema = ManagedSchema(schema.copy().fields())
schema.moveSchemata('field mapping', -1)

class SalesforcePFGAdapter(FormActionAdapter):
    """ An adapter for PloneFormGen that saves results to Salesforce.
    """
    schema = schema
    security = ClassSecurityInfo()
        
    if not HAS_PLONE30:
        finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

    meta_type = portal_type = 'SalesforcePFGAdapter'
    archetype_name = 'Salesforce Adapter'
    content_icon = 'salesforce.gif'
    
    def initializeArchetype(self, **kwargs):
        """Initialize Private instance variables
        """
        FormActionAdapter.initializeArchetype(self, **kwargs)
        
        # All Salesforce fields for the current Salesforce object type. Since
        # we need this for every row in our field mapping widget, it's better
        # to just set it on the object when we set the Salesforce object type. 
        # This way we don't query Salesforce for every field on our form.
        self._fieldsForSFObjectType = {}
    

    security.declareProtected(View, 'onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """ The essential method of a PloneFormGen Adapter:
        - collect the submitted form data
        - examine our field map to determine which Saleforce fields
          to populate
        - if there are any mappings, submit the data to Salesforce
          and check the result
        """
        logger.debug('Calling onSuccess()')
        sObject = self._buildSObjectFromForm(fields, REQUEST)
        if len(sObject.keys()) > 1:
            salesforce = getToolByName(self, 'portal_salesforcebaseconnector')
            result = salesforce.create(sObject)[0]
            if result['success']:
                logger.debug("Successfully created new %s %s in Salesforce" % \
                             (self.SFObjectType, result['id']))
            else:
                errorStr = 'Failed to create new %s in Salesforce: %s' % \
                    (str(self.SFObjectType), result['errors'][0]['message'])
                raise errorStr
        else:
            logger.warn('No valid field mappings found. Not calling Salesforce.')
            
    def _buildSObjectFromForm(self, fields, REQUEST=None):
        """ Used by the onSuccess handler to convert the fields from the form
            into the fields to be stored in Salesforce.
            
            Also munges dates into the required (mm/dd/yyyy) format.
        """
        logger.debug('Calling _buildSObjectFromForm()')
        sObject = dict(type=self.SFObjectType)
        for field in fields:
            formFieldName = field.Title().strip()
            formFieldValue = REQUEST.form.get(field.fgField.getName(),'')
            if field.meta_type == 'FormDateField':
               formFieldValue = DateTime(formFieldValue + ' GMT+0').HTML4()
            if not self._getSFFieldForFormField(formFieldName):
                continue
            salesforceFieldName = self._getSFFieldForFormField(formFieldName)
            sObject[salesforceFieldName] = formFieldValue
        return sObject
    
    security.declareProtected(ModifyPortalContent, 'setFieldMap')
    def setFieldMap(self, currentFieldMap):
        # 1) Iterate over current list of form field titles, and remove
        # any FixedRow objects whose 'key things' don't appear in the
        # current list of *stripped* form field titles.
        """(
              {'form_field': 'Your E-Mail Address', 'sf_field': 'Email'}, 
              {'form_field': 'Subject', 'sf_field': 'FirstName'},
              {'form_field': 'Comments', 'sf_field': ''}
        )
        """
        logger.debug('calling setFieldMap()')
        latestFormFieldTitles = self._getIPloneFormGenFieldProviderTitles()
        cleanMapping = []
    
        for mapping in currentFieldMap:
            if mapping.has_key('form_field') and mapping['form_field'] in latestFormFieldTitles:
                cleanMapping.append(mapping)
                
        self.fieldMap = tuple(cleanMapping)
            
    security.declareProtected(ModifyPortalContent, 'setSFObjectType')    
    def setSFObjectType(self, newType):
        """When we set the Salesforce object type,
           we also need to reset all the possible fields
           for our mapping selection menus.
        """
        logger.debug('Calling setSFObjectType()')
        self.SFObjectType = newType
        self._fieldsForSFObjectType = self._querySFFieldsForType()
    
    security.declareProtected(ModifyPortalContent, 'displaySFObjectTypes')
    def displaySFObjectTypes(self):
        logger.debug('Calling displaySFObjectTypes()')        
        """ returns vocabulary for available Salesforce Object Types 
            we can create. 
        """
        types = self._querySFObjectTypes()
        typesDisplay = DisplayList()
        for type in types:
            typesDisplay.add(type, type)
        return typesDisplay

    def _requiredFieldSorter(self, a, b):
        """Custom sort function
        Any fields marked as required should appear first, and sorted, in the list, 
        followed by all non-required fields, also sorted. This:
            tuples = [
                        ('A', 'A'), 
                        ('B','B (required)'), 
                        ('E', 'E'), 
                        ('Z','Z (required)'), 
                    ]
                    
        would be sorted to:
            tuples = [
                        ('B','B (required)'), 
                        ('Z','Z (required)'), 
                        ('A', 'A'), 
                        ('E', 'E'), 
                    ]
        
        """
        if (a[1].endswith(REQUIRED_MARKER) and b[1].endswith(REQUIRED_MARKER)) or \
                (not a[1].endswith(REQUIRED_MARKER) and not b[1].endswith(REQUIRED_MARKER)):
            # both items are the same in their requiredness
            if a[0] > b[0]:
                return 1
            else:
                return -1
        else:
            if a[1].endswith(REQUIRED_MARKER):
                return -1
            else:
                return 1

    security.declareProtected(ModifyPortalContent, 'buildSFFieldOptionList')
    def buildSFFieldOptionList(self):
        """Returns a DisplayList of all the fields
           for the currently selected Salesforce object
           type.
        """
        sfFields = self._fieldsForSFObjectType
        
        fieldList = []
        for k, v in sfFields.items():
            # determine whether each field is required and mark appropriately
            
            if v.nillable or v.defaultedOnCreate or not v.createable:
                fieldList.append((k, k))
            else:
                fieldList.append((k, str("%s %s" % (k, REQUIRED_MARKER))))
        # We provide our own custom sort mechanism
        # rather than relying on DisplayList's because we
        # want all required fields to appear first in the
        # selection menu.
        fieldList.sort(self._requiredFieldSorter)
        fieldList.insert(0, ('', ''))
        dl = DisplayList(fieldList)
        
        return dl
    
    security.declareProtected(ModifyPortalContent, 'generateFormFieldRows')
    def generateFormFieldRows(self):
        """This method returns a list of rows for the field mapping
           ui. One row is returned for each field in the form folder.
        """
        fixedRows = []

        for formFieldTitle in self._getIPloneFormGenFieldProviderTitles():
            logger.debug("creating mapper row for %s" % formFieldTitle)
            fixedRows.append(FixedRow(keyColumn="form_field",
                        initialData={"form_field" : formFieldTitle, "sf_field" : ""}))
        return fixedRows
    
    def _getIPloneFormGenFieldProviderTitles(self):
        formFolder = aq_parent(self)
        formFieldTitles = []
        
        for formField in formFolder.objectIds():
            fieldObj = getattr(formFolder, formField)
            if IPloneFormGenField.providedBy(fieldObj):
                formFieldTitles.append(fieldObj.Title().strip())
                
        return formFieldTitles
                                                  
    def _querySFFieldsForType(self):
        """Return a tuple of all the possible fields for the current
           Salesforce object type
        """
        salesforce = getToolByName(self, 'portal_salesforcebaseconnector')
        salesforceFields = salesforce.describeSObjects(self.SFObjectType)[0].fields
        return salesforceFields
    
    def _querySFObjectTypes(self):
        """Returns a tuple of all Salesforce object type names.
        """
        salesforce = getToolByName(self, 'portal_salesforcebaseconnector')
        types = salesforce.describeGlobal()['types']
        return types
        
    def _getSFFieldForFormField(self, target):
        """  Return the Salesforce field
             mapped to a given Form field. 
        """
        sfField = None
        for mapping in self.fieldMap:
            if mapping['form_field'] == target and mapping['sf_field']:
                sfField = mapping['sf_field'] 
                break
        return sfField


registerATCT(SalesforcePFGAdapter, PROJECTNAME)

try:
    from Products.Archetypes.interfaces import IMultiPageSchema
    classImplements(SalesforcePFGAdapter, IMultiPageSchema)
except ImportError:
    pass