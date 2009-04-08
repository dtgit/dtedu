from zope.publisher.browser import BrowserView
from AccessControl import getSecurityManager, Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
import sys, urllib2, urllib

class GroupManager(BrowserView):

    def getCohortAssignments(self, brains):
        """ Return list of brains for assignments of viewer's cohort members  """

        member = self.context.portal_membership.getAuthenticatedMember()
        groups = member.getGroups()
        group = ''
        for group in groups:
            if group.find('cohort') == 0:
                break
        if group:
            cohort_brains = []
            for brain in brains:
                owner = self.context.portal_membership.getMemberById(brain.Creator)
                if group in owner.getGroups():
                    cohort_brains += [brain,]
            return cohort_brains
        elif 'Manager' in member.getRoles():
            return brains
        else:
            return []        

    def addGroup(self, group_id, title=''):
        """ Create a group based on a specific id """

        pm = self.context.portal_membership
        if pm.isAnonymousUser():
            return False
        
        group = None
        success = 0
        groups = []
        roles = []
        kw = {}
        properties = None

        pg = self.context.portal_groups
        id = group_id
        if not title:
            title = group_id

        descrip = "Cohort for enrollees in the Certificate of Teaching Mastery"

        # Get the group managers, often there is just one: source_groups in acl_users.
        managers = pg._getGroupManagers()

        # Check to see if a group with the id already exists fail if it does
        results = pg.acl_users.searchPrincipals(id=id, exact_match=True)
        if results:
            return False

        if not managers:
            return False
        for mid, manager in managers:
            success = manager.addGroup(id, title=title,
                                       description=descrip)
            if success:
                pg.setRolesForGroup(id, roles)
                for g in groups:
                    manager.addPrincipalToGroup(g, id)
                break

        if success:
            group = pg.getGroupById(id)
            group.setGroupProperties(properties or kw)
            try:
                self.addGroupToLuvFoo(id)
            except urllib2.HTTPError, e:
                if e == '201':
                    #hack to get around urllib2 mismanaging of success code
                    return True
                else:
                    return e

    def addMemberToGroup(self, user_id, group_id):
        """ Add a user to the group """

        pm = self.context.portal_membership
        if pm.isAnonymousUser():
            return False

        pg = self.context.portal_groups
        managers = pg._getGroupManagers()
        if not managers:
            return False
        for mid, manager in managers:
            if manager.addPrincipalToGroup(user_id, group_id):
                try:
                    self.addMemberToLuvFooGroup(user_id, group_id)
                except urllib2.HTTPError, e:
                    if e == '201':
                        #hack to get around urllib2 mismanaging of success code
                        return True
        return False

    def addMemberToCTMMentors(self, user_id, group_id):
        """ Add a user to the CTMMentor group """

        pm = self.context.portal_membership
        if pm.isAnonymousUser():
            return False

        pg = self.context.portal_groups
        managers = pg._getGroupManagers()
        if not managers:
            return False
        for mid, manager in managers:
            manager.addPrincipalToGroup(user_id, group_id)
        return False




    def addGroupToLuvFoo(self, group_id):
        #add group to social network
        url = 'http://10.6.0.5:8080/users/twbadmin/groups.xml'
        data = urllib.urlencode([('group[name]', group_id),
                                 ('group[description]', 'CTM Cohort'),
                                 ('group[visibility]', 0),
                                 ('group[requires_approval_to_join]', 1),
                                 ('api_key',
                                  '68458bb917b77de7f61f631e10981797ecca65a73575e3d8ba08b9e554efacc032bc9fd04e5c59624c87910dbdb71c7a34634ea4ad7cd021b255468a5c21beea')])
        req = urllib2.Request(url)
        fd = urllib2.urlopen(req, data)


    def addMemberToLuvFooGroup(self, user_id, group_id):
        #Add member to group
        url = 'http://10.6.0.5:8080/groups/%s/memberships.xml' % group_id
        data = urllib.urlencode([('user_id', user_id),
                                 ('api_key',
                                  '68458bb917b77de7f61f631e10981797ecca65a73575e3d8ba08b9e554efacc032bc9fd04e5c59624c87910dbdb71c7a34634ea4ad7cd021b255468a5c21beea')])

        req = urllib2.Request(url)
        fd = urllib2.urlopen(req, data)


    def getCohortsWithoutMentor(self):
        #Return a list of cohorts that do not have a member that is also in the CTMMentor Group
        grp_tool = self.context.portal_groups
        groupids = grp_tool.getGroupIds()
        cohorts = []
        for id in groupids:
            if 'cohort' in id:
                cohorts += [id,]

        ctm_mentors = grp_tool.getGroupMembers('CTMMentor')

        mentorless_cohorts = []
        for cohort in cohorts:
            flagged = False
            #get members in cohort, check to see if they are in CTMMentor group
            members = grp_tool.getGroupMembers(cohort)
            for member in members:
                if member in ctm_mentors:
                    flagged = True
                    break
            if not flagged:
                mentorless_cohorts += [cohort]
        return mentorless_cohorts



