## Controller Python Script "widget_attachmentsmanager_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Delete attachments

status = 'success'
message = ''

if len(attachmentIds) > 1:
   message = '%d attachments deleted' % len(attachmentIds)
elif len(attachmentIds) == 1:
   message = 'Attachment deleted'
else:
    status = 'failure'
    message = "You must select at least one attachment to delete."

# Delete images
context.manage_delObjects(attachmentIds)

return state.set(status = status,
                 portal_status_message = message)
