import difflib
from Globals import InitializeClass
from Products.CMFDiffTool.FieldDiff import FieldDiff

class TextDiff(FieldDiff):
    """Text difference"""

    meta_type = "Lines Diff"

    def _parseField(self, value):
        """Parse a field value in preparation for diffing"""
        # Split the text into a list for diffs
        return value.split('\n')

    def unified_diff(self):
        """Return a unified diff"""
        a = [str(i) for i in self._parseField(self.oldValue)]
        b = [str(i) for i in self._parseField(self.newValue)]
        return '\n'.join(difflib.unified_diff(a, b, self.id1, self.id2))

    def html_diff(self, context=True, wrapcolumn=40):
        """Return an HTML table showing differences"""
        a = [str(i) for i in self._parseField(self.oldValue)]
        b = [str(i) for i in self._parseField(self.newValue)]
        vis_diff = difflib.HtmlDiff(wrapcolumn=wrapcolumn)
        return vis_diff.make_table(a, b, self.id1, self.id2, context=context)

InitializeClass(TextDiff)
