/*****************************************************************************
 *
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/

function KupuUITestCase() {
    this.name = 'KupuUITestCase';
    SelectionTestCase.apply(this);
    this.base_setUp = this.setUp;

    this.setUp = function() {
        this.base_setUp();
        this.editor = new KupuEditor(this.kupudoc, {}, null);
        this.preserve = document.getElementById('preserve-this-div').innerHTML;
        this.ui = new KupuUI('kupu-tb-styles');
        this.ui.editor = this.editor;
    };

    this.tearDown = function() {
        document.getElementById('preserve-this-div').innerHTML = this.preserve;
    };

    this._selectTableCells = function(indices, verificationString) {
        var tableNodes = this.body.getElementsByTagName("table");
        var cellNodes = [];
        
        var curNode = null;
        var direction = null;
        var foundNext = null;
        
        for(var i = 0; i < tableNodes.length; i = i + 1) {
            curNode = tableNodes[i].firstChild;
            //what if no child?
            direction = 'down';
            
            while( curNode.nodeName.toLowerCase() != 'table' ) {
                /*if(indices[1]==2) {
                   alert(curNode.nodeName);
                   alert(curNode.innerHTML);
                }*/
                if( curNode.nodeName.toLowerCase() == 'td' || curNode.nodeName.toLowerCase() == 'th' ) {
                    cellNodes.push(curNode);
                };
            
                foundNext = false;
                while( !foundNext && curNode.nodeName.toLowerCase() != 'table' ) {
                    if( direction == 'right' ) {
                        if( curNode.nextSibling ) {
                            curNode = curNode.nextSibling;
                            direction = 'down';
                            foundNext = true;
                        } else {
                            curNode = curNode.parentNode;
                        };
                    } else if( direction == 'down' ) {
                        if( curNode.firstChild ) {
                            curNode = curNode.firstChild;
                            foundNext = true;
                        } else {
                            direction = 'right';
                        };
                    };
                };
            };
        }; 

        this.selection.selection.removeAllRanges();
        for(var i = 0; i < indices.length; i = i + 1) {
            var range = this.doc.createRange();
            range.selectNode(cellNodes[indices[i]]);
            this.selection.selection.addRange(range);
        };
        this.assertEquals('"'+this.selection.toString().replace(/\r|\n/g, '')+'"',
                          '"'+verificationString+'"');
    };

    this.test_updateState = function() {
        this.body.innerHTML = '<p>foo</p><pre>bar</pre><p>baz</p>';
        var node = this.body.getElementsByTagName('pre')[0];
        this.ui.cleanStyles();
        this.ui.enableOptions(false);
        this.ui.tsselect.selectedIndex = 0;
        this.assertEquals(this.ui.tsselect.selectedIndex, 0);
        this.ui.updateState(node);
        this.assertEquals(this.ui.tsselect.selectedIndex, 3);
    };

    this.updateStateTest = function(html, start, end, verify, ieskew, label) {
        this.body.innerHTML = html;
        this.ui.cleanStyles();
        this.ui.enableOptions(false);
        this._setSelection(start, null, end, null, verify, ieskew);
        node = this.editor.getSelectedNode();
        this.ui.updateState(node);
        var select = this.ui.tsselect;
        this.assertEquals(select.options[select.selectedIndex].text, label);
    };
    this.test_updateState2 = function() {
        this.updateStateTest('<table><tr><td>foo</td><td class="odd">bar</td></tr></table>',
            1, 3, 'oo', 1, "Plain Cell");
    };

    this.test_updateState3 = function() {
        this.updateStateTest('<table><tr><td>foo</td><td class="odd">bar</td></tr></table>',
            4, 6, 'ar', 2, "Odd Cell");
    };

    this.test_updateState4 = function() {
        this.updateStateTest('<table><tr><td>foo<span class="highlight">baz</span></td></tr></table>',
            4, 6, 'az', 1, "Highlight");
    }
    
    this.test_updateState5 = function() {
        this.updateStateTest('<table><tr><td>foo<div class="Caption">baz</div></td></tr></table>',
            4, 6, 'az', 2, "Caption");
    }

    this.test_updateState6 = function() {
        this.updateStateTest('<p>foo</p><div class="other">baz</div>',
            5, 7, 'az', 0, "Other: div other");
    }

    this.test_updateState7 = function() {
        this.updateStateTest('<p>foo</p><div class="other">baz</div>',
            1, 7, 'oobaz', 0, "Mixed styles");
    }
    opera_is_broken(this, 'test_updateState7');

    this.test_setTextStyle = function() {
        this.body.innerHTML = '<p>foo</p><p>bar</p><p>baz</p>';
        // select                          |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.ui.setTextStyle('h1');
        this.assertEquals(this._cleanHtml(this.body.innerHTML),
                          '<p>foo</p><h1>bar</h1><p>baz</p>');
    };
    
    this.test_setTextStyle_ParaStyle_SingleTableCell = function() {
        //Apply a paragraph style inside a table cell 
        var data = '<table><tbody><tr><td>bar</td></tr></tbody></table>';
        var expected =  '<table><tbody><tr><td><h1 class="te st">bar</h1></td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(0, null, 3, null, 'bar', 1);
        this.ui.setTextStyle('h1|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };

    this.test_removeTextStyle_ParaStyle_SingleTableCell = function() {
        //Remove a paragraph style inside a table cell 
        var data = '<table><tbody><tr><td>foo<h1 class="te st">bar</h1>baz</td></tr></tbody></table>';
        var expected =  '<table><tbody><tr><td>foo<br>bar<br>baz</td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(4, null, 6, null, 'ar', 2);
        this.ui.setTextStyle('');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };

    this.test_removeTextStyle_SpanStyle_SingleTableCell = function() {
        //Remove a paragraph style inside a table cell 
        var data = '<table><tbody><tr><td>foo<span class="te st">bar</span>baz</td></tr></tbody></table>';
        var expected =  '<table><tbody><tr><td>foobarbaz</td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(3, null, 6, null, 'bar', 1);
        this.ui.setTextStyle('');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };

    this.test_removeTextStyle_NoStyle = function() {
        //Remove a paragraph style when there isn't one 
        var data = 'hello world';
        var expected =  'hello world';
        this.body.innerHTML = data;
        this._setSelection(3, null, 6, null, 'lo ', 0);
        this.ui.setTextStyle('');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };

    this.test_setTextStyle_TableRow = function() {
        //Apply a table row style inside a table cell 
        var data = '<table><tbody><tr><td>foo</td><td>bar</td></tr></tbody></table>';
        var expected =  '<table><tbody><tr class="te st"><td>foo</td><td>bar</td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(1, null, 5, null, 'ooba', 1, 2);
        this.ui.setTextStyle('tr|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };
    
    this.test_setTextStyle_TableRow2 = function() {
        //Apply a table row style across 2 rows 
        var data = '<table><tbody><tr><td>foo</td></tr><tr><td>bar</td></tr></tbody></table>';
        var expected =  '<table><tbody><tr class="te st"><td>foo</td></tr><tr class="te st"><td>bar</td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(1, null, 5, null, 'ooba', 1, 2);
        this.ui.setTextStyle('tr|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };

    this.test_setTextStyle_ParaStyleThenCellStyle_SingleTableCell = function() {
        //Change the paragraph style inside a table cell, then change the cell
        //style to a td with a class
        var data = '<table><tbody><tr><td>bar</td></tr></tbody></table>';
        var expected = '<table><tbody><tr><td><div class="te st">bar</div></td></tr></tbody></table>';
        var withcellstyle = '<table><tbody><tr><td class="te st"><div class="te st">bar</div></td></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(0, null, 3, null, 'bar', 1);
        this.ui.setTextStyle('div|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
        this._setSelection(0, null, 3, null, 'bar', 1);
        this.ui.setTextStyle('td|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), withcellstyle);
    };
    opera_is_broken(this, 'test_setTextStyle_ParaStyleThenCellStyle_SingleTableCell');

    this.test_setTextStyle_TableHeaderThenParaStyle_SingleTableCell = function() {
        //Apply a table header style to a cell, then a paragraph style
        data = '<table><tbody><tr><td>bar</td></tr></tbody></table>';
        expected = '<table><tbody><tr><th class="te st">bar</th></tr></tbody></table>';
        withblockstyle = '<table><tbody><tr><th class="te st"><div class="te st">bar</div></th></tr></tbody></table>';
        this.body.innerHTML = data;
        this._setSelection(0, null, 3, null, 'bar', 1);
        this.ui.setTextStyle('th|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
        this._setSelection(0, null, 3, null, 'bar', 1);
        this.ui.setTextStyle('div|te st');
        if (_SARISSA_IS_IE) {
            this.assertEquals(this._cleanHtml(this.body.innerHTML), withblockstyle);
        } else {
            // Firefox doesn't give us the answer we want
            this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
        }
    };
    
    this.test_setTextStyle_ParaStyle_AdjacentCells = function() {
        //Change the paragraph style including *class*, when the selection
        //covers two adjacent table cells
        data = '<table><tbody><tr><td>foo</td><td>bar</td></tr></tbody></table>';
        expected = '<table><tbody><tr><td><h1 class="te st">foo</h1></td><td><h1 class="te st">bar</h1></td></tr></tbody></table>';
        this.body.innerHTML = data;
        if( _SARISSA_IS_IE ) {
            this._setSelection(1, null, 8, null, 'foobar');
        } else {
            this._selectTableCells([0,1],'foo\tbar');
        };
        this.ui.setTextStyle('h1|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };
    opera_is_broken(this, 'test_setTextStyle_ParaStyle_AdjacentCells');

    this.test_setTextStyle_SetCellStyle_Column = function() {
        //Apply a table cell (td) style, *with class*, on a column of cells --
        //only available with Mozilla
        data = '<table><tbody><tr><td>foo</td><td>foz</td></tr><tr><td>bar</td><td>baz</td></tr></tbody></table>'; 
        expected = '<table><tbody><tr><td class="te st">foo</td><td>foz</td></tr><tr><td class="te st">bar</td><td>baz</td></tr></tbody></table>'

        this.body.innerHTML = data; 
        this._selectTableCells([0,2],'foo\tbar');
        this.ui.setTextStyle('td|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };
    opera_is_broken(this, 'test_setTextStyle_SetCellStyle_Column');
    ie_is_broken(this, 'test_setTextStyle_SetCellStyle_Column');

    this.test_setTextStyle_ParaStyle_Column = function() {
        //Apply a paragraph style, *with class*, on a column of cells -- only
        //available with Mozilla
        data = '<table><tbody><tr><td>foo</td><td>foz</td></tr><tr><td>bar</td><td>baz</td></tr></tbody></table>';
        expected = '<table><tbody><tr><td><h1 class="te st">foo</h1></td><td>foz</td></tr><tr><td><h1 class="te st">bar</h1></td><td>baz</td></tr></tbody></table>'
        this.body.innerHTML = data;
        this._selectTableCells([0,2],'foo\tbar');
        this.ui.setTextStyle('h1|te st');
        this.assertEquals(this._cleanHtml(this.body.innerHTML), expected);
    };
    opera_is_broken(this, 'test_setTextStyle_ParaStyle_Column');
    ie_is_broken(this, 'test_setTextStyle_ParaStyle_Column');

    this.test_setTextStyleReplacingDiv = function() {
        this.body.innerHTML = '<p>foo</p><div>bar</div><p>baz</p>';
        // select                            |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.ui.setTextStyle('h1');
        this.assertEquals(this._cleanHtml(this.body.innerHTML),
                          '<p>foo</p><h1>bar</h1><p>baz</p>');
    };
};

KupuUITestCase.prototype = new SelectionTestCase;

function ImageToolTestCase() {
    this.name = 'ImageToolTestCase';
    SelectionTestCase.apply(this);
    this.base_setUp = this.setUp;

    this.setUp = function() {
        this.base_setUp();
        this.editor = new KupuEditor(this.kupudoc, {}, new DummyLogger());
        this.editor._initialized = true;
        this.imagetool = new ImageTool();
        this.imagetool.editor = this.editor;
    };

    this.test_createImage = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.imagetool.createImage('bar.png');
        this.assertEquals(this._cleanHtml(this.body.innerHTML),
                          '<p>foo <img src="bar.png"> baz</p>');
    };

    this.test_createImageFull = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.imagetool.createImage('bar.png', 'spam', 'image-inline');
        var nodes = this.body.getElementsByTagName('img');
        this.assertEquals(nodes.length, 1);
        this.assertEquals(nodes[0].className, 'image-inline');
        this.assertEquals(nodes[0].alt, 'spam');
    };
};

ImageToolTestCase.prototype = new SelectionTestCase;

function LinkToolTestCase() {
    this.name = 'LinkToolTestCase';
    SelectionTestCase.apply(this);
    this.base_setUp = this.setUp;

    this.setUp = function() {
        this.base_setUp();
        this.editor = new KupuEditor(this.kupudoc, {}, new DummyLogger());
        this.editor._initialized = true;
        this.linktool = new LinkTool();
        this.linktool.editor = this.editor;
    };

    this.test_createLink = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.linktool.createLink('http://www.example.org');
        this.assertEquals(this._cleanHtml(this.body.innerHTML),
                          '<p>foo <a href="http://www.example.org">bar</a> baz</p>');
    };

    this.test_createLinkEmpty = function() {
        this.body.innerHTML = '<p>foo bar baz</p>';
        // select                    |bar|
        this._setSelection(4, null, 7, null, 'bar');
        this.linktool.createLink('');
        this.assertEquals(this._cleanHtml(this.body.innerHTML),
                          '<p>foo bar baz</p>');
    };
};

LinkToolTestCase.prototype = new SelectionTestCase;
