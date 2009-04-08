PloneTestCase 0.9.7
(c) 2003-2007, Stefan H. Holek, stefan@epy.co.at
http://plone.org/products/plonetestcase
License: GPL
Zope: 2.6-2.11


PloneTestCase Readme

    PloneTestCase is a thin layer on top of the ZopeTestCase package. It has
    been developed to simplify testing of Plone-based applications and products.


    The PloneTestCase package provides:

        - The function 'installProduct' to install a Zope product into the
          test environment.

        - The function 'installPackage' to install a Python package
          registered via five:registerPackage into the test environment.
          Requires Zope 2.10.4 or higher.

        - The function 'setupPloneSite' to create a Plone portal in the test db.

          Note: 'setupPloneSite' accepts an optional 'products' argument, which
          allows you to specify a list of products that will be added to the
          portal using the quickinstaller tool. Since 0.8.2 you can also pass
          an 'extension_profiles' argument to import GS extension profiles.

        - The class 'PloneTestCase' of which to derive your test cases.

        - The class 'FunctionalTestCase' of which to derive your test cases
          for functional unit testing.

        - The classes 'Sandboxed' and 'Functional' to mix-in with your own
          test cases.

        - The constants 'portal_name', 'portal_owner', 'default_policy',
          'default_products', 'default_base_profile', 'default_extension_profiles',
          'default_user', and 'default_password'.

        - The constant 'PLONE21' which evaluates to true for Plone
          versions >= 2.1.

        - The constant 'PLONE25' which evaluates to true for Plone
          versions >= 2.5.

        - The constant 'PLONE30' which evaluates to true for Plone
          versions >= 3.0.

        - The constant 'PLONE31' which evaluates to true for Plone
          versions >= 3.1.

        - The constant 'PLONE40' which evaluates to true for Plone
          versions >= 4.0.

        - The module 'utils' which contains all utility functions from the
          ZopeTestCase package.


    Example PloneTestCase::

        from Products.PloneTestCase import PloneTestCase

        PloneTestCase.installProduct('SomeProduct')
        PloneTestCase.setupPloneSite(products=('SomeProduct',))

        class TestSomething(PloneTestCase.PloneTestCase):

            def afterSetup(self):
                self.folder.invokeFactory('Document', 'doc')

            def testEditDocument(self):
                self.folder.doc.edit(text_format='plain', text='data')
                self.assertEqual(self.folder.doc.EditableBody(), 'data')


    Example PloneTestCase setup with GenericSetup::

        from Products.PloneTestCase import PloneTestCase

        PloneTestCase.installProduct('SomeProduct')
        PloneTestCase.setupPloneSite(extension_profiles=('SomeProduct:default',))


    Please see the docs of the ZopeTestCase package, especially those
    of the PortalTestCase class.

    Look at the example tests in this directory to get an idea of how
    to use the PloneTestCase package. Also see the tests coming with
    Plone 2.x.

    Copy testSkeleton.py to start your own tests.

