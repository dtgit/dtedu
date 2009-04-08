/*****************************************************************************
 *
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/

// $Id: test_kupuhelpers.js 49344 2007-12-04 16:24:14Z duncan $

function SelectionTestCase() {
    var visibleEmptyElements = ['IMG', 'BR', 'HR'];
    var blockElements = ['P', 'DIV'];

    this.setUp = function() {
        var iframe = document.getElementById('iframe');
        this.doc = iframe.contentWindow.document;
        this.body = this.doc.getElementsByTagName('body')[0];
        this.kupudoc = new KupuDocument(iframe);
        this.selection = this.kupudoc.getSelection();
        this.kupudoc.getWindow().focus();
    };

    this._MozillaPosition = function(element, offset, lastnode) {
        // this does not skip invisible whitespace
        var node = element.firstChild;
        for (var i=0; i < element.childNodes.length; i++) {
            if (node.nodeType == Node.TEXT_NODE) {
                var endcounts = !node.nextSibling &&
                         blockElements.contains(element.tagName.toUpperCase());
                if ((offset < node.data.length) ||
                    ((offset == node.data.length) && (!lastnode || endcounts))) {
                    return [node, offset];
                };
                if (endcounts) {
                    offset -= 1;
                };
                offset -= node.data.length;
            } else if (node.nodeType == Node.ELEMENT_NODE) {
                if (visibleEmptyElements.contains(node.tagName.toUpperCase())) {
                    if (offset > 0 && !node.nextSibling) {
                        offset -= 1;
                        i += 1;
                    };
                    if (offset == 0) {
                        return [element, i];
                    };
                    offset -= 1;
                } else {
                    position = this._MozillaPosition(node, offset, lastnode);
                    if (position[0]) {
                        return position;
                    };
                    offset = position[1];
                };
            };
            node = node.nextSibling;
        };
        return [node, offset];
    };

    this._setSelection = function(startOffset, startNextNode, endOffset,
        endNextNode, verificationString, ieskew, endskew) {
        var element = this.body;
        var innerSelection = this.selection.selection;
        if (innerSelection.createRange) {
            if (ieskew) {
                startOffset += ieskew;
                if (endskew) {
                    endOffset += endskew;
                } else {
                    endOffset += ieskew;
                }
            };
            var range = innerSelection.createRange();
            var endrange = innerSelection.createRange();
            range.moveToElementText(element);
            range.moveStart('character', startOffset);
            endrange.moveToElementText(element);
            endrange.moveStart('character', endOffset);
            range.setEndPoint('EndToStart', endrange);
            range.select();
        } else {
            var position = this._MozillaPosition(element, startOffset, startNextNode);
            var epos = null;
            if (startOffset != endOffset) {
                var epos = this._MozillaPosition(element, endOffset, endNextNode);
            }
            innerSelection.collapse(position[0], position[1]);
            if (epos) {
                innerSelection.extend(epos[0], epos[1]);
            };
        };
        this.assertEquals('"'+this.selection.toString().replace(/(\r|\n|\t)+/g, '')+'"',
                          '"'+verificationString+'"');
    };

    this._cleanHtml = function(s) {
        s = s.toLowerCase().replace(/[\r\n]/g, "");
        s = s.replace(/\>[ ]+\</g, "><");
        s = s.replace(/\/>/g, ">");
        s = s.replace(' style=""', "");
        s = s.replace(" style=''", "");
        s = s.replace(/ kupu-src="[^"]*"/, "");
        return s;
    };

    this.tearDown = function() {
        this.body.innerHTML = '';
    };
};

SelectionTestCase.prototype = new TestCase;

function KupuHelpersTestCase() {
    this.name = 'KupuHelpersTestCase';

    this.setUp = function() {
        var iframe = document.getElementById('iframe');
        this.doc = iframe.contentWindow.document;
        this.body = this.doc.getElementsByTagName('body')[0];
        this._testdiv = document.getElementById('testdiv');
    };
        
    this.testSelectSelectItem = function() {
        var select = this.doc.createElement('select');
        this.body.appendChild(select);
        var option = this.doc.createElement('option');
        option.value = 'foo';
        select.appendChild(option);
        var option2 = this.doc.createElement('option');
        option2.value = 'bar';
        select.appendChild(option2);

        this.assertEquals(select.selectedIndex, 0);
        var ret = selectSelectItem(select, 'bar');
        this.assertEquals(select.selectedIndex, 1);
        var ret = selectSelectItem(select, 'baz');
        this.assertEquals(select.selectedIndex, 0);
    };

    this.testArrayContains = function() {
        var array = [1, 2, 3];
        this.assert(array.contains(1));
        this.assert(array.contains(2));
        this.assertFalse(array.contains(4));
        this.assert(array.contains('1'));
        this.assertFalse(array.contains('1', 1));
    };

    this.testStringStrip = function() {
        // an empty string
        var str = "";
        this.assertEquals(str.strip(), str);
        // a string only containg whitespace
        str = " \n  \t ";
        this.assertEquals(str.strip(), "");
        // a string not containg any whitespaces
        str = "foo"
        this.assertEquals(str.strip(), str);
        // a word wrapped around whitespace
        str = "\n  foo \t  ";
        // a single character wrapped in whitespace
        str = "\n\t a \t\n";
        this.assertEquals(str.strip(), "a");
        // a string containing whitespace in the middle
        str = "foo bar baz";
        this.assertEquals(str.strip(), str);
        // a string containing spaces around it and in it
        str = " \t  foo bar\n baz  ";
        this.assertEquals(str.strip(), "foo bar\n baz");
        str = "  tu quoque Brute filie mee  ";
        this.assertEquals(str.strip(), "tu quoque Brute filie mee");
    };

    this.testLoadDictFromXML = function() {
        var dict = loadDictFromXML(document, 'xmlisland');
        this.assertEquals(dict['foo'], 'bar');
        this.assertEquals(dict['sna'], 'fu');
        for (var attr in dict) {
            this.assert(attr == 'foo' || attr == 'sna' || 
                            attr == 'some_int' || attr == 'nested' ||
                            attr == 'list');
        };
        this.assertEquals(dict['some_int'], 1);
        this.assertEquals(dict['nested']['foo'], 'bar');
        this.assertEquals(dict['list'][0], 0);
        this.assertEquals(dict['list'].length, 2);
    };

    this.testGetFromSelector = function() {
        data = '<div><span id="xspan" class="xyzzy"></span></div>';
        this._testdiv.innerHTML = data;
        node = getFromSelector("xspan");
        this.assertEquals(node && node.id, "xspan");
        node = getFromSelector("#testdiv span.xyzzy");
        this.assertEquals(node && node.id, "xspan");
        data = '<div><button class="xyzzy"></button><span id="xspan" class="foo xyzzy bar"></span></div>';
        this._testdiv.innerHTML = data;
        node = getFromSelector("#testdiv span.xyzzy");
        this.assertEquals(node && node.id, "xspan");
    };

    this.tearDown = function() {
        this.body.innerHTML = '';
        this._testdiv.innerHTML = '';
    };
};

KupuHelpersTestCase.prototype = new TestCase;

function KupuSelectionTestCase() {
    this.cleanbody = function() {
        var s = this.body.innerHTML.toLowerCase();
        s = s.replace(/<img([^\/>]*)\/>/g, '<img$1>');
        return s;
    }
    this.testReplaceWithNode = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        node = this.doc.createElement('img');
        this.selection.replaceWithNode(node, true);
        this.assertEquals(this.cleanbody(), '<p>foo <img> baz</p>');
    };

    this.testReplaceWithNodeTwice = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        node = this.doc.createElement('img');
        this.selection.replaceWithNode(node, true);
        this.selection.replaceWithNode(node, true);
        this.assertEquals(this.cleanbody(), '<p>foo <img> baz</p>');
    };

    this.testParentElementMissing = function() {
        this.body.innerHTML = '<p>foo <b>bar</b><img><img> baz</p>';
        // remove selection
        var selection = this.selection.selection;
        _SARISSA_IS_IE ? selection.empty() : selection.removeAllRanges();
        node = this.doc.getElementsByTagName('p')[0];
        this.assertEquals(this.selection.parentElement(), node);
    };

    this.testParentElementBold = function() {
        this.body.innerHTML = '<p>foo <b>xbar!</b><img/><img/> baz</p>';
        // select                        |bar|
        // kludged for opera which cannot do a selection involving the
        // first character of the <b> tag.
        this._setSelection(5, true, 8, true, 'bar');
        node = this.doc.getElementsByTagName('b')[0];
        this.assertEquals(this.selection.parentElement(), node);
    };

    this.testParentElementImg = function() {
        this.body.innerHTML = '<p>foo <b>bar</b><img/><img/> baz</p>';
        // select                              |<img/>|
        this._setSelection(7, true, 8, false, '');
        node = this.doc.getElementsByTagName('img')[0];
        this.assertEquals(this.selection.parentElement(), node);
    };
    opera_is_broken(this, 'testParentElementImg');

    this.testParentElementImgSpecial = function() {
        this.body.innerHTML = '<p>foo <a><img/></a></p>';
        // select                       |<img/>|
        this._setSelection(4, true, 5, null, '');
        node = this.doc.getElementsByTagName('img')[0];
        foo = this.selection.parentElement();
        this.assertEquals(this.selection.parentElement(), node);
    };
    opera_is_broken(this, 'testParentElementImgSpecial');

    this.testParentElementMixed = function() {
        this.body.innerHTML = '<p>foo <b>bar</b><img><img> baz</p>';
        // select                        |ar</b><img><img> b|
        this._setSelection(5, null, 11, null, 'ar b');
        node = this.doc.getElementsByTagName('p')[0];
        this.assertEquals(this.selection.parentElement(), node);
    };

    this.testParentElement_r9516 = function() {
        this.body.innerHTML = '<p>foo <b>bar</b><img/></p><p>baz</p>';
        // select                              |<img/></p><p>baz|
        this._setSelection(6, true, 12, false, 'rbaz');
        node = this.doc.getElementsByTagName('body')[0];
        this.assertEquals(this.selection.parentElement(), node);
    };

    this.testGetContentLength = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.assertEquals(this.selection.getContentLength(), 3);
    };

    this.testToString = function() {
        this.body.innerHTML = '<p>foo <b>bar</b> baz</p>';
        var selection = this.kupudoc.getSelection();
        selection.selectNodeContents(this.body);
        this.assertEquals('['+selection.toString()+']', '[foo bar baz]');
        selection.selectNodeContents(this.body.firstChild.childNodes[1]);
        this.assertEquals(selection.toString(), 'bar');
    };
    opera_is_broken(this, 'testToString');
};

KupuSelectionTestCase.prototype = new SelectionTestCase;
