##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for events.

$Id: event.py 77019 2007-06-24 19:01:14Z hannosch $
"""

from zope.app.form.browser import DatetimeI18nWidget
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Set
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import URI

from Products.CMFCore.interfaces import IMetadataTool
from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.formlib.form import DisplayFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.vocabulary import SimpleVocabulary

from Products.CMFCalendar.interfaces import IMutableEvent
from Products.CMFCalendar.utils import Message as _


class EventTypeVocabulary(object):

    """Vocabulary factory for available event types.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        mdtool = getUtility(IMetadataTool)
        items = [ (str(v), unicode(v), _(v))
                  for v in mdtool.listAllowedSubjects(context) ]
        return SimpleVocabulary.fromTitleItems(items)

EventTypeVocabularyFactory = EventTypeVocabulary()


class IEventSchema(Interface):

    """Schema for event views.
    """

    title = TextLine(
        title=_(u'Title'),
        required=False,
        missing_value=u'',
        max_length=100)

    contact_name = TextLine(
        title=_(u'Contact Name'),
        required=False,
        missing_value=u'',
        max_length=100)

    location = TextLine(
        title=_(u'Location'),
        required=False,
        missing_value=u'',
        max_length=100)

    contact_email = EmailLine(
        title=_(u'Contact Email'),
        required=False)

    categories = Set(
        title=_(u'Category'),
        required=False,
        missing_value=set(),
        value_type=Choice(vocabulary="cmf.calendar.AvailableEventTypes"))

    contact_phone = TextLine(
        title=_(u'Contact Phone'),
        required=False,
        missing_value=u'',
        max_length=100)

    event_url = URI(
        title=_(u'URL'),
        required=False,
        missing_value=u'',
        max_length=100)

    start_date = Datetime(
        title=_(u'From'),)

    stop_date = Datetime(
        title=_(u'To'),)

    description = Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'')


class EventSchemaAdapter(SchemaAdapterBase):

    """Adapter for IMutableEvent.
    """

    adapts(IMutableEvent)
    implements(IEventSchema)

    title = ProxyFieldProperty(IEventSchema['title'], 'Title', 'setTitle')
    contact_name = ProxyFieldProperty(IEventSchema['contact_name'])
    location = ProxyFieldProperty(IEventSchema['location'])
    contact_email = ProxyFieldProperty(IEventSchema['contact_email'])
    categories = ProxyFieldProperty(IEventSchema['categories'],
                                    'Subject', 'setSubject')
    contact_phone = ProxyFieldProperty(IEventSchema['contact_phone'])
    event_url = ProxyFieldProperty(IEventSchema['event_url'])
    start_date = ProxyFieldProperty(IEventSchema['start_date'],
                                    'start', 'setStartDate')
    stop_date = ProxyFieldProperty(IEventSchema['stop_date'],
                                   'end', 'setEndDate')
    description = ProxyFieldProperty(IEventSchema['description'],
                                     'Description', 'setDescription')


class EventViewMixin(object):

    def setUpWidgets(self, ignore_request=False):
        super(EventViewMixin,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['title'].split = True
        self.widgets['contact_name'].split = True
        self.widgets['location'].split = True
        self.widgets['contact_email'].split = True
        self.widgets['categories'].split = True
        self.widgets['categories'].size = 4
        self.widgets['contact_phone'].split = True
        self.widgets['start_date'].split = True
        self.widgets['stop_date'].split = True
        self.widgets['description'].height = 5


class EventView(EventViewMixin, DisplayFormBase):

    """View for IEvent.
    """

    form_fields = form.FormFields(IEventSchema)


class EventEditView(EventViewMixin, ContentEditFormBase):

    """Edit view for IMutableEvent.
    """

    form_fields = form.FormFields(IEventSchema)
    form_fields['start_date'].custom_widget = DatetimeI18nWidget
    form_fields['stop_date'].custom_widget = DatetimeI18nWidget
