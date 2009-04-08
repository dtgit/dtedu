## Script (Python) "getXMLSelectVocab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=method,param,value
##title=Get a DisplayList and format for XML request

params = {param:value, 'display_list': True}

vocab = getattr(context, method)(**params)
site_encoding = context.plone_utils.getSiteEncoding()

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml;charset=%s' % site_encoding)
translate = context.translate

results = [(translate(vocab.getValue(item)),item) for item in vocab]

item_strings = [u'^'.join(a) for a in results]
result_string = u'|'.join(item_strings)

return "<div>%s</div>" % result_string.encode(site_encoding)