## Controller Python Script "widget_imagesmanager_move"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=imageIds=[]
##title=Move images

from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')

context.moveObjectsToTop(imageIds)
plone_utils.reindexOnReorder(context)

message = "Images(s) moved to top of list."

return state.set(status = 'success',
                 portal_status_message = message)
