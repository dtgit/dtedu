##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
# Helper classes
# Filter list: filter name, title, enabled by default, css class
FILTERS = [
    ('save-button', 'Save button', True, 'kupu-save'),
    ('bg-basicmarkup', 'Bold/Italic group', True, None),
    ('bold-button', 'Bold button', True, 'kupu-bold'),
    ('italic-button', 'Italic button', True, 'kupu-italic'),
    ('bg-subsuper', 'Subscript/Superscript group', False, None),
    ('subscript-button', 'Subscript button', False, 'kupu-subscript'),
    ('superscript-button', 'Superscript button', False, 'kupu-superscript'),
    ('bg-colorchooser', 'Colour chooser group', False, None),
    ('forecolor-button', 'Psychedelic foreground', False, 'kupu-forecolor'),
    ('hilitecolor-button', 'Psychedelic background', False, 'kupu-hilitecolor'),
    ('bg-justify', 'Justify group', True, None),
    ('justifyleft-button', 'Justify left button', True, 'kupu-justifyleft'),
    ('justifycenter-button', 'Justify center button', True, 'kupu-justifycenter'),
    ('justifyright-button', 'Justify right button', True, 'kupu-justifyright'),
    ('bg-list', 'List group', True, None),
    ('list-ol-addbutton', 'Add ordered list button', True, 'kupu-insertorderedlist'),
    ('list-ul-addbutton', 'Add unordered list button', True, 'kupu-insertunorderedlist'),
    ('definitionlist', 'Definition list', True, 'kupu-insertdefinitionlist'),
    ('bg-indent', 'Indent group', True, None),
    ('outdent-button', 'Outdent button', True, 'kupu-outdent'),
    ('indent-button', 'Indent button', True, 'kupu-indent'),
    ('bg-drawers', 'Drawers group', True, None),
    ('imagelibdrawer-button', 'Image drawer button', True, 'kupu-image'),
    ('linklibdrawer-button', 'Link drawer button', True, 'kupu-inthyperlink'),
    ('linkdrawer-button', 'External link drawer button', True, 'kupu-exthyperlink'),
    ('embed-tab', 'Embed tab in External link drawer', False, None),
    ('anchors-button', 'Anchor drawer button', True, 'kupu-anchors'),
    ('manage-anchors-tab', 'Manage Anchors tab in anchor drawer', True, None),
    ('toc-tab', 'Table of Contents in anchor drawer', False, None),
    ('tabledrawer-button', 'Table drawer button', True, 'kupu-table'),
    ('bg-remove', 'Remove group', True, None),
    ('removeimage-button', 'Remove image button', True, 'kupu-removeimage'),
    ('removelink-button', 'Remove link button', True, 'kupu-removelink'),
    ('bg-undo', 'Undo group', False, None),
    ('undo-button', 'Undo button', False, 'kupu-undo'),
    ('redo-button', 'Redo button', False, 'kupu-redo'),
    ('spellchecker', 'Spellchecker', False, 'kupu-spellchecker'),
    ('source', 'Source', True, 'kupu-source'),
    ('styles', 'Styles pulldown', True, None),
    ('ulstyles', 'Unordered list style pulldown', False, None),
    ('olstyles', 'Ordered list style pulldown', True, None),
    ('zoom', 'Zoom button', True, 'kupu-zoom'),
]
FILTERDICT = dict([(k,v) for (k,title,v,cl) in FILTERS])

class ButtonFilter:
    """Helper class to control visibility of buttons.
    Works from both a whitelist and a blacklist in the widget.
    The configlet also provides a master list of visibilities
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, tool, context, field=None):
        def isButtonAllowed(name):
            visible = visible_buttons.get(name, None)
            if visible is None:
                visible = FILTERDICT.get(name, True)
            if allow_buttons is not None:
                return visible and name in allow_buttons
            if filter_buttons is not None:
               return visible and name not in filter_buttons
            return visible

        widget = getattr(field, 'widget', None)
        filter_buttons = getattr(widget, 'filter_buttons', None)
        allow_buttons = getattr(widget, 'allow_buttons', None)
        visible_buttons, gvisible = tool.getToolbarFilters(context, field)
        if gvisible is None:
            gvisible = FILTERDICT.keys()
        else:
            for k in FILTERDICT.keys():
                setattr(self, k, False)
        for k in gvisible:
            setattr(self, k, isButtonAllowed(k))
