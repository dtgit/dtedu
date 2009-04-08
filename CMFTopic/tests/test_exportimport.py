##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for GenericSetup export / import support for topics / criteria.

$Id: test_exportimport.py 71240 2006-11-21 13:14:15Z yuppie $
"""

import unittest

from DateTime.DateTime import DateTime

from Products.GenericSetup.testing import ExportImportZCMLLayer
from Products.GenericSetup.tests.conformance \
        import ConformsToIFilesystemExporter
from Products.GenericSetup.tests.conformance \
        import ConformsToIFilesystemImporter
from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext

_DATE_STR = '2005-11-20T12:00:00Z'
_CRITERIA_DATA = (
    ('a', 'String Criterion', {'value': 'A'}),
    ('b', 'Integer Criterion', {'value': 3, 'direction': 'min'}),
    ('c', 'Friendly Date Criterion', {'value': DateTime(_DATE_STR),
                                      'operation': 'min',
                                      'daterange': 'old',
                                     }),
    ('d', 'List Criterion', {'value': ('D', 'd'), 'operator': 'or'}),
    ('e', 'Sort Criterion', {'reversed': 0}),
)


class TopicExportImportTests(BaseRegistryTests,
                             ConformsToIFilesystemExporter,
                             ConformsToIFilesystemImporter,
                            ):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.CMFTopic.exportimport import TopicExportImport
        return TopicExportImport

    def _makeOne(self, context, *args, **kw):
        return self._getTargetClass()(context, *args, **kw)

    def _makeTopic(self, id, with_criteria=False):
        from Products.CMFTopic.Topic import Topic
        topic = Topic(id)

        if with_criteria:
            for field, c_type, attrs in _CRITERIA_DATA:
                topic.addCriterion(field, c_type)
                criterion = topic.getCriterion(field)
                criterion.edit(**attrs)

        return topic

    def test_listExportableItems(self):
        topic = self._makeTopic('lEI', False).__of__(self.root)
        adapter = self._makeOne(topic)

        self.assertEqual(len(adapter.listExportableItems()), 0)
        topic.addCriterion('field_a', 'String Criterion')
        self.assertEqual(len(adapter.listExportableItems()), 0)

    def test__getExportInfo_empty(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        info = adapter._getExportInfo()
        self.assertEqual(len(info['criteria']), 0)

    def test_export_empty(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/empty/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/empty/criteria.xml' )
        self._compareDOM( text, _EMPTY_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test__getExportInfo_with_criteria(self):
        topic = self._makeTopic('with_criteria', True).__of__(self.root)
        adapter = self._makeOne(topic)

        info = adapter._getExportInfo()
        self.assertEqual(len(info['criteria']), len(_CRITERIA_DATA))

        for found, expected in zip(info['criteria'], _CRITERIA_DATA):
            attributes = expected[2]
            for k, v in attributes.items():
                if type(v) in (list, tuple):
                    attributes[k] = ','.join(v)

            self.assertEqual(found['criterion_id'], 'crit__%s' % expected[0])
            self.assertEqual(found['type'], expected[1])
            self.assertEqual(found['field'], expected[0])
            self.assertEqual(dict(found['attributes']), attributes)

    def test_export_with_string_criterion(self):
        topic = self._makeTopic('with_string', False).__of__(self.root)
        data = _CRITERIA_DATA[0]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_string/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_string/criteria.xml' )
        self._compareDOM( text, _STRING_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_export_with_integer_criterion(self):
        topic = self._makeTopic('with_integer', False).__of__(self.root)
        data = _CRITERIA_DATA[1]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_integer/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_integer/criteria.xml' )
        self._compareDOM( text, _INTEGER_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_export_with_date_criterion(self):
        topic = self._makeTopic('with_date', False).__of__(self.root)
        data = _CRITERIA_DATA[2]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_date/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_date/criteria.xml' )
        self._compareDOM( text, _DATE_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_export_with_list_criterion(self):
        topic = self._makeTopic('with_list', False).__of__(self.root)
        data = _CRITERIA_DATA[3]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_list/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_list/criteria.xml' )
        self._compareDOM( text, _LIST_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_export_with_sort_criterion(self):
        topic = self._makeTopic('with_sort', False).__of__(self.root)
        data = _CRITERIA_DATA[4]
        topic.addCriterion(data[0], data[1])
        topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_sort/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_sort/criteria.xml' )
        self._compareDOM( text, _SORT_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_export_with_mixed_criteria(self):
        topic = self._makeTopic('with_mixed', False).__of__(self.root)
        for index in 0, 2, 4:
            data = _CRITERIA_DATA[index]
            topic.addCriterion(data[0], data[1])
            topic.getCriterion(data[0]).edit(**data[2])
        adapter = self._makeOne(topic)

        context = DummyExportContext(topic)
        adapter.export(context, 'test', False)

        self.assertEqual( len( context._wrote ), 2 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, 'test/with_mixed/.objects' )
        self.assertEqual( text, '' )
        self.assertEqual( content_type, 'text/comma-separated-values' )

        filename, text, content_type = context._wrote[ 1 ]
        self.assertEqual( filename, 'test/with_mixed/criteria.xml' )
        self._compareDOM( text, _MIXED_TOPIC_CRITERIA )
        self.assertEqual( content_type, 'text/xml' )

    def test_import_empty_with_string_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _STRING_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        expected = _CRITERIA_DATA[0]
        found = topic.listCriteria()
        self.assertEqual(len(found), 1)

        criterion = found[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(criterion.value, expected[2]['value'])

    def test_import_empty_with_integer_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _INTEGER_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        expected = _CRITERIA_DATA[1]
        found = topic.listCriteria()
        self.assertEqual(len(found), 1)

        criterion = found[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(criterion.value, expected[2]['value'])
        self.assertEqual(criterion.direction, expected[2]['direction'])

    def test_import_empty_with_date_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _DATE_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        expected = _CRITERIA_DATA[2]
        found = topic.listCriteria()
        self.assertEqual(len(found), 1)

        criterion = found[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(criterion.value, expected[2]['value'])
        self.assertEqual(criterion.operation, expected[2]['operation'])
        self.assertEqual(criterion.daterange, expected[2]['daterange'])

    def test_import_empty_with_list_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _LIST_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        expected = _CRITERIA_DATA[3]
        found = topic.listCriteria()
        self.assertEqual(len(found), 1)

        criterion = found[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(','.join(criterion.value), expected[2]['value'])
        self.assertEqual(criterion.operator, expected[2]['operator'])

    def test_import_empty_with_sort_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _SORT_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        expected = _CRITERIA_DATA[4]
        found = topic.listCriteria()
        self.assertEqual(len(found), 1)

        criterion = found[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.field, None)
        self.assertEqual(criterion.index, expected[0])
        self.assertEqual(criterion.reversed, bool(expected[2]['reversed']))

    def test_import_empty_with_mixed_criterion(self):
        topic = self._makeTopic('empty', False).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, encoding='ascii')
        context._files['test/empty/criteria.xml'] = _MIXED_TOPIC_CRITERIA

        adapter.import_(context, 'test', False)

        found = topic.listCriteria()
        self.assertEqual(len(found), 3)

        criterion = found[0]
        expected = _CRITERIA_DATA[0]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(criterion.value, expected[2]['value'])

        criterion = found[1]
        expected = _CRITERIA_DATA[2]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.Field(), expected[0])
        self.assertEqual(criterion.value, expected[2]['value'])
        self.assertEqual(criterion.operation, expected[2]['operation'])
        self.assertEqual(criterion.daterange, expected[2]['daterange'])

        criterion = found[2]
        expected = _CRITERIA_DATA[4]

        self.assertEqual(criterion.getId(), 'crit__%s' % expected[0])
        self.assertEqual(criterion.Type(), expected[1])
        self.assertEqual(criterion.field, None)
        self.assertEqual(criterion.index, expected[0])
        self.assertEqual(criterion.reversed, bool(expected[2]['reversed']))

    def test_import_without_purge_leaves_existing_criteria(self):

        topic = self._makeTopic('with_criteria', True).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, purge=False)
        context._files['test/with_criteria/criteria.xml'
                      ] = _EMPTY_TOPIC_CRITERIA

        self.assertEqual(len(topic.listCriteria()), len(_CRITERIA_DATA))
        adapter.import_(context, 'test', False)
        self.assertEqual(len(topic.listCriteria()), len(_CRITERIA_DATA))

    def test_import_with_purge_removes_existing_criteria(self):

        topic = self._makeTopic('with_criteria', True).__of__(self.root)
        adapter = self._makeOne(topic)

        context = DummyImportContext(topic, purge=True)
        context._files['test/with_criteria/criteria.xml'
                      ] = _EMPTY_TOPIC_CRITERIA

        self.assertEqual(len(topic.listCriteria()), len(_CRITERIA_DATA))
        adapter.import_(context, 'test', False)
        self.assertEqual(len(topic.listCriteria()), 0)

_EMPTY_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
</criteria>
"""

