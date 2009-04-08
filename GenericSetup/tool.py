##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes:  SetupTool

$Id: tool.py 82137 2007-12-05 09:34:56Z wichert $
"""

import os
import time
import logging
from warnings import warn
from cgi import escape

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from OFS.Folder import Folder
from OFS.Image import File
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.interface import implementedBy

from interfaces import BASE
from interfaces import EXTENSION
from interfaces import ISetupTool
from interfaces import SKIPPED_FILES
from permissions import ManagePortal
from context import DirectoryImportContext
from context import SnapshotImportContext
from context import TarballExportContext
from context import TarballImportContext
from context import SnapshotExportContext
from differ import ConfigDiff
from registry import ImportStepRegistry
from registry import ExportStepRegistry
from registry import ToolsetRegistry
from registry import _profile_registry

from upgrade import listUpgradeSteps
from upgrade import listProfilesWithUpgrades
from upgrade import _upgrade_registry

from utils import _getDottedName
from utils import _resolveDottedName
from utils import _wwwdir

IMPORT_STEPS_XML = 'import_steps.xml'
EXPORT_STEPS_XML = 'export_steps.xml'
TOOLSET_XML = 'toolset.xml'

def exportStepRegistries(context):

    """ Built-in handler for exporting import / export step registries.
    """
    setup_tool = context.getSetupTool()
    logger = context.getLogger('registries')

    import_steps_xml = setup_tool.getImportStepRegistry().generateXML()
    context.writeDataFile('import_steps.xml', import_steps_xml, 'text/xml')

    export_steps_xml = setup_tool.getExportStepRegistry().generateXML()
    context.writeDataFile('export_steps.xml', export_steps_xml, 'text/xml')

    logger.info('Step registries exported.')

def importToolset(context):

    """ Import required / forbidden tools from XML file.
    """
    site = context.getSite()
    encoding = context.getEncoding()
    logger = context.getLogger('toolset')

    xml = context.readDataFile(TOOLSET_XML)
    if xml is None:
        logger.info('Nothing to import.')
        return

    setup_tool = context.getSetupTool()
    toolset = setup_tool.getToolsetRegistry()

    toolset.parseXML(xml, encoding)

    existing_ids = site.objectIds()
    existing_values = site.objectValues()

    for tool_id in toolset.listForbiddenTools():

        if tool_id in existing_ids:
            site._delObject(tool_id)

    for info in toolset.listRequiredToolInfo():

        tool_id = str(info['id'])
        tool_class = _resolveDottedName(info['class'])

        existing = getattr(aq_base(site), tool_id, None)
        # Don't even initialize the tool again, if it already exists.
        if existing is None:
            try:
                new_tool = tool_class()
            except TypeError:
                new_tool = tool_class(tool_id)
            else:
                try:
                    new_tool._setId(tool_id)
                except (ConflictError, KeyboardInterrupt):
                    raise
                except:
                    # XXX: ImmutableId raises result of calling MessageDialog
                    pass

            site._setObject(tool_id, new_tool)
        else:
            unwrapped = aq_base(existing)
            if not isinstance(unwrapped, tool_class):
                site._delObject(tool_id)
                site._setObject(tool_id, tool_class())

    logger.info('Toolset imported.')

def exportToolset(context):

    """ Export required / forbidden tools to XML file.
    """
    setup_tool = context.getSetupTool()
    toolset = setup_tool.getToolsetRegistry()
    logger = context.getLogger('toolset')

    xml = toolset.generateXML()
    context.writeDataFile(TOOLSET_XML, xml, 'text/xml')

    logger.info('Toolset exported.')


class SetupTool(Folder):

    """ Profile-based site configuration manager.
    """

    implements(ISetupTool)

    meta_type = 'Generic Setup Tool'

    _baseline_context_id = ''
    # BBB _import_context_id is a vestige of a stateful import context
    _import_context_id = ''

    _profile_upgrade_versions = {}

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = str(id)
        self._import_registry = ImportStepRegistry()
        self._export_registry = ExportStepRegistry()
        self._export_registry.registerStep('step_registries',
                                           _getDottedName(exportStepRegistries),
                                           'Export import / export steps.',
                                          )
        self._toolset_registry = ToolsetRegistry()

    #
    #   ISetupTool API
    #
    security.declareProtected(ManagePortal, 'getEncoding')
    def getEncoding(self):

        """ See ISetupTool.
        """
        return 'utf-8'

    security.declareProtected(ManagePortal, 'getImportContextID')
    def getImportContextID(self):

        """ See ISetupTool.
        """
        warn('getImportContextId, and the very concept of a stateful '
             'active import context, is deprecated.  You can find the '
             'base profile that was applied using getBaselineContextID.',
             DeprecationWarning, stacklevel=2)
        return self._import_context_id

    security.declareProtected(ManagePortal, 'getBaselineContextID')
    def getBaselineContextID(self):

        """ See ISetupTool.
        """
        return self._baseline_context_id

    security.declareProtected(ManagePortal, 'setImportContext')
    def setImportContext(self, context_id, encoding=None):
        """ See ISetupTool.
        """
        warn('setImportContext is deprecated.  Use setBaselineContext to '
             'specify the baseline context, and/or runImportStepFromProfile '
             'to run the steps from a specific import context.',
             DeprecationWarning, stacklevel=2)
        self._import_context_id = context_id

        context_type = BASE  # snapshots are always baseline contexts
        if context_id.startswith('profile-'):
            profile_info = _profile_registry.getProfileInfo(context_id[8:])
            context_type = profile_info['type']

        if context_type == BASE:
            self.setBaselineContext(context_id, encoding)

    security.declareProtected(ManagePortal, 'setBaselineContext')
    def setBaselineContext(self, context_id, encoding=None):
        """ See ISetupTool.
        """
        self._baseline_context_id = context_id
        self.applyContextById(context_id, encoding)


    security.declareProtected(ManagePortal, 'applyContextById')
    def applyContextById(self, context_id, encoding=None):
        context = self._getImportContext(context_id)
        self.applyContext(context, encoding)


    security.declareProtected(ManagePortal, 'applyContext')
    def applyContext(self, context, encoding=None):
        self._updateImportStepsRegistry(context, encoding)
        self._updateExportStepsRegistry(context, encoding)

    security.declareProtected(ManagePortal, 'getImportStepRegistry')
    def getImportStepRegistry(self):

        """ See ISetupTool.
        """
        return self._import_registry

    security.declareProtected(ManagePortal, 'getExportStepRegistry')
    def getExportStepRegistry(self):

        """ See ISetupTool.
        """
        return self._export_registry

    security.declareProtected(ManagePortal, 'getToolsetRegistry')
    def getToolsetRegistry(self):

        """ See ISetupTool.
        """
        return self._toolset_registry

    security.declareProtected(ManagePortal, 'runImportStepFromProfile')
    def runImportStepFromProfile(self, profile_id, step_id,
                                 run_dependencies=True, purge_old=None):
        """ See ISetupTool.
        """
        old_context = self._import_context_id
        context = self._getImportContext(profile_id, purge_old)

        self.applyContext(context)

        info = self._import_registry.getStepMetadata(step_id)

        if info is None:
            self._import_context_id = old_context
            raise ValueError, 'No such import step: %s' % step_id

        dependencies = info.get('dependencies', ())

        messages = {}
        steps = []
        if run_dependencies:
            for dependency in dependencies:

                if dependency not in steps:
                    message = self._doRunImportStep(dependency, context)
                    messages[dependency] = message or ''
                    steps.append(dependency)

        message = self._doRunImportStep(step_id, context)
        message_list = filter(None, [message])
        message_list.extend( ['%s: %s' % x[1:] for x in context.listNotes()] )
        messages[step_id] = '\n'.join(message_list)
        steps.append(step_id)

        self._import_context_id = old_context

        return { 'steps' : steps, 'messages' : messages }

    security.declareProtected(ManagePortal, 'runImportStep')
    def runImportStep(self, step_id, run_dependencies=True, purge_old=None):

        """ See ISetupTool.
        """
        warn('The runImportStep method is deprecated.  Please use '
             'runImportStepFromProfile instead.',
             DeprecationWarning, stacklevel=2)
        return self.runImportStepFromProfile(self._import_context_id,
                                             step_id,
                                             run_dependencies,
                                             purge_old,
                                             )

    security.declareProtected(ManagePortal, 'runAllImportStepsFromProfile')
    def runAllImportStepsFromProfile(self, profile_id, purge_old=None):

        """ See ISetupTool.
        """
        __traceback_info__ = profile_id

        old_context = self._import_context_id
        context = self._getImportContext(profile_id, purge_old)

        result = self._runImportStepsFromContext(context, purge_old=purge_old)
        prefix = 'import-all-%s' % profile_id.replace(':', '_')
        name = self._mangleTimestampName(prefix, 'log')
        self._createReport(name, result['steps'], result['messages'])

        self._import_context_id = old_context

        return result

    security.declareProtected(ManagePortal, 'runAllImportSteps')
    def runAllImportSteps(self, purge_old=None):

        """ See ISetupTool.
        """
        warn('The runAllImportSteps method is deprecated.  Please use '
             'runAllImportStepsFromProfile instead.',
             DeprecationWarning, stacklevel=2)
        context_id = self._import_context_id
        return self.runAllImportStepsFromProfile(self._import_context_id,
                                                 purge_old)

    security.declareProtected(ManagePortal, 'runExportStep')
    def runExportStep(self, step_id):

        """ See ISetupTool.
        """
        return self._doRunExportSteps([step_id])

    security.declareProtected(ManagePortal, 'runAllExportSteps')
    def runAllExportSteps(self):

        """ See ISetupTool.
        """
        return self._doRunExportSteps(self._export_registry.listSteps())

    security.declareProtected(ManagePortal, 'createSnapshot')
    def createSnapshot(self, snapshot_id):

        """ See ISetupTool.
        """
        context = SnapshotExportContext(self, snapshot_id)
        messages = {}
        steps = self._export_registry.listSteps()

        for step_id in steps:

            handler = self._export_registry.getStep(step_id)

            if handler is None:
                logger = logging.getLogger('GenericSetup')
                logger.error('Step %s has an invalid handler' % step_id)
                continue

            messages[step_id] = handler(context)


        return { 'steps' : steps
               , 'messages' : messages
               , 'url' : context.getSnapshotURL()
               , 'snapshot' : context.getSnapshotFolder()
               }

    security.declareProtected(ManagePortal, 'compareConfigurations')
    def compareConfigurations(self,
                              lhs_context,
                              rhs_context,
                              missing_as_empty=False,
                              ignore_blanks=False,
                              skip=SKIPPED_FILES,
                             ):
        """ See ISetupTool.
        """
        differ = ConfigDiff(lhs_context,
                            rhs_context,
                            missing_as_empty,
                            ignore_blanks,
                            skip,
                           )

        return differ.compare()

    security.declareProtected(ManagePortal, 'markupComparison')
    def markupComparison(self, lines):

        """ See ISetupTool.
        """
        result = []

        for line in lines.splitlines():

            if line.startswith('** '):

                if line.find('File') > -1:
                    if line.find('replaced') > -1:
                        result.append(('file-to-dir', line))
                    elif line.find('added') > -1:
                        result.append(('file-added', line))
                    else:
                        result.append(('file-removed', line))
                else:
                    if line.find('replaced') > -1:
                        result.append(('dir-to-file', line))
                    elif line.find('added') > -1:
                        result.append(('dir-added', line))
                    else:
                        result.append(('dir-removed', line))

            elif line.startswith('@@'):
                result.append(('diff-range', line))

            elif line.startswith(' '):
                result.append(('diff-context', line))

            elif line.startswith('+'):
                result.append(('diff-added', line))

            elif line.startswith('-'):
                result.append(('diff-removed', line))

            elif line == '\ No newline at end of file':
                result.append(('diff-context', line))

            else:
                result.append(('diff-header', line))

        return '<pre>\n%s\n</pre>' % (
            '\n'.join([('<span class="%s">%s</span>' % (cl, escape(l)))
                                  for cl, l in result]))

    #
    #   ZMI
    #
    manage_options = (Folder.manage_options[:1]
                    + ({'label' : 'Profiles',
                        'action' : 'manage_tool'
                       },
                       {'label' : 'Import',
                        'action' : 'manage_importSteps'
                       },
                       {'label' : 'Export',
                        'action' : 'manage_exportSteps'
                       },
                       {'label' : 'Upgrades',
                        'action' : 'manage_upgrades'
                        },
                       {'label' : 'Snapshots',
                        'action' : 'manage_snapshots'
                       },
                       {'label' : 'Comparison',
                        'action' : 'manage_showDiff'
                       },
                      )
                    + Folder.manage_options[3:] # skip "View", "Properties"
                     )

    security.declareProtected(ManagePortal, 'manage_tool')
    manage_tool = PageTemplateFile('sutProperties', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_updateToolProperties')
    def manage_updateToolProperties(self, context_id, RESPONSE):
        """ Update the tool's settings.
        """
        self.setBaselineContext(context_id)

        RESPONSE.redirect('%s/manage_tool?manage_tabs_message=%s'
                         % (self.absolute_url(), 'Properties+updated.'))

    security.declareProtected(ManagePortal, 'manage_importSteps')
    manage_importSteps = PageTemplateFile('sutImportSteps', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_importSelectedSteps')
    def manage_importSelectedSteps(self, ids, run_dependencies, context_id=None):
        """ Import the steps selected by the user.
        """
        messages = {}
        if not ids:
            summary = 'No steps selected.'

        else:
            if context_id is None:
                context_id = self.getBaselineContextID()
            steps_run = []
            for step_id in ids:
                result = self.runImportStepFromProfile(context_id,
                                                       step_id,
                                                       run_dependencies)
                steps_run.extend(result['steps'])
                messages.update(result['messages'])

            summary = 'Steps run: %s' % ', '.join(steps_run)

            name = self._mangleTimestampName('import-selected', 'log')
            self._createReport(name, result['steps'], result['messages'])

        return self.manage_importSteps(manage_tabs_message=summary,
                                       messages=messages)

    security.declareProtected(ManagePortal, 'manage_importSelectedSteps')
    def manage_importAllSteps(self, context_id=None):

        """ Import all steps.
        """
        if context_id is None:
            context_id = self.getBaselineContextID()
        result = self.runAllImportStepsFromProfile(context_id, purge_old=None)

        steps_run = 'Steps run: %s' % ', '.join(result['steps'])

        return self.manage_importSteps(manage_tabs_message=steps_run,
                                       messages=result['messages'])

    security.declareProtected(ManagePortal, 'manage_importExtensions')
    def manage_importExtensions(self, RESPONSE, profile_ids=()):

        """ Import all steps for the selected extension profiles.
        """
        detail = {}
        if len(profile_ids) == 0:
            message = 'Please select one or more extension profiles.'
            RESPONSE.redirect('%s/manage_tool?manage_tabs_message=%s'
                                  % (self.absolute_url(), message))
        else:
            message = 'Imported profiles: %s' % ', '.join(profile_ids)
        
            for profile_id in profile_ids:

                result = self.runAllImportStepsFromProfile(profile_id)

                for k, v in result['messages'].items():
                    detail['%s:%s' % (profile_id, k)] = v

            return self.manage_importSteps(manage_tabs_message=message,
                                        messages=detail)

    security.declareProtected(ManagePortal, 'manage_importTarball')
    def manage_importTarball(self, tarball):
        """ Import steps from the uploaded tarball.
        """
        if getattr(tarball, 'read', None) is not None:
            tarball = tarball.read()

        context = TarballImportContext(tool=self,
                                       archive_bits=tarball,
                                       encoding='UTF8',
                                       should_purge=True,
                                      )
        result = self._runImportStepsFromContext(context,
                                                 purge_old=True)
        steps_run = 'Steps run: %s' % ', '.join(result['steps'])

        name = self._mangleTimestampName('import-all', 'log')
        self._createReport(name, result['steps'], result['messages'])

        return self.manage_importSteps(manage_tabs_message=steps_run,
                                       messages=result['messages'])

    security.declareProtected(ManagePortal, 'manage_exportSteps')
    manage_exportSteps = PageTemplateFile('sutExportSteps', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_exportSelectedSteps')
    def manage_exportSelectedSteps(self, ids, RESPONSE):

        """ Export the steps selected by the user.
        """
        if not ids:
            RESPONSE.redirect('%s/manage_exportSteps?manage_tabs_message=%s'
                             % (self.absolute_url(), 'No+steps+selected.'))

        result = self._doRunExportSteps(ids)
        RESPONSE.setHeader('Content-type', 'application/x-gzip')
        RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % result['filename'])
        return result['tarball']

    security.declareProtected(ManagePortal, 'manage_exportAllSteps')
    def manage_exportAllSteps(self, RESPONSE):

        """ Export all steps.
        """
        result = self.runAllExportSteps()
        RESPONSE.setHeader('Content-type', 'application/x-gzip')
        RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % result['filename'])
        return result['tarball']

    security.declareProtected(ManagePortal, 'manage_upgrades')
    manage_upgrades = PageTemplateFile('setup_upgrades', _wwwdir)

    security.declareProtected(ManagePortal, 'upgradeStepMacro')
    upgradeStepMacro = PageTemplateFile('upgradeStep', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_snapshots')
    manage_snapshots = PageTemplateFile('sutSnapshots', _wwwdir)

    security.declareProtected(ManagePortal, 'listSnapshotInfo')
    def listSnapshotInfo(self):

        """ Return a list of mappings describing available snapshots.

        o Keys include:

          'id' -- snapshot ID

          'title' -- snapshot title or ID

          'url' -- URL of the snapshot folder
        """
        result = []
        snapshots = self._getOb('snapshots', None)

        if snapshots:

            for id, folder in snapshots.objectItems('Folder'):

                result.append({ 'id' : id
                               , 'title' : folder.title_or_id()
                               , 'url' : folder.absolute_url()
                               })
        return result

    security.declareProtected(ManagePortal, 'listProfileInfo')
    def listProfileInfo(self):

        """ Return a list of mappings describing registered profiles.
        Base profile is listed first, extensions are sorted.

        o Keys include:

          'id' -- profile ID

          'title' -- profile title or ID

          'description' -- description of the profile

          'path' -- path to the profile within its product

          'product' -- name of the registering product
        """
        base = []
        ext = []
        for info in _profile_registry.listProfileInfo():
            if info.get('type', BASE) == BASE:
                base.append(info)
            else:
                ext.append(info)
        ext.sort(lambda x, y: cmp(x['id'], y['id']))
        return base + ext

    security.declareProtected(ManagePortal, 'listContextInfos')
    def listContextInfos(self):

        """ List registered profiles and snapshots.
        """
        def readableType(x):
            if x is BASE:
                return 'base'
            elif x is EXTENSION:
                return 'extension'
            return 'unknown'

        s_infos = [{'id': 'snapshot-%s' % info['id'],
                     'title': info['title'],
                     'type': 'snapshot',
                   }
                    for info in self.listSnapshotInfo()]
        p_infos = [{'id': 'profile-%s' % info['id'],
                    'title': info['title'],
                    'type': readableType(info['type']),
                   }
                   for info in self.listProfileInfo()]

        return tuple(s_infos + p_infos)

    security.declareProtected(ManagePortal, 'getProfileImportDate')
    def getProfileImportDate(self, profile_id):
        """ See ISetupTool.
        """
        prefix = ('import-all-%s-' % profile_id).replace(':', '_')
        candidates = [x for x in self.objectIds('File')
                        if x.startswith(prefix)]
        if len(candidates) == 0:
            return None
        candidates.sort()
        last = candidates[-1]
        stamp = last[len(prefix):-4]
        assert(len(stamp) == 14)
        return '%s-%s-%sT%s:%s:%sZ' % (stamp[0:4],
                                       stamp[4:6],
                                       stamp[6:8],
                                       stamp[8:10],
                                       stamp[10:12],
                                       stamp[12:14],
                                      )

    security.declareProtected(ManagePortal, 'manage_createSnapshot')
    def manage_createSnapshot(self, RESPONSE, snapshot_id=None):

        """ Create a snapshot with the given ID.

        o If no ID is passed, generate one.
        """
        if snapshot_id is None:
            snapshot_id = self._mangleTimestampName('snapshot')

        self.createSnapshot(snapshot_id)

        RESPONSE.redirect('%s/manage_snapshots?manage_tabs_message=%s'
                         % (self.absolute_url(), 'Snapshot+created.'))
        return ""

    security.declareProtected(ManagePortal, 'manage_showDiff')
    manage_showDiff = PageTemplateFile('sutCompare', _wwwdir)

    def manage_downloadDiff(self,
                            lhs,
                            rhs,
                            missing_as_empty,
                            ignore_blanks,
                            RESPONSE,
                           ):
        """ Crack request vars and call compareConfigurations.

        o Return the result as a 'text/plain' stream, suitable for framing.
        """
        comparison = self.manage_compareConfigurations(lhs,
                                                       rhs,
                                                       missing_as_empty,
                                                       ignore_blanks,
                                                      )
        RESPONSE.setHeader('Content-Type', 'text/plain')
        return _PLAINTEXT_DIFF_HEADER % (lhs, rhs, comparison)

    security.declareProtected(ManagePortal, 'manage_compareConfigurations')
    def manage_compareConfigurations(self,
                                     lhs,
                                     rhs,
                                     missing_as_empty,
                                     ignore_blanks,
                                    ):
        """ Crack request vars and call compareConfigurations.
        """
        lhs_context = self._getImportContext(lhs)
        rhs_context = self._getImportContext(rhs)

        return self.compareConfigurations(lhs_context,
                                          rhs_context,
                                          missing_as_empty,
                                          ignore_blanks,
                                         )

    #
    # Upgrades management
    #
    security.declareProtected(ManagePortal, 'getLastVersionForProfile')
    def getLastVersionForProfile(self, profile_id):
        """Return the last upgraded version for the specified profile.
        """
        version = self._profile_upgrade_versions.get(profile_id, 'unknown')
        return version

    security.declareProtected(ManagePortal, 'setLastVersionForProfile')
    def setLastVersionForProfile(self, profile_id, version):
        """Set the last upgraded version for the specified profile.
        """
        if isinstance(version, basestring):
            version = tuple(version.split('.'))
        prof_versions = self._profile_upgrade_versions.copy()
        prof_versions[profile_id] = version
        self._profile_upgrade_versions = prof_versions

    security.declareProtected(ManagePortal, 'getVersionForProfile')
    def getVersionForProfile(self, profile_id):
        """Return the registered filesystem version for the specified
        profile.
        """
        info = _profile_registry.getProfileInfo(profile_id)
        return info.get('version', 'unknown')

    security.declareProtected(ManagePortal, 'listProfilesWithUpgrades')
    def listProfilesWithUpgrades(self):
        return listProfilesWithUpgrades()

    security.declarePrivate('_massageUpgradeInfo')
    def _massageUpgradeInfo(self, info):
        """Add a couple of data points to the upgrade info dictionary.
        """
        info = info.copy()
        info['haspath'] = info['source'] and info['dest']
        info['ssource'] = '.'.join(info['source'] or ('all',))
        info['sdest'] = '.'.join(info['dest'] or ('all',))
        return info

    security.declareProtected(ManagePortal, 'listUpgrades')
    def listUpgrades(self, profile_id, show_old=False):
        """Get the list of available upgrades.
        """
        if show_old:
            source = None
        else:
            source = self.getLastVersionForProfile(profile_id)
        upgrades = listUpgradeSteps(self, profile_id, source)
        res = []
        for info in upgrades:
            if type(info) == list:
                subset = []
                for subinfo in info:
                    subset.append(self._massageUpgradeInfo(subinfo))
                res.append(subset)
            else:
                res.append(self._massageUpgradeInfo(info))
        return res

    security.declareProtected(ManagePortal, 'manage_doUpgrades')
    def manage_doUpgrades(self, request=None):
        """Perform all selected upgrade steps.
        """
        if request is None:
            request = self.REQUEST
        logger = logging.getLogger('GenericSetup')
        steps_to_run = request.form.get('upgrades', [])
        profile_id = request.get('profile_id', '')
        for step_id in steps_to_run:
            step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
            if step is not None:
                step.doStep(self)
                msg = "Ran upgrade step %s for profile %s" % (step.title,
                                                              profile_id)
                logger.log(logging.INFO, msg)

        # XXX should be a bit smarter about deciding when to up the
        #     profile version
        profile_info = _profile_registry.getProfileInfo(profile_id)
        version = profile_info.get('version', None)
        if version is not None:
            self.setLastVersionForProfile(profile_id, version)

        url = self.absolute_url()
        request.RESPONSE.redirect("%s/manage_upgrades?saved=%s" % (url, profile_id))

    #
    #   Helper methods
    #
    security.declarePrivate('_getProductPath')
    def _getProductPath(self, product_name):

        """ Return the absolute path of the product's directory.
        """
        try:
            # BBB: for GenericSetup 1.1 style product names
            product = __import__('Products.%s' % product_name
                                , globals(), {}, ['initialize'])
        except ImportError:
            try:
                product = __import__(product_name
                                    , globals(), {}, ['initialize'])
            except ImportError:
                raise ValueError('Not a valid product name: %s'
                                 % product_name)

        return product.__path__[0]

    security.declarePrivate('_getImportContext')
    def _getImportContext(self, context_id, should_purge=None):

        """ Crack ID and generate appropriate import context.
        """
        encoding = self.getEncoding()

        if context_id.startswith('profile-'):

            context_id = context_id[len('profile-'):]
            info = _profile_registry.getProfileInfo(context_id)

            if info.get('product'):
                path = os.path.join(self._getProductPath(info['product'])
                                   , info['path'])
            else:
                path = info['path']
            if should_purge is None:
                should_purge = (info.get('type') != EXTENSION)
            return DirectoryImportContext(self, path, should_purge, encoding)

        elif context_id.startswith('snapshot-'):
            context_id = context_id[len('snapshot-'):]
            if should_purge is None:
                should_purge = True
            return SnapshotImportContext(self, context_id, should_purge, encoding)
        else:
            raise KeyError, 'Unknown context "%s"' % context_id

    security.declarePrivate('_updateImportStepsRegistry')
    def _updateImportStepsRegistry(self, context, encoding):

        """ Update our import steps registry from our profile.
        """
        if context is None:
            context = self._getImportContext(self._import_context_id)
        xml = context.readDataFile(IMPORT_STEPS_XML)
        if xml is None:
            return

        info_list = self._import_registry.parseXML(xml, encoding)

        for step_info in info_list:

            id = step_info['id']
            version = step_info['version']
            handler = step_info['handler']
            dependencies = tuple(step_info.get('dependencies', ()))
            title = step_info.get('title', id)
            description = ''.join(step_info.get('description', []))

            self._import_registry.registerStep(id=id,
                                               version=version,
                                               handler=handler,
                                               dependencies=dependencies,
                                               title=title,
                                               description=description,
                                              )

    security.declarePrivate('_updateExportStepsRegistry')
    def _updateExportStepsRegistry(self, context, encoding):

        """ Update our export steps registry from our profile.
        """
        if context is None:
            context = self._getImportContext(self._import_context_id)
        xml = context.readDataFile(EXPORT_STEPS_XML)
        if xml is None:
            return

        info_list = self._export_registry.parseXML(xml, encoding)

        for step_info in info_list:

            id = step_info['id']
            handler = step_info['handler']
            title = step_info.get('title', id)
            description = ''.join(step_info.get('description', []))

            self._export_registry.registerStep(id=id,
                                               handler=handler,
                                               title=title,
                                               description=description,
                                              )

    security.declarePrivate('_doRunImportStep')
    def _doRunImportStep(self, step_id, context):

        """ Run a single import step, using a pre-built context.
        """
        __traceback_info__ = step_id
        marker = object()

        handler = self._import_registry.getStep(step_id)

        if handler is marker:
            raise ValueError('Invalid import step: %s' % step_id)

        if handler is None:
            msg = 'Step %s has an invalid import handler' % step_id
            logger = logging.getLogger('GenericSetup')
            logger.error(msg)
            return 'ERROR: ' + msg

        return handler(context)

    security.declarePrivate('_doRunExportSteps')
    def _doRunExportSteps(self, steps):

        """ See ISetupTool.
        """
        context = TarballExportContext(self)
        messages = {}
        marker = object()

        for step_id in steps:

            handler = self._export_registry.getStep(step_id, marker)

            if handler is marker:
                raise ValueError('Invalid export step: %s' % step_id)

            if handler is None:
                msg = 'Step %s has an invalid import handler' % step_id
                logger = logging.getLogger('GenericSetup')
                logger.error(msg)
                messages[step_id] = msg
            else:
                messages[step_id] = handler(context)

        return { 'steps' : steps
               , 'messages' : messages
               , 'tarball' : context.getArchive()
               , 'filename' : context.getArchiveFilename()
               }

    security.declarePrivate('_runImportStepsFromContext')
    def _runImportStepsFromContext(self, context, steps=None, purge_old=None):
        self.applyContext(context)

        if steps is None:
            steps = self._import_registry.sortSteps()
        messages = {}

        for step in steps:
            message = self._doRunImportStep(step, context)
            message_list = filter(None, [message])
            message_list.extend( ['%s: %s' % x[1:]
                                  for x in context.listNotes()] )
            messages[step] = '\n'.join(message_list)
            context.clearNotes()

        return { 'steps' : steps, 'messages' : messages }

    security.declarePrivate('_mangleTimestampName')
    def _mangleTimestampName(self, prefix, ext=None):

        """ Create a mangled ID using a timestamp.
        """
        timestamp = time.gmtime()
        items = (prefix,) + timestamp[:6]

        if ext is None:
            fmt = '%s-%4d%02d%02d%02d%02d%02d'
        else:
            fmt = '%s-%4d%02d%02d%02d%02d%02d.%s'
            items += (ext,)

        return fmt % items

    security.declarePrivate('_createReport')
    def _createReport(self, name, steps, messages):

        """ Record the results of a run.
        """
        lines = []
        # Create report
        for step in steps:
            lines.append('=' * 65)
            lines.append('Step: %s' % step)
            lines.append('=' * 65)
            msg = messages[step]
            lines.extend(msg.split('\n'))
            lines.append('')

        report = '\n'.join(lines)
        if isinstance(report, unicode):
            report = report.encode('latin-1')

        # BBB: ObjectManager won't allow unicode IDS
        if isinstance(name, unicode):
            name = name.encode('UTF-8')

        file = File(id=name,
                    title='',
                    file=report,
                    content_type='text/plain'
                   )
        self._setObject(name, file)

InitializeClass(SetupTool)

_PLAINTEXT_DIFF_HEADER ="""\
Comparing configurations: '%s' and '%s'

%s"""

_TOOL_ID = 'setup_tool'

addSetupToolForm = PageTemplateFile('toolAdd.zpt', _wwwdir)

def addSetupTool(dispatcher, RESPONSE):
    """
    """
    dispatcher._setObject(_TOOL_ID, SetupTool(_TOOL_ID))

    RESPONSE.redirect('%s/manage_main' % dispatcher.absolute_url())
