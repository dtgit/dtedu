# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# Written by Brent Hendricks

"""Interface for computing object differences"""

from Interface import Attribute
from Interface import Interface

class IChangeSet(Interface):
    """And interface representing all of the differences between two objects"""
    
    same = Attribute('same', 'True if the fields are the "same"')

    def computeDiff(ob1, ob2, recursive=1, exclude=[]):
        """Compute the differences from ob1 to ob2 (ie. ob2 - ob1).

        If resursive is 1, compute differences between subobjects of
        ob1 and ob2 as well, excluding any subobjects whose IDs are
        listed in exclude

        The results can be accessed through getDiffs()"""

    def testChanges(ob):
        """Test the specified object to determine if the change set will apply cleanly.

        Returns None if there would be no erros
        """

    def applyChanges(ob):
        """Apply the computed changes to the specified object"""
        
    def getDiffs():
        """Returns the list of differences between the two objects.

        Each difference is a single object implementing the IDifference interface"""

    def getSubDiffs():
        """If the ChangeSet was computed recursively, returns a list
           of ChangeSet objects representing subobject differences

           Each ChangeSet will have the same ID as the objects whose
           difference it represents.
           """

    def getAddedItems():
        """If the ChangeSet was computed recursively, returns the list
        of IDs of items that were added.

        A copy of these items is available as a cubject of the ChangeSet
        """

    def getRemovedItems():
        """If the ChangeSet was computed recursively, returns the list
        of IDs of items that were removed"""
    
