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
""" Unit tests for GenericSetup tool.

$Id: test_tool.py 81939 2007-11-19 22:44:48Z wichert $
"""
import copy
import os
import unittest
import Testing

from StringIO import StringIO

from Acquisition import aq_base
from OFS.Folder import Folder

from Products.Five import zcml

import Products.GenericSetup
from Products.GenericSetup import profile_registry
from Products.GenericSetup.upgrade import listUpgradeSteps
from Products.GenericSetup.upgrade import UpgradeStep
from Products.GenericSetup.upgrade import _registerUpgradeStep
from Products.GenericSetup.testing import ExportImportZCMLLayer
from Products.GenericSetup.tests.test_zcml import dummy_upgrade_handler

from common import BaseRegistryTests
from common import DummyExportContext
from common import DummyImportContext
from common import FilesystemTestBase
from common import TarballTester
from conformance import ConformsToISetupTool


class SetupToolTests(FilesystemTestBase, TarballTester, ConformsToISetupTool):

    layer = ExportImportZCMLLayer

    _PROFILE_PATH = '/tmp/STT_test'

    def afterSetUp(self):
        self._profile_registry_info = profile_registry._profile_info
        self._profile_registry_ids = profile_registry._profile_ids
        profile_registry.clear()

    def beforeTearDown(self):
        profile_registry._profile_info = self._profile_registry_info
        profile_registry._profile_ids = self._profile_registry_ids
        FilesystemTestBase.beforeTearDown(self)

    def _getTargetClass(self):
        from Products.GenericSetup.tool import SetupTool

        return SetupTool

    def _makeSite( self, title="Don't care" ):

        site = Folder()
        site._setId( 'site' )
        site.title = title

        self.app._setObject( 'site', site )
        return self.app._getOb( 'site' )

    def test_empty( self ):

        tool = self._makeOne('setup_tool')

        self.assertEqual( tool.getBaselineContextID(), '' )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 0 )

        export_registry = tool.getExportStepRegistry()
        export_steps = export_registry.listSteps()
        self.assertEqual( len( export_steps ), 1 )
        self.assertEqual( export_steps[ 0 ], 'step_registries' )

        toolset_registry = tool.getToolsetRegistry()
        self.assertEqual( len( toolset_registry.listForbiddenTools() ), 0 )
        self.assertEqual( len( toolset_registry.listRequiredTools() ), 0 )

    def test_getBaselineContextID( self ):

        from Products.GenericSetup.tool import IMPORT_STEPS_XML
        from Products.GenericSetup.tool import EXPORT_STEPS_XML
        from Products.GenericSetup.tool import TOOLSET_XML
        from test_registry import _EMPTY_IMPORT_XML
        from test_registry import _EMPTY_EXPORT_XML
        from test_registry import _EMPTY_TOOLSET_XML

        tool = self._makeOne('setup_tool')

        self._makeFile(IMPORT_STEPS_XML, _EMPTY_IMPORT_XML)
        self._makeFile(EXPORT_STEPS_XML, _EMPTY_EXPORT_XML)
        self._makeFile(TOOLSET_XML, _EMPTY_TOOLSET_XML)

        profile_registry.registerProfile('foo', 'Foo', '', self._PROFILE_PATH)
        tool.setBaselineContext('profile-other:foo')

        self.assertEqual( tool.getBaselineContextID(), 'profile-other:foo' )

    def test_setBaselineContext_invalid( self ):

        tool = self._makeOne('setup_tool')

        self.assertRaises( KeyError
                         , tool.setBaselineContext
                         , 'profile-foo'
                         )

    def test_setBaselineContext_empty_string( self ):

        tool = self._makeOne('setup_tool')

        self.assertRaises( KeyError
                         , tool.setBaselineContext
                         , ''
                         )

    def test_setBaselineContext( self ):

        from Products.GenericSetup.tool import IMPORT_STEPS_XML
        from Products.GenericSetup.tool import EXPORT_STEPS_XML
        from Products.GenericSetup.tool import TOOLSET_XML
        from test_registry import _SINGLE_IMPORT_XML
        from test_registry import _SINGLE_EXPORT_XML
        from test_registry import _NORMAL_TOOLSET_XML
        from test_registry import ONE_FUNC

        tool = self._makeOne('setup_tool')
        tool.getExportStepRegistry().clear()

        self._makeFile(IMPORT_STEPS_XML, _SINGLE_IMPORT_XML)
        self._makeFile(EXPORT_STEPS_XML, _SINGLE_EXPORT_XML)
        self._makeFile(TOOLSET_XML, _NORMAL_TOOLSET_XML)

        profile_registry.registerProfile('foo', 'Foo', '', self._PROFILE_PATH)
        tool.setBaselineContext('profile-other:foo')

        self.assertEqual( tool.getBaselineContextID(), 'profile-other:foo' )

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = import_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.assertEqual( info[ 'version' ], '1' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.GenericSetup.tests.test_registry.ONE_FUNC')

        self.assertEqual( import_registry.getStep( 'one' ), ONE_FUNC )

        export_registry = tool.getExportStepRegistry()
        self.assertEqual( len( export_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = export_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.GenericSetup.tests.test_registry.ONE_FUNC')

        self.assertEqual( export_registry.getStep( 'one' ), ONE_FUNC )

    def test_runImportStep_nonesuch( self ):

        site = self._makeSite()

        tool = self._makeOne('setup_tool').__of__( site )

        self.assertRaises( KeyError, tool.runImportStepFromProfile,
                           '', 'nonesuch' )

    def test_runImportStep_simple( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'simple', '1', _uppercaseSiteTitle )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'simple' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'simple' )
        self.assertEqual( result[ 'messages' ][ 'simple' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.upper() )

    def test_runImportStep_dependencies( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1', _underscoreSiteTitle )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'dependent' )

        self.assertEqual( len( result[ 'steps' ] ), 2 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'dependable' )
        self.assertEqual( result[ 'messages' ][ 'dependable' ]
                        , 'Underscored title' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )
        self.assertEqual( site.title, TITLE.replace( ' ', '_' ).upper() )

    def test_runImportStep_skip_dependencies( self ):

        TITLE = 'original title'
        site = self._makeSite( TITLE )

        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1', _underscoreSiteTitle )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'dependent',
                                                run_dependencies=False )

        self.assertEqual( len( result[ 'steps' ] ), 1 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.upper() )

    def test_runImportStep_default_purge( self ):

        site = self._makeSite()

        tool = self._makeOne('setup_tool').__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'purging' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Purged' )
        self.failUnless( site.purged )

    def test_runImportStep_explicit_purge( self ):

        site = self._makeSite()

        tool = self._makeOne('setup_tool').__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'purging',
                                                purge_old=True )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Purged' )
        self.failUnless( site.purged )

    def test_runImportStep_skip_purge( self ):

        site = self._makeSite()

        tool = self._makeOne('setup_tool').__of__( site )
        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'purging',
                                                purge_old=False )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ], 'Unpurged' )
        self.failIf( site.purged )

    def test_runImportStep_consistent_context( self ):

        site = self._makeSite()

        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'purging', '1', _purgeIfRequired )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'purging', ) )

        result = tool.runImportStepFromProfile( 'snapshot-dummy', 'dependent',
                                                purge_old=False )
        self.failIf( site.purged )

    def test_runAllImportSteps_empty( self ):

        site = self._makeSite()
        tool = self._makeOne('setup_tool').__of__( site )

        result = tool.runAllImportStepsFromProfile('snapshot-dummy')

        self.assertEqual( len( result[ 'steps' ] ), 0 )

    def test_runAllImportSteps_sorted_default_purge( self ):

        TITLE = 'original title'
        PROFILE_ID = 'snapshot-testing'
        site = self._makeSite( TITLE )
        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportStepsFromProfile(PROFILE_ID)

        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Purged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'messages' ][ 'dependable' ]
                        , 'Underscored title' )

        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.assertEqual( result[ 'messages' ][ 'dependent' ]
                        , 'Uppercased title' )

        self.assertEqual( site.title, TITLE.replace( ' ', '_' ).upper() )
        self.failUnless( site.purged )

        prefix = 'import-all-%s' % PROFILE_ID
        logged = [x for x in tool.objectIds('File') if x.startswith(prefix)]
        self.assertEqual(len(logged), 1)

    def test_runAllImportSteps_unicode_profile_id_creates_reports( self ):

        TITLE = 'original title'
        PROFILE_ID = u'snapshot-testing'
        site = self._makeSite( TITLE )
        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        tool.runAllImportStepsFromProfile(PROFILE_ID)

        prefix = ('import-all-%s' % PROFILE_ID).encode('UTF-8')
        logged = [x for x in tool.objectIds('File') if x.startswith(prefix)]
        self.assertEqual(len(logged), 1)

    def test_runAllImportSteps_sorted_explicit_purge( self ):

        site = self._makeSite()
        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportStepsFromProfile( 'snapshot-dummy', purge_old=True )

        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Purged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.failUnless( site.purged )

    def test_runAllImportSteps_sorted_skip_purge( self ):

        site = self._makeSite()
        tool = self._makeOne('setup_tool').__of__( site )

        registry = tool.getImportStepRegistry()
        registry.registerStep( 'dependable', '1'
                             , _underscoreSiteTitle, ( 'purging', ) )
        registry.registerStep( 'dependent', '1'
                             , _uppercaseSiteTitle, ( 'dependable', ) )
        registry.registerStep( 'purging', '1'
                             , _purgeIfRequired )

        result = tool.runAllImportStepsFromProfile( 'snapshot-dummy', purge_old=False )

        self.assertEqual( len( result[ 'steps' ] ), 3 )

        self.assertEqual( result[ 'steps' ][ 0 ], 'purging' )
        self.assertEqual( result[ 'messages' ][ 'purging' ]
                        , 'Unpurged' )

        self.assertEqual( result[ 'steps' ][ 1 ], 'dependable' )
        self.assertEqual( result[ 'steps' ][ 2 ], 'dependent' )
        self.failIf( site.purged )

    def test_runExportStep_nonesuch( self ):

        site = self._makeSite()
        tool = self._makeOne('setup_tool').__of__( site )

        self.assertRaises( ValueError, tool.runExportStep, 'nonesuch' )

    def test_runExportStep_step_registry( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool

        result = tool.runExportStep( 'step_registries' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , None
                        )
        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EMPTY_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

    def test_runAllExportSteps_default( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool

        result = tool.runAllExportSteps()

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , None
                        )
        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EMPTY_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

    def test_runAllExportSteps_extras( self ):

        from test_registry import _EMPTY_IMPORT_XML

        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool

        import_reg = tool.getImportStepRegistry()
        import_reg.registerStep( 'dependable', '1'
                               , _underscoreSiteTitle, ( 'purging', ) )
        import_reg.registerStep( 'dependent', '1'
                               , _uppercaseSiteTitle, ( 'dependable', ) )
        import_reg.registerStep( 'purging', '1'
                               , _purgeIfRequired )

        export_reg = tool.getExportStepRegistry()
        export_reg.registerStep( 'properties'
                               , _exportPropertiesINI )

        result = tool.runAllExportSteps()

        self.assertEqual( len( result[ 'steps' ] ), 2 )

        self.failUnless( 'properties' in result[ 'steps' ] )
        self.assertEqual( result[ 'messages' ][ 'properties' ]
                        , 'Exported properties'
                        )

        self.failUnless( 'step_registries' in result[ 'steps' ] )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , None
                        )

        fileish = StringIO( result[ 'tarball' ] )

        self._verifyTarballContents( fileish, [ 'import_steps.xml'
                                              , 'export_steps.xml'
                                              , 'properties.ini'
                                              ] )
        self._verifyTarballEntryXML( fileish, 'import_steps.xml'
                                   , _EXTRAS_STEP_REGISTRIES_IMPORT_XML )
        self._verifyTarballEntryXML( fileish, 'export_steps.xml'
                                   , _EXTRAS_STEP_REGISTRIES_EXPORT_XML )
        self._verifyTarballEntry( fileish, 'properties.ini'
                                , _PROPERTIES_INI % site.title  )

    def test_createSnapshot_default( self ):

        from test_registry import _EMPTY_IMPORT_XML

        _EXPECTED = [ ( 'import_steps.xml', _EMPTY_IMPORT_XML )
                    , ( 'export_steps.xml'
                      , _DEFAULT_STEP_REGISTRIES_EXPORT_XML
                      )
                    ]

        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool

        self.assertEqual( len( tool.listSnapshotInfo() ), 0 )

        result = tool.createSnapshot( 'default' )

        self.assertEqual( len( result[ 'steps' ] ), 1 )
        self.assertEqual( result[ 'steps' ][ 0 ], 'step_registries' )
        self.assertEqual( result[ 'messages' ][ 'step_registries' ]
                        , None
                        )

        snapshot = result[ 'snapshot' ]

        self.assertEqual( len( snapshot.objectIds() ), len( _EXPECTED ) )

        for id in [ x[0] for x in _EXPECTED ]:
            self.failUnless( id in snapshot.objectIds() )

        def normalize_xml(xml):
            # using this might mask a real problem on windows, but so far the
            # different newlines just caused problems in this test
            lines = [ line for line in xml.splitlines() if line ]
            return '\n'.join(lines) + '\n'

        fileobj = snapshot._getOb( 'import_steps.xml' )
        self.assertEqual( normalize_xml( fileobj.read() ),
                          _EMPTY_IMPORT_XML )

        fileobj = snapshot._getOb( 'export_steps.xml' )

        self.assertEqual( normalize_xml( fileobj.read() ),
                          _DEFAULT_STEP_REGISTRIES_EXPORT_XML )

        self.assertEqual( len( tool.listSnapshotInfo() ), 1 )

        info = tool.listSnapshotInfo()[ 0 ]

        self.assertEqual( info[ 'id' ], 'default' )
        self.assertEqual( info[ 'title' ], 'default' )

    def test_applyContext(self):
        from Products.GenericSetup.tool import IMPORT_STEPS_XML
        from Products.GenericSetup.tool import EXPORT_STEPS_XML
        from Products.GenericSetup.tool import TOOLSET_XML
        from test_registry import _SINGLE_IMPORT_XML
        from test_registry import _SINGLE_EXPORT_XML
        from test_registry import _NORMAL_TOOLSET_XML
        from test_registry import ONE_FUNC

        site = self._makeSite()
        tool = self._makeOne('setup_tool').__of__(site)
        tool.getImportStepRegistry().clear()
        tool.getExportStepRegistry().clear()
        tool.getToolsetRegistry().clear()

        context = DummyImportContext( site, tool=tool )
        context._files[ IMPORT_STEPS_XML ] = _SINGLE_IMPORT_XML
        context._files[ EXPORT_STEPS_XML ] = _SINGLE_EXPORT_XML
        context._files[ TOOLSET_XML ] = _NORMAL_TOOLSET_XML

        tool.applyContext(context)

        import_registry = tool.getImportStepRegistry()
        self.assertEqual( len( import_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = import_registry.getStepMetadata( 'one' )

        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.assertEqual( info[ 'version' ], '1' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.GenericSetup.tests.test_registry.ONE_FUNC' )

        self.assertEqual( import_registry.getStep( 'one' ), ONE_FUNC )

        export_registry = tool.getExportStepRegistry()
        self.assertEqual( len( export_registry.listSteps() ), 1 )
        self.failUnless( 'one' in import_registry.listSteps() )
        info = export_registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )
        self.assertEqual( info[ 'handler' ]
                        , 'Products.GenericSetup.tests.test_registry.ONE_FUNC' )

        self.assertEqual( export_registry.getStep( 'one' ), ONE_FUNC )

    def test_listContextInfos_empty(self):
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        infos = tool.listContextInfos()
        self.assertEqual(len(infos), 0)

    def test_listContextInfos_with_snapshot(self):
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        tool.createSnapshot('testing')
        infos = tool.listContextInfos()
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['id'], 'snapshot-testing')
        self.assertEqual(info['title'], 'testing')
        self.assertEqual(info['type'], 'snapshot')

    def test_listContextInfos_with_registered_base_profile(self):
        from Products.GenericSetup.interfaces import BASE
        profile_registry.registerProfile('foo', 'Foo', '', self._PROFILE_PATH,
                                         'Foo', BASE)
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        infos = tool.listContextInfos()
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['id'], 'profile-Foo:foo')
        self.assertEqual(info['title'], 'Foo')
        self.assertEqual(info['type'], 'base')

    def test_listContextInfos_with_registered_extension_profile(self):
        from Products.GenericSetup.interfaces import EXTENSION
        profile_registry.registerProfile('foo', 'Foo', '', self._PROFILE_PATH,
                                         'Foo', EXTENSION)
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        infos = tool.listContextInfos()
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['id'], 'profile-Foo:foo')
        self.assertEqual(info['title'], 'Foo')
        self.assertEqual(info['type'], 'extension')

    def test_getProfileImportDate_nonesuch(self):
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        self.assertEqual(tool.getProfileImportDate('nonesuch'), None)

    def test_getProfileImportDate_simple_id(self):
        from OFS.Image import File
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        filename = 'import-all-foo-20070315123456.log'
        tool._setObject(filename, File(filename, '', ''))
        self.assertEqual(tool.getProfileImportDate('foo'),
                         '2007-03-15T12:34:56Z')

    def test_getProfileImportDate_id_with_colon(self):
        from OFS.Image import File
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        filename = 'import-all-foo_bar-20070315123456.log'
        tool._setObject(filename, File(filename, '', ''))
        self.assertEqual(tool.getProfileImportDate('foo:bar'),
                         '2007-03-15T12:34:56Z')

    def test_profileVersioning(self):
        site = self._makeSite()
        site.setup_tool = self._makeOne('setup_tool')
        tool = site.setup_tool
        profile_id = 'dummy_profile'
        product_name = 'GenericSetup'
        directory = os.path.split(__file__)[0]
        path = os.path.join(directory, 'versioned_profile')

        # register profile
        orig_profile_reg = (profile_registry._profile_info.copy(),
                            profile_registry._profile_ids[:])
        profile_registry.registerProfile(profile_id,
                                         'Dummy Profile',
                                         'This is a dummy profile',
                                         path,
                                         product=product_name)

        # register upgrade step
        from Products.GenericSetup.upgrade import _upgrade_registry
        orig_upgrade_registry = copy.copy(_upgrade_registry._registry)
        step = UpgradeStep("Upgrade", "GenericSetup:dummy_profile", '*', '1.1', '',
                           dummy_upgrade_handler,
                           None, "1")
        _registerUpgradeStep(step)

        # test initial states
        profile_id = ':'.join((product_name, profile_id))
        self.assertEqual(tool.getVersionForProfile(profile_id), '1.1')
        self.assertEqual(tool.getLastVersionForProfile(profile_id),
                         'unknown')

        # run upgrade steps
        request = site.REQUEST
        request.form['profile_id'] = profile_id
        steps = listUpgradeSteps(tool, profile_id, '1.0')
        step_id = steps[0]['id']
        request.form['upgrades'] = [step_id]
        tool.manage_doUpgrades()
        self.assertEqual(tool.getLastVersionForProfile(profile_id),
                         ('1', '1'))

        # reset ugprade registry
        _upgrade_registry._registry = orig_upgrade_registry

        # reset profile registry
        (profile_registry._profile_info,
         profile_registry._profile_ids) = orig_profile_reg

