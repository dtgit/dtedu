from zope.component.globalregistry import base
from five.localsitemanager import make_objectmanager_site

from Products.Five.component.browser import ObjectManagerSiteView


class ObjectManagerSiteView(ObjectManagerSiteView):
    """Configure the site setup for an ObjectManager.
    """

    def makeSite(self):
        make_objectmanager_site(self.context)

    def sitemanagerTrail(self):
        if not self.isSite():
            return None

        sm = self.context.getSiteManager()
        trail = []
        while sm is not None and sm != base:
            trail.append(repr(sm))
            sm = sm.__bases__[0]

        if sm == base:
            trail.append('Global Registry')

        trail.reverse()

        return ' => '.join(trail)
