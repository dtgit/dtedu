#
# ChangeSet.py - Zope object representing the differences between
# objects
#
# Code by Brent Hendricks
#
# (C) 2003 Brent Hendricks - licensed under the terms of the
# GNU General Public License (GPL).  See LICENSE.txt for details

import logging
import transaction
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass
from OFS.CopySupport import CopyError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDiffTool.interfaces import IChangeSet
from Products.CMFDiffTool.interfaces.IChangeSet import IChangeSet as IChangeSetZ2

logger = logging.getLogger('CMFDiffTool')

def manage_addChangeSet(self, id, title='', REQUEST=None):
    """Creates a new ChangeSet object """
    id=str(id)
    if not id:
        raise "Bad Request", "Please specify an ID."

    self=self.this()
    cs = ChangeSet(id, title)
    self._setObject(id, cs)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


factory_type_information = (
    {'id': 'ChangeSet',
     'content_icon': 'changeset.png',
     'meta_type': 'Change Set',
     'description': ('A collection of changes between two objects'),
     'product': 'CMFDiffTool',
     'global_allow':0,
     'factory': 'manage_addChangeSet',
     'filter_content_types' : 0,
     'immediate_view': 'changeset_edit_form',
     'actions': ({'id': 'view',
                  'name': 'View Changes',
                  'action': 'changeset_view',
                  'permissions': (View,),
                  'visible':1},
                 {'id': 'edit',
                  'name': 'Edit Change set',
                  'action': 'changeset_edit_form',
                  'permissions': (ModifyPortalContent,),
                  'visible':1},
                 )
     },
    )

class BaseChangeSet(Implicit):
    """A ChangeSet represents the set of differences between two objects"""

    __implements__ = (IChangeSetZ2,)
    implements(IChangeSet)
    # This should really not be needed just for same, we should use a method
    __allow_access_to_unprotected_subobjects__ = 1
    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        """ChangeSet constructor"""
        self.id = id
        self.title = title
        self._diffs = []
        self._added = []
        self._removed = []
        self.ob1_path = []
        self.ob2_path = []
        self._changesets = {}
        self.recursive = 0

    security.declarePublic('getId')
    def getId(self):
        """ChangeSet id"""
        return self.id

    def __getitem__(self, key):
        return self._changesets[key]

    def _isSame(self):
        """Returns true if there are no differences between the two objects"""
        return reduce(lambda x, y: x and y, [d.same for d in self._diffs], 1)

    security.declarePublic('same')
    same = ComputedAttribute(_isSame)

    security.declarePublic('computeDiff')
    def computeDiff(self, ob1, ob2, recursive=1, exclude=[], id1=None, id2=None):
        """Compute the differences from ob1 to ob2 (ie. ob2 - ob1).

        The results can be accessed through getDiffs()"""

        # Reset state
        self._diffs = []
        self._added = []
        self._removed = []
        self._changed = []
        self._changesets = {}

        purl = getToolByName(self, 'portal_url', None)
        if purl is not None:
            try:
                self.ob1_path = purl.getRelativeContentPath(ob1)
                self.ob2_path = purl.getRelativeContentPath(ob2)
            except AttributeError:
                # one or both of the objects may not have a path
                return
        diff_tool = getToolByName(self, "portal_diff")
        self._diffs = diff_tool.computeDiff(ob1, ob2, id1=id1, id2=id2)

        if recursive and ob1.isPrincipiaFolderish and \
                                                     ob2.isPrincipiaFolderish:
            self.recursive = 1
            ids1 = set(ob1.objectIds())
            ids2 = set(ob2.objectIds())
            self._changed = ids1.intersection(ids2)
            self._removed = ids1.difference(ids2)
            self._added = ids2.difference(ids1)

            # Ignore any excluded items
            for id in exclude:
                try:
                    self._added.remove(id)
                except ValueError:
                    pass
                try:
                    self._removed.remove(id)
                except ValueError:
                    pass
                try:
                    self._changed.remove(id)
                except ValueError:
                    pass

            # Calculate a ChangeSet for every subobject that has changed
            # XXX this is a little strange as self._changed doesn't appear
            # to list changed objects, but rather objects which have been
            # reordered or renamed.
            for id in self._changed:
                self._addSubSet(id, ob1, ob2, exclude, id1, id2)

    def _addSubSet(self, id, ob1, ob2, exclude, id1, id2):
        cs = BaseChangeSet(id, title='Changes to: %s' % id)
        cs = cs.__of__(self)
        cs.computeDiff(ob1[id], ob2[id], exclude=exclude, id1=id1, id2=id2)
        self._changesets[id] = aq_base(cs)

    security.declarePublic('testChanges')
    def testChanges(self, ob):
        """Test the specified object to determine if the change set will apply without errors"""
        for d in self._diffs:
            d.testChanges(ob)

        for id in self._changed:
            cs = self[id]
            child = ob[id]
            cs.testChanges(child)

    security.declarePublic('applyChanges')
    def applyChanges(self, ob):
        """Apply the change set to the specified object"""
        for d in self._diffs:
            d.applyChanges(ob)

        if self._removed:
            ob.manage_delObjects(self._removed)

        for id in self._added:
            child = self[id]
            ob.manage_clone(child, id)

        for id in self._changed:
            cs = self[id]
            child = ob[id]
            cs.applyChanges(child)

    security.declarePublic('getDiffs')
    def getDiffs(self):
        """Returns the list differences between the two objects.

        Each difference is a single object implementing the IDifference interface"""
        return self._diffs

    security.declarePublic('getSubDiffs')
    def getSubDiffs(self):
        """If the ChangeSet was computed recursively, returns a list
           of ChangeSet objects representing subjects differences

           Each ChangeSet will have the same ID as the objects whose
           difference it represents.
           """
        return [self[id] for id in self._changed]

    security.declarePublic('getAddedItems')
    def getAddedItems(self):
        """If the ChangeSet was computed recursively, returns the list
        of IDs of items that were added.

        A copy of these items is available as a cubject of the ChangeSet
        """
        return list(self._added)

    security.declarePublic('getRemovedItems')
    def getRemovedItems(self):
        """If the ChangeSet was computed recursively, returns the list
        of IDs of items that were removed"""
        return list(self._removed)


