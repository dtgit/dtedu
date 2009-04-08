# -*- coding: utf-8 -*-

# $Id: __init__.py 48191 2007-08-29 16:08:43Z glenfant $

from Products.CMFCore import utils as cmf_utils
from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation

def initialize(context):
    # (DynamicViewTypeInformation factory is created from ZCML)
    cmf_utils.registerIcon(DynamicViewTypeInformation, 'images/typeinfo.gif', globals())
    return
