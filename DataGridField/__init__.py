"""

    DataGridField initialzer.

    Copyright 2006-2007 DataGridField authors.
    
    Load all submodules and perform Zope security initialize for them.

"""

from __future__ import nested_scopes
__author__ = "Mikko Ohtamaa <mikko@redinnovation.com>"
__docformat__ = 'epytext'


# Plone imports
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types

# Local imports
from Products.DataGridField.DataGridWidget  import DataGridWidget
from Products.DataGridField.DataGridField  import DataGridField
from Products.DataGridField.DataGridField  import FixedRow
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.RadioColumn import RadioColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.LinkColumn import LinkColumn
from Products.DataGridField.HelpColumn import HelpColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn
from Products.DataGridField import validators

from Products.DataGridField.config import PKG_NAME, GLOBALS

registerDirectory('skins', GLOBALS)

def initialize(context):
    # Example content type initialization
    import Products.DataGridField.examples
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME), PKG_NAME,)

    ContentInit(
        '%s Content' % PKG_NAME,
        content_types = content_types,
        permission = AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

try:
    from Products.CMFPlone.migrations import v3_1
except ImportError:
    HAS_PLONE31 = False
else:
    HAS_PLONE31 = True

try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True
