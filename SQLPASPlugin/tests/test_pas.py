from Testing import ZopeTestCase
from Products.SQLPASPlugin.tests import basetestcase
import AccessControl
from Products.PluggableAuthService.UserPropertySheet import _guessSchema
import datetime
import DateTime


class TestPAS(basetestcase.BaseTestCase):

    def afterSetUp(self):
        self.username = 'joe'
        self.password = 'password'
        self.source_users = self.getPAS().source_users
        self.source_properties = self.getPAS().source_properties

    def testGuessSchema(self):
        sm = AccessControl.getSecurityManager()
        user = sm.getUser()

        info = {
            'firstname': 'Joe',
            'lastname': 'Schmoe',
            'email': 'joe@localhost.localdomain',
            'date_created': datetime.datetime.today(),
        }
        self.source_users.doAddUser(user.getUserName(), self.password)
        self.source_properties.updateUserInfo(user=user, set_id=None, set_info=info)

        props = self.source_properties.getPropertiesForUser(user)

        s = ''
        for key, value in props.propertyItems():
            s += 'key=%s; value=%s; type=%s\n' % (key, value, str(type(value)))

        #XXX props.setProperty(user, 'date_created', str(DateTime.DateTime()))

        for value in props.propertyValues():
            value = dict(value=value)
            _guessSchema(value)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPAS))
    return suite
