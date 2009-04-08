from zope.component import getMultiAdapter

from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize import view, instance

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_inner, aq_parent

from Products.eduCommons.utilities.interfaces import IECUtility
from zope.component import getUtility

class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    @view.memoize
    def next(self):
        provider = self._provider()
        if provider is None:
           return None
        return provider.getNextItem(aq_inner(self.context))
    
    @view.memoize
    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(aq_inner(self.context))

    @view.memoize
    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    @instance.memoize
    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        ecutil = getUtility(IECUtility)
        ecparent = ecutil.FindECParent(self.context)

        if 'Course' == ecparent.Type():
            return INextPreviousProvider(ecparent)
        else:
            return INextPreviousProvider(aq_parent(aq_inner(self.context)), None)

    @view.memoize
    def isViewTemplate(self):
        plone = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return plone.is_view_template()


class NextPreviousViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase, NextPreviousView):
    render = ZopeTwoPageTemplateFile('links.pt')
