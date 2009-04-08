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
""" GenericSetup export / import support for topics / criteria.

$Id: exportimport.py 71021 2006-11-01 16:23:56Z yuppie $
"""

from xml.dom.minidom import parseString

from zope.interface import implements

from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.GenericSetup.content import FolderishExporterImporter

try:
    from Products.GenericSetup.utils import PageTemplateResource
except ImportError: # BBB:  no egg support
    from Products.PageTemplates.PageTemplateFile \
        import PageTemplateFile as PageTemplateResource


from Topic import Topic

class TopicExportImport(FolderishExporterImporter):
    """ Dump topic criteria to / from an XML file.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    encoding = None
    _FILENAME = 'criteria.xml'
    _ROOT_TAGNAME = 'criteria'

    def __init__(self, context):
        self.context = context

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        criteria_metatypes = self.context._criteria_metatype_ids()
        return [x for x in FolderishExporterImporter.listExportableItems(self)
                   if x[1].meta_type not in criteria_metatypes]

    def export(self, export_context, subdir, root=False):
        """ See IFilesystemExporter.
        """
        FolderishExporterImporter.export(self, export_context, subdir, root)
        template = PageTemplateResource('xml/%s' % self._FILENAME,
                                        globals()).__of__(self.context)
        export_context.writeDataFile('%s/criteria.xml' % self.context.getId(),
                                     template(info=self._getExportInfo()),
                                     'text/xml',
                                     subdir,
                                    )

    def import_(self, import_context, subdir, root=False):
        """ See IFilesystemImporter
        """
        FolderishExporterImporter.import_(self, import_context, subdir, root)

        self.encoding = import_context.getEncoding()

        if import_context.shouldPurge():
            self._purgeContext()

        data = import_context.readDataFile('%s/criteria.xml'
                                                % self.context.getId(),
                                           subdir)

        if data is not None:
            dom = parseString(data)
            root = dom.firstChild
            assert root.tagName == self._ROOT_TAGNAME
            self._updateFromDOM(root)

    def _getNodeAttr(self, node, attrname, default=None):
        attr = node.attributes.get(attrname)
        if attr is None:
            return default
        value = attr.value
        if isinstance(value, unicode) and self.encoding is not None:
            value = value.encode(self.encoding)
        return value

    def _purgeContext(self):
        context = self.context
        criterion_ids = context.objectIds(context._criteria_metatype_ids())
        for criterion_id in criterion_ids:
            self.context._delObject(criterion_id)

    def _updateFromDOM(self, root):
        for criterion in root.getElementsByTagName('criterion'):
            c_type = self._getNodeAttr(criterion, 'type', None)
            field = self._getNodeAttr(criterion, 'field', None)
            attributes = {}
            for attribute in criterion.getElementsByTagName('attribute'):
                name = self._getNodeAttr(attribute, 'name', None)
                value = self._getNodeAttr(attribute, 'value', None)
                if name == 'reversed':
                    value = value in ('True', 'true', '1')
                attributes[name] = value

            self.context.addCriterion(field, c_type)
            added = self.context.getCriterion(field)
            added.edit(**attributes)

    def _getExportInfo(self):
        context = self.context
        criterion_info = []

        for criterion_id, criterion in context.objectItems(
                                        context._criteria_metatype_ids()):

            # SortCriterion stashes the 'field' as 'index'.
            field = getattr(criterion, 'index', criterion.field)

            info = {'criterion_id': criterion_id,
                    'type': criterion.meta_type,
                    'field': field,
                    'attributes': []
                   }

            attributes = info['attributes']
            for attrname in criterion.editableAttributes():
                value = getattr(criterion, attrname)
                if type(value) in (tuple, list):
                    value = ','.join(value)
                attributes.append((attrname, value))

            criterion_info.append(info)

        return {'criteria': criterion_info,
               }

    def _mustPreserve(self):
        context = self.context
        keepers = FolderishExporterImporter._mustPreserve(self)
        keepers.extend(context.objectItems(context._criteria_metatype_ids()))
        return keepers


class SubtopicFactory(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, id):
        topic = Topic(id)
        topic.portal_type = 'Topic'
        return topic
