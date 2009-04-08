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
"""ATContentTypes Zope3 Interfaces
"""
from Products.ATContentTypes.interface.interfaces import IATContentType
from Products.ATContentTypes.interface.interfaces import IHistoryAware
from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.interface.interfaces import ITextContent
from Products.ATContentTypes.interface.interfaces import IATFavorite
from Products.ATContentTypes.interface.interfaces import ISelectableConstrainTypes
from Products.ATContentTypes.interface.interfaces import IATCTTool

from Products.ATContentTypes.interface.archive import IArchiveAccumulator
from Products.ATContentTypes.interface.archive import IFilterFolder
from Products.ATContentTypes.interface.archive import IArchiver
from Products.ATContentTypes.interface.archive import IDataExtractor
from Products.ATContentTypes.interface.archive import IArchivable

from Products.ATContentTypes.interface.dataExtractor import IDataExtractor

from Products.ATContentTypes.interface.document import IATDocument

from Products.ATContentTypes.interface.event import IATEvent

from Products.ATContentTypes.interface.file import IFileContent
from Products.ATContentTypes.interface.file import IATFile

from Products.ATContentTypes.interface.folder import IFilterFolder
from Products.ATContentTypes.interface.folder import IATFolder
from Products.ATContentTypes.interface.folder import IATBTreeFolder

from Products.ATContentTypes.interface.image import IPhotoAlbum
from Products.ATContentTypes.interface.image import IPhotoAlbumAble
from Products.ATContentTypes.interface.image import IImageContent
from Products.ATContentTypes.interface.image import IATImage

from Products.ATContentTypes.interface.link import IATLink

from Products.ATContentTypes.interface.news import IATNewsItem

from Products.ATContentTypes.interface.topic import IATTopic
from Products.ATContentTypes.interface.topic import IATTopicCriterion
from Products.ATContentTypes.interface.topic import IATTopicSearchCriterion
from Products.ATContentTypes.interface.topic import IATTopicSortCriterion
from Products.ATContentTypes.interface.topic import IATCTTopicsTool

from Products.ATContentTypes.interface.autosort import IAutoSortSupport
from Products.ATContentTypes.interface.autosort import IAutoOrderSupport

from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
