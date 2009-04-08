## Script (Python) "prefs_group_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Manage groups
##
REQUEST=context.REQUEST
groupstool=context.portal_groups

groups=[group[len('group_'):]
        for group in REQUEST.keys()
        if group.startswith('group_')]

for group in groups:
    roles=REQUEST['group_'+group]
    groupstool.editGroup(group, roles = roles, REQUEST=context.REQUEST, )


delete=REQUEST.get('delete',[])
groupstool.removeGroups(delete, REQUEST=context.REQUEST,)

portal_status_message="Changes made."
return state.set(portal_status_message=portal_status_message)
