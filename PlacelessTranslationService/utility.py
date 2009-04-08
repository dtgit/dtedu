from zope.interface import implements
from zope.i18n import interpolate
from zope.publisher.interfaces.browser import IBrowserRequest

from Products.PlacelessTranslationService import getTranslationService
from Products.PlacelessTranslationService.interfaces import \
    IPTSTranslationDomain


class PTSTranslationDomain(object):
    """Makes translation domains that are still kept in PTS available as
    ITranslationDomain utilities. That way they are usable from Zope 3 code
    such as Zope 3 PageTemplates."""

    implements(IPTSTranslationDomain)

    def __init__(self, domain):
        self.domain = domain

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):

        pts  = getTranslationService()
        if pts is None or context is None:
            # If we don't have enough context use interpolate
            return interpolate(default, mapping)

        # Don't accept anything which isn't a real request
        if not IBrowserRequest.providedBy(context) or 'PARENTS' not in context:
            raise ValueError, "You didn't pass in a request as the context."

        parent = context['PARENTS'][-1]
        return pts.translate(self.domain, msgid, mapping, parent,
                             target_language, default)
