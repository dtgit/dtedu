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
"""AT Content Types general interface

"""
__author__  = 'Jean-Francois Roche <jfroche@jfroche.be>'
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute

from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IBaseFolder
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.Archetypes.interfaces import IATHistoryAware

from Products.CMFPlone.interfaces.constrains import \
    ISelectableConstrainTypes


class IATContentType(ISelectableBrowserDefault, IBaseContent):
    """Marker interface for AT Content Types
    """

    default_view = Attribute('''Default view template - used for dynamic view''')
    suppl_views = Attribute('''Supplementary views - used for dynamic view''')

    _atct_newTypeFor = Attribute('''XXX''')

    assocMimetypes = Attribute('''A tuple of mimetypes that are associated
                                  with this type. Format: ('bar/foo', 'foo/*',)
                               ''')

    assocFileExt = Attribute('''A tuple of file extensions that are associated
                                with this type. Format: ('jpeg', 'png',)
                             ''')

    cmf_edit_kws = Attribute('''List of keyword names.
    
    If one of this kw names is used with edit() then the cmf_edit method is
    called.
    ''')

class IHistoryAware(IATHistoryAware):
    """History awareness marker interface
    """

    def getHistorySource():
        """get source for HistoryAwareMixin

        Must return a (raw) string
        """

    def getLastEditor():
        """Returns the user name of the last editor.

        Returns None if no last editor is known.
        """

    def getDocumentComparisons(max=10, filterComment=0):
        """Get history as unified diff
        """

class ICalendarSupport(Interface):
    """Calendar import/export
    """


class ITextContent(Interface):
    """Interface for types containing text
    """

    def getText(**kwargs):
        """
        """

    def setText(value, **kwargs):
        """
        """
        
    def CookedBody(stx_level='ignored'):
        """
        """

    def EditableBody():
        """
        """

from Products.ATContentTypes.interface.link import IATLink
class IATFavorite(IATLink):
    """AT Favorite marker interface
    """

class IATCTTool(Interface):
    """
    """
 
