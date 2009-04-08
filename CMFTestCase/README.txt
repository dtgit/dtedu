CMFTestCase 0.9.7
(c) 2003-2007, Stefan H. Holek, stefan@epy.co.at
http://plone.org/products/cmftestcase
License: ZPL
Zope: 2.6-2.11


CMFTestCase Readme

    CMFTestCase is a thin layer on top of the ZopeTestCase package. It has
    been developed to simplify testing of CMF-based applications and products.


    The CMFTestCase package provides:

        - The function 'installProduct' to install a Zope product into the
          test environment.

        - The function 'installPackage' to install a Python package
          registered via five:registerPackage into the test environment.
          Requires Zope 2.10.4 or higher.

        - The function 'setupCMFSite' to create a CMF portal in the test db.

          Note: 'setupCMFSite' accepts an optional 'products' argument, which
          allows you to specify a list of products that will be added to the
          portal. Product installation is performed via the canonical
          'Extensions.Install.install' function. Since 0.8.2 you can also pass
          an 'extension_profiles' argument to import GS extension profiles.

        - The class 'CMFTestCase' of which to derive your test cases.

        - The class 'FunctionalTestCase' of which to derive your test cases
          for functional unit testing.

        - The classes 'Sandboxed' and 'Functional' to mix-in with your own
          test cases.

        - The constants 'portal_name', 'portal_owner', 'default_products',
          'default_base_profile', 'default_extension_profiles',
          'default_user', and 'default_password'.

        - The constant 'CMF15' which evaluates to true for CMF versions
          >= 1.5.

        - The constant 'CMF16' which evaluates to true for CMF versions
          >= 1.6.

        - The constant 'CMF20' which evaluates to true for CMF versions
          >= 2.0.

        - The constant 'CMF21' which evaluates to true for CMF versions
          >= 2.1.

        - The module 'utils' which contains all utility functions from the
          ZopeTestCase package.


    Example CMFTestCase::

        from Products.CMFTestCase import CMFTestCase

        CMFTestCase.installProduct('SomeProduct')
        CMFTestCase.setupCMFSite(products=('SomeProduct',))

        class TestSomething(CMFTestCase.CMFTestCase):

            def afterSetup(self):
                self.folder.invokeFactory('Document', 'doc')

            def testEditDocument(self):
                self.folder.doc.edit(text_format='plain', text='data')
                self.assertEqual(self.folder.doc.EditableBody(), 'data')


    Example CMFTestCase setup with GenericSetup::

        from Products.CMFTestCase import CMFTestCase

        CMFTestCase.installProduct('SomeProduct')
        CMFTestCase.setupCMFSite(extension_profiles=('SomeProduct:default',))


    Please see the docs of the ZopeTestCase package, especially those
    of the PortalTestCase class.

    Look at the example tests in this directory to get an idea of how
    to use the CMFTestCase package.

    Copy testSkeleton.py to start your own tests.

