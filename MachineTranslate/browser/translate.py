from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.LinguaPlone import LinguaPloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from SOAPpy import WSDL
from BeautifulSoup import BeautifulSoup, NavigableString


class CreateTranslation(BrowserView):

    def _setCanonicalLanguage(self, obj):
        """Make sure an object has a language set (ie is not neutral).
        """
        lang=obj.Language()
        if not lang:
            portal_state=getMultiAdapter((self.context, self.request),
                                    name="plone_portal_state")
            lang=portal_state.language()
            obj.setLanguage(lang)

    def _xlateFields(self, obj):
        """Translate Title, Description, and Categories"""
        portal_url = obj.portal_url()
	newlang=self.request["newlanguage"]

        if newlang == 'ar':
	    url = '%s/enarsoap.wsdl' % portal_url
	else:
	    url = '%s/arensoap.wsdl' % portal_url

	
        _server = WSDL.Proxy(url)
        
        xtitle = _server.ltTranslateClump(unicode(obj.Title(),'utf-8'))
        xdescription = _server.ltTranslateClump(unicode(obj.Description(),'utf-8'))

        xsubjects = ()
        for subject in obj.Subject():
            xlated = _server.ltTranslateClump(unicode(subject,'utf-8'))
            xsubjects += (xlated,)
        
        return xtitle, xdescription, xsubjects

    def _xlateBody(self, obj):
        """ Get machine translation for body """
        text = obj.getText()
        soup = BeautifulSoup(text)
        self._xlateTags(soup.findAll(True))
        text = str(soup)
        return text

    def _xlateTags(self, tags):
        portal_url = self.context.portal_url()
        newlang=self.request["newlanguage"]
        if newlang == 'ar':
	    url = '%s/enarsoap.wsdl' % portal_url
	else:
	    url = '%s/arensoap.wsdl' % portal_url
        _server = WSDL.Proxy(url)

        for tag in tags:
            if tag.__class__ == NavigableString:
                if tag != '&nbsp;':
                    try:
                        xlated = _server.ltTranslateClump(unicode(str(tag),'utf-8'))
                        tag = tag.replaceWith(xlated)
                    except AttributeError:
                        pass
                else:
                    pass
            else:
                self._xlateTags(tag)

    def nextUrl(self, trans):
        """Figure out where users should go after creating the translation.
        """
        try:
            action=trans.getTypeInfo().getActionInfo("object/translate",
                    object=trans)
            return action["url"]
        except ValueError:
            pass

        try:
            action=trans.getTypeInfo().getActionInfo("object/edit",
                    object=trans)
            return action["url"]
        except ValueError:
            pass

        state=getMultiAdapter((trans, self.request), name="plone_context_state")
        return state.view_url()

    def __call__(self):
        status=IStatusMessage(self.request)
        self._setCanonicalLanguage(self.context)

        newlang=self.request["newlanguage"]
	curlang=self.context.Language()
        #generate a flag to utilize machine translation in addTranslation
        checked = 0
        if self.request.has_key('checked'):
            checked = int(self.request['checked'])

        machine_xlate = 0
        if self.request.has_key('machine_xlate'):
            machine_xlate = int(self.request['machine_xlate'])

        if self.context.hasTranslation(newlang):
            state=getMultiAdapter((self.context, self.request),
                                    name="plone_context_state")
            status.addStatusMessage(_(u"message_translation_exists",
                                        default=u"Translation already exists"),
                                    type="error")
            return self.request.response.redirect(state.view_url())

        lt=getToolByName(self.context, "portal_languages")
        lt.setLanguageCookie(newlang)


        #Send to intermediate page if translation is to Arabic
        if newlang == 'ar' and curlang == 'en' and checked == 0:
            url = self.context.absolute_url()
            xlate = '%s/machine_translate?newlanguage=%s' % (url, newlang)
            return self.request.response.redirect(xlate)
        elif newlang == 'en' and curlang == 'ar' and checked == 0:
            url = self.context.absolute_url()
            xlate = '%s/machine_translate?newlanguage=%s' % (url, newlang)
            return self.request.response.redirect(xlate)

        #Customization for eduCommons to ensure parent Division --> Course --> SubObject's parent folder translated first
        if self.context.aq_inner.aq_parent.Type() == 'Plone Site':            
            #Machine Translate Title, Description, Categories, Body
            if machine_xlate == 1:
                title, description, subjects = self._xlateFields(self.context)
                if 'text' in self.context.Schema().keys():
                    text = self._xlateBody(self.context)
                self.context.addTranslation(newlang, title=title, description=description, text=text, subject=subjects)
            else:
                self.context.addTranslation(newlang)                                    

            trans=self.context.getTranslation(newlang)
            status.addStatusMessage(_(u"message_translation_created",
                                      default=u"Translated created."),
                                    type="info")

            return self.request.response.redirect(self.nextUrl(trans))
        else:
            if self.context.aq_inner.aq_parent.aq_explicit.hasTranslation(newlang):
                #Machine Translate Title, Description, Categories, Body
                if machine_xlate == 1:
                    title, description, subjects = self._xlateFields(self.context)
                    if 'text' in self.context.Schema().keys():
                        text = self._xlateBody(self.context)
                    self.context.addTranslation(newlang, title=title, description=description, text=text, subject=subjects)
                else:
                    self.context.addTranslation(newlang)                                    
                trans=self.context.getTranslation(newlang)
                status.addStatusMessage(_(u"message_translation_created",
                                          default=u"Translated created."),
                                        type="info")
                
                return self.request.response.redirect(self.nextUrl(trans))
            else:
                url = self.context.absolute_url()
                not_available = '%s/not_available_lang/view?set_language=%s&parentNotTranslated=True' % (url, newlang)
                return self.request.response.redirect(not_available)