_DEFAULT_STEP_REGISTRIES_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step id="step_registries"
              handler="Products.GenericSetup.tool.exportStepRegistries"
              title="Export import / export steps.">
  
 </export-step>
</export-steps>
"""

_EXTRAS_STEP_REGISTRIES_EXPORT_XML = """\
<?xml version="1.0"?>
<export-steps>
 <export-step
    id="properties"
    handler="Products.GenericSetup.tests.test_tool._exportPropertiesINI"
    title="properties">

 </export-step>
 <export-step
    id="step_registries"
    handler="Products.GenericSetup.tool.exportStepRegistries"
    title="Export import / export steps.">

 </export-step>
</export-steps>
"""

_EXTRAS_STEP_REGISTRIES_IMPORT_XML = """\
<?xml version="1.0"?>
<import-steps>
 <import-step
    id="dependable"
    version="1"
    handler="Products.GenericSetup.tests.test_tool._underscoreSiteTitle"
    title="dependable">
  <dependency step="purging" />

 </import-step>
 <import-step
    id="dependent"
    version="1"
    handler="Products.GenericSetup.tests.test_tool._uppercaseSiteTitle"
    title="dependent">
  <dependency step="dependable" />

 </import-step>
 <import-step
    id="purging"
    version="1"
    handler="Products.GenericSetup.tests.test_tool._purgeIfRequired"
    title="purging">

 </import-step>
