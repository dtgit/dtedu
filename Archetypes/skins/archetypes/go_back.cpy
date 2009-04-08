## Script (Python) "go_back"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=last_referer=None
##title=Go Back

#SESSION = context.REQUEST.SESSION
#old_id = context.getId()
#cflag = SESSION.get('__creation_flag__', {})

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName


REQUEST = context.REQUEST

# Tell the world that we cancelled
lifecycle_view = context.restrictedTraverse('@@at_lifecycle_view')
lifecycle_view.cancel_edit()

if context.isTemporary():
    # object was created using portal factory and it's just a temporary object
    redirect_to = context.getFolderWhenPortalFactory().absolute_url()
    message=_(u'message_add_new_item_cancelled',
        default='Add New Item operation was cancelled.')
##elif old_id in cflag.keys():
##    redirect_to = last_referer
##    context.remove_creation_mark()
##    context.aq_parent.manage_delObjects([old_id])
##    message=_(u'message_edit_item_cancelled',
##        default='Add new item operation was cancelled, object was removed.')
else:
    redirect_to = last_referer
    message=_(u'message_edit_item_cancelled',
        default='Edit cancelled.')

kwargs = {
    'next_action':'redirect_to:string:%s' % redirect_to,
    }

env = state.kwargs
reference_source_url = env.get('reference_source_url')
if reference_source_url is not None:
    reference_source_url = env['reference_source_url'].pop()
    reference_source_field = env['reference_source_field'].pop()
    reference_source_fieldset = env['reference_source_fieldset'].pop()
    kwargs.update({
        'fieldset':reference_source_fieldset,
        'field':reference_source_field,
        'reference_focus':reference_source_field,
        })

addStatusMessage(REQUEST, message)
return state.set(**kwargs)
