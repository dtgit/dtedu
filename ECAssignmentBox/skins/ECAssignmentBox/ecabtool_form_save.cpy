## Controller Python Script "ecabtool_form_save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the ECSpooler
REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

student_id_attr = REQUEST.get('student_id_attr', None)
major_attr = REQUEST.get('major_attr', None)

#context.ecab_utils.manage_changeProperties(REQUEST)
props = context.portal_properties.ecab_properties
props.manage_changeProperties(REQUEST)

# set portal message
msg = context.translate(
        msgid   = 'update_succeeded',
        domain  = I18N_DOMAIN,
        default = 'Your changes have been saved.')

return state.set(portal_status_message = msg)
