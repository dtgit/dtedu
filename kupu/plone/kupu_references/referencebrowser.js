// Replace referencebrowser with Kupu drawers.
function KupuRefDrawer(tool, xsluri, libsuri, searchuri, selecturi) {
    /* a specific LibraryDrawer for selection of references */
    this.init(tool, xsluri, libsuri, searchuri, 'krb_drawer_base', selecturi);

    this.drawertitle = "Add reference";
    this.drawertype = "reference";
    this.xmldata = null;

    this.createContent = function(e, fieldName, label, multiple, resourcetype) {
        this.libsuri = libsuri + resourcetype;
        this.searchuri = searchuri + resourcetype;
        this.selecturi = selecturi + resourcetype;
        this.fieldName = fieldName;

        this.setTitle(label);
        this.loadSelection(fieldName, multiple);
        this.setPosition(e);
        KupuRefDrawer.prototype.createContent.call(this);
    };

    this.loadSelection = function(fieldName, multiple) {
        this.multiple = multiple;
        this.field = document.getElementById(fieldName);
        this.preview = document.getElementById(fieldName+'_preview');
        this.currentSelection = [];

        ids = this.field.value.split(/\n/);
        for (var i = 0; i < ids.length; i++) {
            var id = ids[i].strip();
            if (!id) continue;
            this.currentSelection.push(id);
        }
        this.selectedSrc = this.currentSelection.join(' ');
    };

    this.save = function() {
        var sel = this.currentSelection;
        var titles = [];
        var el = newElement;
        var xml = this.xmldata;

        var preview = this.preview;
        for (var i = sel.length; i > 0;) {
            if (sel[--i]) break;
            delete sel[i];
            sel.length = i;
        }
        var emptymsg = preview.getElementsByTagName('em')[0];
        emptymsg.style.display = (sel.length==0)?'':'none';

        for (var node = preview.firstChild; node; node = nxt) {
            var nxt = node.nextSibling;
            if (node.nodeName.toLowerCase()=='div') {
                preview.removeChild(node);
            };
        };
        for (var i = 0; i < sel.length; i++) {
            var id = sel[i];
            var t = id;
            var node = xml.selectSingleNode("//resource[@id='"+id+"']");
            div = document.createElement("div");
            div.className = i%2?'odd':'even';
            var link = document.createElement('a');
            link.href = node.selectSingleNode('uri/text()').nodeValue.strip()+'/view';

            if (_SARISSA_IS_IE) {
                /* IE won't take a node to transformToDocument */
                var result = node.transformNode(this.shared.xsl);
                link.innerHTML = result;
            } else {
                var result = this.shared.xsltproc.transformToDocument(node);
                var imp = window.document.importNode(result, true);
                Sarissa.copyChildNodes(imp, link, true);
            };

            div.appendChild(link);
            preview.appendChild(div);
        }
        var nvalue =  this.currentSelection.join('\n');
        if (nvalue != this.field.value) {
            this.field.value = nvalue;
            kupuFireEvent(this.field, 'change');
        }
        referencebrowse_showRemove(this.fieldName, this.currentSelection.length);

        drawertool.closeDrawer();
    };

    this.setPosition = function(e){
        // this function adapted from code in pdlib.js in CompositePage
        var drawernode = this.element;

        if (!e)
            e = event;
        var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
          // have to check documentElement in some IE6 releases
        var page_x = window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft;
        var page_y = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;

          // Choose a location for the menu based on where the user clicked
        var node_top, node_left;
        var drawer_w = drawernode.offsetWidth + 20;
        var drawer_h = drawernode.offsetHeight + 20;
        if (drawer_h < 400) {
            drawer_h = 400;
        }          
        var drawer_half_w = Math.floor(drawer_w / 2);
        var drawer_half_h = Math.floor(drawer_h / 2);
        if (page_w - e.clientX < drawer_half_w) {
            // Close to the right edge
            node_left = page_x + page_w - drawer_w; 
        }
        else {
            node_left = page_x + e.clientX - drawer_half_w;
        }
        if (node_left < page_x) {
            node_left = page_x;
        }
        if (page_h - e.clientY < drawer_half_h) {
            // Close to the bottom
            node_top = page_y + page_h - drawer_h;
        }
        else {
            node_top = page_y + e.clientY - drawer_half_h;
        }
        if (node_top < page_y) {
            node_top = page_y;
        }
        drawernode.style.left = '' + node_left + 'px';
        drawernode.style.top = '' + node_top + 'px';
    };    
};

