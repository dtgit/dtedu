from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

def checkPAS(portal, out):
    if portal.acl_users.meta_type != 'Pluggable Auth Service':
        raise RuntimeError("Please install PlonePAS first.")

def registerConfiglet(portal, out):
    controlpanel = getToolByName(portal, 'portal_controlpanel')

    # If it's in place already, do nothing
    for configlet in controlpanel.enumConfiglets(group='Products'):
        if configlet['id'] == 'SQLPASPlugin':
            print >> out, "Configlet already registered."
            return

    controlpanel.registerConfiglet(
        id='SQLPASPlugin',
        name='SQL Authentication',
        action='string:${portal_url}/sqlpas-configure.html',
        condition='python:True',
        permission='Manage Portal',
        category='Products', # out of Plone, Products, Members
        imageUrl='site_icon.gif', # icon in control_panel
        description='SQL Authentication',
        )

    print >> out, "Configlet registered."

def install(portal):
    out = StringIO()

    checkPAS(portal, out)
    registerConfiglet(portal, out)

    return out.getvalue()

def uninstall(portal):
    out = StringIO()

    controlpanel = getToolByName(portal, 'portal_controlpanel')
    controlpanel.unregisterConfiglet('SQLPASPlugin')
    print >> out, "Unregistered configlet."

    return out.getvalue()
