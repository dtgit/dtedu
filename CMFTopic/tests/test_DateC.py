##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for DateCriteria module.

$Id: test_DateC.py 75625 2007-05-08 15:56:26Z tseaver $
"""

import unittest
from Testing import ZopeTestCase

from DateTime.DateTime import DateTime
from zope.app.component.hooks import setSite

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFDefault.testing import FunctionalLayer
from Products.CMFTopic.Topic import Topic

from common import CriterionTestCase

def _replace_DC__as_of(new_callable):
    from Products.CMFTopic import DateCriteria
    old_value = DateCriteria._as_of
    DateCriteria._as_of = new_callable
    return old_value


class FriendlyDateCriterionTests(CriterionTestCase):

    lessThanFiveDaysOld = { 'value': 5
                          , 'operation': 'max'
                          , 'daterange': 'old'
                          }

    lessThanOneMonthAhead = { 'value': 31
                            , 'operation': 'max'
                            , 'daterange': 'ahead'
                            }
    today = { 'value': 0
            , 'operation': 'within_day'
            , 'daterange': 'ahead'
            }

    def setUp(self):
        self._now = DateTime()
        self._old_as_of = _replace_DC__as_of(lambda: self._now)

    def tearDown(self):
        _replace_DC__as_of(self._old_as_of)

    def _getTargetClass(self):
        from Products.CMFTopic.DateCriteria import FriendlyDateCriterion

        return FriendlyDateCriterion

    def test_Empty( self ):
        friendly = self._makeOne('foo', 'foofield')

        self.assertEqual( friendly.getId(), 'foo' )
        self.assertEqual( friendly.field, 'foofield' )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )
        self.assertEqual( len( friendly.getCriteriaItems() ), 0 )

    def test_ListOfDefaultDates( self ):
        friendly = self._makeOne('foo', 'foofield')

        d = friendly.defaultDateOptions()
        self.assertEqual( d[0][0], 0 )
        self.assertEqual( d[1][0], 1 )
        self.assertEqual( d[2][0], 2 )

    def test_Clear( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.edit( value=None )
        self.assertEqual( friendly.value, None )
        self.assertEqual( friendly.operation, 'min' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_Basic( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.value, 5 )
        self.assertEqual( friendly.operation, 'max' )
        self.assertEqual( friendly.daterange, 'old' )

    def test_BadInput( self ):
        friendly = self._makeOne('foo', 'foofield')

        # Bogus value
        self.assertRaises( ValueError, friendly.edit, 'blah' )

        # Bogus operation
        self.assertRaises( ValueError, friendly.edit, 4, 'min:max', 'old' )

        # Bogus daterange
        self.assertRaises( ValueError, friendly.edit, 4, 'max', 'new' )

    def test_StringAsValue( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.edit( '4' )
        self.assertEqual( friendly.value, 4 )

        friendly.edit( '-4' )
        self.assertEqual( friendly.value, -4 )

        friendly.edit( '' )
        self.assertEqual( friendly.value, None )

    def test_Today( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.today )
        self.assertEqual( friendly.daterange, 'ahead' )

        now = DateTime()

        result = friendly.getCriteriaItems()
        self.assertEqual( len(result), 1 )
        self.assertEqual( result[0][0], 'foofield' )
        self.assertEqual( result[0][1]['query'],
                          ( now.earliestTime(), now.latestTime() ) )
        self.assertEqual( result[0][1]['range'], 'min:max' )

    def test_FiveDaysOld( self ):
        # This should create a query
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanFiveDaysOld )
        self.assertEqual( friendly.daterange, 'old' )

        result = friendly.getCriteriaItems()
        self.assertEqual( len(result), 1 )
        self.assertEqual( result[0][0], 'foofield' )
        expect_earliest, expect_now = result[0][1]['query']
        self.assertEqual( expect_earliest.Date(),
                          ( DateTime() - 5 ).Date() )
        self.assertEqual( result[0][1]['range'], 'min:max' )

    def test_OneMonthAhead( self ):
        friendly = self._makeOne('foo', 'foofield')

        friendly.apply( self.lessThanOneMonthAhead )
        self.assertEqual( friendly.daterange, 'ahead' )

        result = friendly.getCriteriaItems()
        expect_now, expect_latest = result[0][1]['query']
        self.assertEqual( expect_latest.Date(), ( DateTime() + 31 ).Date() )
        self.assertEqual( expect_now.Date(), DateTime().Date() )
        self.assertEqual( result[0][1]['range'], 'min:max' )


class FriendlyDateCriterionFunctionalTests(ZopeTestCase.FunctionalTestCase):

    layer = FunctionalLayer

    # Test the date criterion using a "real CMF" with catalog etc.
    selectable_diffs = [0, 1, 2, 5, 7, 14, 31, 93, 186, 365, 730]
    nonzero_diffs = [1, 2, 5, 7, 14, 31, 93, 186, 365, 730]
    day_diffs = [-730, -365, -186, -93, -31, -14, -7, -5, -2, -1]
    day_diffs.extend(selectable_diffs)

    def afterSetUp(self):
        setSite(self.app.site)
        self.site = self.app.site
        self.site._setObject( 'topic', Topic('topic') )
        self.topic = self.site.topic
        self.topic.addCriterion('modified', 'Friendly Date Criterion')
        self.topic.addCriterion('portal_type', 'String Criterion')
        type_crit = self.topic.getCriterion('portal_type')
        type_crit.edit(value='Dummy Content')
        self.criterion = self.topic.getCriterion('modified')
        self.now = DateTime()
        self._old_as_of = _replace_DC__as_of(lambda: self.now)

        for i in self.day_diffs:
            dummy_id = 'dummy%i' % i
            self.site._setObject( dummy_id, DummyContent( id=dummy_id
                                                        , catalog=1
                                                        ) )
            dummy_ob = getattr(self.site, dummy_id)
            dummy_ob.modified_date = self.now + i
            dummy_ob.reindexObject()

    def beforeTearDown(self):
        _replace_DC__as_of(self._old_as_of)

    def test_Harness(self):
        # Make sure the test harness is set up OK
        ob_values = self.site.objectValues(['Dummy'])
        self.assertEqual(len(ob_values), len(self.day_diffs))

        catalog_results = self.site.portal_catalog(portal_type='Dummy Content')
        self.assertEqual(len(catalog_results), len(self.day_diffs))

    def test_WithinDayAgo(self):
        # What items were modified "On the day X days ago"
        for diff in self.selectable_diffs:
            self.criterion.edit( value=abs(diff)
                               , operation='within_day'
                               , daterange='old'
                               )
            results = self.topic.queryCatalog()

            # There is only one item with an modified date for this day
            self.assertEquals(len(results), 1)
            self.assertEquals( results[0].modified.Date()
                             , (self.now-diff).Date()
                             )

    def test_WithinDayAhead(self):
        # What items were modified "On the day X days ahead"
        for diff in self.selectable_diffs:
            self.criterion.edit( value=abs(diff)
                               , operation='within_day'
                               , daterange='ahead'
                               )
            results = self.topic.queryCatalog()

            # There is only one item with an modified date for this day
            self.assertEquals(len(results), 1)
            self.assertEquals( results[0].modified.Date()
                             , (self.now+diff).Date()
                             )

    def test_MoreThanDaysAgo(self):
        # What items are modified "More than X days ago"
        resultset_size = len(self.nonzero_diffs)

        for diff in self.nonzero_diffs:
            self.criterion.edit( value=diff
                               , operation='min'
                               , daterange='old'
                               )
            results = self.topic.queryCatalog()

            # As we move up in our date difference range, we must find as
            # many items as we have "modified" values <= the current value
            # in our sequence of user-selectable time differences. As we
            # increase the "value", we actually move backwards in time, so
            # the expected count of results *decreases*
            self.assertEquals(len(results), resultset_size)
            for brain in results:
                self.failUnless(brain.modified <= self.now-diff)

            resultset_size -= 1

    def test_MoreThanZeroDaysAgo(self):
        # What items are modified "More than 0 days ago"?
        # This represents a special case. The "special munging"
        # that corrects the query terms to what a human would expect
        # are not applied and the search is a simple
        # "everything in the future" search.
        resultset_size = len(self.selectable_diffs)
        self.criterion.edit( value=0
                           , operation='min'
                           , daterange='old'
                           )
        results = self.topic.queryCatalog()
        self.assertEquals(len(results), resultset_size)
        for brain in results:
            self.failUnless(brain.modified >= self.now)

    def test_MoreThanDaysAhead(self):
        # What items are modified "More than X days ahead"
        resultset_size = len(self.nonzero_diffs)

        for diff in self.nonzero_diffs:
            self.criterion.edit( value=diff
                               , operation='min'
                               , daterange='ahead'
                               )
            results = self.topic.queryCatalog()

            # As we move up in our date difference range, we must find as
            # many items as we have "modified" values >= the current value
            # in our sequence of user-selectable time differences. As we
            # increase the "value", we actually move formward in time, so
            # the expected count of results *decreases*
            self.assertEquals(len(results), resultset_size)
            for brain in results:
                self.failUnless(brain.modified >= self.now+diff)

            resultset_size -= 1

    def test_MoreThanZeroDaysAhead(self):
        # What items are modified "More than 0 days ahead"?
        # This represents a special case. The "special munging"
        # that corrects the query terms to what a human would expect
        # are not applied and the search is a simple
        # "everything in the future" search.
        resultset_size = len(self.selectable_diffs)
        self.criterion.edit( value=0
                           , operation='min'
                           , daterange='ahead'
                           )
        results = self.topic.queryCatalog()
        self.assertEquals(len(results), resultset_size)
        for brain in results:
            self.failUnless(brain.modified >= self.now)

    def test_LessThanDaysAgo(self):
        # What items are modified "Less than X days ago"
        resultset_size = 2

        for diff in self.nonzero_diffs:
            self.criterion.edit( value=diff
                               , operation='max'
                               , daterange='old'
                               )
            results = self.topic.queryCatalog()

            # With this query we are looking for items modified "less than
            # X days ago", meaning between the given time and now. As we move
            # through the selectable day values we increase the range to
            # search through and thus increase the resultset size.
            self.assertEquals(len(results), resultset_size)
            for brain in results:
                self.failUnless(self.now-diff <= brain.modified <= self.now)

            resultset_size += 1

    def test_LessThanZeroDaysAgo(self):
        # What items are modified "Less than 0 days ago"?
        # This represents a special case. The "special munging"
        # that corrects the query terms to what a human would expect
        # are not applied and the search is a simple
        # "everything in the past" search.
        resultset_size = len(self.selectable_diffs)
        self.criterion.edit( value=0
                           , operation='max'
                           , daterange='old'
                           )
        results = self.topic.queryCatalog()
        self.assertEquals(len(results), resultset_size)
        for brain in results:
            self.failUnless(brain.modified <= self.now)

    def test_LessThanDaysAhead(self):
        # What items are modified "Less than X days ahead"
        resultset_size = 2

        for diff in self.nonzero_diffs:
            self.criterion.edit( value=diff
                               , operation='max'
                               , daterange='ahead'
                               )
            results = self.topic.queryCatalog()

            # With this query we are looking for items modified "less than
            # X days ahead", meaning between now and the given time. As we move
            # through the selectable day values we increase the range to
            # search through and thus increase the resultset size.
            self.assertEquals(len(results), resultset_size)
            for brain in results:
                self.failUnless(self.now+diff >= brain.modified >= self.now)

            resultset_size += 1

    def test_LessThanZeroDaysAhead(self):
        # What items are modified "Less than 0 days ahead"?
        # This represents a special case. The "special munging"
        # that corrects the query terms to what a human would expect
        # are not applied and the search is a simple
        # "everything in the past" search.
        resultset_size = len(self.selectable_diffs)
        self.criterion.edit( value=0
                           , operation='max'
                           , daterange='ahead'
                           )
        results = self.topic.queryCatalog()
        self.assertEquals(len(results), resultset_size)
        for brain in results:
            self.failUnless(brain.modified <= self.now)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FriendlyDateCriterionTests),
        unittest.makeSuite(FriendlyDateCriterionFunctionalTests),
        ))

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
