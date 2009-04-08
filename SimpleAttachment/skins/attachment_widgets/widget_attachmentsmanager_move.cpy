## Controller Python Script "widget_attachmentsmanager_move"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Move attachments

from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')

context.moveObjectsToTop(attachmentIds)
plone_utils.reindexOnReorder(context)

message = "Attachment(s) moved to top of list."

return state.set(status = 'success',
                 portal_status_message = message)
