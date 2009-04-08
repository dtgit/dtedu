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
""" Unit tests for Document module.

$Id: test_Document.py 77186 2007-06-28 19:06:19Z yuppie $
"""

import unittest
import Testing

from os.path import abspath
from os.path import dirname
from os.path import join as path_join
from re import compile
from StringIO import StringIO

from DocumentTemplate.DT_Util import html_quote
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.CMFCore.testing import ConformsToContent
from Products.CMFCore.tests.base.content import BASIC_HTML
from Products.CMFCore.tests.base.content import BASIC_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import DOCTYPE
from Products.CMFCore.tests.base.content import ENTITY_IN_TITLE
from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import HTML_TEMPLATE
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_NO_HEADERS
from Products.CMFCore.tests.base.content import STX_NO_HEADERS_BUT_COLON
from Products.CMFCore.tests.base.content import STX_WITH_HTML
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.testcase import RequestTest
from Products.CMFCore.tests.base.tidata import FTIDATA_CMF15
from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFDefault import utils


class RequestTestBase(RequestTest):

    def _getTargetClass(self):
        from Products.CMFDefault.Document import Document

        return Document

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)


class DocumentTests(ConformsToContent, RequestTestBase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFDefault.interfaces.Document import IDocument
        from Products.CMFDefault.interfaces.Document import IMutableDocument

        verifyClass(IDocument, self._getTargetClass())
        verifyClass(IMutableDocument, self._getTargetClass())

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFDefault.interfaces import IDocument
        from Products.CMFDefault.interfaces import IMutableDocument

        verifyClass(IDocument, self._getTargetClass())
        verifyClass(IMutableDocument, self._getTargetClass())

    def test_Empty(self):
        d = self._makeOne('foo', text_format='structured-text')

        self.assertEqual( d.title, '' )
        self.assertEqual( d.description, '' )
        self.assertEqual( d.text, '' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d._stx_level, 1 )
        self.assertEqual( d.get_size(), 0 )

    def test_editBasicHTML(self):
        d = self._makeOne('foo')
        d.edit('html', BASIC_HTML)

        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( d.cooked_text, '\n  <h1>Not a lot here</h1>\n ' )

        # Since the format is html, the STX level operands should
        # have no effect.
        ct = d.CookedBody(stx_level=3, setlevel=1)
        self.assertEqual( d._stx_level, 1 )

    def test_editSimpleXHTML(self):
        d = self._makeOne('foo')
        d.edit('html', SIMPLE_XHTML)

        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.cooked_text, '\n  <h1>Not a lot here</h1>\n ')

    def test_UpperedHtml(self):
        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'TITLE IN TAG' )
        self.assertEqual( d.text.find('</BODY'), -1 )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_EntityInTitle(self):
        self.REQUEST['BODY'] = ENTITY_IN_TITLE
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.title, '&Auuml;rger' )

    def test_HtmlWithDoctype(self):
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Description(), 'Describe me' )

    def test_HtmlWithoutNewlines(self):
        self.REQUEST['BODY'] = ''.join((BASIC_HTML.split('\n')))
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )

    def test_EditPlainDocumentWithEmbeddedHTML(self):
        d = self._makeOne('foo')
        d.edit('structured-text', FAUX_HTML_LEADING_TEXT)
        fully_edited = d.cooked_text
        d._edit(FAUX_HTML_LEADING_TEXT)
        partly_edited = d.cooked_text
        self.assertEquals(fully_edited, partly_edited)

    def test_BigHtml(self):
        d = self._makeOne('foo')
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        self.REQUEST['BODY'] = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.CookedBody(), body )

    def test_BigHtml_via_upload(self):
        d = self._makeOne('foo')
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        html = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        _file = StringIO( html )
        d.edit(text_format='html', text='', file=_file)
        self.assertEqual( d.CookedBody(), body )

    def test_Htmltag_removal_and_formatchange(self):
        # Test for http://www.zope.org/Collectors/CMF/214
        d = self._makeOne('foo')
        quoted_html = html_quote(BASIC_HTML)

        # Put HTML into a plain text document
        d.edit(text_format='plain', text=BASIC_HTML)
        new_body = d.CookedBody()
        self.failIf(new_body==BASIC_HTML)
        self.failUnless(new_body.startswith(quoted_html[:5]))

        # Now we change the format. The body *must* change because
        # the format change will trigger re-cooking
        old_body = d.CookedBody()
        d.setFormat('html')
        new_body = d.CookedBody()
        self.failIf(old_body==new_body)
        self.failIf(new_body==BASIC_HTML)

    def test_Html_Fragment(self):
        # Test that edits with HTML fragments behave nicely
        FRAGMENT = '<div id="placeholder">CONTENT</div>'
        d = self._makeOne('foo')
        d.edit(text_format='html', text=FRAGMENT)
        self.assertEqual( d.CookedBody(), FRAGMENT )
        self.assertEqual( d.get_size(), len(FRAGMENT) )

    def test_plain_text(self):
        # test that plain text forrmat works
        PLAIN_TEXT = '*some plain text*\nwith a newline'
        d = self._makeOne('foo')
        d.edit(text_format='plain', text=PLAIN_TEXT)
        self.assertEqual( d.CookedBody(),
                          '*some plain text*<br />with a newline')
        self.assertEqual( d.get_size(), len(PLAIN_TEXT) )

    def test_EditStructuredTextWithHTML(self):
        d = self._makeOne('foo')
        d.edit(text_format='structured-text', text=STX_WITH_HTML)

        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.get_size(), len(STX_WITH_HTML) )

    def test_StructuredText(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )
        self.failUnless( d.CookedBody().find('<h1') >= 0 )

        # Make sure extra HTML is NOT found
        self.failUnless( d.cooked_text.find('<title>') < 0 )
        self.failUnless( d.cooked_text.find('<body>') < 0 )

        # test subject/keyword headers
        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_STX_Levels(self):
        d = self._makeOne('foo')
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody()
        self.failUnless( d.CookedBody().find('<h1') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2, setlevel=1)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 2 )

        ct = d.CookedBody()
        self.assertEqual( d._stx_level, 2 )
        self.failIf( d.CookedBody().find('<h1') >= 0 )
        self.failUnless( d.CookedBody().find('<h2') >= 0 )

    def test_Init(self):
        self.REQUEST['BODY']=BASIC_STRUCTUREDTEXT
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

        d = self._makeOne('foo', text='')
        self.REQUEST['BODY']=BASIC_HTML
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( len(d.Contributors()), 3 )

        d = self._makeOne('foo', text_format='structured-text',
                          title='Foodoc')
        self.assertEqual( d.text, '' )
        self.failIf( d.CookedBody() )
        self.assertEqual( d.title, 'Foodoc' )
        self.assertEqual( d.Format(), 'text/plain' )

        # Tracker issue 435:  initial text is not cooked.
        d = self._makeOne('foo', text_format='structured-text',
                          text=STX_NO_HEADERS)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS )
        self.failUnless( d.CookedBody() )
        self.assertEqual( d.Format(), 'text/plain' )

    def test_STX_NoHeaders( self ):
        self.REQUEST['BODY']=STX_NO_HEADERS
        d = self._makeOne('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )

        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )

    def test_STX_NoHeaders_but_colon( self ):
        d = self._makeOne('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.edit(text_format='structured-text', text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )

    def test_ZMI_edit( self ):
        d = self._makeOne('foo')
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.manage_editDocument( text_format='structured-text'
                             , text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )

    def test_Format_methods(self):
        d = self._makeOne('foo')
        d.setFormat('plain')
        self.assertEqual( d.text_format, 'plain' )
        self.assertEqual( d.Format(), 'text/plain' )
        d.setFormat( d.Format() )
        self.assertEqual( d.text_format, 'plain' )

        d.setFormat('structured-text')
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d.Format(), 'text/plain' )
        d.setFormat( d.Format() )
        self.assertEqual( d.text_format, 'structured-text' )

        d.setFormat('html')
        self.assertEqual( d.text_format, 'html' )
        self.assertEqual( d.Format(), 'text/html' )
        d.setFormat( d.Format() )
        self.assertEqual( d.text_format, 'html' )

        d.setFormat('foo')
        self.assertEqual( d.text_format, 'structured-text' )

    def test_default_format( self ):
        d = self._makeOne('foo', text='')

        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.text_format, 'structured-text' )