</import-steps>
"""

_PROPERTIES_INI = """\
[Default]
Title=%s
"""


def _underscoreSiteTitle( context ):

    site = context.getSite()
    site.title = site.title.replace( ' ', '_' )
    return 'Underscored title'

def _uppercaseSiteTitle( context ):

    site = context.getSite()
    site.title = site.title.upper()
    return 'Uppercased title'

def _purgeIfRequired( context ):

    site = context.getSite()
    purged = site.purged = context.shouldPurge()
    return purged and 'Purged' or 'Unpurged'

def _exportPropertiesINI( context ):

    site = context.getSite()
    text = _PROPERTIES_INI % site.title

    context.writeDataFile( 'properties.ini', text, 'text/plain' )

    return 'Exported properties'


class _ToolsetSetup(BaseRegistryTests):

    def _initSite( self ):

        from Products.GenericSetup.tool import SetupTool
        site = Folder()
        site._setId( 'site' )
        self.app._setObject( 'site', site )
        site = self.app._getOb( 'site' )
        site._setObject('setup_tool', SetupTool('setup_tool'))
        return site


class Test_exportToolset(_ToolsetSetup):

    layer = ExportImportZCMLLayer

    def test_empty( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import exportToolset

        site = self._initSite()
        context = DummyExportContext( site, tool=site.setup_tool )

        exportToolset( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, TOOLSET_XML )
        self._compareDOM( text, _EMPTY_TOOLSET_XML )
        self.assertEqual( content_type, 'text/xml' )

    def test_normal( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import exportToolset

        site = self._initSite()
        toolset = site.setup_tool.getToolsetRegistry()
        toolset.addForbiddenTool( 'doomed' )
        toolset.addRequiredTool( 'mandatory', 'path.to.one' )
        toolset.addRequiredTool( 'obligatory', 'path.to.another' )

        context = DummyExportContext( site, tool=site.setup_tool )

        exportToolset( context )

        self.assertEqual( len( context._wrote ), 1 )
        filename, text, content_type = context._wrote[ 0 ]
        self.assertEqual( filename, TOOLSET_XML )
        self._compareDOM( text, _NORMAL_TOOLSET_XML )
        self.assertEqual( content_type, 'text/xml' )


class Test_importToolset(_ToolsetSetup):

    layer = ExportImportZCMLLayer

    def test_import_updates_registry(self):
        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset
        from test_registry import _NORMAL_TOOLSET_XML

        site = self._initSite()
        context = DummyImportContext( site, tool=site.setup_tool )

        # Import forbidden
        context._files[ TOOLSET_XML ] = _FORBIDDEN_TOOLSET_XML
        importToolset( context )

        tool = context.getSetupTool()
        toolset = tool.getToolsetRegistry()

        self.assertEqual( len( toolset.listForbiddenTools() ), 3 )
        self.failUnless( 'doomed' in toolset.listForbiddenTools() )
        self.failUnless( 'damned' in toolset.listForbiddenTools() )
        self.failUnless( 'blasted' in toolset.listForbiddenTools() )

        # Import required
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML
        importToolset( context )

        self.assertEqual( len( toolset.listRequiredTools() ), 2 )
        self.failUnless( 'mandatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'mandatory' )
        self.assertEqual( info[ 'class' ],
                          'Products.GenericSetup.tests.test_tool.DummyTool' )
        self.failUnless( 'obligatory' in toolset.listRequiredTools() )
        info = toolset.getRequiredToolInfo( 'obligatory' )
        self.assertEqual( info[ 'class' ],
                          'Products.GenericSetup.tests.test_tool.DummyTool' )

    def test_tool_ids( self ):
        # The tool import mechanism used to rely on the fact that all tools
        # have unique IDs set at the class level and that you can call their
        # constructor with no arguments. However, there might be tools
        # that need IDs set.
        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()
        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        for tool_id in ( 'mandatory', 'obligatory' ):
            tool = getattr( site, tool_id )
            self.assertEqual( tool.getId(), tool_id )

    def test_tool_id_required(self):
        # Tests that tool creation will still work when an id is required
        # by the tool constructor.
        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()
        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _WITH_ID_TOOLSET_XML

        importToolset( context )

        for tool_id in ( 'mandatory', 'requires_id' ):
            tool = getattr( site, tool_id )
            self.assertEqual( tool.getId(), tool_id )

    def test_forbidden_tools( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset
        TOOL_IDS = ( 'doomed', 'blasted', 'saved' )

        site = self._initSite()

        for tool_id in TOOL_IDS:
            pseudo = Folder()
            pseudo._setId( tool_id )
            site._setObject( tool_id, pseudo )

        self.assertEqual( len( site.objectIds() ), len( TOOL_IDS ) + 1 )

        for tool_id in TOOL_IDS:
            self.failUnless( tool_id in site.objectIds() )

        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _FORBIDDEN_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 2 )
        self.failUnless( 'setup_tool' in site.objectIds() )
        self.failUnless( 'saved' in site.objectIds() )

    def test_required_tools_missing( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()
        self.assertEqual( len( site.objectIds() ), 1 )

        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )
        self.failUnless( isinstance( aq_base( site._getOb( 'mandatory' ) )
                                   , DummyTool ) )
        self.failUnless( isinstance( aq_base( site._getOb( 'obligatory' ) )
                                   , DummyTool ) )

    def test_required_tools_no_replacement( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()

        mandatory = DummyTool()
        mandatory._setId( 'mandatory' )
        site._setObject( 'mandatory', mandatory )

        obligatory = DummyTool()
        obligatory._setId( 'obligatory' )
        site._setObject( 'obligatory', obligatory )

        self.assertEqual( len( site.objectIds() ), 3 )

        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )
        self.failUnless( aq_base( site._getOb( 'mandatory' ) ) is mandatory )
        self.failUnless( aq_base( site._getOb( 'obligatory' ) ) is obligatory )

    def test_required_tools_with_replacement( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()

        mandatory = AnotherDummyTool()
        mandatory._setId( 'mandatory' )
        site._setObject( 'mandatory', mandatory )

        obligatory = AnotherDummyTool()
        obligatory._setId( 'obligatory' )
        site._setObject( 'obligatory', obligatory )

        self.assertEqual( len( site.objectIds() ), 3 )

        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.assertEqual( len( site.objectIds() ), 3 )

        self.failIf( aq_base( site._getOb( 'mandatory' ) ) is mandatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'mandatory' ) )
                                   , DummyTool ) )

        self.failIf( aq_base( site._getOb( 'obligatory' ) ) is obligatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'obligatory' ) )
                                   , DummyTool ) )

    def test_required_tools_missing_acquired_nofail( self ):

        from Products.GenericSetup.tool import TOOLSET_XML
        from Products.GenericSetup.tool import importToolset

        site = self._initSite()
        parent_site = Folder()

        mandatory = AnotherDummyTool()
        mandatory._setId( 'mandatory' )
        parent_site._setObject( 'mandatory', mandatory )

        obligatory = AnotherDummyTool()
        obligatory._setId( 'obligatory' )
        parent_site._setObject( 'obligatory', obligatory )

        site = site.__of__(parent_site)

        # acquiring subobjects of a different class during import
        # should not prevent new objects from being created if they
        # don't exist in the site

        context = DummyImportContext( site, tool=site.setup_tool )
        context._files[ TOOLSET_XML ] = _REQUIRED_TOOLSET_XML

        importToolset( context )

        self.failIf( aq_base( site._getOb( 'mandatory' ) ) is mandatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'mandatory' ) )
                                   , DummyTool ) )

        self.failIf( aq_base( site._getOb( 'obligatory' ) ) is obligatory )
        self.failUnless( isinstance( aq_base( site._getOb( 'obligatory' ) )
                                   , DummyTool ) )


class DummyTool( Folder ):

    pass

class AnotherDummyTool( Folder ):

    pass

class DummyToolRequiresId( Folder ):

    def __init__(self, id):
        Folder.__init__(self)
        self._setId(id)


_EMPTY_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
</tool-setup>
"""

