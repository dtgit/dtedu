from Products.ATContentTypes.content.file import ATFile
from Products.Archetypes.public import registerType

class FileAttachment(ATFile):
    """A file attachment"""
    portal_type = meta_type = 'FileAttachment'

registerType(FileAttachment)

