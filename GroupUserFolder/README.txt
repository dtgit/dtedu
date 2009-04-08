GroupUserFolder


(c)2002-03-04 Ingeniweb



(This is a structured-text formated file)



ABSTRACT

  GroupUserFolder is a kind of user folder that provides a special kind of user management.
  Some users are "flagged" as GROUP and then normal users will be able to belong to one or
  serveral groups.

  See http://ingeniweb.sourceforge.net/Products/GroupUserFolder for detailed information.

DOWNLOAD

  See http://sourceforge.net/project/showfiles.php?group_id=55262&package_id=81576


STRUCTURE

  Group and "normal" User management is distinct. Here's a typical GroupUserFolder hierarchy::

     - acl_users (GroupUserFolder)
     |
     |-- Users (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)
     |
     |-- Groups (GroupUserFolder-related class)
     | |
     | |-- acl_users (UserFolder or derived class)


  So, INSIDE the GroupUserFolder (or GRUF), there are 2 acl_users :

    - The one in the 'Users' object manages real users

    - The one in the 'Groups' object manages groups

  The two acl_users are completely independants. They can even be of different kinds.
  For example, a Zope UserFolder for Groups management and an LDAPUserFolder for Users management.

  Inside the "Users" acl_users, groups are seen as ROLES (that's what we call "groles") so that 
  roles can be assigned to users using the same storage as regular users. Groups are prefixed
  by "group " so that they could be easily recognized within roles.

  Then, on the top GroupUserFolder, groups and roles both are seen as users, and users have their
  normal behaviour (ie. "groles" are not shown), except that users affected to one or several groups
  have their roles extended with the roles affected to the groups they belong to.


  Just for information : one user can belong to zero, one or more groups.
  One group can have zero, one or more users affected.

  [2003-05-10] There's currently no way to get a list of all users belonging to a particular group.


GROUPS BEHAVIOUR

  
  ...will be documented soon...


GRUF AND PLONE

  See the dedicated README-Plone file.


GRUF AND SimpleUserFolder

  You might think there is a bug using GRUF with SimpleUserFolder (but there's not): if you create
  a SimpleUserFolder within a GRUF a try to see it from the ZMI, you will get an InfiniteRecursionError.

  That's because SimpleUserFolder tries to fetch a getUserNames() method and finds GRUF's one, which 
  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's one, 
  which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds GRUF's 
  one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and finds 
  GRUF's one, which  tries to call SimpleUserFolder's one which tries to fetch a getUserNames() method and 
  finds GRUF's one, which  tries to call SimpleUserFolder's one which tries (see what I mean ?)

  To avoid this, just create a new_getUserNames() object (according to SimpleUserFolder specification) in the folder
  where you put your SimpleUserFolder in (ie. one of 'Users' or 'Groups' folders).

  GRUF also implies that the SimpleUserFolder methods you create are defined in the 'Users' or 'Groups' folder.
  If you define them above in the ZODB hierarchy, they will never be acquired and GRUF ones will be catched
  instead, causing infinite recursions.


GRUF AND LDAPUserFolder

  [NEW IN 3.0 VERSION: PLEASE READ README-LDAP.stx INSTEAD]

BUGS

  There is a bug using GRUF with Zope 2.5 and Plone 1.0Beta3 : when trying to join the plone site
  as a new user, there is a Zope error "Unable to unpickle object"... I don't know how to fix that now.
  With Zope 2.6 there is no such bug.

DEBUG

  If you put a file named 'debug.txt' in your GRUF's product directory, it will switch the product in
  debug mode next time you restart Zope. This is the common behaviour for all Ingeniweb products.
  Debug mode is normally just a way of printing more things on the console. But, with GRUF, debug
  mode (since 3.1 version) enables a basic user source integrity check. If you've got a broken user 
  folder product on your hard drive that you use as a source with GRUF, it will allow you to unlock
  the situation.

LICENCE

  GRUF > 2 is released under the terms of the Zope Public Licence (ZPL). Specific arrangements can be found for closed-source projects : please contact us.

