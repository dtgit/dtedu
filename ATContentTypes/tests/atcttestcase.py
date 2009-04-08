# -*- coding: latin1 -*-
#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""Common imports and declarations

common includes a set of basic things that every test needs.
"""

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import portal_name
from Products.PloneTestCase.setup import portal_owner
ZopeTestCase.installProduct('SiteAccess')
PloneTestCase.setupPloneSite(extension_profiles=['Products.CMFPlone:testfixture'])

import os
import transaction

from Interface.Verify import verifyObject
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.DublinCore import MutableDublinCore as IMutableDublinCore
from Products.Archetypes.interfaces.base import IBaseContent
from Products.Archetypes.atapi import *
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.Archetypes.interfaces.templatemixin import ITemplateMixin
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Products.Archetypes.tests.test_baseschema import BaseSchemaTest
from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes import permission as ATCTPermissions
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import idValidator
from Products.ATContentTypes.tests.utils import FakeRequestSession
from Products.ATContentTypes.tests.utils import DummySessionDataManager
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.Translatable import ITranslatable

# Z3 imports
from Products.ATContentTypes.interface import IATContentType as Z3IATContentType
from zope.interface.verify import verifyObject as Z3verifyObject

test_home = os.path.dirname(__file__)

class ATCTSiteTestCase(PloneTestCase.PloneTestCase):
    pass

class ATCTFunctionalSiteTestCase(PloneTestCase.FunctionalTestCase):
    pass

class ATCTTypeTestCase(ATCTSiteTestCase):
    """AT Content Types test

    Tests some basics of a type
    """

    klass = None
    cmf_klass = None
    portal_type = ''
    cmf_portal_type = ''
    title = ''
    meta_type = ''
    icon = ''

    def afterSetUp(self):
        #self.setRoles(['Manager', 'Member'])
        self._ATCT = self._createType(self.folder, self.portal_type, 'ATCT')
        if self.cmf_klass:
            self._cmf = self._createType(self.folder, self.cmf_portal_type, 'cmf')

    def _createType(self, context, portal_type, id, **kwargs):
        """Helper method to create a new type
        """
        ttool = getToolByName(context, 'portal_types')
        cat = self.portal.portal_catalog

        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id, **kwargs)
        obj = getattr(context.aq_inner.aq_explicit, id)
        cat.indexObject(obj)
        return obj

    def test_000testsetup(self):
        # test if we really have the right test setup
        # vars
        self.failUnless(self.klass)
        self.failUnless(self.portal_type)
        self.failUnless(self.title)
        self.failUnless(self.meta_type)
        self.failUnless(self.icon)
        if self.cmf_klass:
            self.failUnless(self.cmf_klass)
            self.failUnless(self.cmf_portal_type)

        # portal types
        self.failUnlessEqual(self._ATCT.portal_type, self.portal_type)
        if self.cmf_klass:
            self.failUnlessEqual(self._cmf.portal_type, self.cmf_portal_type)

        # classes
        atct_class = self._ATCT.__class__
        self.failUnlessEqual(self.klass, atct_class)
        if self.cmf_klass:
            cmf_class = self._cmf.__class__
            self.failUnlessEqual(self.cmf_klass, cmf_class)

    def test_dcEdit(self):
        new = self._ATCT
        dcEdit(new)
        if self.cmf_klass:
            old = self._cmf
            dcEdit(old)
            self.compareDC(old, new)

    def test_typeInfo(self):
        ti = self._ATCT.getTypeInfo()
        self.failUnlessEqual(ti.getId(), self.portal_type)
        self.failUnlessEqual(ti.Title(), self.title)
        self.failUnlessEqual(ti.getIcon(), self.icon)
        self.failUnlessEqual(ti.Metatype(), self.meta_type)

    def test_doesImplementDC(self):
        self.failUnless(IDublinCore.isImplementedBy(self._ATCT))
        self.failUnless(IMutableDublinCore.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IDublinCore, self._ATCT))
        self.failUnless(verifyObject(IMutableDublinCore, self._ATCT))

    def test_doesImplementATCT(self):
        self.failUnless(IATContentType.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IATContentType, self._ATCT))

    def test_doesImplementZ3ATCT(self):
        iface = Z3IATContentType
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_doesImplementAT(self):
        self.failUnless(IBaseContent.isImplementedBy(self._ATCT))
        self.failUnless(IReferenceable.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(IBaseContent, self._ATCT))
        self.failUnless(verifyObject(IReferenceable, self._ATCT))

    def test_implementsTranslateable(self):
        # lingua plone is adding the ITranslatable interface to all types
        if not HAS_LINGUA_PLONE:
            return
        self.failUnless(ITranslatable.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(ITranslatable, self._ATCT))

    def test_not_implements_ITemplateMixin(self):
        self.failIf(ITemplateMixin.isImplementedBy(self._ATCT))

    def test_implements_ISelectableBrowserDefault(self):
        iface = ISelectableBrowserDefault
        self.failUnless(iface.providedBy(self._ATCT))
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def compareDC(self, first, second=None, **kwargs):
        """
        """
        if second != None:
            title = second.Title()
            description = second.Description()
        else:
            title = kwargs.get('title')
            description = kwargs.get('description')

        self.failUnlessEqual(first.Title(), title)
        self.failUnlessEqual(first.Description(), description)

    def test_idValidation(self):
        self.setRoles(['Manager', 'Member']) # for ATTopic
        asdf = self._createType(self.folder, self.portal_type, 'asdf')
        asdf2 = self._createType(self.folder, self.portal_type, 'asdf2')
        self.setRoles(['Member'])

        request = FakeRequestSession()

        # invalid ids
        ids = ['asdf2', '???', '/asdf2', ' asdf2', 'portal_workflow',
            'portal_url']
        for id in ids:
            request.form = {'id':id, 'fieldset':'default'}
            self.assertNotEquals(asdf.validate(REQUEST=request), {}, "Not catched id: %s" % id)

        # valid ids
        ids = ['', 'abcd', 'blafasel']
        for id in ids:
            request.form = {'id':id}
            self.assertEquals(asdf.validate(REQUEST=request), {})

    def test_getobjpositioninparent(self):
        # TODO: not a real test
        self._ATCT.getObjPositionInParent()

    def test_schema_marshall(self):
        atct = self._ATCT
        schema = atct.Schema()
        marshall = schema.getLayerImpl('marshall')
        marshallers = [RFC822Marshaller]
        try:
            from Products.Marshall import ControlledMarshaller
            marshallers.append(ControlledMarshaller)
        except ImportError:
            pass
        self.failUnless(isinstance(marshall, tuple(marshallers)), marshall)

    def beforeTearDown(self):
        self.logout()

class ATCTFieldTestCase(BaseSchemaTest):
    """ ATContentTypes test including AT schema tests """

    def afterSetUp(self):
        # initalize the portal but not the base schema test
        # because we want to overwrite the dummy and don't need it
        ATSiteTestCase.afterSetUp(self)
        self.setRoles(['Manager',])

    def createDummy(self, klass, id='dummy'):
        portal = self.portal
        dummy = klass(oid=id)
        # put dummy in context of portal
        dummy = dummy.__of__(portal)
        portal.dummy = dummy
        dummy.initializeArchetype()
        return dummy

    def test_description(self):
        dummy = self._dummy
        field = dummy.getField('description')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, '')
        self.failUnlessEqual(field.searchable, True)
        self.failUnlessEqual(field.primary, False)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, True)
        self.failUnlessEqual(field.accessor, 'Description')
        self.failUnlessEqual(field.mutator, 'setDescription')
        self.failUnlessEqual(field.edit_accessor, 'getRawDescription')
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'mVc')
        #self.failUnless(field.generateMode == 'veVc', field.generateMode)
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'text')
        self.failUnless(isinstance(field.storage, MetadataStorage))
        self.failUnless(field.getLayerImpl('storage') == MetadataStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, TextAreaWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnlessEqual(tuple(vocab), ())

    def test_id(self):
        dummy = self._dummy
        field = dummy.getField('id')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, None)
        self.failUnlessEqual(field.searchable, True)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, False)
        self.failUnlessEqual(field.isMetadata, False)
        self.failUnlessEqual(field.accessor, 'getId')
        self.failUnlessEqual(field.mutator, 'setId')
        self.failUnlessEqual(field.edit_accessor, 'getRawId')
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'string')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, idValidator)
        self.failUnless(isinstance(field.widget, IdWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))
        self.failUnlessEqual(tuple(vocab), ())

    def test_relateditems(self):
        dummy = self._dummy
        field = dummy.getField('relatedItems')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnlessEqual(field.required, False)
        self.failUnlessEqual(field.default, None)
        self.failUnlessEqual(field.searchable, False)
        self.failUnlessEqual(getattr(field, 'primary', None), None)
        vocab = field.vocabulary
        self.failUnlessEqual(vocab, ())
        self.failUnlessEqual(field.enforceVocabulary, False)
        self.failUnlessEqual(field.multiValued, True)
        self.failUnlessEqual(field.isMetadata, True)
        self.failUnlessEqual(field.accessor, 'getRelatedItems')
        self.failUnlessEqual(field.mutator, 'setRelatedItems')
        self.failUnlessEqual(field.edit_accessor, 'getRawRelatedItems')
        self.failUnlessEqual(field.read_permission, View)
        self.failUnlessEqual(field.write_permission, ModifyPortalContent)
        self.failUnlessEqual(field.generateMode, 'veVc')
        self.failUnlessEqual(field.force, '')
        self.failUnlessEqual(field.type, 'reference')
        self.failUnless(isinstance(field.storage, AttributeStorage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage())
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, ReferenceBrowserWidget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList))