function kupuFireEvent(el, event) {
    if (el.fireEvent) {
        el.fireEvent('on'+event); //IE
    } else {
        var evt = document.createEvent("HTMLEvents");
        evt.initEvent(event,true,true);
        el.dispatchEvent( evt );
    }
}
function fakeEditor() {
    this.getBrowserName = function() {
        if (_SARISSA_IS_MOZ) {
            return "Mozilla";
        } else if (_SARISSA_IS_IE) {
            return "IE";
        } else {
            throw "Browser not supported!";
        }
    };    

    this.resumeEditing = function() {};
    this.suspendEditing = function() {};
    this.config = {};
    this._saveSelection = function() {};
    this.busy = function() {};
    this.notbusy = function() {};
};

var drawertool;

function krb_initdrawer(link_xsl_uri, link_libraries_uri, search_links_uri, selecturi) {
    // Delay init until the drawer is actually opened.
    if (!KupuRefDrawer.init) {
        KupuRefDrawer.prototype = new LibraryDrawer;
        // drawertool must be set, but must not change if already set.
        drawertool = window.drawertool || new DrawerTool;
    }

    var klass = KupuRefDrawer;
    klass.linktool = new LinkTool();
    klass.link_xsl_uri = link_xsl_uri;
    klass.link_libraries_uri = link_libraries_uri;
    klass.search_links_uri = search_links_uri;
    klass.selecturi = selecturi;

    editor = new fakeEditor();
    drawertool.initialize(editor);
};

function referencebrowser_draweropen(e, fieldName, label, multival, resource_type) {
    var name = 'krbdrawer-'+fieldName;
    var drawer = drawertool.drawers[name];
    if (!drawer) {
        var klass=KupuRefDrawer;
        drawer = new klass(klass.linktool, klass.link_xsl_uri,
            klass.link_libraries_uri, klass.search_links_uri, klass.selecturi);
        drawertool.registerDrawer(name, drawer);
    }
    drawertool.openDrawer(name, [e, fieldName, label, multival,resource_type]);
};

function referencebrowse_showRemove(fieldName, items)
{
    var btnRemove = document.getElementById(fieldName+'_remove');
    if (btnRemove) btnRemove.style.display = items?'':'none';
}

// function to clear the reference field or remove items
// from the multivalued reference list.
function referencebrowser_removeReference(fieldName)
{
    var field = document.getElementById(fieldName);
    var preview = document.getElementById(fieldName + '_preview');

    var emptymsg = preview.getElementsByTagName('em')[0];
    emptymsg.style.display = '';
    for (var node = preview.firstChild; node; node = nxt) {
        var nxt = node.nextSibling;
        if (node.nodeName.toLowerCase()=='div') {
            preview.removeChild(node);
        };
    };
    field.value = '';
    kupuFireEvent(field, 'change');
    referencebrowse_showRemove(fieldName, false);
};

/*------------------- Fallback code for non-kupu versions --------------*/
// function to open the popup window
function fallback_openBrowser(path, fieldName, at_url, fieldRealName)
{
    atrefpopup = window.open(path + '/referencebrowser_popup?fieldName=' + fieldName + '&fieldRealName=' + fieldRealName +'&at_url=' + at_url,'referencebrowser_popup','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
}

// function to return a reference from the popup window back into the widget
function referencebrowser_setReference(widget_id, uid, label, multi)
{
    // differentiate between the single and mulitselect widget
    // since the single widget has an extra label field.
    if (multi==0) {
        element=document.getElementById(widget_id)
            label_element=document.getElementById(widget_id + '_label')
            element.value=uid
            label_element.value=label
    }  else {
        list=document.getElementById(widget_id)
         // check if the item isn't already in the list
            for (var x=0; x < list.length; x++) {
            if (list[x].value == uid) {
                return false;
            }
        }         
          // now add the new item
        theLength=list.length;
        list[theLength] = new Option(label);
        list[theLength].selected='selected';
        list[theLength].value=uid
    }
}

// function to clear the reference field or remove items
// from the multivalued reference list.
function fallback_removeReference(widget_id, multi)
{
    if (multi) {
        list=document.getElementById(widget_id)
            for (var x=list.length-1; x >= 0; x--) {
            if (list[x].selected) {
                list[x]=null;
            }
        }
        for (var x=0; x < list.length; x++) {
            list[x].selected='selected';
        }        
    } else {
        element=document.getElementById(widget_id);
        label_element=document.getElementById(widget_id + '_label');
        label_element.value = "";
        element.value="";
    }
}

