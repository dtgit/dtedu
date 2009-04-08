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
"""
"""

__author__ = 'Alec Mitchell'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase
from Products.ATContentTypes.tests.utils import dcEdit

import transaction
from Products.CMFCore.permissions import View
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *

from Products.Archetypes.Field import BooleanField
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ChangeTopics
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.interfaces import IATTopic
from Interface.Verify import verifyObject
from OFS.IOrderSupport import IOrderedContainer as IZopeOrderedContainer

from Products.CMFPlone.PloneBatch import Batch

# z3 imports
from Products.ATContentTypes.interface import IATTopic as Z3IATTopic
from zope.interface.verify import verifyObject as Z3verifyObject


ACQUIRE  = True
LIMIT    = False
COUNT  = '150'
CUSTOM   = True
FIELDS   = ('start','end', 'Creator')

CRITERIA_SETUP = {'Integer Criterion':      #Meta Type
                        ('portal_type',     #Field
                         '10 10',            #Value
                         'min:max'),        #Direction
                  'String Criterion':
                        ('SearchableText',
                         'portal'),
                  'Friendly Date Criterion':
                        ('start',
                         '10',
                         'within_day',       #Operation
                         'ahead'),          #DateRange
                  'List Criterion':
                        ('Subject',
                         "value1\nportal\ntest",
                         'OR'),             #Operator
                  'Sort Criterion':
                        ('getId',
                         False),            #Reversed
                }

CRIT_MAP = {'Integer Criterion': 'ATSimpleIntCriterion',
            'String Criterion': 'ATSimpleStringCriterion',
            'Friendly Date Criterion': 'ATFriendlyDateCriteria',
            'List Criterion': 'ATListCriterion',
            'Sort Criterion': 'ATSortCriterion'}

REV_CRIT_MAP = dict([[v,k] for k,v in CRIT_MAP.items()])

def editATCT(obj):
    dcEdit(obj)
    obj.setAcquireCriteria(ACQUIRE)
    obj.setLimitNumber(LIMIT)
    obj.setItemCount(COUNT)
    #obj.setCustomView(CUSTOM)
    #obj.setCustomViewFields(FIELDS)
    for meta in CRITERIA_SETUP.keys():
        AT_META = CRIT_MAP[meta]
        CRIT_FIELD = CRITERIA_SETUP[meta][0]
        obj.addCriterion(CRIT_FIELD, AT_META)
    for crit in obj.listCriteria():
        CRIT_TYPE = crit.meta_type
        OLD_CRIT_TYPE = REV_CRIT_MAP[CRIT_TYPE]
        params = CRITERIA_SETUP[OLD_CRIT_TYPE][1:]
        if CRIT_TYPE not in ['ATSortCriterion','ATSimpleIntCriterion']:
            crit.setValue(params[0])
        if CRIT_TYPE == 'ATFriendlyDateCriteria':
            crit.setOperation(params[1])
            DATE_RANGE = (params[2] == 'ahead' and '+') or '-'
            crit.setDateRange(DATE_RANGE)
        if CRIT_TYPE == 'ATListCriterion':
            crit.setOperator(params[1])
        if CRIT_TYPE == 'ATSimpleIntCriterion':
            value = params[0].split(' ')
            crit.setValue(value[0])
            if len(value) > 1:
                crit.setValue2(value[1])
            crit.setDirection(params[1])
        if CRIT_TYPE == 'ATSortCriterion':
            crit.setReversed(params[0])

def convert_old_catalog_usage(criteria_items):
    """Convert old style query parameters into records"""
    if len(criteria_items) > 1:
        field = criteria_items[0][0]
        query_val = criteria_items[0][1]
        extra_param = criteria_items[1][1]
        if '_usage' in criteria_items[1][0]:
            usage = extra_param.split(':')
            extra_type = usage[0].strip()
            extra_param = ':'.join(usage[1:]).strip()
        else:
            extra_type = criteria_items[1][0].replace('%s_'%field,'')
        criteria_items = [(field, {'query': query_val, extra_type: extra_param})]
    return tuple(criteria_items)

def convert_old_catalog_query(query):
    """Convert old style query to new record based query"""
    for k,v in query.items():
        q_field = q_type = q_param = None
        if '_usage' in k:
            q_field = k.replace('_usage','')
            usage = v.split(':')
            q_type = usage[0].strip()
            q_param = ':'.join(usage[1:]).strip()
        elif '_operator' in k:
            q_field = k.replace('_operator','')
            q_type = 'operator'
            q_param = v
        if q_field:
            new_val = query[q_field]
            if not isinstance(v, dict):
                new_val = { 'query' : new_val }
            new_val[q_type] = q_param
            query[q_field] = new_val
            del query[k]
    return query

tests = []

