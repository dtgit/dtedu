## Script (Python) "ecl_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=group=''
##title=
##

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

user_id = str(REQUEST.get('AUTHENTICATED_USER', None))
member  = context.portal_membership.getMemberById(str(user_id))
groups  = member.getGroups()
action  = ''
status  = 'failure'
msg     = 'Enrollment error'

if not context.isParticipant(user_id):
    # check enrollment limit
    if not context.hasEnrollmentLimitReached():
        # try to add user
        if context.addParticipant(user_id):
            status = 'success'
            msg = context.translate(
                msgid   = 'enrollment_sucessful',
                domain  = I18N_DOMAIN,
                default = 'You have been successfully enrolled.')
        else:
            status = 'failure'
            msg = context.translate(
                msgid   = 'enrollment_failed',
                domain  = I18N_DOMAIN,
                default = 'Enrollment failed, please contact the instructor.')
    else:
        # enrollment limit has reached
        status = 'failure'
        msg = context.translate(
            msgid   = 'label_enrollment_limit_reached',
            domain  = I18N_DOMAIN,
            default = 'Enrollment failed. The maximum number of participants has been reached.')
        
else:
    # try to cancel enrollment of user
    if context.removeParticipant(user_id):
        status = 'success'
        msg = context.translate(
            msgid   = 'cancellation_successful',
            domain  = I18N_DOMAIN,
            default = 'You are no longer enrolled.')
    else:
        status = 'failure'
        msg = context.translate(
            msgid   = 'cancellation_failed',
            domain  = I18N_DOMAIN,
            default = 'Cancellation of enrollment failed, please contact the instructor.')

#return state.set(status = status, portal_status_message = msg)
RESPONSE.redirect('%s?portal_status_message=%s' % 
            (context.absolute_url(), msg,))