_STRING_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__a"
    type="String Criterion"
    field="a">
  <attribute name="value" value="A" />
 </criterion>
</criteria>
"""

_INTEGER_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__b"
    type="Integer Criterion"
    field="b">
  <attribute name="value" value="3" />
  <attribute name="direction" value="min" />
 </criterion>
</criteria>
"""

_DATE_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__c"
    type="Friendly Date Criterion"
    field="c">
  <attribute name="value" value="%s" />
  <attribute name="operation" value="min" />
  <attribute name="daterange" value="old" />
 </criterion>
</criteria>
""" % int(DateTime(_DATE_STR))

_LIST_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__d"
    type="List Criterion"
    field="d">
  <attribute name="value" value="D,d" />
  <attribute name="operator" value="or" />
 </criterion>
</criteria>
"""

_SORT_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__e"
    type="Sort Criterion"
    field="e">
  <attribute name="reversed" value="False" />
 </criterion>
</criteria>
"""

_MIXED_TOPIC_CRITERIA = """\
<?xml version="1.0" ?>
<criteria>
 <criterion
    criterion_id="crit__a"
    type="String Criterion"
    field="a">
  <attribute name="value" value="A" />
 </criterion>
 <criterion
    criterion_id="crit__c"
    type="Friendly Date Criterion"
    field="c">
  <attribute name="value" value="%s" />
  <attribute name="operation" value="min" />
  <attribute name="daterange" value="old" />
 </criterion>
 <criterion
    criterion_id="crit__e"
    type="Sort Criterion"
    field="e">
  <attribute name="reversed" value="False" />
 </criterion>
</criteria>
""" % int(DateTime(_DATE_STR))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TopicExportImportTests),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())
