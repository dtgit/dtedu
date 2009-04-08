import xmlrpclib
from base64 import decodestring
from zope.publisher.browser import BrowserView
from Acquisition import aq_parent, aq_inner
from Products.CMFPlone.utils import _createObjectByType
from AccessControl import Unauthorized
from Products.eduCommons import eduCommonsMessageFactory
from Products.ContentLicensing.utilities.interfaces import IContentLicensingUtility
from zope.component import getUtility, queryUtility

class CtmCopy(BrowserView):

    def copyCtmAssignment(self):
        """ Copies a CTM Assignment into the Member workspace """
        pm = self.context.portal_membership
        if pm.isAnonymousUser():
            raise Unauthorized

        actor_id = pm.getAuthenticatedMember().id

        copied_item_path = self._copyCTMItem(actor_id)
        

        self.request.RESPONSE.redirect(copied_item_path)



    def _copyCTMItem(self, actor_id):
        """ Creates a copy of the CTM Assignment in the actor's home folder """

        pm = self.context.portal_membership
        actor_folder = pm.getHomeFolder()

        if not hasattr(actor_folder, 'portal_syndication'):
            actor_folder.portal_syndication.enableSyndication(actor_folder)

        props = self.context.portal_properties

        if self.context.Type() in props.educommons_properties.member_locally_allowed_types and self.context.portal_membership.checkPermission('View',self.context):
            lats = actor_folder.locallyAllowedTypes
            if not self.context.Type() in lats:
                types = lats + (self.context.Type(),)
                actor_folder.setLocallyAllowedTypes(types)
        else:
            raise Unauthorized


        if not hasattr(actor_folder, 'copied-items'):
            _createObjectByType('Folder', actor_folder, id='copied-items', title='Copied Items')
            actor_folder.portal_syndication.enableSyndication(getattr(actor_folder, 'copied-items'))
        copied_items_folder = getattr(actor_folder, 'copied-items')

        parent = aq_parent(aq_inner(self.context))
        obj = parent._getOb(self.context.id, copied_items_folder)
        copied_item = self._rCopyObject(obj, copied_items_folder)

        return copied_item._getURL()

    def _rCopyObject(self, obj, dest_folder):
        
        if getattr(dest_folder, obj.id, None):
            self.context.plone_utils.addPortalMessage(_(u'An object with that id already exists. Cannot copy to your home folder'))
            return obj
        else:
            container = _createObjectByType(obj.portal_type, dest_folder, id=obj.id, title=obj.title)

        accmut = {}
        props = self.context.portal_properties

        for key in obj.schema.keys():
            field = key.capitalize()
            if getattr(obj,'set%s' %(field),None):
                accmut['setfield'] = 'set%s' %(field)
                if getattr(obj,'get%s' %(field),None):
                    accmut['getfield'] = 'get%s' %(field)
                elif getattr(obj,field,None):
                    accmut['getfield'] = field
                else:
                    pass
                
                if type(getattr(obj,accmut['getfield'])).__name__ in ['instancemethod','function']:
                    getattr(container, accmut['setfield'])(getattr(obj, accmut['getfield'])())                
                continue
                
            if getattr(obj, key, None):
                if not type(getattr(obj,key)).__name__ in ['instancemethod','function']:
                    setattr(container,key,getattr(obj,key))

            clutil = getUtility(IContentLicensingUtility)
            holder = clutil.getHolderFromObject(obj)
            license = clutil.getLicenseFromObject(obj)
            if license:
                clutil.setRightsLicense(container,license)
            if holder:
                clutil.setRightsHolder(container,holder)
        
        if not obj.isPrincipiaFolderish:
            return container

        for id in obj.keys():
            if id == 'syndication_information':
                continue
            nobj = obj._getOb(id)

            if obj.portal_membership.checkPermission('View', nobj):
                if nobj.portal_type in props.educommons_properties.member_locally_allowed_types:
                    self._rCopyObject(nobj, container)

        return container

            

