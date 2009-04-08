## Script (Python) "onEditChangeSet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ob1_path, ob2_path
##title=Compute object differences
##

ob1 = context.restrictedTraverse(ob1_path)
ob2 = context.restrictedTraverse(ob2_path)

context.computeDiff(ob1, ob2)
context.REQUEST.RESPONSE.redirect('.')
