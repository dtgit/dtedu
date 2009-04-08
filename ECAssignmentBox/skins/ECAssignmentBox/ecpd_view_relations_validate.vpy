## Script (Python) "ecpd_view_relations_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##

REQUEST = context.REQUEST

I18N_DOMAIN = 'eduComponents'

selectedResults = REQUEST.get('selected_results', None)

#check if at least one result was selected
if not selectedResults or len(selectedResults)<1:
	state.setError('selected_results', 'At least one result must be selected to perform the direct comparison.', new_status='failure')

if state.getErrors():
	state.set(portal_status_message='Please correct the errors.')

return state