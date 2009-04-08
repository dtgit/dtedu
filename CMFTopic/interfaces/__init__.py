##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFTopic product interfaces.

$Id: __init__.py 67932 2006-05-03 14:36:10Z yuppie $
"""

from zope.interface import Interface


class ITopic(Interface):

    """ Topics are 'canned queries'.

    o Each topic holds a set of zero or more Criteria objects specifying
      the query.
    """

    def queryCatalog(REQUEST=None, **kw):
        """ Invoke the catalog using our criteria.

        o Built-in criteria update any criteria passed in 'kw'.
        """


class IMutableTopic(ITopic):

    """ Updatable form of ITopic.
    """


class ICriterion(Interface):
    """\
    A Topic is composed of Criterion objects which specify the query
    used for the Topic.  By supplying some basic information, the
    Criterion objects can be plugged into Topics without the Topic
    having to be too aware of the Criteria types.
    """

    def Type():
        """\
        Return the type of criterion object this is (ie - 'List Criterion')
        """

    def Field():
        """\
        Return the field this criterion object searches on.
        """

    def Description():
        """\
        Return a brief description of the criteria type.
        """

    def editableAttributes():
        """\
        Returns a tuble of editable attributes.  The values of this
        are used by the topic to build commands to send to the
        'edit' method based on each criterion's setup.
        """

    def getEditForm():
        """\
        Return the name of a DTML component used to edit criterion.
        Editforms should be specific to their type of criteria.
        """

    def apply(command):
        """\
        To make it easier to apply values from the rather dynamic
        Criterion edit form using Python Scripts, apply takes a
        mapping object as a default and applies itself to self.edit.

        It's basically a nice and protected wrapper around
        self.edit(**command).
        """

# XXX: Interfaces have to specify the signature.
##    def edit(**kw):
##        """\
##        The signature of this method should be specific to the
##        criterion.  Using the values in the attribute
##        '_editableAttributes', the Topic can apply the right
##        commands to each criteria object as its being edited without
##        having to know too much about the structure.
##        """

    def getCriteriaItems():
        """\
        Return a sequence of key-value tuples, each representing
        a value to be injected into the query dictionary (and,
        therefore, tailored to work with the catalog).
        """


# BBB: will be removed in CMF 2.2
#      create zope2 interfaces
from Interface.bridge import createZope3Bridge
import Criterion

createZope3Bridge(ICriterion, Criterion, 'Criterion')

from Criterion import Criterion
del createZope3Bridge
