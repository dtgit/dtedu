# Copyright (c) 2004 Zope Corporation and Plone Solutions
# ZPL 2.1 license

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ExtendedPathIndex.tests import epitc
from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex


class TestPathIndex(epitc.PathIndexTestCase):
    """ Test ExtendedPathIndex objects """

    def testEmpty(self):
        self.assertEqual(self._index.numObjects() ,0)
        self.assertEqual(self._index.getEntryForObject(1234), None)
        self._index.unindex_object( 1234 ) # nothrow
        self.assertEqual(self._index._apply_index({"suxpath": "xxx"}), None)

    def testUnIndex(self):
        self._populateIndex()
        self.assertEqual(self._index.numObjects(), 18)

        for k in self._values.keys():
            self._index.unindex_object(k)

        self.assertEqual(self._index.numObjects(), 0)
        self.assertEqual(len(self._index._index), 0)
        self.assertEqual(len(self._index._unindex), 0)

    def testReindex(self):
        self._populateIndex()
        self.assertEqual(self._index.numObjects(), 18)

        o = epitc.Dummy('/foo/bar')
        self._index.index_object(19, o)
        self.assertEqual(self._index.numObjects(), 19)
        self._index.index_object(19, o)
        self.assertEqual(self._index.numObjects(), 19)

    def testUnIndexError(self):
        self._populateIndex()
        # this should not raise an error
        self._index.unindex_object(-1)

        # nor should this
        self._index._unindex[1] = "/broken/thing"
        self._index.unindex_object(1)

    def testRoot_1(self):
        self._populateIndex()
        tests = ( ("/", 0, range(1,19)), )

        for comp, level, results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': path, "level": level}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

        for comp, level, results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': ((path, level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

    def testRoot_2(self):
        self._populateIndex()
        tests = ( ("/", 0, range(1,19)), )

        for comp,level,results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': path, "level": level}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

        for comp, level, results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': ((path, level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

    def testSimpleTests(self):
        self._populateIndex()
        tests = [
            ("aa", 0, [1,2,3,4,5,6,7,8,9]),
            ("aa", 1, [1,2,3,10,11,12] ),
            ("bb", 0, [10,11,12,13,14,15,16,17,18]),
            ("bb", 1, [4,5,6,13,14,15]),
            ("bb/cc", 0, [16,17,18]),
            ("bb/cc", 1, [6,15]),
            ("bb/aa", 0, [10,11,12]),
            ("bb/aa", 1, [4,13]),
            ("aa/cc", -1, [3,7,8,9,12]),
            ("bb/bb", -1, [5,13,14,15]),
            ("18.html", 3, [18]),
            ("18.html", -1, [18]),
            ("cc/18.html", -1, [18]),
            ("cc/18.html", 2, [18]),
        ]

        for comp, level, results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': path, "level": level}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

        for comp, level, results in tests:
            for path in [comp, "/"+comp, "/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path": {'query': ((path, level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst, results)

    def testComplexOrTests(self):
        self._populateIndex()
        tests = [
            (['aa','bb'], 1, [1,2,3,4,5,6,10,11,12,13,14,15]),
            (['aa','bb','xx'], 1, [1,2,3,4,5,6,10,11,12,13,14,15]),
            ([('cc',1), ('cc',2)], 0, [3,6,7,8,9,12,15,16,17,18]),
        ]

        for lst, level, results in tests:
            res = self._index._apply_index(
                            {"path": {'query': lst, "level": level, "operator": "or"}})
            lst = list(res[0].keys())
            self.assertEqual(lst, results)

    def testComplexANDTests(self):
        self._populateIndex()
        tests = [
            (['aa','bb'], 1, []),
            ([('aa',0), ('bb',1)], 0, [4,5,6]),
            ([('aa',0), ('cc',2)], 0, [3,6,9]),
        ]

        for lst, level, results in tests:
            res = self._index._apply_index(
                            {"path": {'query': lst, "level": level, "operator": "and"}})
            lst = list(res[0].keys())
            self.assertEqual(lst, results)


class TestExtendedPathIndex(epitc.ExtendedPathIndexTestCase):
    """ Test ExtendedPathIndex objects """

    def testIndexIntegrity(self):
        self._populateIndex()
        index = self._index._index
        self.assertEqual(list(index[None][0].keys()), [1,8,16])
        self.assertEqual(list(index[None][1].keys()), [2,9,10,17,18])
        self.assertEqual(list(index[None][2].keys()), [3,5,11,13])
        self.assertEqual(list(index[None][3].keys()), [4,6,7,12,14,15])

    def testUnIndexError(self):
        self._populateIndex()
        # this should not raise an error
        self._index.unindex_object(-1)

        # nor should this
        self._index._unindex[1] = "/broken/thing"
        self._index.unindex_object(1)

    def testDepthLimit(self):
        self._populateIndex()
        tests = [
            ('/', 0, 1, 0, [1,8,16]),
            ('/', 0, 2, 0, [1,2,8,9,10,16,17,18]),
            ('/', 0, 3, 0, [1,2,3,5,8,9,10,11,13,16,17,18]),
            ]

        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst, results)

    def testDefaultNavtree(self):
        self._populateIndex()
        # depth = 1 by default when using navtree
        tests = [
            ('/'        ,0,1,1,[1,8,16]),
            ('/aa'      ,0,1,1,[1,2,8,9,16]),
            ('/aa'      ,1,1,1,[2,3,9,10,13,17,18]),
            ('/aa/aa'   ,0,1,1,[1,2,3,8,9,16]),
            ('/aa/aa/aa',0,1,1,[1,2,3,4,8,9,16]),
            ('/aa/bb'   ,0,1,1,[1,2,5,8,9,16]),
            ('/bb'      ,0,1,1,[1,8,10,16,17,18]),
            ('/bb/aa'   ,0,1,1,[1,8,10,13,16,17,18]),
            ('/bb/bb'   ,0,1,1,[1,8,10,11,16,17,18]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

    def testShallowNavtree(self):
        self._populateIndex()
        # With depth 0 we only get the parents
        tests = [
            ('/'        ,0,0,1,[]),
            ('/aa'      ,0,0,1,[8]),
            ('/aa'      ,1,0,1,[18]),
            ('/aa/aa'   ,0,0,1,[8]),
            ('/aa/aa/aa',0,0,1,[8]),
            ('/aa/bb'   ,0,0,1,[8,9]),
            ('/bb'      ,0,0,1,[16]),
            ('/bb/aa'   ,0,0,1,[16,18]),
            ('/bb/bb'   ,0,0,1,[16,17]),
            ('/bb/bb/aa'   ,0,0,1,[16,17]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

    def testNonexistingPaths(self):
        self._populateIndex()
        # With depth 0 we only get the parents
        # When getting non existing paths, 
        # we should get as many parents as possible when building navtree
        tests = [
            ('/'        ,0,0,1,[]),
            ('/aa'      ,0,0,1,[8]), # Exists
            ('/aa/x'    ,0,0,1,[8]), # Doesn't exist
            ('/aa'      ,1,0,1,[18]),
            ('/aa/x'    ,1,0,1,[18]),
            ('/aa/aa'   ,0,0,1,[8]),
            ('/aa/aa/x' ,0,0,1,[8]),
            ('/aa/bb'   ,0,0,1,[8,9]),
            ('/aa/bb/x' ,0,0,1,[8,9]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

    def testEmptyFolderDepthOne(self):
        # Shouldn't return folder when we want children of empty folder
        self._values = {
          1 : epitc.Dummy("/portal/emptyfolder"),
          2 : epitc.Dummy("/portal/folder"),
          3 : epitc.Dummy("/portal/folder/document"),
          4 : epitc.Dummy("/portal/folder/subfolder"),
          5 : epitc.Dummy("/portal/folder/subfolder/newsitem")
          }
        self._populateIndex()
        tests = [
            ('/portal/folder'                       ,0,1,0,[3,4]),
            ('/portal/emptyfolder'                  ,0,1,0,[]),
            ('/portal/folder/document'              ,0,1,0,[]),
            ('/portal/folder/subfolder'             ,0,1,0,[5]),
            ('/portal/folder/subfolder/newsitem'    ,0,1,0,[]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

    def testSiteMap(self):
        self._values = {
          1 : epitc.Dummy("/portal/emptyfolder"),
          2 : epitc.Dummy("/portal/folder"),
          3 : epitc.Dummy("/portal/folder/document"),
          4 : epitc.Dummy("/portal/folder/subfolder"),
          5 : epitc.Dummy("/portal/folder/subfolder/newsitem")
          }
        self._populateIndex()
        tests = [
            ('/' ,0,1,0,[]),
            ('/' ,0,2,0,[1,2]),
            ('/' ,0,3,0,[1,2,3,4]),
            ('/' ,0,4,0,[1,2,3,4,5]),
            ('/' ,0,5,0,[1,2,3,4,5]),
            ('/' ,0,6,0,[1,2,3,4,5]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': lst, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)


    def testBreadCrumbsWithStart(self):
        self._populateIndex()
        # Adding a navtree_start > 0 to a breadcrumb search should generate
        # breadcrumbs back to that level above the root.  The given path
        # will always be included, i.e. start > cur_level -> start = cur_level
        tests = [
            ('/'                   ,0,1,1,[]),
            ('/aa'                 ,0,1,1,[8]),
            ('/aa/aa'              ,0,1,1,[8]),
            ('/aa/aa/aa'           ,0,1,1,[8]),
            ('/aa/bb'              ,0,1,1,[8,9]),
            ('/bb'                 ,0,1,1,[16]),
            ('/bb/aa'              ,0,1,1,[16,18]),
            ('/bb/aa'              ,0,1,2,[18]),
            ('/bb/bb'              ,0,1,1,[16,17]),
            ('/bb/bb'              ,0,1,2,[17]),
            ('/bb/bb/bb/12.html'   ,0,1,1,[12,16,17]),
            ('/bb/bb/bb/12.html'   ,0,1,2,[12,17]),
            ('/bb/bb/bb/12.html'   ,0,1,3,[12]),
            ]
        for path, depth, navtree, navtree_start, results in tests:
            res = self._index._apply_index(
                {"path": {'query': path,  "depth": depth, "navtree": navtree,
                                              "navtree_start":navtree_start}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results,
                        '%s != %s Failed on %s start %s'%(
                                               lst,results,path,navtree_start))

    def testNegativeDepthQuery(self):
        self._populateIndex()
        tests = [
            ('/'                   ,0,-1,0,range(1,19)), # Depth -1
            ('/aa'                 ,0,-1,0,[2,3,4,5,6,7,8,9]),
            ('/aa/aa'              ,0,-1,0,[3,4]),
            ('/aa/bb'              ,0,-1,0,[5,6,7,9]),
            ('/bb'                 ,0,-1,0,[10,11,12,13,14,15,16,17,18]),
            ('/bb/aa'              ,0,-1,0,[13,14,18]),
            ('/bb/bb'              ,0,-1,0,[11,12,15,17]),
        ]

        for path, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': path, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results,
                        '%s != %s Failed on %s level %s depth %s navtree %s'%(
                                        lst,results,path,level,depth,navtree))

    def testPhysicalPathOptimization(self):
        self._populateIndex()
        # Fake a physical path for the index
        self._index.old_getPhysicalPath = self._index.getPhysicalPath
        self._index.getPhysicalPath = lambda: ('','aa')
        self.assertEqual(self._index.getPhysicalPath(), ('','aa'))
        # Test a variety of arguments
        tests = [
            ('/'                   ,0,1,0,[1,8,16]), # Sitemap
            ('/'                   ,0,0,1,[]), # Non-Existant
            ('/'                   ,0,0,1,[]), # Breadcrumb tests
            ('/aa'                 ,0,0,1,[8]),
            ('/aa/aa'              ,0,0,1,[8]),
            ('/'                   ,0,1,1,[1,8,16]), # Navtree tests
            ('/aa'                 ,0,1,1,[1,2,8,9,16]),
            ('/aa/aa'              ,0,1,1,[1,2,3,8,9,16]),
            ('/'                   ,0,0,0,[]), # Depth Zero tests
            ('/aa'                 ,0,0,0,[8]),
            ('/aa/aa'              ,0,0,0,[]),
            ('/'                   ,0,-1,0,range(1,19)), # Depth -1
            ('/aa'                 ,0,-1,0,range(1,19)), # Should assume that
                                                         # all paths are
                                                         # relevant
        ]

        for path, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path": {'query': path, "level": level, "depth": depth, "navtree": navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results,
                        '%s != %s Failed on %s level %s depth %s navtree %s'%(
                                        lst,results,path,level,depth,navtree))

        self._index.getPhysicalPath = self._index.old_getPhysicalPath
        self.assertEqual(self._index.getPhysicalPath(), ('path',))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPathIndex))
    suite.addTest(makeSuite(TestExtendedPathIndex))
    return suite

if __name__ == '__main__':
    framework()
