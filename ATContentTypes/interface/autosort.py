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

from zope.interface import Interface
from zope.interface import Attribute
from zope.app.container.interfaces import IOrderedContainer
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

class IAutoOrderSupport(IAutoSortSupport, IOrderedContainer):
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

