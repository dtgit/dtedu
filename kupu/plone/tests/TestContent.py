from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
try:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
except:
    ReferenceBrowserWidget = ReferenceWidget

schema = Schema((
    ReferenceField('singleRef', 
                   multiValued=0,
                   allowed_types=('Document', 'File'),
                   relationship='Rel1',
                   widget=ReferenceBrowserWidget(default_search_index='SearchableText',)),

    # multiRef: allows browsing.
    ReferenceField('multiRef', 
                   multiValued=1,
                   relationship='Rel2',
                   widget=ReferenceBrowserWidget(show_indexes=1,)),

    # multiRef2: no browse
    ReferenceField('multiRef2', 
                   multiValued=1,
                   allowed_types=('Document', 'ATDocument'),
                   relationship='Rel3',
                   widget=ReferenceBrowserWidget(allow_search=1, 
                                                 allow_browse=0,
                                                 show_indexes=1, 
                                                 available_indexes={'SearchableText':'Free text search',
                                                                    'Description': "Object's description"},
                                                )),
    ReferenceField('multiRef3',
                   multiValued=1,
                   relationship='Rel3',
                   widget=ReferenceBrowserWidget(show_indexes=1,
                                                 allow_browse=1,
                                                 base_query={'Subject':'aspidistra'},
                                                 )),
    ReferenceField('multiRef4',
                   multiValued=1,
                   relationship='Rel4',
                   widget=ReferenceBrowserWidget(show_indexes=1,
                                                 allow_browse=0,
                                                 base_query={'Subject':'aspidistra'},
                                                 )),
    ReferenceField('multiRef5',
                   multiValued=1,
                   relationship='Rel5',
                   widget=ReferenceBrowserWidget(show_indexes=1,
                                                 allow_browse=0,
                                                 base_query='dynamicBaseQuery',
                                                 )),
    
                              ))

class TestContent(BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)
    archetype_name = 'TestContent'
    meta_type = portal_type = 'TestContent'

    schema = BaseSchema + \
             schema

registerType(TestContent,'kupu')
