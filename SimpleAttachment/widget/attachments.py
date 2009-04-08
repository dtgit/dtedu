from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

class AttachmentsManagerWidget(TypesWidget):
    """This widget adds support for uploading attachments into documents. To 
    support this, you must use it on a folderish type (derived from BaseFolder) 
    with 'FileAttachment' in the allowed_content_types. Create a BooleanField 
    and use this widget. This will display a form at the bottom of your edit 
    form (presuming it's the last widget, which it probably ought to be) where 
    you can upload images into your content type. The boolean field itself is
    used to select whether an attachment download box should be presented. This
    is similar to the "related items" box in Plone.
    
    Content editors may also reference the images directly in their body
    text.
    
    Caveats: In the edit macro, the upload button may steal the default 
    enter-key-press in base_edit.
    """

    # Use the base class properties, and add two of our own
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro'     : 'widget_attachmentsmanager',
                        'expanded'  : False,
                        },)

# Register the widget with Archetypes
registerWidget(AttachmentsManagerWidget,
               title = 'Attachments manager widget',
               description= ('Renders controls for uploading attachments to documents',),
               used_for = ('Products.Archetypes.Field.BooleanField',)
               )
