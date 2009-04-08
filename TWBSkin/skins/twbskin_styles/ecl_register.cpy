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

	    added_cohort = ''
	    #get list of current cohorts
	    grp_tool = context.portal_groups
 	    groupids = grp_tool.getGroupIds()
	    cohorts = []
	    for id in groupids:
	    	if 'cohort' in id:
		   cohorts += [id,]
            grouped = False
	    for cohort in cohorts:
                if len(grp_tool.getGroupMembers(cohort)) < 20:
		    context.restrictedTraverse('@@addMemberToGroup')(user_id, cohort)
		    grouped = True
		    added_cohort = cohort
		    break
            if grouped == False:
	        new_cohort = 'cohort%s' % (len(cohorts) + 1)
	        new_title = 'cohort %s' % (len(cohorts) + 1)
	        context.restrictedTraverse('@@addGroup')(new_cohort, new_title)
	        context.restrictedTraverse('@@addMemberToGroup')(user_id, new_cohort)
		added_cohort = new_cohort


	    if added_cohort:

	        mtool = context.portal_membership
	        member = mtool.getAuthenticatedMember()

	        member.setProperties(ctmcohort=added_cohort)

            	status = 'success'
            	msg = context.translate(
                    msgid   = 'enrollment_sucessful',
                    domain  = I18N_DOMAIN,
                    default = 'You have been successfully enrolled and a new cohort (' + str(added_cohort) + ') has been added to your profile. Being in a cohort allows you to read the profiles of other cohort members, comment on each others work, share learned experiences, and develop friendships that will improve your ability to teach. View the CTM Tutorial to learn more about the benefits of being in a cohort.')
	    else:
	
                status = 'failure'
                msg = context.translate(
                    msgid   = 'enrollment_failed',
                    domain  = I18N_DOMAIN,
                    default = 'Enrollment failed, unable to add user to cohort.')
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
if status == 'error':
    msgtype = 'failure'
else:
    msgtype = 'info'
context.plone_utils.addPortalMessage(msg,msgtype)
RESPONSE.redirect('%s?portal_status_message=%s' % 
            (context.absolute_url(), msg,))
