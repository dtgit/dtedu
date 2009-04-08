#
# Component architecture support
#

# $Id: five.py 37194 2007-02-13 15:40:24Z shh42 $

from __future__ import nested_scopes

try:
    from zope.testing.cleanup import cleanUp as _cleanUp
except ImportError:
    try:
        from zope.app.testing.placelesssetup import tearDown as _cleanUp
    except ImportError:
        # Zope < 2.8
        def _cleanUp(): pass


def cleanUp():
    '''Cleans up the component architecture.'''
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0


def setDebugMode(mode):
    '''Allows manual setting of Five's inspection of debug mode
       to allow for ZCML to fail meaningfully.
    '''
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode


def safe_load_site():
    '''Loads entire component architecture (w/ debug mode on).'''
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    setDebugMode(0)


def safe_load_site_wrapper(func):
    '''Wraps func with a temporary loading of entire component
       architecture. Used as a decorator.
    '''
    def wrapped_func(*args, **kw):
        safe_load_site()
        value = func(*args, **kw)
        cleanUp()
        return value
    return wrapped_func

