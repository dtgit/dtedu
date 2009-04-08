from zope.interface import implements
from Products.ATContentTypes.interface.dataExtractor import IDataExtractor


class DocumentDataExtractor(object):
    """
    """
    implements(IDataExtractor)
    
    def __init__(self, context):
        self.context = context

    def getData(self,**kwargs):
        """ get the CookedBody of the Document
        """
        return self.context.CookedBody()

class DocumentRawDataExtractor(object):
    """
    """
    implements(IDataExtractor)
 
    def __init__(self, context):
        self.context = context

    def getData(self,**kwargs):
        """ get the raw text of the Document
        """
        return self.context.getRawText()
