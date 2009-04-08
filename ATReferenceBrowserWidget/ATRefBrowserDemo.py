""" demonstrates the use of ATReferenceBrowserWidget """

from Products.Archetypes.atapi import *

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *
from DateTime import DateTime


schema = BaseSchema +  Schema((
    ReferenceField('singleRef', 
                   multiValued=0,
                   allowed_types=('ATDocument','ATFile', 'Article', 'ATRefBrowserDemo'),
                   relationship='Rel1',
                   widget=ReferenceBrowserWidget(default_search_index='SearchableText', description='This is the first field. Pick an object.')),
    ReferenceField('multiRef', 
                   multiValued=1,
                   relationship='Rel2',
                   widget=ReferenceBrowserWidget(show_indexes=1, description='And here is another field with a longer description text to explain the user better what to do with this field.')) ,
    ReferenceField('multiRef2', 
                   multiValued=1,
                   relationship='Rel3',
                   widget=ReferenceBrowserWidget(allow_search=1, 
                                                 allow_browse=0,
                                                 show_indexes=1, 
                                                 available_indexes={'SearchableText':'Free text search',
                                                                    'Description': "Object's description"},
                                                 description='And here is another field.')) ,    
    ReferenceField('multiRef3', 
                   multiValued=1,
                   relationship='Rel3',
                   widget=ReferenceBrowserWidget(show_indexes=1, 
                                                 description='And here is another field.',
                                                 startup_directory='/Members')) ,
    ReferenceField('multiRef4',
                   multiValued=1,
                   relationship='Rel4',
                   widget=ReferenceBrowserWidget(show_indexes=1,
                                                 allow_browse=0,
                                                 description='And here is another field with a fixed query restriction (only published objects will appear).',
                                                 base_query={'review_state':'published'},
                                                 )) ,
    ReferenceField('multiRef5',
                   multiValued=1,
                   relationship='Rel5',
                   widget=ReferenceBrowserWidget(show_indexes=1,
                                                 allow_browse=0,
                                                 description='And here is another field with some dynamic query restrictions (only objects with "start" withing one week of the current date will appear).',
                                                 base_query='dynamicBaseQuery',
                                                 )) ,
    
                              ))

class ATRefBrowserDemo(BaseContent):
    """
    Demo from ATReferenceBrowserWidget
    """
    content_icon = "document_icon.gif"
    schema = schema
    def dynamicBaseQuery(self):
        """This example function generates a base query which ensures that only
        objects whose start property is within one week of the current day"""
        return {'start': {'query':[DateTime()-7,DateTime()+7], 'range':'minmax'}}
    

registerType(ATRefBrowserDemo)
