from Products.ATContentTypes.content.image import ATImage
from Products.Archetypes.public import registerType

class ImageAttachment(ATImage):
    """An image attachment"""
    portal_type = meta_type = 'ImageAttachment'

registerType(ImageAttachment)
