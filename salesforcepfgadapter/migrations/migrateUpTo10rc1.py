# CMF imports
from Products.CMFCore.utils import getToolByName

class Migration(object):
    """Migrate from version prior to 1.0rc1
    """
    adapterMetaType = "SalesforcePFGAdapter"
    adapterTitle = "Salesforce Adapter"
    
    def __init__(self, site, out):
        self.site = site
        self.out = out
        self.catalog = getToolByName(self.site, 'portal_catalog')
        self.types = getToolByName(self.site, 'portal_types')
    
    def _rebuildTypesIndexInCatalog(self):
        """Rebuild the known index that would keep track
           of the incorrect type title
        """
        # rebuild the catalog index for Types
        self.catalog.manage_reindexIndex(['Type',])
    
    def _rebuildFieldsForSFObjectType(self):
        """We need to rebuild the list of fields for the chosen
           SFObject type, so that we can correctly mark required
           fields in the UI.
        """
        results = self.catalog.searchResults(meta_type = 'SalesforcePFGAdapter')
        
        for result in results:
            obj = result.getObject()
            sfobject_type = obj.getSFObjectType()
            # this triggers a call to:
            # self._querySFFieldsForType()
            obj.setSFObjectType(sfobject_type)
    
    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out, "Migrating from SalesforcePFGAdapter versions \
            prior 1.0rc1"
        
        # run our catalog rebuild, which also 
        # calls the _updateAdapterTitle
        self._rebuildTypesIndexInCatalog()
        self._rebuildFieldsForSFObjectType()
    

    