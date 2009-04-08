## Script (Python) "ecpd_search_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##

REQUEST = context.REQUEST

I18N_DOMAIN = 'eduComponents'

msg = ''

#is a valid Normalizer choosen?
normName = REQUEST.get('normalizer_selection', None)
if (not normName) or (not normName in context.getNormalizerNames()):
	msg = 'Please choose a normalizer.'

#is a valid algorithm choosen?
algName = REQUEST.get('algorithm_selection', None)
if (not algName) or (not algName in context.getAlgorithmNames()):
	msg += 'Please choose an algorithm.'
        state.setError('algorithm', 'Please choose an algorithm.', new_status='failure')

#is the MML valid, i.e. >1
mml = REQUEST.get('MML', None)
if mml and (int(mml)<1):
	msg += 'Please set a minimal matching length (MML) greater than 0.'

#is the treshold valid, i.e. 0.0<=treshold<=1.0
treshold = REQUEST.get('treshold', None)
if treshold:
	treshold = round(float(treshold), 2)
	if (treshold<0 or 1<treshold):
		msg += 'Please set a treshold 0<=treshold<=1.'


if msg:
	failure_msg = context.translate(
		msgid = "search_cannot_be_performed",
		domain = I18N_DOMAIN,
		default = "Seach cannot be performed: "+msg)
	return state.set(status='failure', portal_status_message = failure_msg)
else:
	return state
