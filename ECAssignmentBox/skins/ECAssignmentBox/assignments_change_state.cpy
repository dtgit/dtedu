## Script (Python) "all_assignments_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action=None, comment='', message=''
##title=
##

#from Products.CMFPlone import transaction_note
from ZODB.POSException import ConflictError

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

status = 'failure'
message = context.translate('Please select one or more items.')

# check if workflow_action is not None
if not workflow_action:
    message = context.translate('Unexpected workflow action: ${workflow_action}',
                                {'workflow_action': workflow_action},
                                domain = I18N_DOMAIN)
    return state.set(status=status, portal_status_message = message)

# paths
paths = []

# get all boxes
boxes = REQUEST.get('ecabox', [])

for box in boxes:
    # get selected items
    paths.extend(REQUEST.get(box, []))

succeeded = []
succeeded_and_paths = []
failed = []
failed_and_paths = []
excepted = {}

MAX_TITLES_TO_REPORT = 10

# get assignment workflow
portal = context.portal_url.getPortalObject()
portal_workflow= context.portal_workflow


for path in paths:
    # Skip and note any errors
    try:
        obj = portal.restrictedTraverse(path)
        obj_parent = obj.aq_inner.aq_parent

        transitions = portal_workflow.getTransitionsFor(obj)
        transition_ids = [t['id'] for t in transitions]

        if workflow_action in transition_ids:
            portal_workflow.doActionFor(obj, workflow_action, comment=comment)
        
            succeeded.append(obj.title_or_id())
            succeeded_and_paths.append('%s (%s)' % (obj.title_or_id(), path))
        else:
            failed.append(obj.title_or_id())
            failed_and_paths.append('%s (%s)' % (obj.title_or_id(), path))

    except Exception, e:
        excepted[path]= e

if succeeded:
    status='success'
    if len(succeeded) == 1:
        message = context.translate('State for "${titles}" has been changed.',
                                    {'titles': succeeded[0]},
                                    domain = I18N_DOMAIN)
    elif len(succeeded) <= MAX_TITLES_TO_REPORT:
        message = context.translate('State for "${titles}" has been changed.',
                                    {'titles': '", "'.join(succeeded)},
                                    domain = I18N_DOMAIN)
    else:
        message = context.translate('State for ${itemCount} items has been changed.',
                                    {'itemCount': str(len(succeeded))},
                                    domain = I18N_DOMAIN)

    #transaction_note('Accepted %s' % (', '.join(succeeded_and_paths)))
    #transaction_note('State for "%s" has been changed (transition: %s).' % ('", "'.join(succeeded), workflow_action, ))

if failed:
    if message: message = message + '  '
    message = message + context.translate('State for "${titles}" could not be changed.',
                                          {'titles': '", "'.join(failed)},
                                          domain = I18N_DOMAIN)
    
if excepted:
    if message: message = message + '  '
    message = message + context.translate('Changing state for "${titles}" caused an exception.',
                                          {'titles': '", "'.join(excepted.keys())})

return state.set(status=status, portal_status_message = message)