from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.ResourceRegistries import config
from Products.ResourceRegistries import permissions
from Products.ResourceRegistries.interfaces import IKSSRegistry
from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
from Products.ResourceRegistries.tools.BaseRegistry import Resource

from packer import CSSPacker


class KineticStylesheet(Resource):
    security = ClassSecurityInfo()

    def __init__(self, id, **kwargs):
        Resource.__init__(self, id, **kwargs)
        self._data['compression'] = kwargs.get('compression', 'safe')

    security.declarePublic('getCompression')
    def getCompression(self):
        # as this is a new property, old instance might not have that value, so
        # return 'safe' as default
        compression = self._data.get('compression', 'safe')
        if compression in config.KSS_COMPRESSION_METHODS:
            return compression
        return 'none'

    security.declareProtected(permissions.ManagePortal, 'setCompression')
    def setCompression(self, compression):
        self._data['compression'] = compression

InitializeClass(KineticStylesheet)


class KSSRegistryTool(BaseRegistryTool):
    """A Plone registry for managing the linking to kss files."""

    id = config.KSSTOOLNAME
    meta_type = config.KSSTOOLTYPE
    title = 'KSS Registry'

    security = ClassSecurityInfo()

    implements(IKSSRegistry)
    __implements__ = BaseRegistryTool.__implements__

    #
    # ZMI stuff
    #

    manage_kssForm = PageTemplateFile('www/kssconfig', config.GLOBALS)
    manage_kssComposition = PageTemplateFile('www/ksscomposition', config.GLOBALS)

    manage_options = (
        {
            'label': 'KSS Registry',
            'action': 'manage_kssForm',
        },
        {
            'label': 'Merged KSS Composition',
            'action': 'manage_kssComposition',
        },
    ) + BaseRegistryTool.manage_options

    attributes_to_compare = ('getExpression', 'getCookable', 'getCacheable')
    filename_base = 'ploneStyles'
    filename_appendix = '.kss'
    merged_output_prefix = u''
    cache_duration = config.KSS_CACHE_DURATION
    resource_class = KineticStylesheet

    #
    # Private Methods
    #

    security.declarePrivate('clearKineticStylesheets')
    def clearKineticStylesheets(self):
        self.clearResources()

    def _compressKSS(self, content, level='safe'):
        if level == 'full':
            return CSSPacker('full').pack(content)
        elif level == 'safe':
            return CSSPacker('safe').pack(content)
        else:
            return content

    security.declarePrivate('finalizeContent')
    def finalizeContent(self, resource, content):
        """Finalize the resource content."""
        compression = resource.getCompression()
        if compression != 'none' and not self.getDebugMode():
            orig_url = "%s/%s?original=1" % (self.absolute_url(), resource.getId())
            content = "/* %s */\n%s" % (orig_url,
                                     self._compressKSS(content, compression))

        return content

    #
    # ZMI Methods
    #

    security.declareProtected(permissions.ManagePortal, 'manage_addKineticStylesheet')
    def manage_addKineticStylesheet(self, id, expression='', media='',
                             rel='stylesheet', title='', rendering='import',
                             enabled=False, cookable=True, compression='safe',
                             cacheable=True, REQUEST=None):
        """Register a kineticstylesheet from a TTW request."""
        self.registerKineticStylesheet(id, expression, enabled,
                                       cookable, compression, cacheable)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'manage_saveKineticStylesheets')
    def manage_saveKineticStylesheets(self, REQUEST=None):
        """Save kineticstylesheets from the ZMI.

        Updates the whole sequence. For editing and reordering.
        """
        debugmode = REQUEST.get('debugmode',False)
        self.setDebugMode(debugmode)
        autogroupingmode = REQUEST.get('autogroupingmode', False)
        self.setAutoGroupingMode(autogroupingmode)
        records = REQUEST.get('kineticstylesheets')
        records.sort(lambda a, b: a.sort - b.sort)
        self.resources = ()
        kineticstylesheets = []
        for r in records:
            kss = KineticStylesheet(r.get('id'),
                                    expression=r.get('expression', ''),
                                    enabled=r.get('enabled', False),
                                    cookable=r.get('cookable', False),
                                    cacheable=r.get('cacheable', False),
                                    compression=r.get('compression', 'safe'))
            kineticstylesheets.append(kss)
        self.resources = tuple(kineticstylesheets)
        self.cookResources()
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(permissions.ManagePortal, 'manage_removeKineticStylesheet')
    def manage_removeKineticStylesheet(self, id, REQUEST=None):
        """Remove kineticstylesheet from the ZMI."""
        self.unregisterResource(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    #
    # Protected Methods
    #

    security.declareProtected(permissions.ManagePortal, 'registerKineticStylesheet')
    def registerKineticStylesheet(self, id, expression='', enabled=1,
                                  cookable=True, compression='safe',
                                  cacheable=True, skipCooking=False):
        """Register a kineticstylesheet."""
        kineticstylesheet = KineticStylesheet(id,
                                expression=expression,
                                enabled=enabled,
                                cookable=cookable,
                                compression=compression,
                                cacheable=cacheable)
        self.storeResource(kineticstylesheet, skipCooking=skipCooking)

    security.declareProtected(permissions.ManagePortal, 'updateKineticStylesheet')
    def updateKineticStylesheet(self, id, **data):
        kineticstylesheet = self.getResourcesDict().get(id, None)
        if kineticstylesheet is None:
            raise ValueError, 'Invalid resource id %s' % (id)
        
        if data.get('expression', None) is not None:
            kineticstylesheet.setExpression(data['expression'])
        if data.get('enabled', None) is not None:
            kineticstylesheet.setEnabled(data['enabled'])
        if data.get('cookable', None) is not None:
            kineticstylesheet.setCookable(data['cookable'])
        if data.get('compression', None) is not None:
            kineticstylesheet.setCompression(data['compression'])
        if data.get('cacheable', None) is not None:
            kineticstylesheet.setCacheable(data['cacheable'])

    security.declareProtected(permissions.ManagePortal, 'getCompressionOptions')
    def getCompressionOptions(self):
        """Compression methods for use in ZMI forms."""
        return config.KSS_COMPRESSION_METHODS

    security.declareProtected(permissions.View, 'getContentType')
    def getContentType(self):
        """Return the registry content type."""
        plone_utils = getToolByName(self, 'plone_utils')
        encoding = plone_utils.getSiteEncoding()
        return 'text/css;charset=%s' % encoding


InitializeClass(KSSRegistryTool)
