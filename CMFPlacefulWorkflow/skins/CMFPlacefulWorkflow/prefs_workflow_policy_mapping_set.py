##parameters=submit, wfpid, title, description, wf, default_workflow_id
##title=set local workflow policy mapping
#-*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow import CMFPlacefulWorkflowMessageFactory as _

request = context.REQUEST
policy = getToolByName(context, 'portal_placeful_workflow').getWorkflowPolicyById(wfpid)

policy.setTitle(title)
policy.setDescription(description)

policy.setDefaultChain(default_chain=(default_workflow_id,),REQUEST=context.REQUEST)

for pt, wf in wf.items():
    policy.setChain(portal_type=pt, chain=(wf,),REQUEST=context.REQUEST)

wf_tool = getToolByName(context, 'portal_workflow')
wf_tool.updateRoleMappings()

context.plone_utils.addPortalMessage(_(u'Changes to criteria saved.'))
if request:
    request.RESPONSE.redirect('prefs_workflow_policy_mapping?wfpid=%s' % wfpid)

return request
