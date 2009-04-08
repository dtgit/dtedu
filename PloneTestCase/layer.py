#
# Layer support
#

# $Id: layer.py 49924 2007-09-22 21:57:20Z shh42 $

import five

_deferred_setup = []
_deferred_cleanup = []


class ZCML:

    def setUp(cls):
        '''Sets up the CA by loading etc/site.zcml.'''
        five.safe_load_site()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        five.cleanUp()
    tearDown = classmethod(tearDown)

ZCMLLayer = ZCML


class PloneSite(ZCML):

    def setUp(cls):
        '''Sets up the Plone site(s).'''
        for func, args, kw in _deferred_setup:
            func(*args, **kw)
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Removes the Plone site(s).'''
        for func, args, kw in _deferred_cleanup:
            func(*args, **kw)
    tearDown = classmethod(tearDown)

PloneSiteLayer = PloneSite


def onsetup(func):
    '''Defers a function call to PloneSite layer setup.
       Used as a decorator.
    '''
    def deferred_func(*args, **kw):
        _deferred_setup.append((func, args, kw))
    return deferred_func


def onteardown(func):
    '''Defers a function call to PloneSite layer tear down.
       Used as a decorator.
    '''
    def deferred_func(*args, **kw):
        _deferred_cleanup.append((func, args, kw))
    return deferred_func


# Derive from ZopeLite layer if available
try:
    from Testing.ZopeTestCase.layer import ZopeLite
except ImportError:
    pass
else:
    ZCML.__bases__ = (ZopeLite,)

