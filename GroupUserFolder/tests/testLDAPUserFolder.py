# -*- coding: utf-8 -*-
## GroupUserFolder
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: testLDAPUserFolder.py 34725 2006-12-15 12:27:06Z encolpe $
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))



# Load fixture
from Testing import ZopeTestCase

# Permissions / security
from AccessControl.Permissions import access_contents_information, view, add_documents_images_and_files, change_images_and_files, view_management_screens
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl import Unauthorized
from AccessControl.User import UnrestrictedUser

import urllib

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)

# Start the web server
host, port = ZopeTestCase.utils.startZServer(4)
base = 'http://%s:%d/%s' %(host, port, ZopeTestCase.folder_name)

    
# Get global vars
#from Products.GroupUserFolder.global_symbols import *
from Products.GroupUserFolder.interfaces import IUserFolder
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('LDAPUserFolder')

import GRUFTestCase
import testGroupUserFolderAPI
from Log import *


try:
    from LDAPconfig import defaults
except ImportError:
    Log(LOG_ERROR, """
    To perform this test case, you must provide a 'LDAPconfig.py' file with the following structure:

defaults = { 'title'  : 'LDAP User Folder'
           , 'server' : 'localhost:389'
           , 'login_attr' : 'cn'
           , 'uid_attr': 'cn'
           , 'users_base' : 'ou=people,dc=dataflake,dc=org'
           , 'users_scope' : 2
           , 'roles' : 'Anonymous'
           , 'groups_base' : 'ou=groups,dc=dataflake,dc=org'
           , 'groups_scope' : 2
           , 'binduid' : 'cn=Manager,dc=dataflake,dc=org'
           , 'bindpwd' : 'mypass'
           , 'binduid_usage' : 1
           , 'rdn_attr' : 'cn'
           , 'local_groups' : 1                 # Keep this true
           , 'use_ssl' : 0
           , 'encryption' : 'SHA'
           , 'read_only' : 0
           }

    Of course, you've got to replace all values by some relevant ones for your project.
    This test case won't complete without.

    NEVER PUT THIS FILE INTO YOUR CVS ! Unless you want your password to be publicly known...
    """)
    ldapuf = False
else:
    ldapuf = True
    dg = defaults.get




class TestLDAPUserFolderBasics(GRUFTestCase.GRUFTestCase):
    """
    Basic LDAPUserFolder binding
    This test just creates a LDAPUF connexion for the user source and performs a few API tests.
    Heavy LDAP testing is delegated to TestLDAPUserFolder class.
    """

    def gruf_sources_setup(self,):
        """
        Basic LDAP initialization inside gruf's user source
        """
        # User source replacement
        self.gruf.replaceUserSource("Users",
            "manage_addProduct/LDAPUserFolder/manage_addLDAPUserFolder",
            #title = dg('title'),
            #LDAP_server = dg('server'),
            #login_attr = dg('login_attr'),
            #uid_attr = dg('uid_attr'),
            #users_base = dg('users_base'),
            #users_scope = dg('users_scope'),
            #roles= dg('roles'),
            #groups_base = dg('groups_base'),
            #groups_scope = dg('groups_scope'),
            #binduid = dg('binduid'),
            #bindpwd = dg('bindpwd'),
            #binduid_usage = dg('binduid_usage'),
            #rdn_attr = dg('rdn_attr'),
            #local_groups = dg('local_groups'),
            #encryption = dg('encryption'),
            #use_ssl = dg('use_ssl'),
            #read_only=dg('read_only'),
            )

        # Edit LDAPUF 'cause objectClass cannot be set otherwise :(
        self.gruf.Users.acl_users.manage_edit(
            title = dg('title'),
            login_attr = dg('login_attr'),
            uid_attr = dg('uid_attr'),
            users_base = dg('users_base'),
            users_scope = dg('users_scope'),
            roles= dg('roles'),
            obj_classes = 'top,inetOrgPerson',
            groups_base = dg('groups_base'),
            groups_scope = dg('groups_scope'),
            binduid = dg('binduid'),
            bindpwd = dg('bindpwd'),
            binduid_usage = dg('binduid_usage'),
            rdn_attr = dg('rdn_attr'),
            local_groups = dg('local_groups'),
            encryption = dg('encryption'),
            read_only=dg('read_only'),
            )

        # Purge existing users in order to start on a clean basis
        self.delete_created_users()


    def test01_LDAPUp(self,):
        """Ensure LDAP is up and running
        """
        self.gruf.Users.acl_users.getUsers()



class TestLDAPUserFolderAPI(TestLDAPUserFolderBasics, testGroupUserFolderAPI.TestGroupUserFolderAPI):
    """
    Whole API test for GRUF+LDAP

    Users stored in LDAP
    Groups stored in ZODB
    """
    def test_getPureUsers(self):
        """
        The original test didn't work because of LDAPUF's cache -> we disable
        """
        pass

    def test_getUsers(self,):
        """
        The original test didn't work because of LDAPUF's cache -> we disable
        """
        pass

    def test_userSetDomains(self,):
        """
        LDAPUF has no domain support
        """
        pass

    def test_setProperty(self,):
        """Set user's properties
        """
        u1 = self.gruf.getUser("u1")

        # Simplest case: sn property setting
        u1.setProperty("sn", "Second Name Value")

        # We check that it has been changed
        self.failUnless(u1.getProperty("sn") == "Second Name Value", u1.getProperty("sn"), )



    def test_searchUsersByAttribute(self,):
        # Simple match
        self.failUnlessEqual(
            self.gruf.searchUsersByAttribute(defaults['login_attr'], "u3"),
            ["u3",],
            )

        # Different case matching
        self.failUnlessEqual(
            self.gruf.searchUsersByAttribute(defaults['login_attr'], "U3"),
            ["u3",],
            )

        # Multiple (different case) matching
        s = self.gruf.searchUsersByAttribute(defaults['login_attr'], "U")
        s.sort()
        self.failUnlessEqual(
            s,
            ['u1', 'u10', 'u11', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', ],
            )
        


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
##        suite.addTest(unittest.makeSuite(TestLDAPUserFolderBasics))
        if ldapuf:
            suite.addTest(unittest.makeSuite(TestLDAPUserFolderAPI))
        return suite

