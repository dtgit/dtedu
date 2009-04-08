from zope.publisher.browser import BrowserView

class XmlRpcMethods(BrowserView):


    def xmlrpc_createMemberArea(self, user_id):
        """ Adds a member area upon account creation """
        pm = self.context.portal_membership
        if pm.isAnonymousUser():
            return False
        pm.createMemberArea()
        return True
