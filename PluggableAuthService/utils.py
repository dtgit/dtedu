##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import sha
import unittest

from Globals import package_home

try:
    from Products.Five.bridge import fromZ2Interface
except ImportError:
    def fromZ2Interface(i):
        # Raise ValueError to work around a cornerish case where
        # zope.interface is available but Five is not.
        raise ValueError, i

from zope import interface
def directlyProvides(obj, *interfaces):
    # convert any Zope 2 interfaces to Zope 3 using fromZ2Interface
    normalized_interfaces = []
    for i in interfaces:
        try:
            i = fromZ2Interface(i)
        except ValueError: # already a Zope 3 interface
            pass
        normalized_interfaces.append(i)
    return interface.directlyProvides(obj, *normalized_interfaces)

def classImplements(class_, *interfaces):
    # convert any Zope 2 interfaces to Zope 3 using fromZ2Interface
    normalized_interfaces = []
    for i in interfaces:
        try:
            i = fromZ2Interface(i)
        except ValueError: # already a Zope 3 interface
            pass
        normalized_interfaces.append(i)
    return interface.classImplements(class_, *normalized_interfaces)

# postonly protection
try:
    # Zope 2.8.9, 2.9.7 and 2.10.3 (and up)
    from AccessControl.requestmethod import postonly
except ImportError:
    try:
        # Try the hotfix too
        from Products.Hotfix_20070320 import postonly
    except:
        def postonly(callable): return callable


product_dir = package_home( globals() )
product_prefix = os.path.join( os.path.split(product_dir)[:-1] )

_wwwdir = os.path.join( product_dir, 'www' )

#
#   Most of this module is shamelessly ripped off from Zope3.test
#
def remove_stale_bytecode( arg, dirname, names ):
    """
        Troll product, removing compiled turds whose source is now gone.
    """
    names = map( os.path.normcase, names )

    for name in names:

        if name.endswith( ".pyc" ) or name.endswith( ".pyo" ):

            srcname = name[:-1]

            if srcname not in names:

                fullname = os.path.join( dirname, name )

                if __debug__:
                    print "Removing stale bytecode file", fullname

                os.unlink( fullname )

class TestFileFinder:

    def __init__( self ):
        self.files = []

    def visit( self, prefix, dir, files ):
        """
            Visitor for os.path.walk:  accumulates filenamse of unittests.
        """
        #if dir[-5:] != "tests":
        #    return

        # ignore tests that aren't in packages
        if not "__init__.py" in files:

            if not files or files == ['CVS']:
                return

            if 0 and __debug__: # XXX: don't care!
                print "not a package", dir

            return

        for file in files:

            if file.startswith( prefix ) and file.endswith( ".py" ):
                path = os.path.join(dir, file)
                self.files.append(path)

def find_unit_test_files( from_dir=product_dir, test_prefix='test' ):
    """
        Walk the product, return a list of all unittest files.
    """
    finder = TestFileFinder()
    os.path.walk( from_dir, finder.visit, test_prefix )
    return finder.files

def module_name_from_path( path ):
    """
        Return the dotted module name matching the filesystem path.
    """
    assert path.endswith( '.py' )
    path = path[:-3]
    path = path[ len(product_prefix) + 1: ] # strip extraneous crap
    dirs = []
    while path:
        path, end = os.path.split( path )
        dirs.insert( 0, end )
    return ".".join( dirs )

def get_suite( file ):
    """
        Retrieve a TestSuite from 'file'.
    """
    module_name = module_name_from_path( file )
    loader = unittest.defaultTestLoader
    try:
        suite = loader.loadTestsFromName( '%s.test_suite' % module_name )
    except AttributeError:

        try:
            suite = loader.loadTestsFromName(  module_name )
        except ImportError, err:
            print "Error importing %s\n%s" % (module_name, err)
            raise
    return suite

def allTests( from_dir=product_dir, test_prefix='test' ):
    """
        Walk the product and build a unittest.TestSuite aggregating tests.
    """
    os.path.walk( from_dir, remove_stale_bytecode, None )
    test_files = find_unit_test_files( from_dir, test_prefix )
    test_files.sort()

    suite = unittest.TestSuite()

    for test_file in test_files:

        s = get_suite( test_file )
        if s is not None:
            suite.addTest( s )

    return suite


def makestr(s):
    """Converts 's' to a non-Unicode string"""
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return str(s)

def createViewName(method_name, user_handle=None):
    """
        Centralized place for creating the "View Name" that identifies
        a ZCacheable record in a RAMCacheManager
    """
    if not user_handle:
        return makestr(method_name)
    else:
        return '%s-%s' % (makestr(method_name), makestr(user_handle))

def createKeywords(**kw):
    """
        Centralized place for creating the keywords that identify
        a ZCacheable record in a RAMCacheManager.

        Keywords are hashed so we don't accidentally expose sensitive
        information.
    """
    keywords = sha.new()

    items = kw.items()
    items.sort()
    for k, v in items:
        keywords.update(makestr(k))
        keywords.update(makestr(v))

    return {'keywords': keywords.hexdigest()}