class TestSiteATTopic(atcttestcase.ATCTTypeTestCase):

    klass = ATTopic
    portal_type = 'Topic'
    title = 'Collection'
    meta_type = 'ATTopic'
    icon = 'topic_icon.gif'

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self._ATCT = self._createType(self.folder, self.portal_type, 'ATCT')
        self.setRoles(['Member'])

    def test_implementsATTopic(self):
        iface = IATTopic
        self.failUnless(iface.isImplementedBy(self._ATCT))
        self.failUnless(verifyObject(iface, self._ATCT))

    def test_Z3implementsATTopic(self):
        iface = Z3IATTopic
        self.failUnless(Z3verifyObject(iface, self._ATCT))

    def test_isNotOrdered(self):
        iface = IZopeOrderedContainer
        self.failIf(iface.isImplementedBy(self._ATCT))
        self.failIf(iface.isImplementedByInstancesOf(self.klass))

    def test_Empty( self ):
        topic = self._ATCT

        query = topic.buildQuery()
        self.assertEquals( query, None )

    def test_canContainSubtopics(self):
        ttool = self.portal.portal_types
        fti = ttool.getTypeInfo(self.portal_type)
        self.failUnless(self.portal_type in fti.allowed_content_types,
                        'Topics should be allowed to contain topics')

    def test_Simple( self ):
        topic = self._ATCT

        topic.addCriterion( 'foo', 'ATSimpleStringCriterion' )
        self.failUnless('crit__foo_ATSimpleStringCriterion' in
            topic.objectIds(), topic.objectIds())
        topic.getCriterion( 'foo_ATSimpleStringCriterion' ).setValue( 'bar' )

        query = topic.buildQuery()
        self.assertEquals( len(query), 1 )
        self.assertEquals( query['foo'], 'bar' )

        topic.addCriterion( 'baz', 'ATSimpleIntCriterion' )
        topic.getCriterion( 'baz_ATSimpleIntCriterion' ).setValue( '43' )

        query = topic.buildQuery()
        self.assertEquals( len( query ), 2 )
        self.assertEquals( query[ 'foo' ], 'bar' )
        self.assertEquals( query[ 'baz' ], {'query': 43} )

    def test_nested( self ):
        topic = self._ATCT

        topic.addCriterion( 'foo', 'ATSimpleStringCriterion' )
        self.failUnless('crit__foo_ATSimpleStringCriterion' in
            topic.objectIds(), topic.objectIds())
        topic.getCriterion( 'foo_ATSimpleStringCriterion' ).setValue( 'bar' )

        self.setRoles(['Manager', 'Member'])
        topic.addSubtopic( 'qux' )
        self.setRoles(['Member'])
        subtopic = topic.qux

        subtopic.setAcquireCriteria(True)

        #Ensure an empty subtopic uses it's parents' queries
        self.failUnlessEqual(subtopic.buildQuery(), topic.buildQuery())

        subtopic.addCriterion( 'baz', 'ATSimpleStringCriterion' )
        self.failUnless('crit__baz_ATSimpleStringCriterion' in
            subtopic.objectIds(), subtopic.objectIds())
        subtopic.getCriterion( 'baz_ATSimpleStringCriterion' ).setValue( 'bam' )

        query = subtopic.buildQuery()
        self.assertEquals( len( query ), 2 )
        self.assertEquals( query['foo'], 'bar' )
        self.assertEquals( query['baz'], 'bam' )

        subtopic.setAcquireCriteria(False)
        query = subtopic.buildQuery()
        self.assertEquals( len( query ), 1 )
        self.assertEquals( query['baz'], 'bam' )

    def test_edit(self):
        new = self._ATCT
        editATCT(new)

    def test_hasSubTopics(self):
        #Ensure that has subtopics returns True if there are subtopics,
        #    false otherwise
        topic = self._ATCT
        self.failUnlessEqual(topic.hasSubtopics(), False)
        self.setRoles(['Manager', 'Member'])
        topic.invokeFactory('Topic', 'subtopic')
        self.setRoles(['Member'])
        self.failUnlessEqual(topic.hasSubtopics(), True)

    def test_queryCatalogBatching(self):
        # Ensure that has we return a proper batch if requested
        topic = self._ATCT
        self.failUnless(isinstance(topic.queryCatalog(batch=True),Batch))
        self.failIf(isinstance(topic.queryCatalog(),Batch))
        # try it with some content now
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')
        self.failUnless(isinstance(topic.queryCatalog(batch=True),Batch))
        self.failIf(isinstance(topic.queryCatalog(),Batch))

    def test_queryCatalogBatchingWithLimit(self):
        # Ensure that the number of results is the same with or without a
        # limit
        topic = self._ATCT
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')
        # set a sort criterion because sort_limit affects result batching.
        topic.setSortCriterion('created', False)
        # add a few folders
        for i in range(6):
            self.folder.invokeFactory('Folder', 'folder_%s'%i)
            getattr(self.folder, 'folder_%s'%i).reindexObject()
        num_items = len(topic.queryCatalog())
        # We better have some folders
        self.failUnless(num_items >= 6)
        self.assertEqual(topic.queryCatalog(batch=True).sequence_length, num_items)
        # Set some limits
        topic.setLimitNumber(True)
        topic.setItemCount(2)
        self.assertEqual(topic.queryCatalog(batch=True).sequence_length, num_items)

    def test_queryCatalogBrains(self):
        #Ensure that we feturn full objects when requested
        topic = self._ATCT
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')
        self.failUnless(isinstance(topic.queryCatalog(full_objects=True)[0], ATFolder))
        self.failIf(isinstance(topic.queryCatalog()[0], ATFolder))

    def test_queryCatalogLimitChangesBatchSize(self):
        #Ensure that a set limit overrides batch size
        topic = self._ATCT
        topic.setLimitNumber(True)
        topic.setItemCount(10)
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')
        # Add a bunch of folders.
        for i in range(1, 20):
            self.folder.invokeFactory('Folder', str(i))
        self.failUnless(isinstance(topic.queryCatalog(batch=True),Batch))
        # Check the batch length
        self.assertEqual(len(topic.queryCatalog(batch=True)), 10)

    def test_queryCatalogBSizeChangesBatchSize(self):
        #Ensure that a set limit overrides batch size
        topic = self._ATCT
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')
        # Add a bunch of folders.
        for i in range(1, 20):
            self.folder.invokeFactory('Folder', str(i))
        self.failUnless(isinstance(topic.queryCatalog(batch=True, b_size=5),Batch))
        # Check the batch length
        self.assertEqual(len(topic.queryCatalog(batch=True, b_size=5)), 5)

    def test_get_size(self):
        atct = self._ATCT
        self.failUnlessEqual(atct.get_size(), 1)

    def test_syndication_enabled_by_default(self):
        syn = self.portal.portal_syndication
        self.failUnless(syn.isSyndicationAllowed(self._ATCT))

    def test_schema_marshall(self):
        pass

    def test_sort_criterion_does_not_affect_available_fields(self):
        topic = self._ATCT
        # set a sort criterion
        topic.setSortCriterion('created', False)
        # It should still be available for other criteria
        self.failUnless([i for i in topic.listAvailableFields()
                         if i[0] == 'created'])
        # Add a normal criteria for the same field
        crit = topic.addCriterion('created', 'ATFriendlyDateCriteria')
        # It should no longer be available
        self.failIf([i for i in topic.listAvailableFields()
                     if i[0] == 'created'])


