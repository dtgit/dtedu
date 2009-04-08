from zope.interface import implements
from Products.ATContentTypes.interface.folder import IFilterFolder

class FolderFilter(object):
    """
    """
    implements(IFilterFolder)

    def __init__(self, context):
        self.context = context

    def listObjects(self):
        return self.context.objectValues()

