## Script (Python) "all_assignments_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete assignments
##

# Borrowed from Plone's folder_delete.cpy

#from Products.CMFPlone import transaction_note
from ZODB.POSException import ConflictError

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

I18N_DOMAIN = 'eduComponents'

status = 'failure'
message = 'Please select one or more items to delete.'
portal = context.portal_url.getPortalObject()
titles = []
titles_and_paths = []
failed = {}

# paths
paths = []

# get all boxes
boxes = REQUEST.get('ecabox', [])

# get selected items
for box in boxes:
    paths.extend(REQUEST.get(box, []))


for path in paths:
    # Skip and note any errors
    try:
        obj = portal.restrictedTraverse(path)
        obj_parent = obj.aq_inner.aq_parent
        obj_parent.manage_delObjects([obj.getId()])
        titles.append(obj.title_or_id())
        titles_and_paths.append('%s (%s)' % (obj.title_or_id(), path))
    except ConflictError:
        raise
    except Exception, e:
        failed[path]= e

if titles:
    status='success'
    message = context.translate('"${titles}" has been deleted.',
                                {'titles': '", "'.join(titles)},
                                domain = I18N_DOMAIN)

    #transaction_note('Deleted "%s"' % ('", "'.join(titles_and_paths)))

if failed:
    if message: message = message + '  '
    message = message + context.translate('"${titles}" could not be deleted.',
                                          {'titles': '", "'.join(failed.keys())},
                                          domain = I18N_DOMAIN)

return state.set(status=status, portal_status_message=message)

