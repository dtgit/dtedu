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
                                                                           
                      GRUF3 Feature-preview stuff.                         
                                                                           
 This code shouldn't be here but allow people to preview advanced GRUF3    
 features (eg. flexible LDAP searching in 'sharing' tab, ...) in Plone 2,  
 without having to upgrade to Plone 2.1.
                                                                           
 Methods here are monkey-patched by now but will be provided directly by
 Plone 2.1.
 Please forgive this 'uglyness' but some users really want to have full    
 LDAP support without switching to the latest Plone version ! ;)


 BY DEFAULT, this thing IS enabled with Plone 2.0.x
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: PloneFeaturePreview.py 30098 2006-09-08 12:35:01Z encolpe $
__docformat__ = 'restructuredtext'

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from OFS.Image import Image
from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base
from AccessControl.User import nobody
from AccessControl import ClassSecurityInfo
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from interfaces.portal_groups import portal_groups as IGroupsTool
from global_symbols import *


# This is "stollen" from MembershipTool.py
# this should probably be in MemberDataTool.py
def searchForMembers( self, REQUEST=None, **kw ):
    """
    searchForMembers(self, REQUEST=None, **kw) => normal or fast search method.

    The following properties can be provided:
    - name
    - email
    - last_login_time
    - roles

    This is an 'AND' request.

    If name is provided, then a _fast_ search is performed with GRUF's
    searchUsersByName() method. This will improve performance.

    In any other case, a regular (possibly _slow_) search is performed.
    As it uses the listMembers() method, which is itself based on gruf.getUsers(),
    this can return partial results. This may change in the future.
    """
    md = self.portal_memberdata
    mt = self.portal_membership
    if REQUEST:
        dict = REQUEST
    else:
        dict = kw

    # Attributes retreiving & mangling
    name = dict.get('name', None)
    email = dict.get('email', None)
    roles = dict.get('roles', None)
    last_login_time = dict.get('last_login_time', None)
    is_manager = mt.checkPermission('Manage portal', self)
    if name:
        name = name.strip().lower()
    if email:
        email = email.strip().lower()


    # We want 'name' request to be handled properly with large user folders.
    # So we have to check both the fullname and loginname, without scanning all
    # possible users.
    md_users = None
    uf_users = None
    if name:
        # We first find in MemberDataTool users whose _full_ name match what we want.
        lst = md.searchMemberDataContents('fullname', name)
        md_users = [ x['username'] for x in lst ]

        # Fast search management if the underlying acl_users support it.
        # This will allow us to retreive users by their _id_ (not name).
        acl_users = self.acl_users
        meth = getattr(acl_users, "searchUsersByName", None)
        if meth:
            uf_users = meth(name)           # gruf search

    # Now we have to merge both lists to get a nice users set.
    # This is possible only if both lists are filled (or we may miss users else).
    Log(LOG_DEBUG, md_users, uf_users, )
    members = []
    if md_users is not None and uf_users is not None:
        names_checked = 1
        wrap = mt.wrapUser
        getUser = acl_users.getUser
        for userid in md_users:
            members.append(wrap(getUser(userid)))
        for userid in uf_users:
            if userid in md_users:
                continue             # Kill dupes
            usr = getUser(userid)
            if usr is not None:
                members.append(wrap(usr))

        # Optimization trick
        if not email and \
               not roles and \
               not last_login_time:
            return members          
    else:
        # If the lists are not available, we just stupidly get the members list
        members = self.listMembers()
        names_checked = 0

    # Now perform individual checks on each user
    res = []
    portal = self.portal_url.getPortalObject()

    for member in members:
        #user = md.wrapUser(u)
        u = member.getUser()
        if not (member.listed or is_manager):
            continue
        if name and not names_checked:
            if (u.getUserName().lower().find(name) == -1 and
                member.getProperty('fullname').lower().find(name) == -1):
                continue
        if email:
            if member.getProperty('email').lower().find(email) == -1:
                continue
        if roles:
            user_roles = member.getRoles()
            found = 0
            for r in roles:
                if r in user_roles:
                    found = 1
                    break
            if not found:
                continue
        if last_login_time:
            if member.last_login_time < last_login_time:
                continue
        res.append(member)
    Log(LOG_DEBUG, res)
    return res