class DocumentFTPGetTests(RequestTestBase):

    def setUp(self):
        RequestTest.setUp(self)
        self.site = DummySite('site').__of__(self.root)

    def testHTML( self ):
        self.REQUEST['BODY']=BASIC_HTML

        ttool = self.site._setObject( 'portal_types', TypesTool() )
        fti = FTIDATA_CMF15[0].copy()
        del fti['id']
        ttool._setObject( 'Document', FTI('Document', **fti) )

        zpt = self.site._setObject( 'source_html',
                                    ZopePageTemplate('source_html') )
        dir = abspath( dirname(utils.__file__) )
        _file = path_join(dir, 'skins', 'zpt_content', 'source_html.pt')
        data = open(_file, 'r').read()
        zpt.write(data)

        d = self._makeOne('foo')
        d._setPortalTypeName('Document')
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )
        simple_lines = rnlinesplit.split( BASIC_HTML )
        get_lines = rnlinesplit.split( d.manage_FTPget() )

        # strip off headers
        meta_pattern = compile( r'meta name="([a-z]*)" '
                                 + r'content="([a-z]*)"'
                                 )
        title_pattern = compile( r'<title>(.*)</title>' )
        simple_headers = []
        while simple_lines and simple_lines[0] != '<BODY>':
            header = simple_lines[0].strip().lower()
            match = meta_pattern.search( header )
            if match:
                simple_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    simple_headers.append( ( 'title', match.group(1) ) )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0] != '<BODY>':
            header = get_lines[0].strip().lower()
            match = meta_pattern.search( header )
            if match:
                get_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    get_headers.append( ( 'title', match.group(1) ) )
            get_lines = get_lines[1:]

        self.assertEqual( get_lines, simple_lines )

        self.failUnless( get_headers )
        self.failUnless( simple_headers )
        self.failUnless( len( get_headers ) >= len( simple_headers ) )

        for header in simple_headers:
            self.failUnless( header in get_headers )

        body1 = d.EditableBody()
        self.REQUEST['BODY'] = d.manage_FTPget()
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.EditableBody(), body1 )

    def testSTX( self ):
        self.REQUEST['BODY']=SIMPLE_STRUCTUREDTEXT
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )

        get_text = d.manage_FTPget()
        simple_lines = rnlinesplit.split( SIMPLE_STRUCTUREDTEXT )
        get_lines = rnlinesplit.split( get_text )

        # strip off headers
        simple_headers = []
        while simple_lines and simple_lines[0]:
            simple_headers.append( simple_lines[0] )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0]:
            get_headers.append( get_lines[0] )
            get_lines = get_lines[1:]

        self.assertEqual( get_lines, simple_lines )

        for header in simple_headers:
            self.failUnless( header in get_headers )


