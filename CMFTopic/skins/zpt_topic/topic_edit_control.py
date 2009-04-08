##parameters=title, description, acquireCriteria=False, **kw
##
from Products.CMFDefault.utils import Message as _

if title!=context.title or description != context.description or \
        acquireCriteria != context.acquireCriteria:
    context.edit(title=title, description=description,
                 acquireCriteria=acquireCriteria)
    return context.setStatus(True, _(u'Topic changed.'))
else:
    return context.setStatus(False, _(u'Nothing to change.'))
