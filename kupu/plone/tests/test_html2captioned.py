import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from kuputestcase import *

from unittest  import TestCase, TestSuite, main, makeSuite
from os.path import join, abspath, dirname

from Products.PortalTransforms.tests.test_transforms import *
from Products.PortalTransforms.tests.utils import normalize_html
from Products.kupu import kupu_globals

PREFIX = abspath(dirname(__file__))

def input_file_path(file):
    return join(PREFIX, 'input', file)

def output_file_path(file):
    return join(PREFIX, 'output', file)

tests =(
('Products.kupu.plone.html2captioned', "minimal.in", "minimal.out", normalize_html, 0),
('Products.kupu.plone.html2captioned', "simple.in", "simple.out", normalize_html, 0),
('Products.kupu.plone.html2captioned', "baduid.in", "baduid.out", normalize_html, 0),
('Products.kupu.plone.html2captioned', "notquoted.in", "notquoted.out", normalize_html, 0),
('Products.kupu.plone.html2captioned', "notcaptioned.in", "notcaptioned.out", normalize_html, 0),
('Products.kupu.plone.html2captioned', "linked.in", "linked.out", normalize_html, 0),
    )

class TransformTest(KupuTestCase):
    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        input = open(self.input)
        orig = input.read()
        input.close()
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename, context=self.portal)
        self.assert_(idatastream.isImplementedBy(res_data))
        got = res_data.getData()
        try:
            output = open(output)
        except IOError:
            import sys
            print >>sys.stderr, 'No output file found.'
            print >>sys.stderr, 'File %s created, check it !' % self.output
            output = open(output, 'w')
            output.write(got)
            output.close()
            self.assert_(0)
        expected = output.read()
        raw_got, raw_expected = got, expected
        if self.normalize is not None:
            expected = self.normalize(expected)
            got = self.normalize(got)
        output.close()

        self.assertEquals(got, expected,
                          'Got:\n[%s]\n\n!=\n\nExpected:\n[%s]\n\nIN %s(%s)' % (
            got, expected, self.transform.name(), self.input))
        self.assertEquals(self.subobjects, len(res_data.getSubObjects()),
                          'Subobjects:\n%s\n\n!=\n\nLength: %s\n\nIN %s(%s)' % (
            self.subobjects, len(res_data.getSubObjects()), self.transform.name(), self.input))

    def testSame(self):
        self.setup_content()
        self.do_convert(filename=self.input)

    def testSameNoFilename(self):
        self.setup_content()
        self.do_convert()

    def __repr__(self):
        return self.transform.name()

TR_NAMES = None

def make_tests(test_descr):
    """generate tests classes from test info

    return the list of generated test classes
    """
    tests = []
    for _transform, tr_input, tr_output, _normalize, _subobjects in test_descr:
        # load transform if necessary
        if type(_transform) is type(''):
            try:
                _transform = load(_transform).register()
            except:
                import traceback
                traceback.print_exc()
                continue
        #
        if TR_NAMES is not None and not _transform.name() in TR_NAMES:
            print 'skip test for', _transform.name()
            continue

        class TransformTestSubclass(TransformTest):
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    return tests

def test_suite():
    t = [ (_transform,
        input_file_path(tr_input),
        output_file_path(tr_output),
        _normalize,
        _subobjects)
        for _transform, tr_input, tr_output, _normalize, _subobjects in tests ]
        
    return TestSuite([makeSuite(test) for test in make_tests(t)])

if __name__=='__main__': 
    main(defaultTest='test_suite') 
