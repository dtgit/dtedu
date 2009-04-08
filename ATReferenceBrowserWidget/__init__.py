from Products.CMFCore import utils
from Products.Archetypes.atapi import process_types, listTypes
from config import *

import ATRefBrowserDemo

def initialize(context):
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        ).initialize(context)
