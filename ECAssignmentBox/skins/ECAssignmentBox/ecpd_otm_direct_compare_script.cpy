## Controller Python Script "ecpd_otm_direct_compare_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Search for plagiarism in given texts

REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

#get the selected assignments which are to be compared
selectedAssignments = REQUEST.get('selectedAssignments', None)

#get assignment objects
if selectedAssignments and (selectedAssignments >= 2):
	assignment1 = context.restrictedTraverse(selectedAssignments[0])
	assignment2 = context.restrictedTraverse(selectedAssignments[1])
else:
	#set error
	#TODO:
	return state

#get assignments
#all_objs = context.objectValues()
#objects = [o for o in all_objs if context.ecab_utils.isAssignmentBoxType(o)]
#strList = []
#idList = []
#for o in objects:
#     try:
#          strList.append(str(o.getFile()))
#          idList.append(o.pretty_title_or_id())
#     except:
#          pass

normName = 'NORMAL'
algName = 'NGRAM'
mML = None
treshold = None

id1 = assignment1.pretty_title_or_id()
text1 = str(assignment1.getFile())
id2 = assignment2.pretty_title_or_id()
text2 = str(assignment2.getFile())

#compute PlagResult
plagResults = context.compareList([text1, text2], [id1, id2], normName, algName, mML, treshold)

#compute html texts
htmlTexts = context.resultToHtml(plagResults[0], text1, text2)

#set ids and texts
REQUEST.set('text1_name', id1)
REQUEST.set('text2_name', id2)
REQUEST.set('text1', htmlTexts[0])
REQUEST.set('text2', htmlTexts[1])


return state
