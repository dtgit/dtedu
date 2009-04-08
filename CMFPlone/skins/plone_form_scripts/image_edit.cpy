## Controller Python Script "image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=precondition='', file='', id='', title=None, description=None
##title=Edit an image
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

isIDAutoGenerated = context.plone_utils.isIDAutoGenerated
original_id=context.getId()
filename=getattr(file,'filename', '')

if file and filename and isIDAutoGenerated(original_id):
#  if there is no id or an autogenerated id, use the filename as the id
#  if not id or context.isIDAutoGenerated(id):
#  if there is no id, use the filename as the id
    if not id:
        id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:]
if file and hasattr(file, 'seek'):
    file.seek(0)

# if there is no id specified, keep the current one
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.plone_utils.contentEdit(new_context,
                                    id=id,
                                    title=title,
                                    description=description)

if file or precondition:
    new_context.edit(precondition=precondition, file=file)

transaction_note('Edited image %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Image changes saved.'))
return state.set(context=new_context)