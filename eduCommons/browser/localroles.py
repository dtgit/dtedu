from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.eduCommons.browser.interfaces import IeduCommonsSharingPageRole

from Products.eduCommons import eduCommonsMessageFactory as _

# These are for everyone

class ProducerRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"Producer")
    required_permission = None
    
class QARole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"QA", default=u"QA")
    required_permission = None
    
class PublisherRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"Publisher")
    required_permission = None

class ViewerRole(object):
    implements(IeduCommonsSharingPageRole)

    title = _(u"Viewer")
    required_permission = None