tests.append(TestSiteATTopic)

class TestATTopicFields(atcttestcase.ATCTFieldTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTFieldTestCase.afterSetUp(self)
        self._dummy = self.createDummy(klass=ATTopic)

    def test_acquireCriteriaField(self):
        dummy = self._dummy
        field = dummy.getField('acquireCriteria')
        field_vocab = BooleanField._properties.get('vocabulary', ())

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == field_vocab,
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getAcquireCriteria',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setAcquireCriteria',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == tuple([x[0] for x in field_vocab]),
                        'Value is %s' % str(tuple(vocab)))

    def test_limitNumberField(self):
        dummy = self._dummy
        field = dummy.getField('limitNumber')
        field_vocab = BooleanField._properties.get('vocabulary', ())

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == field_vocab,
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getLimitNumber',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setLimitNumber',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == tuple([x[0] for x in field_vocab]),
                        'Value is %s' % str(tuple(vocab)))

    def test_itemCountField(self):
        dummy = self._dummy
        field = dummy.getField('itemCount')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == 0, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getItemCount',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setItemCount',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'integer', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, IntegerWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_customViewField(self):
        # XXX not in the current version
        return
        dummy = self._dummy
        field = dummy.getField('customView')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == False, 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getCustomView',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setCustomView',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'boolean', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(dummy)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_customViewFieldsField(self):
        # XXX not in the current version
        return
        dummy = self._dummy
        field = dummy.getField('customViewFields')

        self.failUnless(ILayerContainer.isImplementedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == ('Title',), 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 0, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == 'listMetaDataFields',
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == True,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getCustomViewFields',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setCustomViewFields',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ChangeTopics,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, InAndOutWidget),
                        'Value is %s' % id(field.widget))

tests.append(TestATTopicFields)

class TestATTopicFunctional(atctftestcase.ATCTIntegrationTestCase):

    def afterSetUp(self):
        # adding topics is restricted
        self.setRoles(['Manager', 'Member',])
        atctftestcase.ATCTIntegrationTestCase.afterSetUp(self)

    def test_dynamic_view_without_view(self):
        # dynamic view magic should work
        response = self.publish('%s/' % self.obj_path, self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200) #

    portal_type = 'Topic'
    views = ('atct_topic_view', 'criterion_edit_form', 'atct_topic_subtopics')

tests.append(TestATTopicFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
