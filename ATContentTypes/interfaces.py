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
"""AT Content Types general Zope 2 interfaces

All these interfaces are DEPRECATED.
Please use Z3 interfaces defined in the interface folder


"""

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Interface import Interface


from Interface import Attribute

from Products.Archetypes.interfaces.base import IBaseContent
from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault

from Products.Archetypes.OrderedBaseFolder import IOrderedContainer
from Products.Archetypes.OrderedBaseFolder import IZopeOrderedContainer
from Products.Archetypes.interfaces.athistoryaware import IATHistoryAware

from Products.CMFPlone.interfaces.ConstrainTypes import \
    ISelectableConstrainTypes

_marker = object()

class IAutoSortSupport(Interface):
    """Interface for auto sorting
    """

    _default_sort_key = Attribute('Sort key, default: Title')
    _default_sort_reverse = Attribute('Reverse, default: False')
    _default_sort_folderish_first = Attribute('Sort folderish first, default: True')
    # auto sort flag is required to make tpValues happy
    _default_sort_auto = Attribute('Enable auto, default: True')

    def setDefaultSorting(key, reverse=_marker):
        """Set default sorting key and direction.
        """

    def getDefaultSorting():
        """Get default sorting key and direction.

        Return sort_on attribute, reverse
        sort_on attribute is either an attribute or method name
        """

    def setSortFolderishFirst(value):
        """Set the value for sorting folderish objects before ordinary items
        """

    def getSortFolderishFirst():
        """Get the value for sorting folderish objects before ordinary items
        """

    def setSortReverse(value):
        """Set reverse sort setting
        """

    def getSortReverse():
        """Get reverse sort setting
        """

    def setSortAuto(value):
       """Set auto sort setting
       """

    def getSortAuto():
        """Get auto sort setting
        """

class IAutoOrderSupport(IAutoSortSupport, IOrderedContainer, IZopeOrderedContainer):
    """Interface for auto sorting and auto ordering
    """

    def autoOrderItems():
        """Auto order all containing items according to the settings
        """

    def moveObjectsByDelta(ids, delta, subset_ids=None, disable_auto_sort=True):
        """Move specified sub-objects by delta.

        Overwritten to disable auto sort
        """

    def manage_renameObject(id, new_id, REQUEST=None):
        """Rename a particular sub-object without changing its position.

        Overwritten to keep auto sort
        """

    def manage_afterAdd(item, container):
        """after add hook

        Overwritten to auto sort items
        """



class IATContentType(ISelectableBrowserDefault, IBaseContent):
    """interface for AT Content Types
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

class IImageContent(Interface):
    """Interface for types containing an image
    """

    def getImage(**kwargs):
        """
        """

    def setImage(value, **kwargs):
        """
        """

    def tag(**kwargs):
        """
        """

class IFileContent(Interface):
    """Interface for types containing a file
    """

    def getFile(**kwargs):
        """
        """

    def setFile(value, **kwargs):
        """
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

# content types

class IATDocument(ITextContent):
    """AT Document marker interface
    """

class IATEvent(IATContentType):
    """AT Event marker interface
    """

class IATLink(IATContentType):
    """AT Link marker interface
    """

class IATFile(IFileContent):
    """AT File marker interface
    """

class IATFolder(IATContentType):
    """AT Folder marker interface
    """

class IATBTreeFolder(IATContentType):
    """AT BTree Folder marker interface
    """

class IATImage(IImageContent):
    """AT Image marker Interface
    """

class IATLink(IATContentType):
    """AT Link marker interface
    """

# second class content types

class IATNewsItem(IATDocument, IImageContent):
    """AT News Item marker interface
    """


class IATFavorite(IATLink):
    """AT Favorite marker interface
    """

# topic types

class IATTopic(IATContentType):
    """AT Topic marker interface
    """

    def listCriteriaTypes():
        """List available criteria types as dict
        """

    def listCriteriaMetaTypes():
        """List available criteria
        """

    def listSearchCriteriaTypes():
        """List available search criteria types as dict
        """

    def listSearchCriteriaMetaTypes():
        """List available search criteria
        """

    def listSortCriteriaTypes():
        """List available sort criteria types as dict
        """

    def listSortCriteriaMetaTypes():
        """List available sort criteria
        """

    def listCriteria():
        """Return a list of our criteria objects.
        """

    def listSearchCriteria():
        """Return a list of our search criteria objects.
        """

    def hasSortCriterion():
        """Tells if a sort criterai is already setup.
        """

    def getSortCriterion():
        """Return the Sort criterion if setup.
        """

    def removeSortCriterion():
        """remove the Sort criterion.
        """

    def setSortCriterion(field, reversed):
        """Set the Sort criterion.
        """

    def listAvailableFields():
        """Return a list of available fields for new criteria.
        """

    def listSortFields():
        """Return a list of available fields for sorting."""

    def listSubtopics():
        """Return a list of our subtopics.
        """

    def buildQuery():
        """Construct a catalog query using our criterion objects.
        """

    def queryCatalog(REQUEST=None, **kw):
        """Invoke the catalog using our criteria to augment any passed
            in query before calling the catalog.
        """

    def addCriterion(field, criterion_type):
        """Add a new search criterion.
        """

    def deleteCriterion(criterion_id):
        """Delete selected criterion.
        """

    def getCriterion(criterion_id):
        """Get the criterion object.
        """

    def addSubtopic(id):
        """Add a new subtopic.
        """


class IATTopicCriterion(Interface):
    """AT Topic Criterion interface
    """

    def widget(field_name, mode="view", field=None, **kwargs):
        """redefine widget() to allow seperate field_names from field
        """

    def getId():
        """get the objects id
        """

    def Type():
        """
        """

    def Description():
        """
        """

    def getCriteriaItems():
        """Return a sequence of items to be used to build the catalog query.
        """

class IATTopicSearchCriterion(IATTopicCriterion):
    """Interface for criteria used for searching
    """

class IATTopicSortCriterion(IATTopicCriterion):
    """Interface for criteria used for sorting
    """

class IATCTTool(Interface):
    """
    """

class IATCTTopicsTool(Interface):
    """Mixin class for providing features to customize the display of topics
    """
