## Python imports
import logging
from beatbox import PythonClient as SalesforceClient
from beatbox import SessionTimeoutError

## Zope imports
from zope.interface import implements

## Plone imports
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ManagePortal

## Interfaces
from interfaces.salesforcebaseconnector import ISalesforceBaseConnector, ISalesforceBaseConnectorInfo, \
    SalesforceRead, SalesforceWrite

logger = logging.getLogger('SalesforceBaseConnector')

class SalesforceBaseConnector (UniqueObject, SimpleItem):
    """A tool for storing/managing connections and connection information when interacting
       with Salesforce.com via beatbox.
    """
    implements(ISalesforceBaseConnector,ISalesforceBaseConnectorInfo)
    
    def __init__(self):
        self._username = ''
        self._password = ''
        self._v_sfclient = None
    
    id = 'portal_salesforcebaseconnector'
    meta_type = 'Salesforce Base Connector'
    title = 'Connect to an external Salesforce instance'

    security = ClassSecurityInfo()

    manage_options=(( { 'label' : 'Configure Authentication'
                        , 'action' : 'manage_config'
                        },
                      ) + SimpleItem.manage_options
                    )
    
    ##   ZMI methods
    security.declareProtected(ManagePortal, 'manage_config')
    manage_config = PageTemplateFile('www/manageAuthConfig', globals() )
    manage_config._owner = None


    def _login(self):
        logger.debug('logging into salesforce...')
        username = self._username
        passwd = self._password
        res = self._v_sfclient.login(username, passwd)
        return res
    
    def _getClient(self):
        logger.debug('calling _getClient')
        if not hasattr(self, '_v_sfclient') or self._v_sfclient is None:
            self._v_sfclient = SalesforceClient()
        if not self._v_sfclient.isConnected():
            logger.debug('No open connection to Salesforce. Trying to log in...')
            response = self._login()
            if not response:
                raise "Salesforce login failed"
        return self._v_sfclient 

    def _resetClient(self):
        logger.debug('reseting client')
        self._v_sfclient = None
        
        
    security.declareProtected(ManagePortal, 'manage_configSalesforceCredentials')
    def manage_configSalesforceCredentials(self, username, password, REQUEST=None):
        """Called by the ZMI auth management tab """
        portalMessage = ''
        try:
            self.setCredentials(username, password)
            portalMessage = 'Authentication tested successfully. Username and password saved.'
        except Exception, exc:
            portalMessage = 'The supplied credentials could not be authenticated.  Salesforce exception code: %s' % exc.faultString
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_config?portal_status_message=%s' % (self.absolute_url(),portalMessage))
    
    security.declareProtected(ManagePortal, 'setCredentials')
    def setCredentials(self, username, password):
        # do test log in first to confirm valid credentials
        # (will raise exception that can be handled by our caller, if invalid)
        testClient = SalesforceClient()
        testClient.login(username, password)
        
        self._username = username
        self._password = password
        # Disconnect from any previously connected Salesforce instance
        self._resetClient()
        return True

    security.declareProtected(ManagePortal, 'setBatchSize')
    def setBatchSize(self, batchsize):
        """Set the batchsize used by query and queryMore"""
        try:
            self._getClient().batchSize = batchsize
        except SessionTimeoutError:
            self._resetClient()
            self._getClient().batchSize = batchsize
    
    security.declareProtected(ManagePortal, 'getUsername')    
    def getUsername(self):
        """Return the current stored Salesforce username"""
        return self._username

    security.declareProtected(ManagePortal, 'getPassword')
    def getPassword(self):
        """Return the current stored Salesforce password"""
        return self._password
        
    ##
    # Convenience methods not included in Salesforce API
    # #
    
    security.declareProtected(SalesforceRead, 'listFieldsRequiredForCreation')
    def listFieldsRequiredForCreation(self, sObjectType):
        """See .interfaces.salesforcebaseconnector
        """
        dataTypeInfo = self.describeSObjects(sObjectType)[0].fields
        fieldList = []

        for fieldName, fieldData in dataTypeInfo.items():
            if self._isRequired(fieldData):
                fieldList.append(fieldName)
                
        return fieldList
            
    
    def _isRequired(self, fieldData):
        return not fieldData.nillable and not fieldData.defaultedOnCreate and fieldData.createable
        
    ##
    # Salesforce API
    ##
    
    ## Accessors
    security.declareProtected(SalesforceRead, 'query')
    def query(self, fieldList, sObjectType, whereClause=''):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling query()')
        if sObjectType is None:
            raise ValueError, "Invalid argument: sObjectType must not be None"
        if not fieldList:
            raise ValueError, "Invalid argument: must pass list of desired fields"
            
        fieldString = ','.join(fieldList)
        try:
            result = self._getClient().query(fieldString, sObjectType, whereClause)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().query(fieldString, sObjectType, whereClause)
            
        return result
    
    security.declareProtected(SalesforceRead, 'describeGlobal')
    def describeGlobal(self):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling describeGlobal')
        try:
            result = self._getClient().describeGlobal()
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().describeGlobal()
        
        return result
        
    security.declareProtected(SalesforceRead, 'describeSObjects')
    def describeSObjects(self, sObjectTypes):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling describeSObjects')
        try:
            result = self._getClient().describeSObjects(sObjectTypes)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().describeSObjects(sObjectTypes)
        
        return result        
        
    security.declareProtected(SalesforceRead, 'queryMore')
    def queryMore(self, queryLocator):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling queryMore')
        try:
            result = self._getClient().queryMore(queryLocator)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().queryMore(queryLocator)
        
        return result
        
    security.declareProtected(SalesforceRead, 'retrieve')
    def retrieve(self, fields, sObjectType, ids):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling retrieve')
        fieldString = ''
        if fields:
            fieldString = ','.join(fields)
        try:
            result = self._getClient().retrieve(fieldString, sObjectType, ids)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().retrieve(fieldString, sObjectType, ids)
        
        return result        
        
    security.declareProtected(SalesforceRead, 'getDeleted')
    def getDeleted(self, sObjectType, start, end):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling getDeleted')
        try:
            result = self._getClient().getDeleted(sObjectType, start, end)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().getDeleted(sObjectType, start, end)
        
        return result
    
    security.declareProtected(SalesforceRead, 'getUpdated')
    def getUpdated(self, sObjectType, start, end):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling getUpdated')
        try:
            result = self._getClient().getUpdated(sObjectType, start, end)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().getUpdated(sObjectType, start, end)
        
        return result
    
    security.declareProtected(SalesforceRead, 'getUserInfo')
    def getUserInfo(self):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling getUserInfo')
        try:
            result = self._getClient().getUserInfo()
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().getUserInfo()
        
        return result

    security.declareProtected(SalesforceRead, 'describeTabs')
    def describeTabs(self):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling describeTabs')
        try:
            result = self._getClient().describeTabs()
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().describeTabs()
        
        return result
           

    ## Mutators
    security.declareProtected(SalesforceWrite, 'create')
    def create(self, sObjects):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling create')
        try:
            result = self._getClient().create(sObjects)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().create(sObjects)
        
        return result
        
    security.declareProtected(SalesforceWrite, 'update')
    def update(self, sObjects):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling update')
        try:
            result = self._getClient().update(sObjects)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().update(sObjects)
        
        return result

    security.declareProtected(SalesforceWrite, 'upsert')
    def upsert(self, externalIdName, sObjects):
        """See .interfaces.salesforcebaseconnector
        """
        logger.debug('calling upsert')
        try:
            result = self._getClient().upsert(externalIdName, sObjects)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().upsert(externalIdName, sObjects)
        
        return result

    security.declareProtected(SalesforceWrite, 'delete')    
    def delete(self, ids):
        """See .interfaces.salesforcebaseconnector
        """        
        logger.debug('calling delete')
        try:
            result = self._getClient().delete(ids)
        except SessionTimeoutError:
            self._resetClient()
            result = self._getClient().delete(ids)
        
        return result
    
InitializeClass(SalesforceBaseConnector)