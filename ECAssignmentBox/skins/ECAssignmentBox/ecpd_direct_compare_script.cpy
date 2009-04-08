## Controller Python Script "ecpd_direct_compare_script"
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

#get the result which is to be shown
result = REQUEST.get('selected_result', None)
#get all available PlagResult objects as a list
results = REQUEST.SESSION.get('results', None)
#get assignments
all_objs = context.objectValues()
objects = [o for o in all_objs if context.ecab_utils.isAssignmentBoxType(o)]
strList = []
idList = []
for o in objects:
     try:
          strList.append(str(o.getFile()))
          idList.append(o.pretty_title_or_id())
     except:
          pass

if result and results:
    #get ids from result = 'identifier1, identifier2'
    ids = result.split(',')
    #get PlagResult object
    plagResult = None
    for r in results:
        if context.containsIdentifier(r, ids[0]) and context.containsIdentifier(r, ids[1]):
            plagResult = r
            break
    #get texts for each id
    if plagResult:
        #get ids in correct order from plagResult object
        ids = context.getIdentifier(plagResult)
        #compute html texts
        htmlTexts = context.resultToHtml(plagResult, strList[idList.index(ids[0])], strList[idList.index(ids[1])])
        #set ids and texts
        REQUEST.set('text1_name', ids[0])
        REQUEST.set('text2_name', ids[1])
        REQUEST.set('text1', htmlTexts[0])
        REQUEST.set('text2', htmlTexts[1])

#refresh selected_results
#REQUEST.set('selected_results', REQUEST.get('selected_results'))

return state
