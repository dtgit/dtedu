from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Field import TextField
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.exceptions import ReferenceException
from ZPublisher.HTTPRequest import FileUpload
from Products.CMFCore.utils import getToolByName
from Products.kupu.plone.config import UID_PATTERN
import re

class ReftextField(TextField):
    __implements__ = TextField.__implements__

    _properties = TextField._properties.copy()
    _properties.update({
        'widget': RichWidget,
        'default_content_type' : 'text/html',
        'default_output_type'  : 'text/x-html-captioned',
        'allowable_content_types' : ('text/html',),
        'relationship' : None, # defaults to field name
        'referenceClass' : Reference,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """ Assign input value to object. If mimetype is not specified,
        pass to processing method without one and add mimetype
        returned to kwargs. Assign kwargs to instance.
        """
        if value is None:
            # nothing to do
            return

        TextField.set(self, instance, value, **kwargs)

        if isinstance(value, BaseUnit):
            # Baseunit: can occur when overriding atct text fields.
            value = value()
        if not isinstance(value, basestring):
            value.seek(0);
            value = value.read()

        # build list of uids from the value here
        uids = [ m.group('uid') for m in UID_PATTERN.finditer(value) ]
        uids = dict.fromkeys(uids).keys() # Remove duplicate uids.

        tool = getToolByName(instance, REFERENCE_CATALOG)

        relationship = self.relationship
        if relationship is None:
            relationship = self.__name__

        targetUIDs = [ref.targetUID for ref in
                      tool.getReferences(instance, relationship)]

        add = [v for v in uids if v and v not in targetUIDs]
        sub = [t for t in targetUIDs if t not in uids]

        # tweak keyword arguments for addReference
        addRef_kw = kwargs.copy()
        addRef_kw.setdefault('referenceClass', self.referenceClass)
        if addRef_kw.has_key('schema'): del addRef_kw['schema']

        for uid in add:
            __traceback_info__ = (instance, uid, value, targetUIDs)
            try:
                # throws ReferenceException if uid is invalid
                tool.addReference(instance, uid, relationship, **addRef_kw)
            except ReferenceException:
                pass
        for uid in sub:
            tool.deleteReference(instance, uid, relationship)

#         print "Result was:",[ref.targetUID for ref in
#                       tool.getReferences(instance, relationship)]
#         print "Objects:",[ref.getTargetObject() for ref in
#                       tool.getReferences(instance, relationship)]
