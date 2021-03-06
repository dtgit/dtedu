## Script (Python) "unicodeTestIn"
##title=Test if a unicode string is in a unicode list
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=value, vocab

if vocab is None or len(vocab) == 0:
    return 0

value = context.unicodeEncode(value)
vocab = [context.unicodeEncode(v) for v in vocab]

return value in vocab
