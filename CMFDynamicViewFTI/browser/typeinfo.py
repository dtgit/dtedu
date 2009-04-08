# -*- coding: utf-8 -*-
"""
Add DynamicView FTI form (ZMI)
"""
# $Id: typeinfo.py 48191 2007-08-29 16:08:43Z glenfant $

from Products.CMFCore.browser.typeinfo import FactoryTypeInformationAddView
from Products.CMFDynamicViewFTI import DynamicViewTypeInformation

class DVFactoryTypeInformationAddView(FactoryTypeInformationAddView):
    """See FactoryTypeInformationAddView that does all the job"""

    klass = DynamicViewTypeInformation

    description = u'A dynamic view type information object defines a portal type.'

