## Controller Python Script "saveandcont"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Set a bookmark
##

from Products.CMFPlone import PloneMessageFactory as _

url = context.absolute_url()
mtool = context.portal_membership
member = mtool.getAuthenticatedMember()
mtool.getAuthenticatedMember().setProperties(ctmbookmark=url)
nexturl = context.restrictedTraverse('@@plone_nextprevious_view').next()['url']
context.REQUEST.response.redirect(nexturl)

