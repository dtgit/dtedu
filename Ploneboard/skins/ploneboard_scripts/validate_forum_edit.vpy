## Controller Validator "validate_forum_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a forum_edit_form submit
# $Id: validate_forum_edit.vpy 60683 2008-03-14 12:21:49Z wichert $

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

putils = getToolByName(context, 'plone_utils')

title = context.REQUEST.get('title', '')

if len(title) <= 0:
        state.setError('title', 'No text entered', new_status='failure')

if state.getErrors():
    message = _(u'Please correct the indicated errors.')
    putils.addPortalMessage(message)

return state
