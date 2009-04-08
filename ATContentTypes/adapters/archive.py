from zope.interface import implements
from Products.ATContentTypes.interface.archive import IArchiveAccumulator
from Products.ATContentTypes.interface.folder import IFilterFolder
from Products.ATContentTypes.interface.archive import IArchiver
from Products.ATContentTypes.interface.dataExtractor import IDataExtractor
from Products.ATContentTypes.interface.archive import IArchivable
from cStringIO import StringIO
from zExceptions import BadRequest
from zipfile import ZipFile

class FolderishArchiver(object):
    """
    store your files in a zip file
    """
    implements(IArchiver)

    #XXXX Refactor common methods inside Folderish and non Folderish object

    def __init__(self, context):
        """
        """
        self.context = context

    def getRawArchive(self, accumulator=None, **kwargs):
        """
        """
        if(not accumulator):
            accumulator = ZipAccumulator(self.context)
        self.createArchive(None,accumulator, **kwargs)
        return accumulator.getRaw()

    def createArchive(self, path, accumulator, **kwargs):
        """
        get the archive file object
        """
        recursive = kwargs.get('recursive',1)
        adapter = IFilterFolder(self.context)
        for item in adapter.listObjects():
            if IArchivable.providedBy(item):
                archiver = IArchiver(item)
                folderish = isinstance(archiver,FolderishArchiver)
                if path:
                    cpath = '%s/%s' % (path, self.context.getId())
                else:
                    cpath = self.context.getId()
                if (recursive and folderish) or not folderish:
                    archiver.createArchive(cpath, accumulator, **kwargs)


class NonFolderishArchiver(object):
    """
    store your files in a zip file
    """
    implements(IArchiver)
    def __init__(self, context):
        self.context = context

    def getRawArchive(self, accumulator=None, **kwargs):
        if(not accumulator):
            accumulator = ZipAccumulator(self.context)
        self.createArchive(None, accumulator, **kwargs)
        return accumulator.getRaw()

    def createArchive(self, path, accumulator, **kwargs):
        """
        get the zip file object
        """
        dataExtractor = IDataExtractor(self.context)
        if dataExtractor and IArchivable.providedBy(self.context):
            data = dataExtractor.getData(**kwargs)
            if path:
              filepath = '%s/%s' % (path, self.context.getId())
            else:
              filepath = self.context.getId()
            accumulator.setFile(filepath,data)


class ZipAccumulator(object):
    """ Implements an accumulator for zip files.
    Note: This should be derived from a superclass allowing for other
    compression types, and also for specific handling of object 
    specific content - hence the object parameter.
    """
    implements(IArchiveAccumulator)

    _zip = None
    sIO = None

    def __init__(self, context):
        self.context = context
        self.sIO = StringIO()
        self._zip = ZipFile(self.sIO,"w",8)

    def setFile(self,filename,data):
        """
        store the file inside the zip file
        """
        if(self._zip):
            self._zip.writestr(filename,data)
        else:
            raise BadRequest, "Unitialized Zip file"

    def setZip(self):
        """
        initialize the zipe file
        """
        self._zip = ZipFile(self.sIO,"w",8)

    def close(self):
        """
        close the zip file
        """
        self._zip.close()

    def getRaw(self):
        """
        return the raw zip file
        """
        if(self._zip):
            self.close()
            value = self.sIO.getvalue()
            self.setZip()
            return value
        else:
            raise BadRequest, "Unitialized Zip file"
