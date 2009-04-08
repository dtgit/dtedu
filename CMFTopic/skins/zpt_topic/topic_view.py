##parameters=b_start=0
##
from ZTUtils import Batch
from Products.CMFDefault.utils import decode


options = {}

subtopics = [ {'title': item.Title() or item.getId(),
               'url': item.absolute_url()}
              for item in context.contentValues() ]
options['listSubtopicInfos'] = subtopics

queries = context.buildQuery()
options['listQueries'] = tuple([ '%s: %s' % q for q in queries.items() ])

target = context.REQUEST['ACTUAL_URL']
items = context.queryCatalog()
batch_obj = Batch(items, 20, b_start, orphan=1)

items = [ {'creators': item.listCreators,
           'date': item.Date,
           'description': item.Description,
           'id': item.getId,
           'title': item.Title and ('(%s)' % item.Title) or '',
           'url': '%s/view' % item.getURL()}
          for item in batch_obj ]

navigation = context.getBatchNavigation(batch_obj, target)
options['batch'] = {'listItemInfos': items,
                    'navigation': navigation}

return context.topic_view_template(**decode(options, script))
