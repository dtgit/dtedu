## Controller Python Script "ecpd_view_relations_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Compute Results to be shown

REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

#get all available PlagResult objects as a list
results = REQUEST.SESSION.get('results', None)

#if wished use only positive results
if REQUEST.get('only_positive_results', None):
	results = [r for r in results if context.isSuspectPlagiarism(r)]

#check if grouped view is desired
if REQUEST.get('group_view', None):
	groups = context.getPlagiarismGroups(results)
	REQUEST.SESSION.set('groups', groups)
	REQUEST.SESSION.set('act_results', None)
else:
	REQUEST.SESSION.set('act_results', results)
	REQUEST.SESSION.set('groups', None)


return state
