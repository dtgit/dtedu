from zope.interface import Interface, Attribute
from Products.CMFCore.permissions import setDefaultRoles

# Permissions
SalesforceRead = 'Salesforce: Read'
SalesforceWrite = 'Salesforce: Write'

setDefaultRoles(SalesforceRead, ('Manager'))
setDefaultRoles(SalesforceWrite, ('Manager'))


class ISalesforceBaseConnectorInfo(Interface):
    """Defines a READ ONLY interface for Salesforce
    """
    id = Attribute('id','Must be set to "portal_salesforcebaseconnector"')
        
    def describeGlobal():
        '''Retrieves list of available object Types
        (Account, Opportunity, etc., including custom
        types)
        >>> sbc = portal.portal_salesforcebaseconnector 
        >>> sbc.describeGlobal() 
        {'encoding': 'UTF-8', 
         'maxBatchSize': 200, 
         'types': ['Account', 
                   'AccountContactRole', 
                   'AccountPartner', 
                   'AccountShare', 
                   'Approval', 
                   'Asset', 
                   ....
                   ....
                   ....
                   'User', 
                   'UserRole', 
                   'WebLink']} 
        '''
        
    def describeSObjects(sObjectTypes):
        '''Introspection on Salesforce datatypes. 
        Returns a dict with properties for each Object 
        type passed in the List argument:
        >>> sbc = portal.portal_salesforcebaseconnector         
        >>> contactSchema = sbc.describeSObjects('Contact')[0]
               or
        >>> contactSchema = sbc.describeSObjects(['Contact',])[0]               
        >>> contactSchema.__dict__
        {'ChildRelationships': [], 
         'activateable': False, 
         'createable': True, 
         'custom': False, 
         'deletable': True, 
         'fields': {'AccountId': , 'AssistantName': , ... UserName__c': },
         'keyPrefix': '003', 
         'label': 'Contact', 
         'labelPlural': 'Contacts', 
         'layoutable': True, 
         'name': 'Contact', 
         'queryable': True, 
         'replicateable': True, 
         'retrieveable': True, 
         'searchable': True, 
         'undeletable': False, 
         'updateable': True, 
         'urlDetail': 'https://na1.salesforce.com/{ID}', 
         'urlEdit': 'https://na1.salesforce.com/{ID}/e', 
         'urlNew': 'https://na1.salesforce.com/003/e'}
        '''
        
    def query(fields, sObjectType, conditionExpression=''):
        """Run a SoQL query against a Salesforce instance, and returns
        a dict as a result set.
        >>> sbc = portal.portal_salesforcebaseconnector 
        >>> sbc.query(['FirstName',],'Contact',"FirstName='Stella'")
        {'records': [{'Id': '0037000000TAERdAAP', 'UserName__c': 'joe'}],
         'done': True, 
         'queryLocator': <beatbox.python_client.QueryLocator object at ...>, 
         'size': 1}
        """
        
    def queryMore(queryLocator):
        '''Query more record(s) in Salesforce
           The param is a queryLocator object returned by query(). The 'done' 
           attribute of the query result should be inspected to determine
           if a complete result set has been return. If 'done' is false, 
           queryMore() will return the next batch of results.
        '''
        
    def retrieve(fields, sObjectType, ids):
        '''Retrieve record(s) in Salesforce based on one SF Object ID's.
           This method always returns a list, even if only one ID is
           provided as an argument:
        >>> sbc = portal.portal_salesforcebaseconnector 
        >>> sbc.retrieve(['FirstName','Id'],'Contact','0033000000JKDFxAAP')
            or
        >>> sbc.retrieve(['FirstName','Id'],'Contact',['0033000000JKDFxAAP'])         
        [{'Id': '0033000000JKDFxAAP', 'FirstName': 'Siddartha'}]                
        '''
        
    def getDeleted(sObjectType, start, end):
        '''Get Salesforce Objects deleted between start and 
           end dates (dates should be passed as python 
           datetime.datetime objects):
           
           >>> enddate = datetime.datetime.utcnow()
           >>> startdate = enddate - datetime.timedelta(hours=3)
           >>> sbc.getDeleted('Contact', startdate, endate)
           [{'deletedDate': datetime.datetime(2008, 2, 16, 0, 24, 45), 'id': '0035000000UkFq7AAF'}]
        '''
        
    def getUpdated(sObjectType, start, end):
        '''Get Salesforce Objects updated between start and
           end dates (dates should be passed as python 
           datetime.datetime objects):
           
           >>> enddate = datetime.datetime.utcnow()
           >>> startdate = enddate - datetime.timedelta(hours=3)
           >>> sbc.getUpdated('Contact', startdate, endate)
           ['0035000000UkFqcAAF']
        '''
        
    def getUserInfo():
        '''Retrieves information about the authenticated user and
        returns it as a dictionary. This is the user that connects
        to Salesforce, not a Salesforce content object. This user
        and their password are set in the ZMI configuration form.
        >>> sbc.getUserInfo() 
        {'accessibilityMode': False, 
         'currencySymbol': '$', 
         'organizationId': '00D300000006UCDEA2', 
         'organizationMultiCurrency': False, 
         'organizationName': 'NPower Seattle', 
         'userDefaultCurrencyIsoCode': '', 
         'userEmail': 'jesses@npowerseattle.org', 
         'userFullName': 'Jesse Snyder', 
         'userId': '00530000000vCGAAA2', 
         'userLanguage': 'en_US', 
         'userLocale': 'en_US', 
         'userTimeZone': 'America/Los_Angeles', 
         'userUiSkin': 'Theme2'}         
        '''

    def listFieldsRequiredForCreation(sObjectType):
        '''Returns a list of the fields that must be provided to create an
           instance of the given Salesforce object type'''
           
    def describeTabs():
        '''Describe the apps that have been configured for the user'''

    ## Not currently implemented in beatbox.
    #def describeLayout(sObjectType):
    #    '''Retrieves metadata about page layouts'''

        
class ISalesforceBaseConnector(ISalesforceBaseConnectorInfo):
    """Defines full interface for Salesforce, including write access
    """
    
    def setCredentials(username, password):
        '''Set username and password for SF. Returns Boolean. This will 
           reset the connection after credentials are set.
        >>> sbc.setCredentials('george','secret')
        '''
        
    def setBatchSize(sObjectType):
        '''Set maximum size of batch for queryMore()
        >>> sbc.setBatchSize(500)
        '''
        
    def create(sObjects):
        '''Create record(s) in Salesforce from one or more dicts:
        >>> obj = dict(type='Contact',
                       LastName='Doe',
                       FirstName='John',
                       Phone='123-456-7890',
                       Email='john@doe.com',
                       Birthdate = datetime.date(1970, 1, 4)
                       )
        >>> sbc.create(obj)
        [{'errors': [], 'id': '0033000000QXZfmAAH', 'success': True}]
        '''
        
    def update(sObjects):
        '''Update record(s) in Salesforce. The dict passed to update()
        must include 'Id' and 'type' keys:
        >>> updateData = dict(Id='0033000000QXZfmAAH', 
                              type='Contact',
                              LastName='Dunn') 
        >>> sbc.update(updateData)
        [{'errors': [], 'id': '0033000000QXZfmAAH', 'success': True}]
        '''

    def upsert(externalIdName, sObjects):
        '''If record(s) already exist in Salesforce an update is performed.
        Otherwise, new record(s) are created.'''

    def delete(ids):
        '''Delete record(s) in Salesforce by id or an array of ids.'''