class DocumentPUTTests(RequestTestBase):

    def test_PUTBasicHTML(self):
        self.REQUEST['BODY'] = BASIC_HTML
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'Title in tag' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.assertEqual( d.Contributors()[-1],
                          'Benotz, Larry J (larry@benotz.stuff)' )
        self.assertEqual( d.cooked_text, '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( r.status, 204 )

        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_PUTSimpleXHTML(self):
        self.REQUEST['BODY'] = SIMPLE_XHTML
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( d.cooked_text, '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( r.status, 204 )

    def test_PutStructuredTextWithHTML(self):
        self.REQUEST['BODY'] = STX_WITH_HTML
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutStructuredText(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutHtmlWithDoctype(self):
        html = '%s\n\n  \n   %s' % (DOCTYPE, BASIC_HTML)
        self.REQUEST['BODY'] = html
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )

    def test_PutHtmlWithoutMetadata(self):
        html = HTML_TEMPLATE % {'title': 'Foo', 'body': 'Bar'}
        self.REQUEST['BODY'] = html
        d = self._makeOne('foo')
        r = d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), 'Foo' )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Subject(), () )
        self.assertEqual( d.Contributors(), () )
        self.assertEqual( d.EffectiveDate(), 'None' )
        self.assertEqual( d.ExpirationDate(), 'None' )
        self.assertEqual( d.Language(), '' )
        self.assertEqual( d.Rights(), '' )
        self.assertEqual( r.status, 204 )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DocumentTests),
        unittest.makeSuite(DocumentFTPGetTests),
        unittest.makeSuite(DocumentPUTTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
