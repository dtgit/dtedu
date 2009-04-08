from zope import schema
from zope.component import getMultiAdapter, getUtility
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.eduCommons.utilities.interfaces import IECUtility


class ITWBSearchPortlet(IPortletDataProvider):
    """ A portlet displaying a (live) search box
    """
    enableLivesearch = schema.Bool(
            title = _(u"Enable LiveSearch"),
            description = _(u"Enables the LiveSearch feature, which shows "
                             "live results if the browser supports "
                             "JavaScript."),
            default = True,
            required = False)

class Assignment(base.Assignment):
    implements(ITWBSearchPortlet)

    def __init__(self, enableLivesearch=True):
        self.enableLivesearch=True

    @property
    def title(self):
        return _(u"TWB Search Portlet")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('twbsearch.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()

    def enable_livesearch(self):
        return self.data.enableLivesearch

    def folder_path(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        folder = context_state.folder()
        return '/'.join(folder.getPhysicalPath())

    def search_action(self):
        return '%s/search' % self.portal_url

    def search_string(self):
        ecutils = getUtility(IECUtility)
        parent_type = ecutils.FindECParent(self.context).Type()
        if parent_type != 'Plone Site':
            return 'Search this %s' % parent_type
        else:
            return 'Search Site'


class AddForm(base.AddForm):
    form_fields = form.Fields(ITWBSearchPortlet)
    label = _(u"Add Search Portlet")
    description = _(u"This portlet shows a search box.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ITWBSearchPortlet)
    label = _(u"Edit Search Portlet")
    description = _(u"This portlet shows a search box.")
