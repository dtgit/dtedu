def install(self):
    out = []

    if getattr(self, 'portal_quickinstaller', None) is None:
        addTool = self.manage_addProduct['CMFQuickInstallerTool'].manage_addTool
        addTool('CMF QuickInstaller Tool', None)
        out.append('Added QuickInstaller Tool')

    return '\n'.join(out)
