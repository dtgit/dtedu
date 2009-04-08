from zExceptions import Unauthorized
from beatbox import SoapFaultError
from base import SalesforceBaseConnectorTestCase
from Products.salesforcebaseconnector.interfaces.salesforcebaseconnector import ISalesforceBaseConnector, \
        ISalesforceBaseConnectorInfo, SalesforceRead, SalesforceWrite
from Products.salesforcebaseconnector.salesforcebaseconnector import SalesforceBaseConnector
from zope.interface.verify import verifyClass
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission as checkPermission
import datetime

# be sure to set USERNAME/PASSWORD for test config
from Products.salesforcebaseconnector.tests import sfconfig

class TestSalesforceBaseConnector(SalesforceBaseConnectorTestCase):
    def afterSetUp(self):
        """docstring for afterSetUp"""
        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.toolbox = getToolByName(self.portal, "portal_salesforcebaseconnector")
        self.toolbox.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list() # keep track of ephemeral test data to delete

    def testInterface(self):
        """ Some basic boiler plate testing of Interfaces and objects"""
        # verify ISalesforceBaseConnector
        self.failUnless(ISalesforceBaseConnector.implementedBy(SalesforceBaseConnector))
        self.failUnless(verifyClass(ISalesforceBaseConnector,SalesforceBaseConnector))

        # verify ISalesforceBaseConnectorInfo
        self.failUnless(ISalesforceBaseConnectorInfo.implementedBy(SalesforceBaseConnector))
        self.failUnless(verifyClass(ISalesforceBaseConnectorInfo,SalesforceBaseConnector))

        # verify we're an object of the expected class
        self.failUnless(isinstance(self.toolbox,SalesforceBaseConnector))
    
    def testCredentialTestOnTool(self):
        """salesforcebaseconnector has a private method _canditateCredentialTestOk
        that interacts with beatbox to create a PythonClient connection object 
        based on the credentials in  sfconfig.py.  The implications of this 
        test failing are either:
       
        1) that the salesforcebaseconnector object is unable to connect to Salesforce 
        via beatbox and thus unable to set the password and username attributes 
        on the object 
       
        Or more likely...
       
        2) that the sfconfig.py login information provided in sfconfig.py is incorrect.
        """

        # try testing our connection and the validity of our passwords
        self.failUnless(self.toolbox.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD) \
            , "You may have incorrectly entered your Salesforce login within the sfconfig.py file, otherwise we're having troubles connecting to Salesforce.")

        # try making up some *hopefully* nonsensical username and password to show the connection is failing
        self.assertRaises(SoapFaultError, self.toolbox.setCredentials,
            'username_supercalifragilisticexpialidocious', 'password_supercalifragilisticexpialidocious')

    def testBaseConnectorSecurity(self):
        """ None of the base connector's attributes should be publicly traversable.
        """
        for attr in ISalesforceBaseConnector:
            if not callable(attr):
                continue
            try:
                self.assertRaises(Unauthorized, self.toolbox.restrictedTraverse, attr)
            except AssertionError, e:
                # annotate the assertion error with the current attribute
                e.args = [e.args[0] + ': %s attribute' % attr] + list(e.args[1:])
                raise
    
    def testSalesforcePermissions(self):
        """ Make sure that the Manager role has the Salesforce read and write permissions,
            by default. """
        self.setRoles(())
        self.failIf(checkPermission(SalesforceRead, self.portal))
        self.failIf(checkPermission(SalesforceWrite, self.portal))
        self.setRoles(('Manager',))
        self.failUnless(checkPermission(SalesforceRead, self.portal))
        self.failUnless(checkPermission(SalesforceWrite, self.portal))

