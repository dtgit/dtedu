HAS_ZOPE = False

try:
    import Zope2 # > 2.8
    HAS_ZOPE = True
except ImportError:
    try:
        import Zope as Zope2 # < 2.8
        HAS_ZOPE = True
    except ImportError:
        # HAS_ZOPE is set to False by default
        pass

if HAS_ZOPE:
    from ZService import ZService as Service
else:
    # stand alone validator
    from service import Service

from validators import initialize

validation = Service()

initialize(validation)
