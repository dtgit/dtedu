/*****************************************************************************
 *
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/
/*extern DummyLogger noContextMenu */
// $Id: kupuploneinit.js 51114 2008-01-29 16:13:48Z duncan $

function initPloneKupu(editorId) {
    var prefix = '#'+editorId+' ';

    var iframe = getFromSelector(prefix+'iframe.kupu-editor-iframe');
    if (iframe._kupuIsInitialized) {
	    return window.kupu;
    };
    iframe._kupuIsInitialized = true;
    var textarea = getFromSelector(prefix+'textarea.kupu-editor-textarea');
    var form = textarea.form;
    var initialtext = textarea.value || (_SARISSA_IS_IE?'<p></p>':'<p><br></p>');

    // first we create a logger
    var l = new DummyLogger();

    // now some config values
    var conf = loadDictFromXML(document, prefix+'xml.kupuconfig');

    // the we create the document, hand it over the id of the iframe
    var doc = new KupuDocument(iframe);

    // now we can create the controller
    var kupu = (window.kupu = new KupuEditor(doc, conf, l));
    kupu.setHTMLBody(initialtext);

    // now we can create a UI object which we can use from the UI
    var ui = new KupuUI(prefix+'select.kupu-tb-styles');
    window.kupuui = ui;

    // the ui must be registered to the editor like a tool so it can be notified
    // of state changes
    kupu.registerTool('ui', ui); // XXX Should this be a different method?

    // function that returns a function to execute a button command
    var execCommand = function(cmd) {
        return function(button, editor) {
            editor.execCommand(cmd);
        };
    };

    var boldchecker = parentWithStyleChecker(['b', 'strong'],
                                             'font-weight', 'bold');
    var boldbutton = new KupuStateButton(prefix+'button.kupu-bold',
                                         execCommand('bold'),
                                         boldchecker,
                                         'kupu-bold',
                                         'kupu-bold-pressed');
    kupu.registerTool('boldbutton', boldbutton);

    var italicschecker = parentWithStyleChecker(['i', 'em'],
                                                'font-style', 'italic');
    var italicsbutton = new KupuStateButton(prefix+'button.kupu-italic',
                                            execCommand('italic'),
                                            italicschecker,
                                            'kupu-italic',
                                            'kupu-italic-pressed');
    kupu.registerTool('italicsbutton', italicsbutton);

    /* disabled
    var underlinechecker = parentWithStyleChecker(['u']);
    var underlinebutton = new KupuStateButton(prefix+'button.kupu-underline',
                                              execCommand('underline'),
                                              underlinechecker,
                                              'kupu-underline',
                                              'kupu-underline-pressed');
    kupu.registerTool('underlinebutton', underlinebutton);
    */

    var subscriptchecker = parentWithStyleChecker(['sub']);
    var subscriptbutton = new KupuStateButton(prefix+'button.kupu-subscript',
                                              execCommand('subscript'),
                                              subscriptchecker,
                                              'kupu-subscript',
                                              'kupu-subscript-pressed');
    kupu.registerTool('subscriptbutton', subscriptbutton);

    var superscriptchecker = parentWithStyleChecker(['super', 'sup']);
    var superscriptbutton = new KupuStateButton(prefix+'button.kupu-superscript',
                                                execCommand('superscript'),
                                                superscriptchecker,
                                                'kupu-superscript',
                                                'kupu-superscript-pressed');
    kupu.registerTool('superscriptbutton', superscriptbutton);

    var justifyleftbutton = new KupuButton(prefix+'button.kupu-justifyleft',
                                           execCommand('justifyleft'));
    kupu.registerTool('justifyleftbutton', justifyleftbutton);

    var justifycenterbutton = new KupuButton(prefix+'button.kupu-justifycenter',
                                             execCommand('justifycenter'));
    kupu.registerTool('justifycenterbutton', justifycenterbutton);

    var justifyrightbutton = new KupuButton(prefix+'button.kupu-justifyright',
                                            execCommand('justifyright'));
    kupu.registerTool('justifyrightbutton', justifyrightbutton);

    var outdentbutton = new KupuButton(prefix+'button.kupu-outdent', execCommand('outdent'));
    kupu.registerTool('outdentbutton', outdentbutton);

    var indentbutton = new KupuButton(prefix+'button.kupu-indent', execCommand('indent'));
    kupu.registerTool('indentbutton', indentbutton);

    var undobutton = new KupuButton(prefix+'button.kupu-undo', execCommand('undo'));
    kupu.registerTool('undobutton', undobutton);

    var redobutton = new KupuButton(prefix+'button.kupu-redo', execCommand('redo'));
    kupu.registerTool('redobutton', redobutton);

    var removeimagebutton = new KupuRemoveElementButton(prefix+'button.kupu-removeimage',
                                                        'img',
                                                        'kupu-removeimage');
    kupu.registerTool('removeimagebutton', removeimagebutton);

    var removelinkbutton = new KupuRemoveElementButton(prefix+'button.kupu-removelink',
                                                       'a',
                                                       'kupu-removelink');
    kupu.registerTool('removelinkbutton', removelinkbutton);

    // add some tools
    var colorchoosertool = new ColorchooserTool(prefix+'button.kupu-forecolor',
                                                prefix+'button.kupu-hilitecolor',
                                                prefix+'table.kupu-colorchooser');
    kupu.registerTool('colorchooser', colorchoosertool);

    var listtool = new ListTool(prefix+'button.kupu-insertunorderedlist',
                                prefix+'button.kupu-insertorderedlist',
                                prefix+'select.kupu-ulstyles',
                                prefix+'select.kupu-olstyles');
    kupu.registerTool('listtool', listtool);

    var definitionlisttool = new DefinitionListTool(prefix+'button.kupu-insertdefinitionlist');
    kupu.registerTool('definitionlisttool', definitionlisttool);

    var tabletool = new TableTool();
    kupu.registerTool('tabletool', tabletool);

    var anchortool = new AnchorTool();
    kupu.registerTool('anchortool', anchortool);

    var showpathtool = new ShowPathTool('kupu-showpath-field');
    kupu.registerTool('showpathtool', showpathtool);

    var sourceedittool = new SourceEditTool(prefix+'button.kupu-source',
                                            prefix+'textarea.kupu-editor-textarea');
    kupu.registerTool('sourceedittool', sourceedittool);

    var imagetool = noContextMenu(new ImageTool());
    kupu.registerTool('imagetool', imagetool);

    var linktool = noContextMenu(new LinkTool());
    kupu.registerTool('linktool', linktool);

    var zoom = new KupuZoomTool(prefix+'button.kupu-zoom',
                                prefix+'select.kupu-tb-styles',
                                prefix+'button.kupu-logo');
    kupu.registerTool('zoomtool', zoom);

    if (typeof KupuSpellChecker != 'undefined') {
        var spellchecker = new KupuSpellChecker('kupu-spellchecker-button',
                                                'kupu_library_tool/spellcheck');
        kupu.registerTool('spellchecker', spellchecker);
    } else {
        // hide the button when not available
        var sc = getFromSelector(prefix+'span.kupu-spellchecker-span');
        if (sc) sc.style.display = 'none';
    }

    // Use the generic beforeUnload handler if we have it:
    var beforeunloadTool = window.onbeforeunload && window.onbeforeunload.tool;
    if (beforeunloadTool) {
        var initialBody = kupu.getHTMLBody();
        beforeunloadTool.addHandler(function() {
            for (var n = textarea; n; n = n.parentNode) {
                if (n===document) {
                    return kupu.getHTMLBody() != initialBody;
                }
            }
            return false; /* textarea is no longer in the document */
        });
        beforeunloadTool.chkId[textarea.id] = function() { return false; };
        beforeunloadTool.addForm(form);
    }
    // Patch for bad AT format pulldown.
    var fmtname = textarea.name+'_text_format';
    var pulldown = form[fmtname];
    if (pulldown && pulldown.type=='select-one') {
        for (var i=0 ; i < pulldown.length; i++) {
            var opt = pulldown.options[i];
            opt.selected = opt.defaultSelected = (opt.value=='text/html');
        }
        pulldown.disabled = true;
        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = fmtname;
        hidden.value = 'text/html';
        pulldown.parentNode.appendChild(hidden);
    };

    // Drawers...

    // Function that returns function to open a drawer
    var opendrawer = function(drawerid) {
        return function(button, editor) {
            drawertool.openDrawer(prefix+drawerid);
        };
    };

    var imagelibdrawerbutton = new KupuButton(prefix+'button.kupu-image',
                                              opendrawer('imagelibdrawer'));
    kupu.registerTool('imagelibdrawerbutton', imagelibdrawerbutton);

    var linklibdrawerbutton = new KupuButton(prefix+'button.kupu-inthyperlink',
                                             opendrawer('linklibdrawer'));
    kupu.registerTool('linklibdrawerbutton', linklibdrawerbutton);

    var linkdrawerbutton = new KupuButton(prefix+'button.kupu-exthyperlink',
                                          opendrawer('linkdrawer'));
    kupu.registerTool('linkdrawerbutton', linkdrawerbutton);

    var anchorbutton = new KupuButton(prefix+'button.kupu-anchors',
                                      opendrawer('anchordrawer'));
    kupu.registerTool('anchorbutton', anchorbutton);

    var tabledrawerbutton = new KupuButton(prefix+'button.kupu-table',
                                           opendrawer('tabledrawer'));
    kupu.registerTool('tabledrawerbutton', tabledrawerbutton);

    // create some drawers, drawers are some sort of popups that appear when a
    // toolbar button is clicked
    var drawertool = window.drawertool || new DrawerTool();
    window.drawertool = drawertool;
    kupu.registerTool('drawertool', drawertool);

    var drawerparent = prefix+'div.kupu-librarydrawer-parent';
    var xsl_uri = conf.xsl_uri;
    var link_resource = conf.link_resource;
    var image_resource = conf.image_resource;
    var lib_prefix = conf.lib_prefix;
    var search_prefix = conf.search_prefix;
    var select_prefix = conf.select_prefix;
    var linklibdrawer = new LinkLibraryDrawer(linktool,
                                              xsl_uri,
                                              lib_prefix+link_resource,
                                              search_prefix+link_resource,
                                              drawerparent,
                                              select_prefix+link_resource);
    drawertool.registerDrawer(prefix+'linklibdrawer', linklibdrawer, kupu);

    var imagelibdrawer = new ImageLibraryDrawer(imagetool,
                                                xsl_uri,
                                                lib_prefix+image_resource,
                                                search_prefix+image_resource,
                                                drawerparent,
                                                select_prefix+image_resource);
    drawertool.registerDrawer(prefix+'imagelibdrawer', imagelibdrawer, kupu);

    var linkdrawer = new LinkDrawer(prefix+'div.kupu-linkdrawer', linktool);
    drawertool.registerDrawer(prefix+'linkdrawer', linkdrawer, kupu);

    var anchordrawer = new AnchorDrawer(prefix+'div.kupu-anchordrawer', anchortool);
    drawertool.registerDrawer(prefix+'anchordrawer', anchordrawer, kupu);

    var tabledrawer = new TableDrawer(prefix+'div.kupu-tabledrawer', tabletool);
    drawertool.registerDrawer(prefix+'tabledrawer', tabledrawer, kupu);

    // register form submit handler, remove the drawer's contents before submitting
    // the form since it seems to crash IE if we leave them alone
    function prepareForm(event) {
        kupu.saveDataToField(this.form, this);
        var drawer = window.document.getElementById('kupu-librarydrawer');
        if (drawer) {
            drawer.parentNode.removeChild(drawer);
        }
    };
    addEventHandler(textarea.form, 'submit', prepareForm, textarea);

    function tabHandler(event) {
        event = event||window.event;
        if (event.keyCode!=9) { return; }
        if (!(/kupu-fulleditor-zoomed/.test(document.body.className))) {
            var form = textarea.form;
            var els = form.elements;
            var target;
            if (event.shiftKey) { // shift-tab goes backwards.
                for (var i = 0; i < els.length; i++) {
                    var el = els[i];
                    if (!el.disabled && el.offsetWidth && el.offsetHeight) {
                        target = el;
                    }
                    if (els[i]===textarea) break;
                }
            } else { // tab forwards
                for (var i = 0; i < els.length; i++) {
                    if (els[i]===textarea) break;
                }
                for (;i < els.length; i++) {
                    var el = els[i];
                    if (!el.disabled && el.offsetWidth && el.offsetHeight) {
                        target = el;
                        break;
                    }
                }
            }
            if (target) {
                window.focus();
                target.focus();
            } else { return; };
        }
        if (event.preventDefault) { event.preventDefault(); event.stopPropagation();}
        event.returnValue = false;
        return false;
    }
    var inner = kupu.getInnerDocument();
    kupu._addEventHandler(inner.documentElement, "keydown", tabHandler);

    kupu.initialize();
    return kupu;
};

// modify LinkDrawer so links don't have a target
LinkDrawer.prototype.target = '';
LinkLibraryDrawer.prototype.target = '';
if (!window.console) {
    window.console = new function() {
        this.log = function() {};
    };
}
