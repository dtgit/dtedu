## Controller Python Script "ecpd_searchplagscript"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Search for plagiarism in given texts

def cmp(r1, r2):
	if context.getSimilarity(r1)>context.getSimilarity(r2):
		return 1
	elif context.getSimilarity(r1)==context.getSimilarity(r2):
		return 0
	else:
		return -1

REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

#get normalizer and algorithm
normName = REQUEST.get('normalizer_selection', None)
algName = REQUEST.get('algorithm_selection', None)
mml = REQUEST.get('MML', None)
treshold = REQUEST.get('treshold', None)

#get texts and ids
#objects = REQUEST.get('paths', None)
all_objs = context.objectValues()
wtool = context.portal_workflow
#objects = [o for o in all_objs if context.ecab_utils.isAssignmentBoxType(o) and wtool.getInfoFor(o, 'review_state', '')!='superseded']
objects = [o for o in all_objs if wtool.getInfoFor(o, 'review_state', '')!='superseded']
strList = []
idList = []
for o in objects:
     try:
          strList.append(str(o.getFile()))
          idList.append(o.pretty_title_or_id())
     except:
          pass

if normName and algName and objects and strList and idList:
     #do search ...
     results = context.compareList(strList, idList, normName, algName, mml, treshold)
     #Remove all results with a similarity value equal to zero
     results = [r for r in results if context.getSimilarity(r)>0]
     #sort result list in descending order
     results.sort(cmp=cmp, reverse=True)
     #save to Request
     REQUEST.set('results', results)

     #save to SESSION
     REQUEST.SESSION.set('results', results)

     #set portal message
     #msg = context.translate(
     #  msgid = 'search_succeeded',
     #  domain = I18N_DOMAIN,
     #  default = 'Search peformed. Plagiarism results are now available.')
     return state

else:
     reasons = ''
     if not normName: reasons = reasons + 'normName, '
     if not algName: reasons = reasons + 'algName, '
     if not objects: reasons = reasons + 'objects, '
     if not strList: reasons = reasons + 'strList, '
     if not idList: reasons = reasons + 'idList, '
     #set portal message
     msg = context.translate(
       msgid = 'search_failed',
       domain = I18N_DOMAIN,
       default = 'Search failed. Reasons: '+reasons)
     #return failed state with failure reasons
     return state.set(portal_status_message = msg)


