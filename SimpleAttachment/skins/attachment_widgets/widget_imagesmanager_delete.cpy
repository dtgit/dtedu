## Controller Python Script "widget_imagesmanager_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=imageIds=[]
##title=Delete images

status = 'success'
message = ''

if len(imageIds) > 1:
   message = '%d images deleted' % len(imageIds)
elif len(imageIds) == 1:
   message = 'Image deleted'
else:
    status = 'failure'
    message = "You must select at least one image to delete."

# Delete images
context.manage_delObjects(imageIds)

return state.set(status = status,
                 portal_status_message = message)
