#
# PTS test
#

import unittest
from Testing import ZopeTestCase

ZopeTestCase.installProduct('PlacelessTranslationService')

from Products.CMFPlone.utils import versionTupleFromString

from Products.PlacelessTranslationService import pts_globals
from Products.PlacelessTranslationService import PlacelessTranslationService as PTS

from Globals import package_home
PACKAGE_HOME = package_home(pts_globals)

def getFSVersionTuple():
    """Reads version.txt and returns version tuple"""
    vfile = "%s/version.txt" % PACKAGE_HOME
    v_str = open(vfile, 'r').read().lower()
    return versionTupleFromString(v_str)


class TestPTS(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.service = self.app.Control_Panel.TranslationService

    def testClassVersion(self):
        clv = PTS._class_version
        fsv = getFSVersionTuple()
        for i in range(3):
            self.assertEquals(clv[i], fsv[i],
                              'class version (%s) does not match filesystem version (%s)' % (clv, fsv))

    def testInterpolate(self):
        # empty mapping
        text = 'ascii'
        self.assertEquals(self.service.interpolate(text, []), text)

        text = 'ascii-with-funky-chars\xe2'
        self.assertEquals(self.service.interpolate(text, []), text)

        text = u'unicode-with-ascii-only'
        self.assertEquals(self.service.interpolate(text, []), text)

        text = u'unicode\xe2'
        self.assertEquals(self.service.interpolate(text, []), text)

        # text is ascii
        text = '${ascii}'
        mapping = {u'ascii' : 'ascii'}
        expected = 'ascii'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii}'
        mapping = {u'ascii' : 'ascii-with-funky-chars\xe2'}
        expected = 'ascii-with-funky-chars\xe2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii}'
        mapping = {u'ascii' : u'unicode-with-ascii-only'}
        expected = u'unicode-with-ascii-only'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii}'
        mapping = {u'ascii' : u'unicode\xe2'}
        expected = u'unicode\xe2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii}'
        mapping = {'ascii' : 1}
        expected = '1'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        # text is ascii with funky chars
        text = '${ascii-with-funky-chars}\xc2'
        mapping = {u'ascii-with-funky-chars' : 'ascii'}
        expected = 'ascii\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii-with-funky-chars}\xc2'
        mapping = {u'ascii-with-funky-chars' : 'ascii-with-funky-chars\xe2'}
        expected = 'ascii-with-funky-chars\xe2\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii-with-funky-chars}\xc2'
        mapping = {u'ascii-with-funky-chars' : u'unicode-with-ascii-only'}
        expected = '${ascii-with-funky-chars}\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii-with-funky-chars}\xc2'
        mapping = {u'ascii-with-funky-chars' : u'unicode\xe2'}
        expected = '${ascii-with-funky-chars}\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = '${ascii-with-funky-chars}\xc2'
        mapping = {'ascii-with-funky-chars' : 1}
        expected = '1\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        # text is unicode with only ascii chars
        text = u'${unicode-with-ascii-only}'
        mapping = {u'unicode-with-ascii-only' : 'ascii'}
        expected = 'ascii'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode-with-ascii-only}'
        mapping = {u'unicode-with-ascii-only' : 'ascii-with-funky-chars\xe2'}
        expected = u'${unicode-with-ascii-only}'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode-with-ascii-only}'
        mapping = {u'unicode-with-ascii-only' : u'unicode-with-ascii-only'}
        expected = u'unicode-with-ascii-only'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode-with-ascii-only}'
        mapping = {u'unicode-with-ascii-only' : u'unicode\xe2'}
        expected = u'unicode\xe2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode-with-ascii-only}'
        mapping = {u'unicode-with-ascii-only' : 1}
        expected = u'1'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        # text is real unicode
        text = u'${unicode}\xc2'
        mapping = {u'unicode' : 'ascii'}
        expected = u'ascii\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode}\xc2'
        mapping = {u'unicode' : 'ascii-with-funky-chars\xe2'}
        expected = u'${unicode}\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode}\xc2'
        mapping = {u'unicode' : u'unicode-with-ascii-only'}
        expected = u'unicode-with-ascii-only\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode}\xc2'
        mapping = {u'unicode' : u'unicode\xe2'}
        expected = u'unicode\xe2\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)

        text = u'${unicode}\xc2'
        mapping = {'unicode' : 1}
        expected = u'1\xc2'
        self.assertEquals(self.service.interpolate(text, mapping), expected)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPTS))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
