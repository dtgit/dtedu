Marshall: A framework for pluggable marshalling policies
========================================================

Features
--------

- A ControlledMarshaller class that delegates to underlying implementations
- A marshall registry tool where you can configure some predicates for
  choosing marshallers based on several pieces of information available. 

Copyright
---------

- This code is copyrighted by Enfold Systems, LLC.
  You can find more information at http://www.enfoldsystems.com/

- Portions of this code are copyright ObjectRealms
  You can find more information at http://www.objectrealms.net

License
-------

- GPL, a LICENSE file should have accompanied this module.  If not
  please contact the package maintainer.

Release Management
------------------

- Jens Klein <jens@bluedynamics.com>

Acknowledgements
----------------

- The workers: 

  o Sidnei da Silva - Designer, Test Champion and Master of Laziness

  o Alan Runyan - Cheerleading.

  o Kapil Thangavelu - ATXML handler

  o Phil Auersperg - refactoring for elementree

  o Gogo Bernhard - uuns namespace for ATXML

- The sponsors:

  o Zope Europe Association - Sponsoring

  o Bibliotheca Hertziana, Max Planck Institute for Art History - Sponsoring

- Zope Corporation for providing such a wonderful application server.

- Python Developers for making things so damn easy.

Requirements
------------

Marshall is tested with

- Python 2.3.5 or greater

- Zope 2.8.8 or greater

- Plone 2.1.3 or greater

- Archetypes 1.3.9 or later

- libxml2 2.6.6+ (previous versions seem to have a bug validating RelaxNG)

- Python elementtree 1.2.6+ 

- DavPack (optional) to support rename-on-upload
