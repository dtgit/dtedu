import Products.Five
import Products.ATContentTypes

from DateTime import DateTime

def addMember(self, username, fullname="", email="", roles=('Member',), last_login_time=None):
    self.portal.portal_membership.addMember(username, 'secret', roles, [])
    member = self.portal.portal_membership.getMemberById(username)
    member.setMemberProperties({'fullname': fullname, 'email': email,
                                'last_login_time': DateTime(last_login_time),})

def setUpDefaultMembersBoardAndForum(self):
    addMember(self, 'member1', 'Member one', roles=('Member',))
    addMember(self, 'member2', 'Member two', roles=('Member',))
    addMember(self, 'manager1', 'Manager one', roles=('Manager',))
    addMember(self, 'reviewer1', 'Manager one', roles=('Reviewer',))

    self.workflow = self.portal.portal_workflow

    self.setRoles(('Manager',))
    self.portal.invokeFactory('Ploneboard', 'board1')
    self.board = self.portal.board1
    self.forum = self.board.addForum('forum1', 'Forum 1', 'Forum one')
    self.setRoles(('Member',))

def disableScriptValidators(portal):
    from Products.CMFFormController.FormController import ANY_CONTEXT, ANY_BUTTON
    scripts = ['add_comment_script', 'add_conversation_script', 'add_forum_script']
    try:
        for v in portal.portal_skins.ploneboard_scripts.objectValues():
            if v.id in scripts:
                v.manage_doCustomize('custom')
                portal.portal_form_controller.addFormValidators(v.id, ANY_CONTEXT, ANY_BUTTON, [])
    except:
        pass

def logoutThenLoginAs(self, browser, userid):
    browser.open('%s/logout' % self.portal.absolute_url())
    browser.open('%s/login_form' % self.portal.absolute_url())
    browser.getControl(name='came_from').value = self.portal.absolute_url()
    browser.getControl(name='__ac_name').value = userid
    browser.getControl(name='__ac_password').value = 'secret'
    browser.getControl('Log in').click()
    return
