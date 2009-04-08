/*****************************************************************************
 *
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/
KupuEditor.prototype._getBase = function(dom) {
    var base = dom.getElementsByTagName('base');
    if (base.length) {
        return base[0].getAttribute('href');
    } else {
        return '';
    }
};

// $Id: kupuploneeditor.js 51158 2008-01-31 16:00:24Z duncan $
KupuEditor.prototype.makeLinksRelative = function(contents,base,debug) {
    // After extracting text from Internet Explorer, all the links in
    // the document are absolute.
    // we can't use the DOM to convert them to relative links, since
    // its the DOM that corrupts them to absolute to begin with.
    // Instead we can find the base from the DOM and do replace on the
    // text until all our links are relative.

    var href = base.replace(/\/[^\/]*$/, '/');
    var pageid = /.*\/([^\/]*)$/.exec(base)[1];
    var hrefparts = href.split('/');
    contents = contents.replace(/(<[^>]* (?:src|href)=")([^"]*)"/g,
        function(str, tag, url, offset, contents) {
        var resolveuid = url.indexOf('/resolveuid/');
        if (resolveuid != -1) {
            str = tag + url.substr(resolveuid+1)+'"';
            return str;
        }
        var urlparts = url.split('#');
        var anchor = urlparts[1] || '';
        url = urlparts[0];
        var urlparts = url.split('/');
        var common = 0;
        while (common < urlparts.length &&
            common < hrefparts.length &&
            urlparts[common]==hrefparts[common]) {
            common++;
        }
        var last = urlparts[common];
        if (common == urlparts.length) { urlparts[common] = '.'; }
        else if (common+1 == urlparts.length && (last=='emptypage'||last==pageid)) {
            urlparts[common] = '';
        }
            // The base and the url have 'common' parts in common.
            // First two are the protocol, so only do stuff if more
            // than two match.
        if (common > 2) {
            var path = [];
            var i = 0;
            for (; i+common < hrefparts.length-1; i++) {
                path[i] = '..';
            };
            while (common < urlparts.length) {
                path[i++] = urlparts[common++];
            };
            if (i==0 && !anchor) {
                path[i++] = '#';
            }
            str = path.join('/');
            if (anchor || str=="") {
                str = [str,anchor].join('#');
            }
            str = tag + str+'"';
        };
        return str;
    });
    // Remove empty links
    contents = contents.replace(/<a\s+href="[^"]*"\s*>\s*<\/a>/g, '');
    // Fixup empty paras.
    contents = contents.replace(/<((p|div)\b[^>]*)>\s*<\/\2>(<br \/>)*/g, '<$1>&nbsp;</$2>').strip();
    return contents;
};

KupuEditor.prototype.saveDataToField = function(form, field) {
    var sourcetool = this.getTool('sourceedittool');
    if (sourcetool) {sourcetool.cancelSourceMode();};

    if (!this._initialized) {
        return;
    };
    this._initialized = false;

    // set the window status so people can see we're actually saving
    window.status= "Please wait while saving document...";

    // pass the content through the filters
    this.logMessage("Starting HTML cleanup");

    var transform = this._filterContent(this.getInnerDocument().documentElement);

    // We need to get the contents of the body node as xml, but we don't
    // want the body node itself, so we use a regex to remove it
    var contents = this.getXMLBody(transform);
    if (/^<body[^>]*>(<\/?(p|br)[^>]*>|\&nbsp;|\s)*<\/body>$/.test(contents)) {
        contents = ''; /* Ignore nearly empty contents */
    }
    var base = this._getBase(transform);
    contents = this._fixupSingletons(contents);
    contents = this.makeLinksRelative(contents, base).replace(/<\/?body[^>]*>/g, "");
    this.logMessage("Cleanup done, sending document to server");

    // now create the form input
    field.value = contents;

    this.content_changed = false;
};
