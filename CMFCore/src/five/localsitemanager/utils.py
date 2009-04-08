from zope.traversing.interfaces import IContainmentRoot

from Acquisition import aq_parent, aq_inner


def get_parent(obj):
    """Returns the container the object was traversed via.  This
    is a version of zope.traversing.api.getParent that is designed to
    handle acquisition as well.

    Returns None if the object is a containment root.
    Raises TypeError if the object doesn't have enough context to get the
    parent.
    """
    
    if IContainmentRoot.providedBy(obj):
        return None
    
    parent = getattr(obj, '__parent__', None)
    if parent is not None:
        return parent

    parent = aq_parent(aq_inner(obj))
    if parent is not None:
        return parent

    raise TypeError("Not enough context information to get parent", obj)
