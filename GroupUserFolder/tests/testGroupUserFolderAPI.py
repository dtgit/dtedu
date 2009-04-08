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
# $Id: testGroupUserFolderAPI.py 34723 2006-12-15 11:25:30Z encolpe $
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

# Permissions / security
from AccessControl.Permissions import access_contents_information, view, \
     add_documents_images_and_files, change_images_and_files, view_management_screens
from AccessControl.SecurityManagement import newSecurityManager, \
     noSecurityManager, getSecurityManager
from AccessControl import Unauthorized
from AccessControl.User import UnrestrictedUser

import urllib
import string

# Create the error_log object
app = ZopeTestCase.app()
ZopeTestCase.utils.setupSiteErrorLog(app)
ZopeTestCase.close(app)
    
from Products.GroupUserFolder.interfaces import IUserFolder
from Products.GroupUserFolder import GroupUserFolder
from Interface import Verify

# Install our product
ZopeTestCase.installProduct('GroupUserFolder')

import GRUFTestCase
import testInterface
from Log import *

class TestGroupUserFolderAPI(GRUFTestCase.GRUFTestCase, testInterface.TestInterface):

    klasses = (        # tell which classes to check
        GroupUserFolder.GroupUserFolder,
        )

    def test10GRUFMethods(self,):
        """
        We test that GRUF's API is well protected
        """
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')
        self.assertRaises(Unauthorized, self.gruf_folder.restrictedTraverse, 'acl_users/getGRUFPhysicalRoot')

    #                                                   #
    #                  GRUF API testing                 #
    #                                                   #
        
    def test_getUserNames(self):
        un = self.gruf.getUserNames()
        users = [
            'g1', 'g2', "g3", "g4",
            "ng1", "ng2", "ng3", "ng4", "ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "extranet", "intranet", "compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getUserIds(self):
        un = self.gruf.getUserIds()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))
                
    def test_getUser(self):
        # Check id access
        usr = self.gruf.getUser("u1")
        self.failUnless(usr.__class__.__name__ == "GRUFUser")
        self.failUnless(usr.getUserName() == "u1")
        grp = self.gruf.getUser("group_g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")

        # Check name access for groups
        grp = self.gruf.getUser("g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")

    def test_hasUsers(self):
        self.failUnlessEqual(self.gruf.hasUsers(), 1, "GRUF should always return 1 on hasUsers but didn't.")

    def test_getUsers(self):
        objects = self.gruf.getUsers()
        un = map(lambda x: x.getId(), objects)
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getUserById(self):
        # Check user & group access
        self.failUnless(self.gruf.getUserById("u1").getUserName() == "u1")
        self.failUnless(self.gruf.getUserById("group_g1").getId() == "group_g1")

        # Prohibit direct group access
        self.failUnless(self.gruf.getUserById("g1", default = None) is None)

        # check exception raising & default values
        ret = self.gruf.getUserById("ZORGLUB")
        self.failUnlessEqual(ret, None, "getUserById should return None")
        self.failUnless(self.gruf.getUserById("ZORGLUB", default = "bla") == "bla")

    def test_getUserByName(self):
        # Check user & group access
        self.failUnless(self.gruf.getUserByName("u1").getUserName() == "u1")
        self.failUnless(self.gruf.getUserByName("g1").getId() == "group_g1")

        # Check group id access
        self.failUnless(self.gruf.getUserByName("group_g1", None).getId() == "group_g1")

        # Check exception raising
        ret = self.gruf.getUserByName("ZORGLUB")
        self.failUnlessEqual(ret, None, "getUserByName should return None")
        self.failUnless(self.gruf.getUserByName("ZORGLUB", default = "bla") == "bla")

    # User access

    def test_getPureUserNames(self):
        """Same as getUserNames() but without groups
        """
        un = self.gruf.getPureUserNames()
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getPureUserIds(self,):
        """Same as getUserIds() but without groups
        """
        un = self.gruf.getPureUserIds()
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getPureUsers(self):
        """Same as getUsers() but without groups.
        """
        # Fetch pure users
        users = [
            "manager",
            "u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8", "u9", "u10", "u11",
            ]
        objects = self.gruf.getPureUsers()
        un = map(lambda x: x.getId(), objects)
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u, ))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getPureUser(self,):
        u = self.gruf.getPureUser("u1")
        self.failUnless(u)
        u = self.gruf.getPureUser("g1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("group_g1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("group_u1")
        self.failUnless(not u)
        u = self.gruf.getPureUser("u4")
        self.failUnless(u)
        
    # Group access

    def test_getGroupNames(self):
        """Same as getUserNames() but without pure users.
        """
        un = self.gruf.getGroupNames()
        users = [
            'g1', 'g2', "g3", "g4",
            "ng1", "ng2", "ng3", "ng4", "ng5",
            "extranet", "intranet", "compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getGroupIds(self,):
        un = self.gruf.getGroupIds()
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))


    def test_getGroups(self):
        objects = self.gruf.getGroups()
        un = map(lambda x: x.getId(), objects)
        users = [
            'group_g1', 'group_g2', "group_g3", "group_g4",
            "group_ng1", "group_ng2", "group_ng3", "group_ng4", "group_ng5",
            "group_extranet", "group_intranet", "group_compta",
            ]
        un.sort()
        users.sort()
        for u in users:
            self.failUnless(u in un, "Invalid users list: '%s' is not in acl_users." % (u,))
        for u in un:
            self.failUnless(u in users, "Invalid users list: '%s' is in acl_users but shouldn't be there." % (u,))

    def test_getGroup(self):
        # Check name access
        grp = self.gruf.getGroup("g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")
        self.failUnless(grp.getId() == "group_g1")

        # Check id access
        grp = self.gruf.getGroup("group_g1")
        self.failUnless(grp.isGroup())
        self.failUnless(grp.getId() == "group_g1")
        self.failUnless(grp.__class__.__name__ == "GRUFGroup")

        # Prevent user access
        usr = self.gruf.getGroup("u1")
        self.failUnless(usr is None)

    def test_getGroupById(self):
        # Id access
        grp = self.gruf.getGroupById("group_g1")
        self.failUnless(grp.getId() == "group_g1")

        # Prevent name access
        grp = self.gruf.getGroupById("g1", default = None)
        self.failUnless(grp is None)

        # Prevent user access
        grp = self.gruf.getGroupById("u1", default = None)
        self.failUnless(grp is None)

        # Check raise if user/group not found
        self.failUnlessEqual(
            self.gruf.getGroupById("ZORGLUB"),
            None,
            )
        self.failUnless(self.gruf.getGroupById("ZORGLUB", default = "bla") == "bla")

    def test_getGroupByName(self):
        # Name access
        grp = self.gruf.getGroupByName("g1")
        self.failUnless(grp.getId() == "group_g1")

        # Allow id access
        grp = self.gruf.getGroupByName("group_g1", default = None)
        self.failUnless(grp.getId() == "group_g1")

        # Prevent user access
        self.failUnless(self.gruf.getGroupByName("u1", default = None) is None)

        # Check raise if user/group not found
        self.failUnlessEqual(
            self.gruf.getGroupByName("ZORGLUB"),
            None,
            )
        self.failUnless(self.gruf.getGroupByName("ZORGLUB", default = "bla") == "bla")

    # Mutators

    def test_userFolderAddUser(self):
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            roles = [],
            groups = [],
            domains = (),
            )
        self.failUnless(self.gruf.getUser("created_user"))
        self.gruf.userFolderAddUser(
            name = "group_test_prefix",
            password = "secret",
            roles = [],
            groups = [],
            domains = (),
            )
        self.failUnless(self.gruf.getUser("group_test_prefix"))
        self.failIf(self.gruf.getUser("group_test_prefix").isGroup())
        
    def test_userFolderEditUser(self):
        self.gruf.userFolderEditUser(
            name = "u1",
            password = "secret2",
            roles = ["r1", ],
            groups = ["g1", ],
            domains = (),
            )
        self.compareRoles(None, "u1", ['r1',], )

    def test_userFolderUpdateUser(self):
        self.gruf.userFolderUpdateUser(
            name = "u5",
            roles = ["r2", ],
            )
        self.compareRoles(None, "u5", ['r1', 'r2',], )
        self.compareGroups("u5", ['g2', 'g3'], )
        self.gruf.userFolderUpdateUser(
            name = "u6",
            roles = None,
            )
        self.compareRoles(None, "u6", ['r1', 'r2', ], )

    def test_userFolderDelUsers(self):
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            roles = [],
            domains = (),
            groups = [],
            )
        self.gruf.userFolderDelUsers(['created_user', ])
        self.failUnless(self.gruf.getUser("created_user") is None)

    def test_userFolderAddGroup(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getGroup("created_group"))
        self.gruf.userFolderAddGroup(
            name = "group_test_prefix",
            roles = [],
            groups = [],
            )
        self.failUnless(self.gruf.getGroup("group_test_prefix"))
        self.failUnless(self.gruf.getGroup("group_test_prefix").isGroup())

        # Prevent group_group_xxx names
        self.failUnless(self.gruf.getGroupById("group_group_test_prefix", None) is None)
        
    def test_userFolderEditGroup(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderEditGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = ["group_g1", ],
            )
        self.compareRoles(None, "created_group", ['r1',], )
        self.failUnless(
            "g1" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )
        self.gruf.userFolderEditGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = ["g2", ],
            )
        self.failUnless(
            "g2" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )
        
    def test_userFolderUpdateGroup(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderUpdateGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = ["group_g1", ],
            )
        self.compareRoles(None, "created_group", ['r1',], )
        self.failUnless(
            "g1" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )
        self.gruf.userFolderUpdateGroup(
            name = "created_group",
            roles = ["r1", ],
            groups = None,
            )
        self.failUnless(
            "g1" in self.gruf.getGroupByName("created_group").getAllGroupNames(),
            self.gruf.getGroupByName("created_group").getAllGroupNames(),
            )

    def test_userFolderDelGroups(self):
        self.gruf.userFolderAddGroup(
            name = "created_group",
            roles = [],
            groups = [],
            )
        self.gruf.userFolderDelGroups(['created_group', ])
        self.failUnless(self.gruf.getGroup("created_group") is None)

    # User mutation

    def test_userSetRoles(self):
        self.gruf.userSetRoles("u1", ["r1", "r2", ], )
        self.compareRoles(None, "u1", ["r1", "r2", ], )
        self.gruf.userSetRoles("u1", [], )
        self.compareRoles(None, "u1", [], )

    def test_userAddRole(self):
        self.gruf.userAddRole("u1", "r1", )
        self.gruf.userAddRole("u1", "r2", )
        self.compareRoles(None, "u1", ["r1", "r2", ], )

    def test_userRemoveRole(self):
        """Remove the role of a user atom
        """
        self.gruf.userSetRoles("u1", ["r1", "r2", ], )
        self.compareRoles(None, "u1", ["r1", "r2", ], )
        self.gruf.userRemoveRole("u1", "r1", )
        self.compareRoles(None, "u1", ["r2", ], )

    def test_userSetPassword(self):
        """Test user password setting
        """
        # Regular user password
        user = self.gruf.getUser('u1')
        self.failUnless(self.gruf.authenticate("u1", 'secret', self.app.REQUEST))
        self.gruf.userSetPassword("u1", "bloub")
        user = self.gruf.getUser('u1')
        self.failUnless(not self.gruf.authenticate("u1", 'secret', self.app.REQUEST))
        self.failUnless(self.gruf.authenticate("u1", 'bloub', self.app.REQUEST))

        # Group password changing must fail
        try: self.gruf.userSetPassword("g1", "bloub")
        except ValueError: pass                # ok
        else: raise "AssertionError", "Should raise"
        try: self.gruf.userSetPassword("group_g1", "bloub")
        except ValueError: pass                # ok
        else: raise "AssertionError", "Should raise"

    def test_userGetDomains(self):
        ""

    def test_userSetDomains(self):
        ""
        u = self.gruf.getUser("u1")
        self.failUnless(not self.gruf.userGetDomains("u1"))
        self.gruf.userSetDomains("u1", ["d1", "d2", "d3", ])
        self.failUnless(self.gruf.userGetDomains("u1") == ("d1", "d2", "d3", ))
        self.gruf.userSetDomains("u1", [])
        self.failUnless(self.gruf.userGetDomains("u1") == ())
        self.gruf.userSetDomains("u1", ["xxx"])
        self.failUnless(self.gruf.userGetDomains("u1") == ("xxx", ))

    def test_userAddDomain(self):
        ""

    def test_userRemoveDomain(self):
        ""

    def test_userSetGroups(self):
        # Test user
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            domains = (),
            roles = (),
            groups = [],
            )
        self.gruf.userSetGroups("created_user", ["g1", "g2", ], )
        self.compareGroups("created_user", ["g1", "g2", ], )
        self.gruf.userSetGroups("created_user", [], )
        self.compareGroups("created_user", [], )

    def test_userAddGroup(self):
        # Test user
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = ["g2", ],
            roles = (),
            domains = (),
            )
        self.gruf.userAddGroup(
            "created_user",
            "g1",
            )
        self.compareGroups("created_user", ["g1", "g2", ], )

    def test_userRemoveGroup(self):
        """Remove the group of a user atom
        """
        self.gruf.userFolderAddUser(
            name = "created_user",
            password = "secret",
            groups = ["g2", "g1", ],
            domains = (),
            roles = (),
            )
        self.gruf.userRemoveGroup("created_user", "g1", )
        self.compareGroups("created_user", ["g2", ], )

    # Searching

    def test_searchUsersByAttribute(self,):
        # Not suitable for regular UFs
        self.failUnlessRaises(
            NotImplementedError,
            self.gruf.searchUsersByAttribute,
            "a",
            "b",
            )

    def test_searchUsersByName(self,):
        # Simple match
        self.failUnlessEqual(
            self.gruf.searchUsersByName("u3"),
            ["u3",],
            )

        # Different case matching
        self.failUnlessEqual(
            self.gruf.searchUsersByName("U3"),
            ["u3",],
            )

        # Multiple (different case) matching
        s = self.gruf.searchUsersByName("U")
        s.sort()
        self.failUnlessEqual(
            s,
            ['u1', 'u10', 'u11', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', ],
            )

    def test_searchUsersById(self,):
        # Simple match
        self.failUnlessEqual(
            self.gruf.searchUsersById("u3"),
            ["u3",],
            )

        # Different case matching
        self.failUnlessEqual(
            self.gruf.searchUsersById("U3"),
            ["u3",],
            )

        # Multiple (different case) matching
        s = self.gruf.searchUsersById("U")
        s.sort()
        self.failUnlessEqual(
            s,
            ['u1', 'u10', 'u11', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', ],
            )

    def test_searchGroupsByAttribute(self,):
        # Not suitable for regular UFs
        self.failUnlessRaises(
            NotImplementedError,
            self.gruf.searchGroupsByAttribute,
            "a",
            "b",
            )

    def test_searchGroupsByName(self,):
        # Simple match
        lst = self.gruf.searchGroupsByName("g3")
        lst.sort()
        self.failUnlessEqual(
            lst,
            ["group_g3", "group_ng3", ],
            )

        # Different case matching
        lst = self.gruf.searchGroupsByName("g3")
        lst.sort()
        self.failUnlessEqual(
            lst,
            ["group_g3", "group_ng3", ],
            )

        # Multiple (different case) matching
        s = self.gruf.searchGroupsByName("1")
        s.sort()
        self.failUnlessEqual(
            s,
            ["group_g1", "group_ng1", ]
            )

    def test_searchGroupsById(self,):
        # Simple match
        self.failUnlessEqual(
            self.gruf.searchGroupsById("g5"),
            ["group_ng5",],
            )

        # Different case matching
        self.failUnlessEqual(
            self.gruf.searchGroupsById("G5"),
            ["group_ng5",],
            )

        # Multiple (different case) matching
        s = self.gruf.searchGroupsById("G1")
        s.sort()
        self.failUnlessEqual(
            s,
            ["group_g1", "group_ng1", ]
            )

    # Security management

    def test_setRolesOnUsers(self):
        """Set a common set of roles for a bunch of user atoms.
        """
        self.gruf.setRolesOnUsers(["r1", "r2", "r3", ], ["u1", "u2", ])
        self.compareRoles(None, "u1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "u2", ["r1", "r2", "r3", ])
        self.gruf.setRolesOnUsers([], ["u2", ])
        self.compareRoles(None, "u1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "u2", [])

    def test_setRolesOnGroups(self,):
        """Same as test_setRolesOnUsers but with groups"""
        self.gruf.setRolesOnUsers(["r1", "r2", "r3", ], ["g1", "g2", ])
        self.compareRoles(None, "g1", ["r1", "r2", "r3", ])
        self.compareRoles(None, "g2", ["r1", "r2", "r3", ])

    def test_getUsersOfRole(self):
        should_be = [
            'group_ng2','group_ng3',
            'group_ng4',
            'group_ng5',
            'u9',
            'u5',
            'u4',
            'u7',
            'u6',
            'u11',
            'u10',
            'group_g3',
            'group_g4',
            ]
        should_be.sort()
        users = list(self.gruf.getUsersOfRole("r2"))
        users.sort()
        self.failUnless(users == should_be, (should_be, users, ))

    def test_getRolesOfUser(self):
        self.failUnless("r1" in self.gruf.getRolesOfUser("u3"), self.gruf.getRolesOfUser("u3"), )

    def test_userFolderGetRoles(self,):
        """
        Test existing roles
        """
        should_be =  [
            'Anonymous',
            'Authenticated',
            'Manager',
            'Owner',
            'r1',
            'r2',
            'r3',
            'test_role_1_',
            ]
        should_be.sort()
        roles = list(self.gruf.userFolderGetRoles())
        roles.sort()
        self.failUnless(roles == should_be)

    def test_userFolderAddRole(self):
        self.gruf.userFolderAddRole("r9")
        self.failUnless(
            "r9" in self.gruf.userFolderGetRoles(),
            )

    def test_userFolderDelRoles(self):
        """Delete roles.
        The removed roles will be removed from the UserFolder's users and groups as well,
        so this method can be very time consuming with a large number of users.
        """
        # Add a role and set it to a few groups
        self.gruf.userFolderAddRole("r9")
        self.failUnless(
            "r9" in self.gruf.userFolderGetRoles(),
            )
        self.gruf.userAddRole("g2", "r9")
        self.gruf.userAddRole("u1", "r9")
        self.failUnless(
            "r9" in self.gruf.getRolesOfUser("u1")
            )
        self.failUnless(
            "r9" in self.gruf.getRolesOfUser("u4")
            )

        # Now, remove it
        self.gruf.userFolderDelRoles(['r9', ])
        self.failUnless(
            "r9" not in self.gruf.getRolesOfUser("u1")
            )
        self.failUnless(
            "r9" not in self.gruf.getRolesOfUser("u4")
            )

    # Groups support

    def test_getMemberIds(self,):
        should_be = [
            'group_ng2',
            'group_ng3',
            'group_ng4',
            'group_ng5',
            'u9',
            'u5',
            'u4',
            'u6',
            'u11',
            'u10',
            ]
        should_be.sort()
        users = list(self.gruf.getMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be))

    def test_getUserMemberIds(self,):
        """This tests nested groups"""
        should_be = [
            'u9',
            'u5',
            'u4',
            'u6',
            'u11',
            'u10',
            ]
        should_be.sort()
        users = list(self.gruf.getUserMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be, ))
        
    def test_getGroupMemberIds(self,):
        should_be = [
            'group_ng2',
            'group_ng3',
            'group_ng4',
            'group_ng5',
            ]
        should_be.sort()
        users = list(self.gruf.getGroupMemberIds("g3"))
        users.sort()
        self.failUnless(users == should_be, (users, should_be, ))

    def test_addMember(self):
        """Add a member to a group
        """
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless("u1" in self.gruf.getMemberIds("ng3"))

    def test_removeMember(self):
        """Remove a member from a group
        """
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless("u1" in self.gruf.getMemberIds("ng3"))
        self.gruf.removeMember("ng3", "u1")
        self.failUnless("u1" not in self.gruf.getMemberIds("ng3"))

    def test_setMembers(self):
        """Set the members of the group
        """
        member_ids = self.gruf.getMemberIds("ng3")
        self.gruf.addMember("ng3", "u1")
        self.gruf.addMember("ng3", "u2")
        self.failIf("u1" not in self.gruf.getMemberIds("ng3"))
        self.failIf("u2" not in self.gruf.getMemberIds("ng3"))
        self.failIf("u3" in self.gruf.getMemberIds("ng3"))

        self.gruf.setMembers("ng3", (member_ids + ["u2", "u3"]))

        self.failIf("u1" in self.gruf.getMemberIds("ng3"))
        self.failIf("u2" not in self.gruf.getMemberIds("ng3"))
        self.failIf("u3" not in self.gruf.getMemberIds("ng3"))

    def test_hasMember(self,):
        self.failUnless(not self.gruf.hasMember("ng3", "u1"))
        self.failUnless(not self.gruf.hasMember("group_ng3", "u1"))
        self.gruf.addMember("ng3", "u1")
        self.failUnless(self.gruf.hasMember("ng3", "u1"))
        self.failUnless(self.gruf.hasMember("group_ng3", "u1"))
        self.gruf.removeMember("ng3", "u1")
        self.failUnless(not self.gruf.hasMember("ng3", "u1"))
        self.failUnless(not self.gruf.hasMember("group_ng3", "u1"))

    # Misc
    def test_getRealId(self,):
        """Test group id without group prefix"""
        g = self.gruf.getUser("group_ng2")
        self.failUnless(g.getRealId() == "ng2")
        u = self.gruf.getUser("u1")
        self.failUnless(u.getRealId() == "u1")

    # Local roles management
    def test_acquireLocalRoles(self,):
        """
        We block LR acquisition on sublr2.
        See GRUFTestCase to understand what happens (basically, roles in brackets
        will be removed from sublr2).
        """
        # Initial check
        self.failUnless(self.compareRoles(self.sublr2, "u2", ("r3", )))
        self.failUnless(self.compareRoles(self.sublr2, "u3", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.sublr2, "u6", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.subsublr2, "u2", ("r3", )))
        self.failUnless(self.compareRoles(self.subsublr2, "u3", ("r1", "r2", "r3", )))
        self.failUnless(self.compareRoles(self.subsublr2, "u6", ("r1", "r2", "r3", )))
        
        # Disable LR acquisition on sublr2 and test the stuff
        self.gruf._acquireLocalRoles(self.sublr2, 0)
        self.failUnless(self.compareRoles(self.sublr2, "u2", ()))
        self.failUnless(self.compareRoles(self.sublr2, "u3", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.sublr2, "u6", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.subsublr2, "u2", ()))
        self.failUnless(self.compareRoles(self.subsublr2, "u3", ("r1", "r2", )))
        self.failUnless(self.compareRoles(self.subsublr2, "u6", ("r1", "r2", )))

    def test_isLocalRoleAcquired(self,):
        self.gruf._acquireLocalRoles(self.sublr2, 0)
        self.failUnless(not self.gruf.isLocalRoleAcquired(self.sublr2))
        self.failUnless(self.gruf.isLocalRoleAcquired(self.subsublr2))
        self.gruf._acquireLocalRoles(self.subsublr2, 0)
        self.failUnless(not self.gruf.isLocalRoleAcquired(self.sublr2))
        self.failUnless(not self.gruf.isLocalRoleAcquired(self.subsublr2))
        self.gruf._acquireLocalRoles(self.sublr2, 1)
        self.failUnless(self.gruf.isLocalRoleAcquired(self.sublr2))
        self.failUnless(not self.gruf.isLocalRoleAcquired(self.subsublr2))
        self.gruf._acquireLocalRoles(self.subsublr2, 1)
        self.failUnless(self.gruf.isLocalRoleAcquired(self.sublr2))
        self.failUnless(self.gruf.isLocalRoleAcquired(self.subsublr2))

    # Audit checks

    def test_getAllLocalRoles(self):
        # Allowed patterns
        normal_allowed = {
            'group_g1': ['r3', ],
            'u6': ['r2', 'r3', ],
            'test_user_1_': ['Owner', ],
            'u3': ['r2', 'r3', ],
            }
        blocked_allowed = {
            'u6': ['r2', ],
            'test_user_1_': ['Owner', ],
            'u3': ['r2', ],
            }

        # Normal behaviour
        ob = self.sublr2
        allowed = self.gruf._getAllLocalRoles(ob)
        self.failUnlessEqual(allowed, normal_allowed)

        # LR-blocking behaviour
        ob = self.sublr2
        self.gruf._acquireLocalRoles(ob, 0)
        allowed = self.gruf._getAllLocalRoles(ob)
        self.failUnlessEqual(allowed, blocked_allowed)


if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestGroupUserFolderAPI))
        return suite

