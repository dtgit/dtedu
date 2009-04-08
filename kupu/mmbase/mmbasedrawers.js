/**
 * Specialized drawer for mmbase-resources.
 * Like LinkLibraryDrawer, but with upload-functionality.
 * $Id: $
 */

function ResourceLibraryDrawer(tool, xsluri, libsuri, searchuri, baseelement) {
    /* a specific LibraryDrawer for links */

    this.drawertitle = "Insert Link";
    this.drawertype = "link";
    this.showupload = '';
    if (tool) {
        this.init(tool, xsluri, libsuri, searchuri, baseelement);
    }

    this.save = function() {
        this.editor.resumeEditing();
        /* create a link in the iframe according to collected data
           from the drawer */
        var selxpath = '//resource[@selected]';
        var selnode = this.xmldata.selectSingleNode(selxpath);
        if (!selnode) {
            var uploadbutton = this.xmldata.selectSingleNode("/libraries/*[@selected]/uploadbutton");
            if (uploadbutton) {
                this.uploadResource();
            }
            return;
        }

        var uri = selnode.selectSingleNode('uri/text()').nodeValue;
        uri = uri.strip();  // needs kupuhelpers.js
        var title = '';
        title = selnode.selectSingleNode('title/text()').nodeValue;
        title = title.strip();

        // XXX requiring the user to know what link type to enter is a
        // little too much I think. (philiKON)
        var type = null;
        var elm = getFromSelector('link_name');
        var name = elm ? elm.value : '';
        var target = null;
        if (getFromSelector('link_target') && getFromSelector('link_target').value != '')
            target = getFromSelector('link_target').value;
        
        this.tool.createLink(uri, type, name, target, title);
        this.drawertool.closeDrawer();
    };
    // upload, on submit/insert press
    this.uploadResource = function() {
        var form = document.getElementById('kupu_upload_form');
        if (!form || form.node_prop_image.value == '') {
            alert("" + form + " " + form.node_prop_image.value);
            return;
        }

        if (form.node_prop_title.value == "") {
            alert("Please enter a title for the image you are uploading");
            return;        
        };
        
        form.submit();
    };
    
    // called for example when no permission to upload for some reason
    this.cancelUpload = function(msg) {
        var s = this.xmldata.selectSingleNode('/libraries/*[@selected]');     
        s.removeAttribute("selected");
        this.updateDisplay();
        if (msg != '') {
            alert(msg);
        };
    };
    
    // called by onLoad within document sent by server
    this.finishUpload = function(url, mimetype) {
        this.editor.resumeEditing();
        var form = document.getElementById('kupu_upload_form');
        var title = "[" + mimetype + ":" + form.node_prop_title.value + "]";        
        this.tool.createLink(url, null, null, null, title);
        this.shared.newimages = 1;
        this.drawertool.closeDrawer();
    };


};

ResourceLibraryDrawer.prototype = new LibraryDrawer;
ResourceLibraryDrawer.prototype.shared = {}; // Shared data
