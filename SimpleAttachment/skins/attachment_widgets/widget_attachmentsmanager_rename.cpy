## Controller Python Script "widget_attachmentsmanager_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentTitles=[]
##title=Rename attachments

message = "Changes saved."

for attachmentTitle in attachmentTitles:
    if not attachmentTitle.has_key('title'):
        attachmentTitle['title'] = ''

    item = getattr(context, attachmentTitle['id'])
    item.setTitle(attachmentTitle['title'])
    item.reindexObject(idxs = ['Title'])

return state.set(status = 'success',
                 portal_status_message = message)