class ChangeSet(BaseChangeSet, SkinnedFolder, DefaultDublinCoreImpl):
    """A persistent skinnable contentish Change Set"""
    meta_type = "Change Set"
    portal_type = "ChangeSet"
    security = ClassSecurityInfo()

    try:
        __implements__ = (BaseChangeSet.__implements__ +
                            SkinnedFolder.__implements__ +
                            DefaultDublinCoreImpl.__implements__)
    except TypeError:
        # FFF for CMF trunk
        __implements__ = (BaseChangeSet.__implements__ +
                            (SkinnedFolder.__implements__,))

    def __init__(self, id, title=''):
        BaseChangeSet.__init__(self, id, title='')
        DefaultDublinCoreImpl.__init__(self)

    def __getitem__(self, key):
        SkinnedFolder.__getitem__(self, key)

    def computeDiff(self, ob1, ob2, recursive=1, exclude=[], id1=None, id2=None):
        self.manage_delObjects(self.objectIds())
        BaseChangeSet.computeDiff(self, ob1, ob2, recursive, exclude, id1, id2)
        if recursive and ob1.isPrincipiaFolderish:
            # Clone any added subobjects
            for id in self._added:
                ob = ob2[id]
                logger.log(logging.DEBUG, "ChangeSet: cloning %s (%s)" % (id, ob))
                try:
                    self.manage_clone(ob, id)
                except CopyError:
                    # If one of the objects isn't actually local to the ZODB
                    # (i.e. it is a version in some other repository), this
                    # will fail
                    pass

        self._p_changed = 1

    # Override _addSubSet to add persistent sub changesets
    def _addSubSet(self, id, ob1, ob2, exclude, id1, id2):
        self.manage_addProduct['CMFDiffTool'].manage_addChangeSet(id,
                                                  title='Changes to: %s' % id)
        transaction.savepoint(optimistic=True)
        self[id].computeDiff(ob1[id], ob2[id], exclude=exclude, id1=id1, id2=id2)


InitializeClass(ChangeSet)
