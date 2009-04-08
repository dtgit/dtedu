## Script (Python) "submission_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##

#REQUEST = context.REQUEST
#user_id = REQUEST.get('AUTHENTICATED_USER', '') #REQUEST.get('user_id', None)

# resourcestrings
I18N_DOMAIN = 'eduComponents'

status = 'failure'

# get current user
mtool = context.portal_membership
member = mtool.getAuthenticatedMember()
isOwner = member.has_role(['Owner', 'Reviewer', 'Manager'], context);

# was the user logged in?
if not member:
    msg = context.translate(\
            msgid   = 'not_logged_in',\
            domain  = I18N_DOMAIN,\
            default = 'You need to be logged in with your username and password.')

# is the assignmentbox effective?
elif not isOwner and not context.isEffective():
    msg = context.translate(\
        msgid   = 'submission_period_effective',\
        domain  = I18N_DOMAIN,\
        default = 'The submission period is not effective. Your submission was rejected.')

# has the assignmentbox expired?
elif not isOwner and context.hasExpired():
    msg = context.translate(\
        msgid   = 'submission_rejected',\
        #msgid   = 'submission_period_expired',\
        domain  = I18N_DOMAIN,\
        default = 'The submission period has expired. Your submission was rejected.')

# has the max number of tries reached?
elif not isOwner and not context.canRetry():
    msg = context.translate(
        msgid   = 'submission_cannot_retry',
        domain  = I18N_DOMAIN,
        default = 'Your submission was rejected: ' +
                  'The maximum number of tries has been reached.')

# are there already submissions which cannot be superseded?
elif not isOwner and not context.canSupersed():
    msg = context.translate(
        msgid   = 'submission_cannot_supersede',
        domain  = I18N_DOMAIN,
        default = 'Your submission was rejected: ' +
                  'An earlier submission is under review or has already been accepted.')

else:
    status = 'success'
    msg = ''

return state.set(status = status, portal_status_message = msg)
