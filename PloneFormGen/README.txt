Product home is http://plone.org/products/ploneformgen .
A documentation
area http://plone.org/products/ploneformgen/documentation and issue
tracker http://plone.org/products/ploneformgen/issues are available at
this location.

Please use the Plone users' mailing list or the #plone irc channel for
support requests. If you are unable to get your questions answered
there, or are interested in helping develop the product, contact Steve
McMahon: steve@dcn.org.

Overview
========

This product provides a generic Plone form generator using fields,
widgets and validators from Archetypes. Use it to build simple,
one-of-a-kind, web forms that save or mail form input.

To build a web form, create a form folder, then add form fields as
contents. Individual fields can display and validate themselves for
testing purposes. The form folder creates a form from all the contained
field content objects.

Final disposition of form input is handled via plug-in action products.
Action adapters included with this release include a mailer, a
save-data adapter that saves input in tab-separated format for later
download, and a custom-script adapter that makes it possible to script
simple actions without recourse to the Zope Management Interface.

To make it easy to get started, newly created form folders are
pre-populated to act as a simple e-mail response form.

Dependencies
============

Requires PythonField, TALESField and TemplateFields from Jens W.
Klein's ScriptableFields bundle: http://plone.org/products/scriptablefields/ 
(automatically loaded if you use buildout or easy_install).

Five, version 1.2 or later. If you have an earlier version of Five and
do not wish to upgrade Five, see the note on this in the Installation
section below.

Encryption of e-mail requires the Gnu Privacy Guard, GnuPG, also known
as gpg. See README_GPG.txt for details.

Installation
============

Buildout
--------

Just add ``Products.PloneFormGen`` to the eggs section of your buildout
configuration and run buildout.

Traditional Zope Product
------------------------

Typical for a Zope/Plone product:

*   Install dependencies.

*   Download a tarball from http://plone.org/products/ploneformgen.

*   Unpack the product package into the Products folder of the
    Zope/Plone instance. Check your ownership and permissions.

*   IF YOU ARE USING FIVE version less than 1.2 (common with Zope 2.8.x / Plone 2.1.x),
    delete or rename "configure.zcml". Otherwise, you will experience a
    variety of problems (e.g., missing component) in portal operation.
    (Note that it's also an option to upgrade your version of Five to
    version 1.2.)

Either Method Final Steps
-------------------------

*   Restart Zope.

*   Go to the Site Setup page in the Plone interface and click on the
    Add/Remove Products link. Choose PloneFormGen (check its checkbox) and
    click the Install button. If PloneFormGen is not available on the
    Add/Remove Products list, it usually means that the product did not
    load due to missing prerequisites.

*   If necessary, use the PloneFormGen configlet in the "Add-on Product
    Configuration" section of Site Setup to customize the product for your
    site.

Permissions
===========

Site managers may control the visibility and availability of many
PloneFormGen functions by changing permissions for user roles. A
control panel configlet controls role/permission associations for the
portal root. For an explanation of how PloneFormGen permissions map to
form folder and form field fields, see improvement proposal #3, Provide
ways to hide advanced options from classes of
users: http://plone.org/products/ploneformgen/roadmap/3 .

Security
========

As shipped, only managers may use TALES expressions to override
defaults and validators. You may wish to add additional roles, but keep
in mind that this is a potential security risk; it basically gives the
same powers as scripting or skin editing.

Known Problems
==============

The "max length" setting for text fields causes problems with all versions
of Plone except 2.5.3. While the field works, every keystroke will cause
javascript errors. The problem is due to various, mutating integration
problems between Archetypes, the i18n machinery, and KSS.

Rationale For This Product
==========================

*   Plone needs a general-purpose form generator that may be used for
    mail forms, RDBMS database interactions and other functions that don't
    require the Archetypes' persistence machinery;

*   Designing a form using such a form generator should not require a)
    work on the file system, b) creation of new content types, c) use of
    the ZMI (except for scripting field population or custom validation).
    [PloneFormMailer is an outstanding, useful product, that suffers only
    for its reliance on the ZMI/Formulator for design.]

*   Archetypes, in conjunction with the CMF Form Controller, has a form
    generator built-in. Ideally, it should be possible to repurpose the
    Archetypes widgets and validators (which were evidently intended to be
    generally useful) for a more general-purpose form generator.

Credits
=======

Archetypes has been ruthlessly mined for concepts and functionality.
The base view and edit macro templates are very slightly modified
versions of Archetype's base_edit and edit_macros.

Form and field icons are scavenged from Martijn Faassen's Formulator,
and were edited only to add transparency to make them look a bit better
on the add items menu.

The mail adapter is basically a tailored version of PloneFormMailer,
minus the Formulator adapter machinery. Thanks to PloneFormMailer's
authors, Jens Klein and Reinout van Rees.

Pierre-Yves Landure provided tremendous help with the i18n machinery.
Sebastien Douche and Pierre-Yves Landure provided the French translation.

Martin Aspeli's RichDocument has provided an invaluable reference,
particularly in how to handle installation and testing issues.

Martin Aspeli, Wichert Akkerman, Eric Steele, Jens Klein and Reinout
van Rees all provided valuable early feedback.

Titus Anderson provided the base code for the Ratings-Scale Field.
Andreas Jung contributed the record-editing feature for the Save Data
adapter.

See the CHANGES.txt file for the very long list of people who helped
with particular features or bugs.

License
=======

Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.
