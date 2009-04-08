##parameters=ids=[]

reference_tool = context.reference_catalog
obj1 = reference_tool.lookupObject(ids[0])
obj2 = reference_tool.lookupObject(ids[1])

dtool = context.portal_diff
diffs = dtool.createChangeSet(obj1, obj2).getDiffs()

ignore_list = context.getIgnoreFields()

diffs = [d for d in diffs if d.field not in ignore_list]

return context.at_changeset(obj1=obj1,
                            obj2=obj2,
                            diffs=diffs)
