Salesforce PFG Adapter (PloneFormGen Add-On)

 Product home is
 "http://plone.org/products/salesforcepfgadapter":http://plone.org/products/salesforcepfgadapter.
 A "documentation area":http://plone.org/products/salesforcepfgadapter/documentation and "issue
 tracker":http://plone.org/products/salesforcepfgadapter/issues are available at
 the linked locations.

 A Google Group, called "Plone Salesforce Integration":http://groups.google.com/group/plonesf 
 exists with the sole aim of discussing and developing tools to make Plone integrate well
 with Salesforce.com.  If you have a question, joining this group and posting to the 
 mailing list is the likely best way to get support.

 Failing that, please try using the Plone users' mailing list or the #plone irc channel for
 support requests. If you are unable to get your questions answered there, or are 
 interested in helping develop the product, see the credits below for 
 individuals you might contact.

Overview

 This product builds on top of the foundation for through the web form 
 creation provided by "PloneFormGen":http://plone.org/products/ploneformgen.
 If you are unfamiliar with PloneFormGen's capabilities and the problem
 space it intends to serve, we encourage you to start by downloading that
 and reading the README.txt file in the root of the product. In particular,
 the Overview and Rationale For This Product sections are recommended.

 Once you've setup a suitable PloneFormGen form folder (and correctly
 installed and configured the Salesforce PFG Adapter and its dependencies), 
 you'll have the option of adding a new action adapter called the
 Salesforce PFG Adapter.

 Once you've added a Salesforce PFG Adapter to your form, you're presented with both 
 "default" and "field mapping" (in addition to the standard "overrides") 
 management screens for editing the adapter. The default screen consists of a 
 drop-down menu populated with all the sObject types (i.e. Salesforce Objects) 
 found in the Salesforce.com instance that corresponds to the credentials
 entered when creating a Salesforce Base Connector in the ZMI. This should include
 both standard and custom sObjects. 
 
 Once you've chosen your sObject type, moving through to the "field mapping"
 management screen will display a two-column form for setting which Salesforce 
 field will be populated by each field on your form. Each field on your form is
 represented by a single row, with the form field name in the left column, and a
 drop-down selection menu of all available Salesforce fields on the right. 
 Select the desired Salesforce field for each form field and click "Save". 
 
 NB: While it is not required to map every form field to a Salesforce field,
 you will want to make sure that all the sObject fields defined as required
 fields in your Salesforce configuration *do* have a mapping.  Otherwise, the
 sObject will not be succesfully created on submission of the form.  See
 "Known Problems"  below for more detail on this final point.
 
 Should you go back and switch to a different sObject type after having provided
 a  mapping at any time, you'll want to recreate your desired mapping.  This is
 intended behavior, since the update would fail (or worse, produce very
 confusing results) if the previously selected sObject type's mapping were
 maintained.
 
Dependencies

 See dependencies for PloneFormGen 1.2.x.  As a pre-requisite, all of these must be 
 met in order to use the Salesforce PFG Adapter.

 Depends upon the beatbox library, which is a Python wrapper to the
  Salesforce.com API (version 7.0).

  To download and install beatbox, please visit:
    http://code.google.com/p/salesforce-beatbox/

 SalesforceBaseConnector.
  See http://svn.plone.org/svn/collective/salesforcebaseconnector/trunk/

 DataGridField - In order to disable DataGridField's add row feature (an often requested 
   UI improvement for Salesforce PFG Adapter), you must use the following branch from subversion:
   https://svn.plone.org/svn/archetypes/MoreFieldsAndWidgets/DataGridField/branches/1.5-RC1
 
 
Installation

 Typical for a Zope/Plone product:

  * Install and *configure* dependencies (includes beatbox setup and creation of 
  Salesforce Base Connector with credentials in the root of the Plone site.)

  * Unpack the product package into the Products folder of the
  Zope/Plone instance. Check your ownership and permissions.

  * Restart Zope.

  * Go to the Site Setup page in the Plone interface and click on the
  Add/Remove Products link. Choose salesforcepfgadapter (check its checkbox) and
  click the Install button. If not done already, this will install PloneFormGen
  in addition to the salesforcepfgadapter.  If PloneFormGen is not available on
  the Add/Remove Products list, it usually means that the product did not load 
  due to missing prerequisites.

Permissions

 See Permissions section of README.txt within PloneFormGen.

Security

 See Security section of README.txt within PloneFormGen.

Known Problems

 * See Known Problems section of README.txt within PloneFormGen. In addition...

 * Technically, one can create two form fields with distinct ids, but the
 same Title (though this would be confusing for someone filling out the 
 form) within a form.  Duplicate titles will result in a confusing user
 interface for the Salesforce PFG Adapter, as the left column of the mapping
 interface will list both form fields for mapping with identical Titles. 
 Since field mapping is done by Title rather than object id, mapping both
 of the resulting form fields will produce unpredictable results.
 
 * Beatbox, the underlying Python wrapper library to the Salesforce.com API
 does not raise a custom exception in the scenario of the API being 
 unavailable due to scheduled maintenance as is evident with in the following 
 response:
 
   SoapFaultError: 'UNKNOWN_EXCEPTION' 'UNKNOWN_EXCEPTION: 
   Server unavailable due to scheduled maintenance'
 
 This is left of unfixed in the 1.0 branch of the Salesforce PFG Adapter, due
 to the modifications that would be required to adequately handle the case with
 technologies lower in the stack, such as Salesforce Base Connector and Beatbox.
 This will be addressed in a future release.
 
Rationale For This Product

 Using the wonderful foundation that is provided by PloneFormGen (and Plone for
 that  matter), the task of creating a form that collects and validates some
 desired information is no longer a task that requires developer intervention,
 but can be done by the content editor with a decent grasp of the Plone user
 interface.  Having this data inside the CMS or emailed is only of limited use
 however. Salesforce.com provides an extensible, powerful platform from which
 to do Customer Relationship Management (CRM) tasks ranging from sales,
 marketing, nonprofit constituent organizing, and customer service. The
 Salesforce PFG Adapter symbolizes the pragmatic joining of a best of breed CMS and
 CRM so that each can focus on its own strengths in a way that is easy for
 non-developers to use.

Credits

 The Plone & Salesforce crew in Seattle and Portland:

    Jon Baldivieso <jonb@onenw.org>
    Andrew Burkhalter <andrewb@onenw.org>
    Brian Gershon <briang@ragingweb.com>
    Jesse Snyder <jesses@npowerseattle.org>

 With special PloneFormGen guest star:

    Steve McMahon <steve@dcn.org> 

 Jesse Snyder and NPower Seattle for the foundation of code that has become
 salesforcebaseconnector
 
 Simon Fell for providing the beatbox Python wrapper to the Salesforce.com API
 
 Salesforce.com Foundation and Enfold Systems for their gift and work on beatbox (see: 
 http://gokubi.com/archives/onenorthwest-gets-grant-from-salesforcecom-to-integrate-with-plone)
 
 See the CHANGES.txt file for the growing list of people who helped
 with particular features or bugs.

License

 Distributed under the GPL.

 See LICENSE.txt and LICENSE.GPL for details.


