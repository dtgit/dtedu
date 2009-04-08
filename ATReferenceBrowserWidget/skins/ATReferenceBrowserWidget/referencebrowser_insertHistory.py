##parameters=path, history_length=20

# Insert 'at_url' into the list of visited path in front.
# The history is stored as list of tuples
# (relative path to Zope root, relative_path to Plone portal root)

history = context.REQUEST.SESSION.get('atrefbrowserwidget_history', [])
portal_path = context.portal_url.getPortalObject().absolute_url(1)

# remove existing entries
for i, tp in enumerate(history):
    if path == tp[0]:
        del history[i]
        break

# generate a friendly path for UI representation        
visible_path = context.absolute_url(1)
visible_path = visible_path.replace(portal_path, '')

# insert at the head of the history list
history.insert(0, (path, visible_path))

# cut off oversized history
history = history[:history_length]

# put it back into the session
history = context.REQUEST.SESSION.set('atrefbrowserwidget_history', history)
