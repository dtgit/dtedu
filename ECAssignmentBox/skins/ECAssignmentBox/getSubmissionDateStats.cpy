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

# [total superseeded, total ECAssignmentBoxes, (1, #), (2, #), ..., (n, #)]
result = []

# get the portal's catalog
catalog = getToolByName(context, 'portal_catalog')

# get all ECAssignments inside this ECFolder
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()),  'depth':100,  }, 
                               sort_on = 'created', 
                               #meta_type = ('ECAssignment', 'ECAutoAssignment', ),
                               isAssignmentType = True,
                               )

if len(brains) > 0:
    lastDate = ""
    currAmount = 0
  
    for brain in brains:
        if not lastDate:
            lastDate = str(brain.created)[:10]
        if str(brain.created)[:10] == lastDate:
            currAmount = currAmount + 1
        else:
            result.append((lastDate, currAmount))
            lastDate = str(brain.created)[:10]
            currAmount = 1
    result.append((lastDate, currAmount))
    result.sort()

return result

#status = 'failure'
#message = context.translate('Please select one or more items.')
#return state.set(status=status, portal_status_message = message)