from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import LogoViewlet
from plone.app.layout.viewlets.common import PathBarViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet


class TWBLogoViewlet(LogoViewlet):
    render = ViewPageTemplateFile('logo.pt')

class TWBPathBarViewlet(PathBarViewlet):
    render = ViewPageTemplateFile('path_bar.pt')

class TWBSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('searchbox.pt')
