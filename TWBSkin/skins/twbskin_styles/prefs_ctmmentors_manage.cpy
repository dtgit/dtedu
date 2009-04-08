## Script (Python) ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=mentors=[]
##title=Assign Mentors
##

from Products.CMFPlone import PloneMessageFactory as _

acl_users = context.acl_users
mtool = context.portal_membership
sf_tool = context.portal_salesforcebaseconnector

for user in mentors:
    #See if user will be assigned
    if hasattr(user, 'cohort'):
	if user.cohort != '':
	    #Assign user to plone and social network cohort
            context.restrictedTraverse('@@addMemberToGroup')(user.id, user.cohort)
            
            #Assign user to CTMMentor group
            context.restrictedTraverse('@@addMemberToCTMMentors')(user.id, 'CTMMentor')

            #define assigned cohort to SalesForce
            updateData = dict(Id=user.sf_id,
                              type='Contact',
                              Mentor_Group__c=user.cohort)
            sf_tool.update(updateData)
            
            #Email Mentor their assignment
            mfrom = 'info@teacherswithoutborders.org'
            subject = 'CTM Mentor Assignment'
            message = "You have been assigned to mentor the following cohort:\n\n"\
                      "%s ::  http://www.teacherswithoutborders.org/groups/%s\n\n"\
                      "Thank you!" % (user.cohort, user.cohort)
            context.MailHost.secureSend(message, 
                                        mto=user.email, 
                                        mfrom=mfrom, 
                                        subject=subject, charset='utf8')
            context.plone_utils.addPortalMessage(_(u'Mentor has been notified of their assignment via e-mail.'))

return state
