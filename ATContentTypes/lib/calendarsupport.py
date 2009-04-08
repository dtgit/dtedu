#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""Calendar export / import

"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from cStringIO import StringIO

from DateTime import DateTime
from Globals import InitializeClass

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.interfaces import ICalendarSupport

PRODID = "-//AT Content Types//AT Event//EN"

# iCal header and footer
ICS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)s
VERSION:2.0
METHOD:PUBLISH
"""

ICS_FOOTER = """\
END:VCALENDAR
"""

# Note: a previous version of event start set "SEQUENCE:0"
# That's not necessary unless we're supporting recurrence.

# iCal event
ICS_EVENT_START = """\
BEGIN:VEVENT
DTSTAMP:%(dtstamp)s
CREATED:%(created)s
UID:ATEvent-%(uid)s
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
DTSTART:%(startdate)s
DTEND:%(enddate)s
"""

# Note: a previous version of event end set "TRANSP:OPAQUE", which would cause
# blocking of the time slot. That's not appropriate for an event
# calendar.
# Also, previous version set "PRIORITY:3", which the RFC interprets as a high
# priority. In absence of a priority field in the event, there's no justification
# for that.

ICS_EVENT_END = """\
CLASS:PUBLIC
END:VEVENT
"""

# vCal header and footer
VCS_HEADER = """\
BEGIN:VCALENDAR
PRODID:%(prodid)s
VERSION:1.0
"""

VCS_FOOTER = """\
END:VCALENDAR
"""

# vCal event
VCS_EVENT_START = """\
BEGIN:VEVENT
DTSTART:%(startdate)s
DTEND:%(enddate)s
DCREATED:%(created)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
"""

VCS_EVENT_END = """\
PRIORITY:3
TRANSP:0
END:VEVENT
"""

class CalendarSupportMixin:
    """Mixin class for iCal/vCal support
    """

    __implements__ = (ICalendarSupport, )

    security       = ClassSecurityInfo()

    actions = ({
        'id'          : 'ics',
        'name'        : 'iCalendar',
        'action'      : 'string:${object_url}/ics_view',
        'permissions' : (View, ),
        'category'    : 'document_actions',
         },
         {
        'id'          : 'vcs',
        'name'        : 'vCalendar',
        'action'      : 'string:${object_url}/vcs_view',
        'permissions' : (View, ),
        'category'    : 'document_actions',
         },
    )

    _at_action_icons = ({
        'category'  : 'plone',
        'action_id' : 'ics',
        'icon_expr' : 'ical_icon.gif',
        'title'     : 'iCalendar export',
        'priority'  : 0,
        },
        {
        'category'  : 'plone',
        'action_id' : 'vcs',
        'icon_expr' : 'vcal_icon.gif',
        'title'     : 'vCalendar export',
        'priority'  : 0,
        },
        )

    security.declareProtected(View, 'getICal')
    def getICal(self):
        """get iCal data
        """
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.CreationDate())),
            'uid'       : self.UID(),
            'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
            'summary'   : vformat(self.Title()),
            'startdate' : rfc2445dt(self.start()),
            'enddate'   : rfc2445dt(self.end()),
            }
        out.write(ICS_EVENT_START % map)
        
        description = self.Description()
        if description:
            out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))

        location = self.getLocation()
        if location:
            out.write('LOCATION:%s\n' % vformat(location))

        eventType = self.getEventType()
        if eventType:
            out.write('CATEGORIES:%s\n' % ','.join(eventType))

        # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)

        cn = []
        contact = self.contact_name()
        if contact:
            cn.append(contact)
        phone = self.contact_phone()
        if phone:
            cn.append(phone)
        email = self.contact_email()
        if email:
            cn.append(email)
        if cn:
            out.write('CONTACT:%s\n' % vformat(', '.join(cn)))

        url = self.event_url()
        if url:
            out.write('URL:%s\n' % url)

        out.write(ICS_EVENT_END)
        return out.getvalue()


    security.declareProtected(View, 'ics_view')
    def ics_view(self, REQUEST, RESPONSE):
        """iCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/calendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.ics"' % self.getId())
        out = StringIO()
        out.write(ICS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getICal())
        out.write(ICS_FOOTER)
        return n2rn(out.getvalue())

    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.CreationDate())),
            'uid'       : self.UID(),
            'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
            'summary'   : vformat(self.Title()),
            'startdate' : rfc2445dt(self.start()),
            'enddate'   : rfc2445dt(self.end()),
            }
        out.write(VCS_EVENT_START % map)
        description = self.Description()
        if description:
            out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
        location = self.getLocation()
        if location:
            out.write('LOCATION:%s\n' % vformat(location))
        out.write(VCS_EVENT_END)
        # TODO
        # Insert missing code here :]
        return out.getvalue()

    security.declareProtected(View, 'vcs_view')
    def vcs_view(self, REQUEST, RESPONSE):
        """vCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/x-vCalendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.vcs"' % self.getId())
        out = StringIO()
        out.write(VCS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getVCal())
        out.write(VCS_FOOTER)
        return n2rn(out.getvalue())

InitializeClass(CalendarSupportMixin)

def vformat(s):
    # return string with escaped commas, colons and semicolons
    return s.strip().replace(',','\,').replace(':','\:').replace(';','\;')

def n2rn(s):
    return s.replace('\n', '\r\n')

def rfc2445dt(dt):
    # return UTC in RFC2445 format YYYYMMDDTHHMMSSZ
    return dt.HTML4().replace('-','').replace(':','')

def foldLine(s):
    # returns string folded per RFC2445 (each line must be less than 75 octets)
    # This code is a minor modification of MakeICS.py, available at:
    # http://www.zope.org/Members/Feneric/MakeICS/
    
    lineLen = 70
    
    workStr = s.strip().replace('\r\n','\n').replace('\r','\n').replace('\n','\\n')
    numLinesToBeProcessed = len(workStr)/lineLen
    startingChar = 0
    res = ''
    while numLinesToBeProcessed >= 1:
        res = '%s%s\n '%(res, workStr[startingChar:startingChar+lineLen])
        startingChar += lineLen
        numLinesToBeProcessed -= 1
    return '%s%s\n' % (res, workStr[startingChar:])