_NORMAL_TOOLSET_XML = """\
<?xml version="1.0" ?>
<tool-setup>
<forbidden tool_id="doomed"/>
<required class="path.to.one" tool_id="mandatory"/>
<required class="path.to.another" tool_id="obligatory"/>
</tool-setup>
"""

_FORBIDDEN_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <forbidden tool_id="doomed" />
 <forbidden tool_id="damned" />
 <forbidden tool_id="blasted" />
</tool-setup>
"""

_REQUIRED_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
 <required
    tool_id="mandatory"
    class="Products.GenericSetup.tests.test_tool.DummyTool" />
 <required
    tool_id="obligatory"
    class="Products.GenericSetup.tests.test_tool.DummyTool" />
</tool-setup>
"""

_WITH_ID_TOOLSET_XML = """\
<?xml version="1.0"?>
<tool-setup>
  <required
    tool_id="mandatory"
    class="Products.GenericSetup.tests.test_tool.DummyTool" />
  <required
    tool_id="requires_id"
    class="Products.GenericSetup.tests.test_tool.DummyToolRequiresId" />
</tool-setup>
"""

def test_suite():
    # reimport to make sure tests are run from Products
    from Products.GenericSetup.tests.test_tool import SetupToolTests
    from Products.GenericSetup.tests.test_tool import Test_exportToolset
    from Products.GenericSetup.tests.test_tool import Test_importToolset

    return unittest.TestSuite((
        unittest.makeSuite( SetupToolTests ),
        unittest.makeSuite( Test_exportToolset ),
        unittest.makeSuite( Test_importToolset ),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())
