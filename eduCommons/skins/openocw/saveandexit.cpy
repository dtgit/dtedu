## Controller Python Script "saveandexit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Set a bookmark and exit to social network
##

from Products.CMFPlone import PloneMessageFactory as _

url = context.absolute_url()
mtool = context.portal_membership
member = mtool.getAuthenticatedMember()
member.setProperties(ctmbookmark=url)
nexturl = context.restrictedTraverse('@@plone_nextprevious_view').next()['url']
context.REQUEST.response.redirect('http://connect.teacherswithoutborders.org')

