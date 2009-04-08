## Controller Python Script "modify_boxes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=submission_period_start=None, use_submission_period_start=False, submission_period_end=None, use_submission_period_end=False, sendNotificationEmail=None, use_sendNotificationEmail=False, maxTries=None, use_maxTries=False, *args
##title=Set the submission period
##

from DateTime import DateTime
from Products.CMFPlone.utils import transaction_note
from ZODB.POSException import ConflictError

REQUEST = context.REQUEST
I18N_DOMAIN = 'eduComponents'

portal = context.portal_url.getPortalObject()
succeeded = []
failed = {}
titles_and_paths = []

status ='failure'
message = ''

if REQUEST.has_key('paths'):
    for path in REQUEST['paths']:
        try:
            obj = portal.restrictedTraverse(path)

            if context.ecab_utils.isAssignmentBoxType(obj):
                if use_submission_period_start:
                    obj.setSubmission_period_start(submission_period_start)
                if use_submission_period_end:
                    obj.setSubmission_period_end(submission_period_end)
                if use_sendNotificationEmail:
                    obj.setSendNotificationEmail(sendNotificationEmail)
                if use_maxTries:
                    obj.setMaxTries(maxTries
                                    or obj.getField('maxTries').default)
                
                succeeded.append(obj.title_or_id())
                titles_and_paths.append('%s (%s)' % (obj.title_or_id(), path))
        except ConflictError:
            raise
        except Exception, e:
            failed[path]= e

if succeeded:
    status = 'success'
    message = context.translate(msgid = 'modify_boxes_success',
                                domain = I18N_DOMAIN,
                                default = 'The options for the following assignment boxes were changed: "${titles}".',
                                mapping = {'itemCount': str(len(succeeded)),
                                           'titles': '", "'.join(succeeded),
                                           'start': submission_period_start or '----',
                                           'end': submission_period_end or '----'},
                                )

    transaction_note('Updated submission periods of: %s' % (', '.join(titles_and_paths)))

if failed:
    if message: message = message + '  '
    message = message + context.translate(msgid = 'modify_boxes_failure',
                                          domain = I18N_DOMAIN,
                                          default = 'The settings of the following assignment boxes could not be changed: "${titles}".',
                                          mapping = {'titles': '", "'.join(failed)})

return state.set(status=status, portal_status_message=message)
