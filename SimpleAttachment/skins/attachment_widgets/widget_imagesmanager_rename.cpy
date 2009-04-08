## Controller Python Script "widget_imagesmanager_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=imageTitles=[]
##title=Rename images

message = "Changes saved."

for imageTitle in imageTitles:
    if not imageTitle.has_key('title'):
        imageTitle['title'] = ''

    item = getattr(context, imageTitle['id'])
    item.setTitle(imageTitle['title'])
    item.reindexObject(idxs = ['Title'])

return state.set(status = 'success',
                 portal_status_message = message)
