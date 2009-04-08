## Script (Python) "validate_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=userid=None, password=None, password2=None
##title=Validate password
from Products.CMFCore.utils import getToolByName

# Determine if we're checking userids or not
pw_tool = getToolByName(context, 'portal_password_reset')
if not pw_tool.checkUser():
    return state

if not userid:
    state.setError('userid', 'This field is required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
