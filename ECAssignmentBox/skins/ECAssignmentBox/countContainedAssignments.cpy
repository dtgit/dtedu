## Script (Python) "countContainedBoxes"
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

# set state names for rejected assignments
rejectedStates = ('rejected', )
# set state names for superseded assignments
supersededStates = ('superseded',)

# result is defined as follows:
# [total, total wihtout superseded, accepted, rejected, all in a dict]
result = [0, 0, 0, 0, {}]

# check if information about completed states is available
if hasattr(context, 'completedStates'):
    completedStates = context.getCompletedStates()
else:
    # if not, set default value
    completedStates = ('accepted', 'graded', )

# get the portal's catalog
catalog = getToolByName(context, 'portal_catalog')

# get all assignments
brains = catalog.searchResults(path = {'query':'/'.join(context.getPhysicalPath()), 'depth':100,  }, 
                               #meta_type = ('ECAssignment', 'ECAutoAssignment', ),
                               isAssignmentType = True,
                               )

# total number of assigments, including superseded
result[0] = len(brains)

for brain in brains:
    state = brain.review_state

    # 1: collect number of assignments in a all available states using a dict
    if not result[4].has_key(state):
        result[4][state] = 0
    
    result[4][state] = result[4][state] + 1

    # 2: exclude superseded assignments
    if not state in supersededStates:
        result[1] = result[1] + 1

    # 3: count special states:
    # count all assignments which are in one of the completed states
    if state in completedStates:
        result[2] = result[2] + 1
    # count all assigments in state rejected
    elif state in rejectedStates:
        result[3] = result[3] + 1

return result