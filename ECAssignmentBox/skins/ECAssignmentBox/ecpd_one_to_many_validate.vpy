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

assignments = REQUEST.get('assignments', None)

#check if at least two assignments were selected
if not assignments or len(assignments)<2:
	state.setError('assignments', 'At least two results must be selected to perform the direct comparison.', new_status='failure')

if state.getErrors():
	state.set(portal_status_message='Please correct the indicated errors.')

return state