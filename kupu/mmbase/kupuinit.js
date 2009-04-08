/*
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/

// $Id: kupuinit.js,v 1.21 2005/09/27 18:26:52 michiel Exp $

//----------------------------------------------------------------------------
// MMBase initialization for it's kupu
//----------------------------------------------------------------------------

// somewhy, IE needs this:
var kupu;



function initKupu(iframe) {
    // first we create a logger
    var l = new PlainLogger('kupu-toolbox-debuglog', 5);

    // now some config values
    var conf = loadDictFromXML(document, 'kupuconfig');

    // the we create the document, hand it over the id of the iframe
    var doc = new KupuDocument(iframe);

    // now we can create the controller
    var kupu = new KupuEditor(doc, conf, l);

    var contextmenu = new ContextMenu();
    kupu.setContextMenu(contextmenu);

    // now we can create a UI object which we can use from the UI
    var ui = new KupuUI('kupu-tb-styles');

    // the ui must be registered to the editor like a tool so it can be notified
    // of state changes
    kupu.registerTool('ui', ui); // XXX Should this be a different method?

    // add the buttons to the toolbar
    var savebuttonfunc = function(button, editor) {saveNode(button, editor);};
    var savebutton = new KupuButton('kupu-save-button', savebuttonfunc);
    kupu.registerTool('savebutton', savebutton);

    // function that returns a function to execute a button command
    var execCommand = function(cmd) {
        return function(button, editor) {
            editor.execCommand(cmd);
        };
    };

    var boldchecker = parentWithStyleChecker(['b', 'strong'], null, null, "bold");
    var boldbutton = new KupuStateButton('kupu-bold-button', execCommand('bold'), boldchecker, 'kupu-bold', 'kupu-bold-pressed');
    kupu.registerTool('boldbutton', boldbutton);

    var italicschecker = parentWithStyleChecker(['i', 'em'], null, null, 'italic');
    var italicsbutton = new KupuStateButton('kupu-italic-button', execCommand('italic'), italicschecker, 'kupu-italic', 'kupu-italic-pressed');
    kupu.registerTool('italicsbutton', italicsbutton);


    var subscriptchecker = parentWithStyleChecker(['sub'], null, null, 'subscript');
    var subscriptbutton = new KupuStateButton('kupu-subscript-button', execCommand('subscript'), subscriptchecker, 'kupu-subscript', 'kupu-subscript-pressed');
    kupu.registerTool('subscriptbutton', subscriptbutton);

    var superscriptchecker = parentWithStyleChecker(['super', 'sup'], null, null, 'superscript');
    var superscriptbutton = new KupuStateButton('kupu-superscript-button', execCommand('superscript'), superscriptchecker, 'kupu-superscript', 'kupu-superscript-pressed');
    kupu.registerTool('superscriptbutton', superscriptbutton);

    var undobutton = new KupuButton('kupu-undo-button', execCommand('undo'));
    kupu.registerTool('undobutton', undobutton);

    var redobutton = new KupuButton('kupu-redo-button', execCommand('redo'));
    kupu.registerTool('redobutton', redobutton);

    var removeimagebutton = new KupuRemoveElementButton('kupu-removeimage-button',
                                                        'img',
                                                        'kupu-removeimage');
    kupu.registerTool('removeimagebutton', removeimagebutton);

    var removelinkbutton = new KupuRemoveElementButton('kupu-removelink-button',
                                                       'a',
                                                       'kupu-removelink');
    kupu.registerTool('removelinkbutton', removelinkbutton);

    var removedivbutton = new KupuRemoveElementButton('kupu-removediv-button', 'div', 'kupu-removediv');
    kupu.registerTool('removedivbutton', removedivbutton);

    var listtool = new ListTool('kupu-list-ul-addbutton', 'kupu-list-ol-addbutton', 'kupu-ulstyles', 'kupu-olstyles');
    kupu.registerTool('listtool', listtool);


    var linktool = new LinkTool();
    // remove 'create link' from context menu, it doesn't work, and there are 2 wokring methods.
    linktool.createContextMenuElements = function(selNode, event) {
        var ret = [];
        var link = linktool.editor.getNearestParentOfType(selNode, 'a');
        if (link) {
            ret.push(new ContextMenuElement(_('Delete link'), linktool.deleteLink, linktool));
        };
        return ret;
    };
    kupu.registerTool('linktool', linktool);
    var linktoolbox = new LinkToolBox("kupu-link-input", "kupu-link-button", 'kupu-toolbox-links', 'kupu-toolbox', 'kupu-toolbox-active');
    linktool.registerToolBox('linktoolbox', linktoolbox);

    var imagetool = new ImageTool();
    // remove 'create image' from context menu, it doesn't work, and there are 2 wokring methods.
    imagetool.createContextMenuElements = function(selNode, event) {
        return [];
    };
    kupu.registerTool('imagetool', imagetool);
    var imagetoolbox = new ImageToolBox('kupu-image-input', 'kupu-image-addbutton',
                                        'kupu-image-float-select', 'kupu-toolbox-images',  'kupu-toolbox', 'kupu-toolbox-active');
    imagetool.registerToolBox('imagetoolbox', imagetoolbox);

    var tabletool = new TableTool();
    kupu.registerTool('tabletool', tabletool);
    var tabletoolbox = new TableToolBox('kupu-toolbox-addtable',
        'kupu-toolbox-edittable', 'kupu-table-newrows', 'kupu-table-newcols',
        'kupu-table-makeheader', 'kupu-table-classchooser',
        'kupu-table-alignchooser', 'kupu-table-addtable-button',
        'kupu-table-addrow-button', 'kupu-table-delrow-button',
        'kupu-table-addcolumn-button', 'kupu-table-delcolumn-button',
        'kupu-table-fix-button', 'kupu-table-del-button',
        'kupu-table-fixall-button', 'kupu-toolbox-tables',
        'kupu-toolbox', 'kupu-toolbox-active');
    tabletool.registerToolBox('tabletoolbox', tabletoolbox);

    var divstool = new DivsTool();
    kupu.registerTool('divstool', divstool);

    var divstoolbox = new DivsToolBox('kupu-div-addbutton',
                                       'kupu-divs-float-select', 'kupu-toolbox-divs',  'kupu-toolbox', 'kupu-toolbox-active');
    divstool.registerToolBox('divstoolbox', divstoolbox);



    var spellchecker = new KupuSpellChecker('kupu-spellchecker-button',
                                            'spellcheck.jspx');
    kupu.registerTool('spellchecker', spellchecker);

    // like the zoom tool, but it doens' realy work.

    var zoom = new KupuZoomTool('kupu-zoom-button');
    kupu.registerTool('zoomtool', zoom);

    // create some drawers, drawers are some sort of popups that appear when a
    // toolbar button is clicked
    var drawertool = new DrawerTool();
    kupu.registerTool('drawertool', drawertool);

   /*
   var sourceedittool = new SourceEditTool('kupu-source-button', 'kupu-editor-textarea');
   kupu.registerTool('sourceedittool', sourceedittool);
   */

   // Drawers...

   // Function that returns function to open a drawer
   var opendrawer = function(drawerid) {
       return function(button, editor) {
           drawertool.openDrawer(drawerid);
       };
   };

   var imagelibdrawerbutton = new KupuButton('kupu-imagelibdrawer-button', opendrawer('imagelibdrawer'));
   kupu.registerTool('imagelibdrawerbutton', imagelibdrawerbutton);

   var linklibdrawerbutton = new KupuButton('kupu-linklibdrawer-button',
                                            opendrawer('linklibdrawer'));
   kupu.registerTool('linklibdrawerbutton', linklibdrawerbutton);

   var linkdrawerbutton = new KupuButton('kupu-linkdrawer-button',
                                         opendrawer('linkdrawer'));
   kupu.registerTool('linkdrawerbutton', linkdrawerbutton);


   // create some drawers, drawers are some sort of popups that appear when a
   // toolbar button is clicked
   var drawertool = new DrawerTool();
   kupu.registerTool('drawertool', drawertool);

   drawertool.search = function() {
       alert('haaai');
   }

   try {
       var linklibdrawer = new ResourceLibraryDrawer(linktool,
                                                 conf['link_xsl_uri'],
                                                 conf['link_libraries_uri'],
                                                 conf['search_links_uri']);
       drawertool.registerDrawer('linklibdrawer', linklibdrawer);

       var imagelibdrawer = new ImageLibraryDrawer(imagetool,
                                                   conf['image_xsl_uri'],
                                                   conf['image_libraries_uri'],
                                                   conf['search_images_uri']);
       drawertool.registerDrawer('imagelibdrawer', imagelibdrawer);

       /*
       var imagelibdrawer2 = new ImageLibraryDrawer(null,
                                                    conf['image_xsl_uri'],
                                                    conf['image_libraries_uri'],
                                                    conf['search_images_uri']);
       drawertool.registerDrawer('nodeimagedrawer', imagelibdrawer2);
       */
   } catch(e) {
       var msg = _('There was a problem initializing the drawers. Most ' +
               'likely the XSLT or XML files aren\'t available. If this ' +
               'is not the Kupu demo version, check your files or the ' +
               'service that provide them (error: ${error}).',
               {'error': (e.message || e.toString())});
       alert(msg);
   };
   var linkdrawer = new LinkDrawer('kupu-linkdrawer', linktool);
   drawertool.registerDrawer('linkdrawer', linkdrawer);

    /*
   var tabledrawerbutton = new KupuButton('kupu-tabledrawer-button',
                                           opendrawer('tabledrawer'));
   kupu.registerTool('tabledrawerbutton', tabledrawerbutton);
    */
   //var tabledrawer = new TableDrawer('kupu-tabledrawer', tabletool);
   // drawertool.registerDrawer('tabledrawer', tabledrawer);

    // register some cleanup filter
    // remove tags that aren't in the XHTML DTD
   var nonxhtmltagfilter = new NonXHTMLTagFilter(
   {'html': 1,
        'body': 1,
        'head': 1,
        'title': 1,
        'a': 1,
        'abbr': 0,
        'acronym': 0,
        'address': 0,
        'b': 1,
        'base': 0,
        'blockquote': 0,
        'br': 1,
        'caption': 1,
        'cite': 0,
        'code': 0,
        'col': 0,
        'colgroup': 0,
        'dd': 0,
        'dfn': 0,
        'div': 1,
        'dl': 0,
        'dt': 0,
        'em': 1,
        'h1': 1,
        'h2': 1,
        'h3': 1,
        'h4': 1,
        'h5': 1,
        'h6': 1,
        'h7': 1,
        'i': 1,
        'img': 1,
        'kbd': 1,
        'li': 1,
        'link': 0,
        'meta': 1,
        'ol': 1,
        'p': 1,
        'pre': 0,
        'q': 0,
        'samp': 0,
        'script': 0,
        'span': 0,
        'strong': 1,
        'style': 0,
        'sub': 1,
        'sup': 1,
        'table': 1,
        'tbody': 1,
        'td': 1,
        'tfoot': 0,
        'th': 1,
        'thead': 0,
        'tr': 1,
        'ul': 1,
        'u': 0,
        'var': 0,
        'font': 0,
        'center': 0
        });
    kupu.registerFilter(nonxhtmltagfilter);

    return kupu;
};
