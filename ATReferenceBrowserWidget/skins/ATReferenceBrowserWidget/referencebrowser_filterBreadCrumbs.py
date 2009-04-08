##parameters=crumbs, startup_directory

# Filter out all breadcrumbs that match folders above
# the current object as represented by the startup_directory

server_url = context.REQUEST.SERVER_URL

if startup_directory.startswith('/'):
    startup_directory = startup_directory[1:]

portal = context.portal_url.getPortalObject()
startup_folder = portal.restrictedTraverse(startup_directory)
startup_folder_url = startup_folder.absolute_url()

return [c 
        for c in crumbs 
        if c['absolute_url'].startswith(startup_folder_url)
       ]

