##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PluginIndexes export / import support.

$Id: exportimport.py 71199 2006-11-20 11:03:29Z yuppie $
"""

from zope.component import adapts
from zope.component import queryMultiAdapter

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import NodeAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.PluginIndexes.interfaces import IDateIndex
from Products.PluginIndexes.interfaces import IDateRangeIndex
from Products.PluginIndexes.interfaces import IFilteredSet
from Products.PluginIndexes.interfaces import IPathIndex
from Products.PluginIndexes.interfaces import IPluggableIndex
from Products.PluginIndexes.interfaces import ITextIndex
from Products.PluginIndexes.interfaces import ITopicIndex
from Products.PluginIndexes.interfaces import IVocabulary


class PluggableIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for FieldIndex, KeywordIndex.
    """

    adapts(IPluggableIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        for value in self.context.getIndexSourceNames():
            child = self._doc.createElement('indexed_attr')
            child.setAttribute('value', value)
            node.appendChild(child)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        indexed_attrs = []
        for child in node.childNodes:
            if child.nodeName == 'indexed_attr':
                indexed_attrs.append(
                                  child.getAttribute('value').encode('utf-8'))
        self.context.indexed_attrs = indexed_attrs
        self.context.clear()

    node = property(_exportNode, _importNode)


class DateIndexNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):

    """Node im- and exporter for DateIndex.
    """

    adapts(IDateIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        node.appendChild(self._extractProperties())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()

        self._initProperties(node)
        self.context.clear()

    node = property(_exportNode, _importNode)


class DateRangeIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for DateRangeIndex.
    """

    adapts(IDateRangeIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        node.setAttribute('since_field', self.context.getSinceField())
        node.setAttribute('until_field', self.context.getUntilField())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self.context._edit(node.getAttribute('since_field').encode('utf-8'),
                           node.getAttribute('until_field').encode('utf-8'))
        self.context.clear()

    node = property(_exportNode, _importNode)


class PathIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for PathIndex.
    """

    adapts(IPathIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        return self._getObjectNode('index')

    node = property(_exportNode, lambda self, val: None)


class VocabularyNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for Vocabulary.
    """

    adapts(IVocabulary, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.setAttribute('deprecated', 'True')
        return node

    node = property(_exportNode, lambda self, val: None)


class TextIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for TextIndex.
    """

    adapts(ITextIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        node.setAttribute('deprecated', 'True')
        return node

    node = property(_exportNode, lambda self, val: None)


class FilteredSetNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for FilteredSet.
    """

    adapts(IFilteredSet, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('filtered_set')
        node.setAttribute('expression', self.context.getExpression())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self.context.setExpression(
                              node.getAttribute('expression').encode('utf-8'))
        self.context.clear()

    node = property(_exportNode, _importNode)


class TopicIndexNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for TopicIndex.
    """

    adapts(ITopicIndex, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        for set in self.context.filteredSets.values():
            exporter = queryMultiAdapter((set, self.environ), INode)
            node.appendChild(exporter.node)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        for child in node.childNodes:
            if child.nodeName == 'filtered_set':
                set_id = str(child.getAttribute('name'))
                if set_id not in self.context.filteredSets:
                    set_meta_type = str(child.getAttribute('meta_type'))
                    self.context.addFilteredSet(set_id, set_meta_type, '')
                set = self.context.filteredSets[set_id]
                importer = queryMultiAdapter((set, self.environ), INode)
                importer.node = child
        self.context.clear()

    node = property(_exportNode, _importNode)
