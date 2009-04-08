from Acquisition import aq_inner
from Products.Five import BrowserView


# map from mimetypes used in allowable_content_types to mimetypes that are stored
# in the base unit
MIMETYPES_MAPPING = {
    'text/x-python' : 'text/python-source',
    'text/restructured': 'text/x-rst',
}


class SelectionWidget(BrowserView):
    """View used in Archetypes language and selection widget.

    We start with a browser view for this widget.  We use a test
    request and some very simple content to initialize it.

    >>> from zope.publisher.browser import TestRequest
    >>> class SimpleContent(object):
    ...     def getCharset(self):
    ...         return 'utf-8'
    >>> widget = SelectionWidget(SimpleContent(), TestRequest())

    Test with a simple vocabulary

    >>> vocab = ('a', 'b', 'c')
    >>> widget.getSelected(vocab, 'a')
    ['a']
    >>> widget.getSelected(vocab, 'A')
    []
    >>> widget.getSelected(vocab, 'd')
    []

    Test with a DisplayList

    >>> from Products.Archetypes.utils import DisplayList
    >>> friends = DisplayList([('Monty Python', u'monty'), (u'Guido van Rossum', u'guido')])
    >>> widget.getSelected(friends, 'monty')
    []
    >>> widget.getSelected(friends, u'guido')
    []
    >>> widget.getSelected(friends, 'Spanish Inquisition')
    []

    getSelected is used to get a list of selected vocabulary items.
    In the widget, we repeat on the vocabulary, comparing
    its values with those returned by getSelected. So,    
    we always return the same encoding as in the vocabulary.

    >>> widget.getSelected(friends, u'Monty Python')
    ['Monty Python']
    >>> widget.getSelected(friends, 'Monty Python')
    ['Monty Python']
    >>> widget.getSelected(friends, u'Guido van Rossum')
    [u'Guido van Rossum']
    >>> widget.getSelected(friends, 'Guido van Rossum')
    [u'Guido van Rossum']

    Test with an IntDisplayList:

    >>> from Products.Archetypes.utils import IntDisplayList
    >>> quarter_vocabulary = IntDisplayList([(0, '0'), (15, '15'), (30, '30'), (45, '45')])
    >>> widget.getSelected(quarter_vocabulary, 5)
    []
    >>> widget.getSelected(quarter_vocabulary, 15)
    [15]
    >>> widget.getSelected(quarter_vocabulary, '15')
    []

    """

    def getSelected(self, vocab, value):
        
        context = aq_inner(self.context)

        site_charset = context.getCharset()

        # compile a dictionary from the vocabulary of
        # items in {encodedvalue : originalvalue} format
        vocabKeys = {}
        for key in vocab:
            # vocabulary keys can only be strings or integers
            if isinstance(key, str):
                vocabKeys[key.decode(site_charset)] = key
            else:
                vocabKeys[key] = key
        
        # compile a dictonary of {encodedvalue : oldvalue} items
        # from value -- which may be a sequence, string or integer.
        values = {}
        if isinstance(value, tuple) or isinstance(value, list):
            for v in value:
                new = v
                if isinstance(v, int):
                    v = str(v)
                elif isinstance(v, str):
                    new = v.decode(site_charset)
                values[new] = v
        else:
            if isinstance(value, str):
                new = value.decode(site_charset)
            elif isinstance(value, int):
                new = value
            else:
                new = str(value)
            values[new] = value

        # now, build a list of the vocabulary keys
        # in their original charsets.
        selected = []
        for v in values:
            ov = vocabKeys.get(v)
            if ov:
                selected.append(ov)

        return selected


class TextareaWidget(BrowserView):
    """View used in Archetypes textarea widget."""

    def getSelected(self, mimetypes, contenttype):
        # An object can have only one contenttype at a time and mimetypes
        # are limited to ASCII-only characters. We already assumed to get all
        # values in all lowercase, so we don't do any case-juggling.

        contenttype = MIMETYPES_MAPPING.get(contenttype, contenttype)

        if contenttype in mimetypes:
            return (contenttype, )

        return ()

    def lookupMime(self, name):
        context = aq_inner(self.context)
        mimetool = context.mimetypes_registry
        mimetypes = mimetool.lookup(name)
        if len(mimetypes):
            return mimetypes[0].name()
        else:
            return name
