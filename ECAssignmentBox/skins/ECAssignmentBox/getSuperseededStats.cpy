## Script (Python) "getFinalStateValues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

# [index of first tuple in list, total superseeded, total ECAssignmentBoxes, total users,
#    (1, #), (2, #), ..., (n, #)]
result = [4,0,0,0,]
submissionsWithDuplicates = []

# get the portal's catalog
catalog = getToolByName(context, 'portal_catalog')

# get the amount of ECAssignmentBoxes
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               #meta_type = ('ECAssignmentBox', 'ECAutoAssignmentBox', ),
                               isAssignmentBoxType = True,
                               )
result[2] = len(brains)

# get all ECAssignments inside this ECFolder
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               sort_on = 'Creator', 
                               #meta_type = ('ECAssignment', 'ECAutoAssignment', ),
                               isAssignmentType = True,
                               )

result[1] = len(brains)

if len(brains) > 0:
    lastCreator = None
    currAmount = 0
    creators = 0
    
    for brain in brains:
        if not lastCreator:
            lastCreator = brain.Creator
            creators = creators + 1
        if brain.Creator == lastCreator:
            currAmount = currAmount + 1
        else:
            submissionsWithDuplicates.append(currAmount)
            lastCreator = brain.Creator
            creators = creators + 1
            currAmount = 1
    
    submissionsWithDuplicates.append(currAmount)
    submissionsWithDuplicates.sort()
    result[3] = creators
    
    # FIXME: dirty hack; rename l
    l = []
    
    while len(submissionsWithDuplicates) > 0:
        last = submissionsWithDuplicates[0]
        l.append((last, submissionsWithDuplicates.count(last)))
        while submissionsWithDuplicates.count(last) > 0:
            submissionsWithDuplicates.remove(last)
            
    #l.sort(lambda a, b: cmp(a[1], b[1]))
    
    result.extend(l)

return result

#status = 'failure'
#message = context.translate('Please select one or more items.')
#return state.set(status=status, portal_status_message = message)