## Script (Python) "getFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,batch=False,b_size=100,full_objects=False
##title=wrapper method around to use catalog to get folder contents
##

mtool = context.portal_membership
cur_path = '/'.join(context.getPhysicalPath())
path = {}

if not contentFilter:
    # The form and other are what really matters
    contentFilter = dict(getattr(context.REQUEST, 'form',{}))
    contentFilter.update(dict(getattr(context.REQUEST, 'other',{})))
else:
    contentFilter = dict(contentFilter)

if not contentFilter.get('sort_on', None):
    contentFilter['sort_on'] = 'getObjPositionInParent'

if contentFilter.get('path', None) is None:
    path['query'] = cur_path
    path['depth'] = 1
    contentFilter['path'] = path

show_inactive = mtool.checkPermission('Access inactive portal content', context)

# Evaluate in catalog context because some containers override queryCatalog
# with their own unrelated method (Topics)
contents = context.portal_catalog.queryCatalog(contentFilter, show_all=1,
                                                  show_inactive=show_inactive)

if full_objects:
    contents = [b.getObject() for b in contents]

if batch:
    from Products.CMFPlone import Batch
    b_start = context.REQUEST.get('b_start', 0)
    batch = Batch(contents, b_size, int(b_start), orphan=0)
    return batch

return contents
