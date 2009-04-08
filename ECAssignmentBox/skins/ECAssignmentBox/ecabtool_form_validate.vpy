## Script (Python) "ecabtool_form_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

for item_name in ('student_id_attr', 'major_attr', 'personal_title_attr'):
    item = REQUEST.get(item_name, None)

    if item is not None:
        item = item.strip()
        REQUEST.set(item_name, item)

    error = context.check_id(item, 0, None)

    if error:
        state.setError(item_name, error, new_status='failure')

if state.getErrors():
    return state.set(status='failure',
                     portal_status_message='Please correct the indicated errors.')
else:
    return state
