from zope.app.component.hooks import setHooks
from zope.testing.cleanup import cleanUp
from Products.Five import zcml

class UidEventZCMLLayer:

    @classmethod
    def testSetUp(cls):
        import Products

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.CMFUid)
        setHooks()

    @classmethod
    def testTearDown(cls):
        cleanUp()