class TestBaseConnectorBeatboxInteraction(SalesforceBaseConnectorTestCase):
    """docstring for SF methods"""

    def afterSetUp(self):
        """docstring for afterSetUp"""
        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.toolbox = getToolByName(self.portal, "portal_salesforcebaseconnector")
        self.toolbox.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list() # keep track of ephemeral test data to delete
    
    def beforeTearDown(self):
        """clean up SF data"""
        ids = self._todelete
        if ids:
            while len(ids) > 200:
                self.toolbox.delete(ids[:200])
                ids = ids[200:]
            self.toolbox.delete(ids)

    def test_query(self):
        """Test a very basic query with a condition (a "where" clause)"""
        svc = self.toolbox
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self._todelete.append(res[0]['id'])
        data2 = dict(type='Contact',
                    LastName='Doe',
                    FirstName='Jane',
                    Phone='123-456-7890',
                    Email='jane@doe.com',
                    Birthdate = datetime.date(1972, 10, 15)
                    )
        res = svc.create([data2])
        janeid = res[0]['id']
        self._todelete.append(janeid)
        res = svc.query(['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate'],
                         'Contact',
                         "LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        res = svc.query(['Id', 'LastName', 'FirstName', 'Phone', 'Email', 'Birthdate'],
                         'Contact', "LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], janeid)

    def test_queryRaisesWithNoSFObjectType(self):
        svc = self.toolbox
        self.assertRaises(ValueError, svc.query, ['LastName'], None, '')
        
    def test_queryRaisesWithNoFieldsRequested(self):
        svc = self.toolbox
        self.assertRaises(ValueError, svc.query, [], None, '')
        
    def test_queryListNotEmpty(self):
        """Test that we can retrieve records based on a 
           list-type field being non-empty."""
        svc = self.toolbox
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Fruit__c=['Pears',]
            )
        res = svc.create([data])
        johnid = res[0]['id']
        self._todelete.append(johnid)
        data2 = dict(type='Contact',
                    LastName='Doe',
                    FirstName='Jane',
                    )
        res = svc.create([data2])
        janeid = res[0]['id']
        self._todelete.append(janeid)
        res = svc.query(['LastName', 'FirstName', 'Phone', 'Favorite_Fruit__c'],
                         'Contact',
                         "LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        res = svc.query(['Id', 'LastName', 'FirstName', 'Favorite_Fruit__c'],
                         'Contact', "LastName = 'Doe' and Favorite_Fruit__c!=''")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], johnid)
        
    def test_update(self):
        """Create a record, retrieve it, update a field, 
           and confirm our update has been recorded when
           we retrieve it again"""
        svc = self.toolbox
        originaldate = datetime.date(1970, 1, 4)
        newdate = datetime.date(1970, 1, 5)
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=originaldate
                    )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve(['LastName', 'Birthdate'], 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], originaldate)
        self.assertEqual(contacts[0]['LastName'], lastname)
        data = dict(type='Contact',
                    Id=id,
                    Birthdate = newdate)
        svc.update(data)
        contacts = svc.retrieve(['LastName', 'Birthdate'], 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], newdate)
        self.assertEqual(contacts[0]['LastName'], lastname)
    
    def test_queryMore(self):
        """docstring for test_queryMore"""
        svc = self.toolbox
        svc.setBatchSize(100)
        data = list()
        for x in range(250):
            data.append(dict(type='Contact',
                            LastName='Doe',
                            FirstName='John',
                            Phone='123-456-7890',
                            Email='john@doe.com',
                            Birthdate = datetime.date(1970, 1, 4)
                            ))
        res = svc.create(data[:200])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.create(data[200:])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.query(['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate'],
                         'Contact', "LastName = 'Doe'")
        self.failUnless(not res['done'])
        self.assertEqual(len(res['records']), 200)
        res = svc.queryMore(res['queryLocator'])
        self.failUnless(res['done'])
        self.assertEqual(len(res['records']), 50)


    def test_setBatchSize(self):
        """Test that we can set maximum number of results in a single results
           set, independent of the maximum number of records that can be created
           in a single call.
        """
        svc = self.toolbox
        createBatchSize = svc.describeGlobal()['maxBatchSize']
        queryBatchSize = createBatchSize + 1
        data = list()
        for x in range(createBatchSize):
            data.append(dict(type='Contact',
                            LastName='Doe',
                            FirstName='John',
                            Phone='123-456-7890',
                            Email='john@doe.com',
                            Birthdate = datetime.date(1970, 1, 4)
                            ))
        res = svc.create(data)
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.create(data)
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
                
        svc.setBatchSize(queryBatchSize)
        res = svc.query(['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate'],
                         'Contact', "LastName = 'Doe'")
        
        self.failUnless(not res['done'])
        self.assertEqual(len(res['records']), queryBatchSize)
        res = svc.queryMore(res['queryLocator'])
        self.failUnless(res['done'])        
        self.assertEqual(len(res['records']), createBatchSize - 1)

    def test_listFieldsRequiredForCreation(self):
        requiredForLead = ['LastName', 'Company']
        testRequired = self.toolbox.listFieldsRequiredForCreation('Lead')
        self.assertEquals(requiredForLead, testRequired, "Required fields list doesn't match")
        requiredForContact = ['LastName']
        testRequired = self.toolbox.listFieldsRequiredForCreation('Contact')
        self.assertEquals(requiredForContact, testRequired, "Required fields list doesn't match")
        
    def test_getDeleted(self):
        svc = self.toolbox
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        id = res[0]['id']
        svc.delete(id)
        self._todelete.append(id)
        res = svc.getDeleted('Contact', startdate, enddate)
        self.failUnless(len(res) != 0)
        ids = [r['id'] for r in res]
        self.failUnless(id in ids)

    def test_getUpdated(self):
        svc = self.toolbox
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                )
        res = svc.create(data)
        id = res[0]['id']
        self._todelete.append(id)
        data = dict(type='Contact',
                Id=id,
                FirstName='Jane')
        svc.update(data)
        res = svc.getUpdated('Contact', startdate, enddate)
        self.failUnless(id in res)
    
    def test_create(self):
        """docstring for test_create"""
        # creation is tested implicitly in the above tests
        pass

    def test_delete(self):
        """docstring for test_create"""
        # deletion is also tested implicitly in the above tests
        pass

    def test_retrieve(self):
        """docstring for test_create"""
        # retrieve is ALSO tested implicitly in the above tests
        pass
    


class TestBaseConnectorConfiguration(SalesforceBaseConnectorTestCase):
    def afterSetUp(self):
        """docstring for afterSetUp"""
        
        # add, but don't configure, since that's the point of our tests
        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.toolbox = getToolByName(self.portal, "portal_salesforcebaseconnector")
    
    def testCanManageConfigTool(self):
        """Confirms #1 at: http://plone.org/products/salesforcebaseconnector/issues/1
        """
        # need to be manager to carry out test
        self.setRoles(['Manager',])
        
        # just collect the value in a variable, and make an assertion, thus
        # confirming we can getUsername and getPassword from ./www/manageAuthConfig.zpt
        _ = self.toolbox.manage_config()
        self.failUnless(_)
    


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBaseConnectorBeatboxInteraction))
    suite.addTest(makeSuite(TestSalesforceBaseConnector))
    suite.addTest(makeSuite(TestBaseConnectorConfiguration))
    return suite

