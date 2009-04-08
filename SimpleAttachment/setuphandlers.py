from Products.CMFCore.utils import getToolByName

def setupAttachments(context):
    if context.readDataFile('simpleattachment_various.txt') is None:
        return
    
    portal = context.getSite()
    
    # Add FileAttachment and ImageAttachment to kupu's linkable and media types
    kupuTool = getToolByName(portal, 'kupu_library_tool')
    linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
    mediaobject = list(kupuTool.getPortalTypesForResourceType('mediaobject'))
    if 'FileAttachment' not in linkable:
        linkable.append('FileAttachment')
    if 'ImageAttachment' not in linkable:
        linkable.append('ImageAttachment')
    if 'ImageAttachment' not in mediaobject:
        mediaobject.append('ImageAttachment')
    # kupu_library_tool has an idiotic interface, basically written purely to
    # work with its configuration page. :-(
    kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                   'old_type'      : 'linkable',
                                   'portal_types'  :  linkable},
                                  {'resource_type' : 'mediaobject',
                                   'old_type'      : 'mediaobject',
                                   'portal_types'  :  mediaobject},))
                                   
def registerImagesFormControllerActions(context, contentType=None, template='base_edit'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    pfc = getToolByName(context, 'portal_form_controller')
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'UploadImage',
                      'traverse_to',
                      'string:widget_imagesmanager_upload')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'RenameImages',
                      'traverse_to',
                      'string:widget_imagesmanager_rename')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveImages',
                      'traverse_to',
                      'string:widget_imagesmanager_move')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteImages',
                      'traverse_to',
                      'string:widget_imagesmanager_delete')
                      
def registerAttachmentsFormControllerActions(context, contentType=None, template='base_edit'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    pfc = getToolByName(context, 'portal_form_controller')
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'UploadAttachment',
                      'traverse_to',
                      'string:widget_attachmentsmanager_upload')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'RenameAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_rename')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_move')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_delete')                                  
