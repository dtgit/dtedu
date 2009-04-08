## Script (Python) "get_macros"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=
##parameters=vdata
from Products.CMFPlone.utils import safe_hasattr

# We need to get the view appropriate for the object in the history, not
# the current object, which may differ due to some migration.
type_info = context.portal_types.getTypeInfo(vdata.object)

# build the name of special versions views
if safe_hasattr(type_info, 'getViewMethod'):
    # Should use IBrowserDefault.getLayout ?
    def_method_name = type_info.getViewMethod(context)
else:
    def_method_name = type_info.getActionInfo('object/view')['url'].split('/')[-1] or getattr(type_info, 'default_view', 'view')
versionPreviewMethodName = 'version_%s'%def_method_name
versionPreviewTemplate = getattr(context, versionPreviewMethodName, None)

# check if a special version view exists
if getattr(versionPreviewTemplate, 'macros', None) is None:
    # Use the Plone's default view template
    
    versionPreviewTemplate = context.restrictedTraverse(def_method_name)

return versionPreviewTemplate.macros['main']
