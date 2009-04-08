Salesforce Base Connector
=========================
Product home is
http://plone.org/products/salesforcebaseconnector.
A `documentation area`_ and `issue
tracker`_ are available at
the linked locations.

.. _documentation area: http://plone.org/documentation/manual/integrating-plone-with-salesforce.com
.. _issue tracker: http://plone.org/products/salesforcebaseconnector/issues

A Google Group, called `Plone Salesforce Integration`_ 
exists with the sole aim of discussing and developing tools to make Plone integrate well
with Salesforce.com.  If you have a question, joining this group and posting to the 
mailing list is the likely best way to get support.

.. _Plone Salesforce Integration: http://groups.google.com/group/plonesf

Failing that, please try using the Plone users' mailing list or the #plone irc channel for
support requests. If you are unable to get your questions answered there, or are 
interested in helping develop the product, see the credits below for 
individuals you might contact.

Overview
========

The Salesforce Base Connector product provides a Zope-aware tool for 
interacting with the Python-based Beatbox Salesforce client and 
for storing username and password information for connecting to
a Salesforce.com instance.

Rationale For This Product
==========================

Salesforce.com provides an extensible, powerful platform from which
to do Customer Relationship Management (CRM) tasks ranging from sales,
marketing, nonprofit constituent organizing, and customer service. 

Beatbox is a Python wrapper to the Salesforce.com API (version 7.0), and provides the 
underpinnings for this product, but suffers from several limitations from within the 
Zope/Plone integrator space.  

Salesforce Base Connector aims to augment Beatbox for Zope/Plone developers, providing a convenient
and cleanly integrated set of features:

- Managing Salesforce credentials
- Managing http connections to Salesforce
- Managing Zope permissions over view and edit actions against Salesforce
- Providing an interface to the Salesforce API from within protected python, for example, in Python Script objects and Zope Page Templates

Additionally, Salesforce Base Connector is intended to decouple Zope/Plone development projects from the specific 
Python toolkit used as the interface to Salesforce. If a more current alternative to Beatbox
comes onto the scene, Salesforce Base Connector can be updated to use this code base as its underlying framework.

Salesforce Base Connector is intended to be used as the foundational piece for your own 
Plone/Salesforce applications. 

Dependencies
============

Depends upon the Beatbox library, which is a Python wrapper to the
Salesforce.com API (version 7.0).

To download and install beatbox, please visit::

 http://code.google.com/p/salesforce-beatbox/

Installation
============

Buildout
--------

Just add ``Products.salesforcebaseconnector`` to the eggs section of your buildout
configuration and run buildout.

Traditional Zope Product
------------------------

Typical for a Zope/Plone product:

* Install dependencies (see beatbox/README.txt for install instructions)

* Unpack the salesforcebaseconnector product package into the Products folder of the Zope/Plone instance. Check your ownership and permissions.

Either Method Final Steps
-------------------------

* Restart Zope.

* In ZMI, add Salesforce Base Connector to root of site, then set username and password. The credentials will be tested for validity before being stored.


Known Problems
==============

See TODO.txt 

Credits
=======

The Plone & Salesforce crew in Seattle and Portland:

- Jon Baldivieso <jonb --AT-- onenw --DOT-- org>
- Andrew Burkhalter <andrewb --AT-- onenw --DOT-- org>
- Brian Gershon <briang --AT-- webcollective --DOT-- coop>
- David Glick <davidglick --AT-- onenw --DOT-- org> 
- Jesse Snyder <jesses --AT-- npowerseattle --DOT-- org>

Jesse Snyder and NPower Seattle for the foundation of code that has become
Salesforce Base Connector
 
Simon Fell for providing the beatbox Python wrapper to the Salesforce.com API

Salesforce.com Foundation and Enfold Systems for their gift and work on beatbox (see: 
http://gokubi.com/archives/onenorthwest-gets-grant-from-salesforcecom-to-integrate-with-plone)

See the CHANGES.txt file for the growing list of people who helped
with particular features or bugs.


License
=======

Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.


Running Tests
=============

To run tests in a unix-like environment, do the following::

 $ cd $INSTANCE/Products/salesforcebaseconnector/tests
 $ cp sfconfig.py.in sfconfig.py
 Then edit sfconfig.py with your Salesforce.com USERNAME and PASSWORD
 $ cd $INSTANCE
 $ ./bin/zopectl test -s Products.salesforcebaseconnector


FAQ about running tests
=======================

If you see an error message like the following and you're certain your login/password combination *IS* valid::

 SoapFaultError: 'INVALID_LOGIN' 'INVALID_LOGIN: Invalid username or password or locked out.'

You're likely running into one of several security measures in effect at Salesforce.com. You can do one of the following.


**Setup your security token within your Salesforce instance and append it to your password**
To do so, following these instructions:

1) Log into your Salesforce.com instance
2) Click Setup
3) My Personal information
4) Reset My Security Token
5) edit sfconfig.py to have "mypassword[token]" (where [token] is your security token)

**Whitelist your IP address**

This can be done at the following:

1) Log into your Salesforce.com instance
2) Click Setup
3) Security Controls
4) Network Access

The latter option may be preferable in a production environment, since the security token is more likely to change over time with password updates.  For testing, either is fine.

You can find the needed background at http://www.salesforce.com/security/

Often tests can fail if one has aborted the running of the tests midstream, thus bypassing
the cleanup (i.e. removing fake contacts) that happens after each individual test is run.  If you
encounter incorrect assertions about the numbers of contacts in your Salesforce instance, 
try searching for and cleaning up dummy John and Jane Doe contacts.