def listAllowedMembers(self,):
    """listAllowedMembers => list only members which belong
    to the same groups/roles as the calling user.
    """
    user = self.REQUEST['AUTHENTICATED_USER']
    caller_roles = user.getRoles()              # Have to provide a hook for admins
    current_members = self.listMembers()
    allowed_members =[]
    for member in current_members:
        for role in caller_roles:
            if role in member.getRoles():
                allowed_members.append(member)
                break
    return allowed_members


def _getPortrait(self, member_id):
    """
    return member_id's portrait if you can.
    If it's not possible, just try to fetch a 'portait' property from the underlying user source,
    then create a portrait from it.
    """
    # fetch the 'portrait' property
    Log(LOG_DEBUG, "trying to fetch the portrait for the given member id")
    portrait = self._former_getPortrait(member_id)
    if portrait:
        Log(LOG_DEBUG, "Returning the old-style portrait:", portrait, "for", member_id)
        return portrait

    # Try to find a portrait in the user source
    member = self.portal_membership.getMemberById(member_id)
    portrait = member.getUser().getProperty('portrait', None)
    if not portrait:
        Log(LOG_DEBUG, "No portrait available in the user source for", member_id)
        return None

    # Convert the user-source portrait into a plone-complyant one
    Log(LOG_DEBUG, "Converting the portrait", type(portrait))
    portrait = Image(id=member_id, file=portrait, title='')
    membertool = self.portal_memberdata
    membertool._setPortrait(portrait, member_id)

    # Re-call ourself to retreive the real portrait
    Log(LOG_DEBUG, "Returning the real portrait")
    return self._former_getPortrait(member_id)


def setLocalRoles( self, obj, member_ids, member_role, reindex=1 ):
    """ Set local roles on an item """
    member = self.getAuthenticatedMember()
    gruf = self.acl_users
    my_roles = member.getRolesInContext( obj )

    if 'Manager' in my_roles or member_role in my_roles:
        for member_id in member_ids:
            u = gruf.getUserById(member_id) or gruf.getGroupByName(member_id)
            if not u:
                continue
            member_id = u.getUserId()
            roles = list(obj.get_local_roles_for_userid( userid=member_id ))

            if member_role not in roles:
                roles.append( member_role )
                obj.manage_setLocalRoles( member_id, roles )

    if reindex:
        # It is assumed that all objects have the method
        # reindexObjectSecurity, which is in CMFCatalogAware and
        # thus PortalContent and PortalFolder.
        obj.reindexObjectSecurity()

def deleteLocalRoles( self, obj, member_ids, reindex=1 ):
    """ Delete local roles for members member_ids """
    member = self.getAuthenticatedMember()
    my_roles = member.getRolesInContext( obj )
    gruf = self.acl_users
    member_ids = [
        u.getUserId() for u in [
            gruf.getUserById(u) or gruf.getGroupByName(u) for u in member_ids
            ] if u
        ]

    if 'Manager' in my_roles or 'Owner' in my_roles:
        obj.manage_delLocalRoles( userids=member_ids )

    if reindex:
        obj.reindexObjectSecurity()

# Monkeypatch it !
if PREVIEW_PLONE21_IN_PLONE20_:
    from Products.CMFCore import MembershipTool as CMFCoreMembershipTool
    CMFCoreMembershipTool.MembershipTool.setLocalRoles = setLocalRoles
    CMFCoreMembershipTool.MembershipTool.deleteLocalRoles = deleteLocalRoles
    from Products.CMFPlone import MemberDataTool
    from Products.CMFPlone import MembershipTool
    MembershipTool.MembershipTool.searchForMembers = searchForMembers
    MembershipTool.MembershipTool.listAllowedMembers = listAllowedMembers
    MemberDataTool.MemberDataTool._former_getPortrait = MemberDataTool.MemberDataTool._getPortrait
    MemberDataTool.MemberDataTool._getPortrait = _getPortrait
    Log(LOG_NOTICE, "Applied GRUF's monkeypatch over Plone 2.0.x. Enjoy!")



