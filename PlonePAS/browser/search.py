from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.interfaces.browser import IPASSearchView


class PASSearchView(BrowserView):
    implements(IPASSearchView)

    @staticmethod
    def extractCriteriaFromRequest(request):
        criteria=request.form.copy()

        for key in [ "form.submitted", "submit", 'b_start', 'b_size']:
            if key in criteria:
                del criteria[key]

        for (key, value) in criteria.items():
            if not value:
                del criteria[key]

        return criteria


    @staticmethod
    def merge(results, key):
        return dict([(result[key], result) for result in results]).values()


    def sort(self, results, key):
        def key_func(a):
            return a.get(key, "").lower()
        results.sort(key=key_func)
        return results


    def searchUsers(self, sort_by=None, **criteria):
        self.pas=getToolByName(self.context, "acl_users")
        results=self.merge(self.pas.searchUsers(**criteria), "userid")
        if sort_by is not None:
            results=self.sort(results, sort_by)
        return results


    def searchUsersByRequest(self, request, sort_by=None):
        criteria=self.extractCriteriaFromRequest(request)
        return self.searchUsers(sort_by=sort_by, **criteria)


    def searchGroups(self, **criteria):
        self.pas=getToolByName(self.context, "acl_users")
        return self.pas.searchGroups(**criteria)


    def searchGroupsByRequest(self, request):
        criteria=self.extractCriteriaFromRequest(request)
        return self.searchGroups(**criteria)


    def getPhysicalPath(self):
        # We call various PAS methods which can be ZCached. The ZCache
        # infrastructure relies on getPhysicalPath on the context being
        # available, which this view does not have, it not being a
        # persistent object. So we fake things and return the physical path
        # for our context.
        return self.context.getPhysicalPath()

