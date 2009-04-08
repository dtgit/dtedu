from Products.Five import BrowserView
from Products.ATContentTypes.interface.archive import IArchiver

class ArchiveView(BrowserView):
    """
    """
    def getZipFile(self,**kwargs):
        """
        """
        adapted = IArchiver(self.context)
        self.request.RESPONSE.setHeader('Content-Type','application/zip')
        self.request.RESPONSE.addHeader("Content-Disposition","filename=%s.zip" % self.context.getId())
        self.request.RESPONSE.write(adapted.getRawArchive(**kwargs))

