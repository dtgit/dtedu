from Globals import InitializeClass
from Products.CMFDiffTool.BaseDiff import BaseDiff, _getValue


class BinaryDiff(BaseDiff):
    """Simple binary difference"""

    meta_type = "Binary Diff"

    def testChanges(self, ob):
        """Test the specified object to determine if the change set will apply without errors"""
        value = _getValue(ob, self.field)
        if not self.same and value != self.oldValue:
            raise ValueError, ("Conflict Error during merge", self.field, value, self.oldValue)
        
    def applyChanges(self, ob):
        """Update the specified object with the difference"""
        # Simplistic update
        self.testChanges(ob)
        if not self.same:
            setattr(ob, self.field, self.newValue)
        
InitializeClass(BinaryDiff)

