# Register our skins directory - this makes it available via portal_skins.

from Products.CMFCore.DirectoryView import registerDirectory

from config import GLOBALS
registerDirectory('skins', GLOBALS)
