from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.PasswordResetTool import product_globals
from StringIO import StringIO
import string

def install(self):
    """Register password reset skins and add the tool"""
    directory_name = 'PasswordReset'
    
    out = StringIO()

    # Add the tool
    portal = getUtility(ISiteRoot)
    try:
        portal.manage_delObjects('portal_password_reset')
        out.write("Removed old portal_password_reset tool\n")
    except:
        pass  # we don't care if it fails
    portal.manage_addProduct['PasswordResetTool'].manage_addTool('Password Reset Tool', None)
    out.write("Adding Password Reset Tool\n")

    # Setup the skins
    skinstool = getToolByName(self, 'portal_skins')
    if directory_name not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', product_globals)
        out.write("Added %s directory view to portal_skins\n" % directory_name)

    # Now we need to go through the skin configurations and insert
    # directory_name into the configurations.  Preferably, this
    # should be right after where 'custom' is placed.  Otherwise, we
    # append it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if directory_name not in path:
            try: path.insert(path.index('custom')+1, directory_name)
            except ValueError:
                path.append(directory_name)
                
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinstool.addSkinSelection(skin, path)
            out.write("Added %s to %s skin\n" % (directory_name, skin))
        else:
            out.write("Skipping %s skin, %s is already set up\n" % (
                skin, directory_name))

    return out.getvalue()
