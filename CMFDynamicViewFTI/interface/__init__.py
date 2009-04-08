from _base import IDynamicViewTypeInformation
from _base import IBrowserDefault
from _base import ISelectableBrowserDefault

from Products.CMFDynamicViewFTI import interfaces
from Interface.bridge import createZope3Bridge

createZope3Bridge(IDynamicViewTypeInformation, interfaces, 'IDynamicViewTypeInformation')
createZope3Bridge(IBrowserDefault, interfaces, 'IBrowserDefault')
createZope3Bridge(ISelectableBrowserDefault, interfaces, 'ISelectableBrowserDefault')