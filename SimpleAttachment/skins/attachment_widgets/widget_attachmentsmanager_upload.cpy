## Controller Python Script "widget_attachmentsmanager_upload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Upload a new attachment
##

from Products.CMFCore.utils import getToolByName

request = context.REQUEST
id = request.get('id', context.getId())
attachmentTitle = request.get('attachmentTitle', None)
attachmentFile = request.get('attachmentFile', None)

plone_utils = getToolByName(context, 'plone_utils')

def findUniqueId(id):
    contextIds = context.objectIds()

    if id not in contextIds:
        return id

    dotDelimited = id.split('.')

    ext = dotDelimited[-1]
    name = '.'.join(dotDelimited[:-1])

    idx = 0
    while(name + '.' + str(idx) + '.' + ext) in contextIds:
        idx=+1

    return(name + '.' + str(idx) + '.' + ext)


# Move object out of portal factory if necessary. We can't create images inside
# a folder in the portal factory
new_context = context.portal_factory.doCreate(context, id)

status = 'failure'
message = "You must select an attachment to upload"

if attachmentFile:

    # Make sure we have a unique file name
    fileName = attachmentFile.filename

    imageId = ''

    if fileName:
        fileName = fileName.split('/')[-1]
        fileName = fileName.split('\\')[-1]
        fileName = fileName.split(':')[-1]

        imageId = plone_utils.normalizeString(fileName)

    if not imageId:
        imageId = plone_utils.normalizeString(attachmentTitle)

    imageId = findUniqueId(imageId)

    newImageId = new_context.invokeFactory(id = imageId, type_name = 'FileAttachment')
    if newImageId is not None and newImageId != '':
        imageId = newImageId

    object = getattr(new_context, imageId, None)
    object.setTitle(attachmentTitle)
    object.setFile(attachmentFile)
    object.reindexObject()
    status = 'success'
    message = "Attachment added"

# Because we may have brough an object out of the portal_factory, we need
# to fiddle the action manually here

templateName = request['PATH_INFO'].split('/')[-1]
targetPath = '/'.join(new_context.getPhysicalPath()) + '/' + templateName

return state.set(context = new_context,
                  status = 'uploaded',
                  portal_status_message = message,
                  next_action = 'traverse_to:string:%s' % targetPath)
