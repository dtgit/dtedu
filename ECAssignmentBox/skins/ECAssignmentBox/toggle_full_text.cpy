## Script (Python) "toggle_full_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# This script redirects to the same location it got called from,
# except that the value of 'show_superseded' in the query string is
# negated.

I18N_DOMAIN = 'eduComponents'

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE
ecab_utils = context.ecab_utils

oquery = ecab_utils.parseQueryString(REQUEST.QUERY_STRING)
query = {}
# "unlistify" the values that `parseQueryString' returned
for k,v in oquery.items():
    query[k]=v[0]

# Negate value of 'fullText'
showFullText = query.get('show_full_text', None)
if showFullText:
    showFullText = ''
else:
    showFullText = 1

query['show_full_text'] = showFullText

# in the following we use redirect to go back to the template
# this overrides settings in toggle_superseded.cpy.metadata
orig_template = 'all_assignments'

if REQUEST.has_key('orig_template'):
    orig_template = REQUEST['orig_template']

    
#target = context.getActionInfo('object/%s' % orig_template)['url']
target = '%s/%s' % (context.absolute_url(), orig_template)
 
return RESPONSE.redirect('%s?%s' % (target, ecab_utils.urlencode(query)))
