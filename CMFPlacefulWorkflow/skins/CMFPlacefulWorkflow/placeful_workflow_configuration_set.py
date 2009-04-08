##parameters=policy_in='', policy_below=''
##title=set placeful workflow configuration
##
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow import CMFPlacefulWorkflowMessageFactory as _

request = context.REQUEST
config = getToolByName(context, 'portal_placeful_workflow').getWorkflowPolicyConfig(context)

if not config:
    message = _(u'No config in this folder.')
else:
    if context.portal_placeful_workflow.getWorkflowPolicyById(policy_in):
        config.setPolicyIn(policy=policy_in)
    elif policy_in == '':
        config.setPolicyIn(policy='')
    else:
        raise str(policy_in)

    if context.portal_placeful_workflow.getWorkflowPolicyById(policy_below):
        config.setPolicyBelow(policy=policy_below)
    elif policy_below == '':
        config.setPolicyBelow(policy='')
    else:
        raise str(policy_below)

    message = _('Changed policies.')
    getToolByName(context, 'portal_workflow').updateRoleMappings()

context.plone_utils.addPortalMessage(message)
request.RESPONSE.redirect('placeful_workflow_configuration')
