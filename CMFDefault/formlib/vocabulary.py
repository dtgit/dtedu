##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Formlib schema vocabulary base classes.

$Id: vocabulary.py 72362 2007-02-04 15:31:51Z yuppie $
"""

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class SimpleVocabulary(SimpleVocabulary):

    def fromTitleItems(cls, items, *interfaces):
        """Construct a vocabulary from a list of (token, value, title) tuples.
        """
        terms = [ cls.createTerm(value, token, title)
                  for (token, value, title) in items ]
        return cls(terms, *interfaces)

    fromTitleItems = classmethod(fromTitleItems)


class StaticVocabulary(object):

    """Vocabulary factory for static items.
    """

    implements(IVocabularyFactory)

    def __init__(self, items):
        self._vocabulary = SimpleVocabulary.fromTitleItems(items)

    def __call__(self, context):
        return self._vocabulary
