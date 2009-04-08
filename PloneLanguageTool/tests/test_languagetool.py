from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()
from Products.PloneLanguageTool import LanguageTool

class TestLanguageToolExists(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id

    def testLanguageToolExists(self):
        self.failUnless(self.id in self.portal.objectIds())


class TestLanguageToolSettings(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testLanguageToolType(self):
        self.failUnless(self.ltool.meta_type == LanguageTool.meta_type)

    def testSetLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                   setCookieN=False, setRequestN=False,
                                   setPathN=False, setForcelanguageUrls=False,
                                   setAllowContentLanguageFallback=True,
                                   setUseCombinedLanguageCodes=True,
                                   startNeutral=False, displayFlags=False)

        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.use_cookie_negotiation==False)
        self.failUnless(self.ltool.use_request_negotiation==False)
        self.failUnless(self.ltool.use_path_negotiation==False)
        self.failUnless(self.ltool.force_language_urls==False)
        self.failUnless(self.ltool.allow_content_language_fallback==True)
        self.failUnless(self.ltool.use_combined_language_codes==True)
        self.failUnless(self.ltool.startNeutral()==False)
        self.failUnless(self.ltool.showFlags()==False)


class TestLanguageTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                              setUseCombinedLanguageCodes=False)
        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

    def testSupportedLanguages(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

        self.ltool.removeSupportedLanguages(supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==[])

        for lang in supportedLanguages:
            self.ltool.addSupportedLanguage(lang)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

    def testDefaultLanguage(self):
        supportedLanguages = ['de','no']

        self.ltool.manage_setLanguageSettings('no', supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.getDefaultLanguage()=='no')

        # default not in supported languages, should set to first supported
        self.ltool.manage_setLanguageSettings('nl', supportedLanguages)

        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.getDefaultLanguage()=='de')

    def testAvailableLanguage(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        availableLanguages = self.ltool.getAvailableLanguageInformation()
        for lang in availableLanguages:
            if lang in supportedLanguages:
                self.failUnless(availableLanguages[lang]['selected'] == True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageToolExists))
    suite.addTest(makeSuite(TestLanguageToolSettings))
    suite.addTest(makeSuite(TestLanguageTool))
    return suite
