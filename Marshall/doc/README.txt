========
Marshall
========

A framework for pluggable marshalling policies
==============================================

:Author: Sidnei da Silva
:Contact: sidnei@awkly.org
:Date: $Date: 2006-06-08 00:21:40 +0200 (Thu, 08 Jun 2006) $
:Version: $Revision: 1.1 $

People coming to Plone from other CMS or from no CMS at all often want
to be able to bulk import existing content. There are also cases of
sites which produce a high volume of content that needs to be
published constantly.

The easiest way to achieve the goal of allowing import/export of
structured content currently is through introspectable
schemas. Archetypes provides this right now. However, Archetypes
expects a schema to have only one marshaller component, and the
default ones are not able to marshall all the facets of a complex
piece of content by themselves.

The Marshall product provides the missing pieces of this complicated
puzzle by giving you:

- A ``ControlledMarshaller`` implementation, which resorts on a tool
  to decide which marshaller implementation should be used for
  marshalling a given piece of content or demarshalling an uploaded
  file.

- A ``marshaller_tool`` which sits on the root of your CMF/Plone site
  and that allows you to do fine grained control of marshallers.

- Simple export functionality to dump the Archetypes-based objects of
  your CMF/Plone site as a hierarchy of files in .zip format.

Installation
------------

Installing is as simple as clicking a button, thanks to
QuickInstaller. However, by default only the ``marshaller_tool`` is
installed. After that, you need to add some ``marshaller predicates``
by yourself. You can do that through the ZMI. The interface should be
verbose enough to tell you all that you need to know to be able to
make a simple setup.

Let's go through a step-by-step example on how to setup the ``Marshaller
Registry`` programatically.

If you follow the steps listed here, you will have a working setup
that can handle uploading either a ``ATXML`` file, or some other file
containing whatever you like.

Assuming you already installed the ``Marshall`` and the
``ATContentTypes`` products using the quick-installer tool, the next step
is to add a couple marshaller predicates.

Our setup will consist of two predicates: one for handling ``ATXML``
files, and another dummy predicate to be used as a ``fallback``, ie:
if it's not ATXML, use the dummy predicate.

Add a predicate of the ``xmlns_attr`` kind. This kind of predicate is
used to check for the existence of a certain attribute or element in a
XML file. If the predicate matches, we will map it to the ``atxml``
marshaller (component_name).

    >>> from Products.Marshall.predicates import add_predicate
    >>> from Products.Marshall.config import TOOL_ID as marshall_tool_id
    >>> from Products.Marshall.config import AT_NS, CMF_NS
    >>> from Products.CMFCore.utils import getToolByName

    >>> tool = getToolByName(self.portal, marshall_tool_id)
    >>> p = add_predicate(tool, id='atxml',
    ...                   title='ATXML Predicate',
    ...                   predicate='xmlns_attr',
    ...                   expression='',
    ...                   component_name='atxml')

Then edit the predicate so that it matches on the existence of a
element named ``metadata`` using the ``AT_NS`` namespace.

    >>> p.edit(element_ns=AT_NS, element_name='metadata', value=None)

Add a default predicate, that just maps to the ``primary_field``
marshaller (which just stuffs the content of the uploaded file into
the object's primary field).

    >>> p = add_predicate(tool, id='default',
    ...                   title='Default Marshaller',
    ...                   predicate='default',
    ...                   expression='',
    ...                   component_name='primary_field')

The next step is making your Archetypes-based schema aware of the
Marshaller Registry, by making it use the ``ControlledMarshaller``
implementation.

For our example, we will use the ``ATDocument`` class from the
``ATContentTypes`` product.

    >>> from Products.ATContentTypes.atct import ATDocument
    >>> from Products.Marshall import ControlledMarshaller

Save current marshaller implementation, and register
``ControlledMarshaller`` on it's place.

    >>> old_marshall = ATDocument.schema.getLayerImpl('marshall')
    >>> ATDocument.schema.registerLayer('marshall',
    ...                              ControlledMarshaller())

At this point, our Article should be able to use the Marshaller
Registry to decide what Marshaller to use at runtime.

    >>> from Products.Archetypes.tests.utils import makeContent
    >>> article = makeContent(self.portal, 'Document', 'article')
    >>> article.getId()
    'article'

    >>> article.Title()
    ''

    >>> article.setTitle('Example Article')
    >>> article.Title()
    'Example Article'

    >>> article.getPortalTypeName()
    'Document'

    >>> article.getText()
    ''

    
Upload a very simple ATXML file and make sure it used the ATXML
Marshaller by checking that the Title got changed and the body is
still empty. Note we also support CDATA sections, so we'll stick some
stuff into the 'blurb' field using CDATA.


  >>> xml_input = """
  ... <?xml version="1.0" ?>
  ... <metadata xmlns="http://plone.org/ns/archetypes/"
  ...           xmlns:dc="http://purl.org/dc/elements/1.1/"
  ...           xmlns:xmp="adobe:ns:meta">
  ...   <dc:title>
  ...     Some Title
  ...   </dc:title>
  ...   <xmp:CreateDate>
  ...     2004-01-01T00:02:04Z
  ...   </xmp:CreateDate>
  ...   <field id="expirationDate">
  ...     2004-09-09T09:09:08Z
  ...   </field>
  ...   <field id="text">
  ...    Here is some Text
  ...   </field>
  ... </metadata>"""

  >>> print http(r"""
  ... PUT /plone/article HTTP/1.1
  ... Content-Type: text/xml
  ... Authorization: Basic portal_owner:secret
  ... %s""" %  xml_input, handle_errors=False)
  HTTP/1.1 204 No Content...

  
  >>> article.Title()
  'Some Title'

  >>> article.getText()
  '<p>Here is some Text</p>'

  >>> article.CreationDate()
  '2004-01-01 00:02:04'

  >>> article.ExpirationDate()
  '2004-09-09 09:09:08'


Upload a text file (in this case, 'text/x-rst') and make sure the body
field was updated with the uploaded file contents.

  >>> rst_input = """
  ... Title
  ... =====
  ...
  ... Some Text
  ... """

  >>> print http(r"""
  ... PUT /plone/article HTTP/1.1
  ... Content-Type: text/x-rst
  ... Authorization: Basic portal_owner:secret
  ... %s""" % rst_input, handle_errors=False)
  HTTP/1.1 204 No Content...

  >>> article.Title()
  'Some Title'

Get the ``raw`` body value. Using getBody() would return the rendered HTML.

  >>> print article.getField('text').getRaw(article)
  Title
  =====
  <BLANKLINE>
  Some Text
  <BLANKLINE>

Now, just restore the previous marshaller, as to leave everything in
the same state it was found:

    >>> ATDocument.schema.registerLayer('marshall',
    ...                                  old_marshall)
