##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Test browserSupportsKupu

$Id: test_browserSupportsKupu.py 49312 2007-12-03 11:47:59Z duncan $
"""

import os, sys
import time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=['ATContentTypes', 'kupu'])

class TestBrowserSupportsKupu(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        md = self.portal.portal_memberdata
        md._updateProperty('wysiwyg_editor', 'Kupu')
        #self.script = self.portal.portal_skins.kupu_plone.browserSupportsKupu
        self.script = self.portal.kupu_library_tool.isKupuEnabled

# List of tuples of id, signature, os, version, browser
# browsers are:
# 1, MOZILLA            -- supported 1.4 and above
# 2, INTERNET_EXPORER   -- supported 5.5 and above
# 3, OPERA              -- not supported
# 4, KONQUEROR          -- not supported
# 5, NETSCAPE           -- not supported
# 6, OTHER              -- not supported
# 7, GOOGLE             -- not supported
# 8, YAHOO              -- not supported
# 9, GALEON             -- not supported

(MOZILLA, INTERNET_EXPLORER, OPERA, KONQUEROR, NETSCAPE, OTHER,
 GOOGLE, YAHOO, GALEON, SAFARI) = range(1,11)

BROWSERNAMES = ['NOTUSED', 'Mozilla', 'Internet Explorer', 'Opera',
                'Konqueror', 'Netscape', 'Other', 'Google',
                'Yahoo', 'Galeon', 'Safari' ]

SUPPORTED = {
    MOZILLA: (1,3,1),
    INTERNET_EXPLORER: (5,5),
    OPERA: (9,0),
    SAFARI: (525,1), #(420,0), # Safari not yet supported
}

# BROWSERS records contain:
#   signature, os, version, browser
BROWSERS = (
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; NetCaptor 7.2.0)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; {F69FABBA-7A20-4724-93CB-A717BBB0AB5A}; MyIE2; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Crazy Browser 1.0.5)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; .NET CLR 1.0.3705)', 'Windows 2000', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows 98)', 'Windows 95', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)', 'Windows 2000', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {514CEB04-E26C-4724-B559-3BBF7D079CF9}; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Googlebot/2.1 (+http://www.googlebot.com/bot.html)', '', '2.1', GOOGLE),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows XP', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Java1.4.0', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0)', 'Windows NT', '5.5', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)', 'Windows 2000', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FunWebProducts)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20040113', 'GNU/Linux', '1.6', MOZILLA),
    ('Opera/7.23 (Windows NT 5.1; U)  [en]', 'Windows XP', '7.23 (Windows NT 5.1; U)', OPERA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6) Gecko/20040113', 'Windows XP', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98) Opera 7.20  [en]', 'Windows 95', '7.20', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; YComp 5.0.0.0; Avalon Ltd.)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/85.7 (KHTML, like Gecko) Safari/85.7', 'Mac PPC', '5.0 (Macintosh; U; PPC Mac OS X; en', SAFARI),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Hotbar 4.4.2.0; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0) Active Cache Request', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 98; DigExt)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; {BEBB62E1-3900-4425-91F4-BC0C940212A1}; FunWebProducts; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)', '', '', YAHOO),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; grub-client-1.0.5; Crawl your own stuff with http://grub.org)', 'uknown OS', '4.0', NETSCAPE),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows NT)', 'Windows NT', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; grub-client-1.5.3; Crawl your own stuff with http://grub.org)', 'uknown OS', '4.0', NETSCAPE),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; YComp 5.0.0.0; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03; FunWebProducts-MyWay)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MyIE2; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 4.0; iOpus-I-M)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; DigExt)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.20  [en]', 'Windows XP', '7.20', OPERA),
    ('MSProxy/2.0', None, None, OTHER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.6) Gecko/20040113', 'Windows 2000', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Q312461)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FunWebProducts-MyWay)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.21  [en]', 'Windows XP', '7.21', OPERA),
    ('Mozilla/3.01 (compatible;)', None, None, OTHER),
    ('Lynx/2.8.4dev.16 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.6', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; TUCOWS; MyIE2)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/124 (KHTML, like Gecko) Safari/125.1', 'Mac PPC', '5.0 (Macintosh; U; PPC Mac OS X; en', SAFARI),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; H010818; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5) Gecko/20031007 Firebird/0.7', 'Windows 2000', '1.5', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Hotbar 4.4.0.0)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; {1D013B5D-D0E7-4EAB-9FCF-AE4016583348})', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7b;) Gecko/20020604 OLYMPIAKOS SFP', 'GNU/Linux', '1.7', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; YComp 5.0.2.6)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 98)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Avant Browser (http://www.avantbrowser.com)', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {624D10FA-5EBC-4100-9316-C6769E251849}; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT)', 'Windows NT', '5.01', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)', 'Windows XP', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; FunWebProducts-MyWay)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.4) Gecko/20030624 Netscape/7.1', 'GNU/Linux', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Q312461; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0) Opera 7.22  [en]', 'Windows 2000', '7.22', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; T312461)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; EurobankSec)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows NT; DigExt)', 'Windows NT', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; NetCaptor 7.5.0 Gold; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 4.0)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Alexa Toolbar)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7b) Gecko/20040316', 'Windows XP', '1.7', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; i-NavFourF)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Scooter/3.3_SF', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {A2D2036B-F33C-4612-AB02-CDACAAA0DC39})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; NetCaptor 7.5.0 Gold)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; ONEWAY NET; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; .NET CLR 1.1.4322)', 'Windows 2000', '5.01', INTERNET_EXPLORER),
    ('Opera/7.21 (Windows NT 5.1; U)  [en]', 'Windows XP', '7.21 (Windows NT 5.1; U)', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MyIE2)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4) Gecko/20030624', 'Windows 2000', '1.4', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7a) Gecko/20040219', 'Windows XP', '1.7', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0) Opera 7.21  [en]', 'Windows 2000', '7.21', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W98 WNT VER03)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Win 9x 4.90; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows ME', '1.6', MOZILLA),
    ('Opera/7.23 (Windows NT 5.0; U)  [en]', 'Windows 2000', '7.23 (Windows NT 5.0; U)', OPERA),
    ('Opera/7.23 (X11; FreeBSD i386; U)  [en]', 'uknown OS', '7.23 (X11; FreeBSD i386; U)', OPERA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5) Gecko/20031007', 'Windows XP', '1.5', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5) Gecko/20031007 Firebird/0.7', 'Windows XP', '1.5', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows 2000', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.16; Mac_PowerPC)', 'Mac PPC', '5.16', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Mac_PowerPC) Opera 7.50  [en]', 'uknown OS', '7.50', OPERA),
    ('Mediapartners-Google/2.1 (+http://www.googlebot.com/bot.html)', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 98; MyIE2)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; .NET CLR 1.1.4322)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20040207 Firefox/0.8', 'GNU/Linux', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; AUTOSIGN W98 WNT VER03)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03; Q312461)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Mac_PowerPC)', 'Mac PPC', '5.0', INTERNET_EXPLORER),
    ('Opera/7.20 (Windows NT 5.1; U)  [en]', 'Windows XP', '7.20 (Windows NT 5.1; U)', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Avant Browser [avantbrowser.com])', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; (R1 1.3); .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90; YComp 5.0.0.0)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Opera/7.23 (Windows 98; U)  [en]', 'Windows 95', '7.23 (Windows 98; U)', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows 98; Feat Ext 18)', 'Windows 95', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q342532)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 Galeon/1.2.12 (X11; Linux i686; U;) Gecko/20031004', 'GNU/Linux', '5.0 Galeon/1.2.12 (X11; Linux i686; U;', GALEON),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) via Avirt Gateway Server v4.2', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:0.9.4) Gecko/20011206 Netscape6/6.2.1', 'Sun OS', '0.9.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.23  [en]', 'Windows XP', '7.23', OPERA),
    ('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.0.2) Gecko/20030208 Netscape/7.02', 'Windows 95', '1.0.2', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; BCD2000)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.0.3705; .NET CLR 1.1.4322; Alexa Toolbar)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.10  [en]', 'Windows XP', '7.10', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FunWebProducts; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Win 9x 4.90; en-US; rv:1.4) Gecko/20030624', 'Windows ME', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.11  [en]', 'Windows XP', '7.11', OPERA),
    ('Mozilla/4.0 (compatible; grub-client-1.4.3; Crawl your own stuff with http://grub.org)', 'uknown OS', '4.0', NETSCAPE),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; el-GR; rv:1.5) Gecko/20031007', 'Windows XP', '1.5', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0) Opera 7.23  [en]', 'Windows 2000', '7.23', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 5.13; Mac_PowerPC)', 'Mac PPC', '5.13', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 4.0; .NET CLR 1.0.3705)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible;)', 'uknown OS', '4.0', NETSCAPE),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Hotbar 4.4.2.0)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Hotbar 4.1.7.0)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; TUCOWS; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; ESB{9404F370-72A9-465A-94D5-C275AE965397})', 'Windows 2000', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; MyIE2; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5) Gecko/20031007', 'Windows 2000', '1.5', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90; .NET CLR 1.1.4322)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.01  [en]', 'Windows XP', '7.01', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 4.01; Windows 98)', 'Windows 95', '4.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; ESB{F65AACA0-5C7B-11D8-B676-00C02628848A})', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; IE@netCD)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0; Compulink Network)', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Alexa Toolbar)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 4.0; T312461; .NET CLR 1.0.3705)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT; Aztec)', 'Windows NT', '5.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; CivilTech)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; de-DE; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows 2000', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; iOpus-I-M)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; TUCOWS)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Hewlett-Packard; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; TUCOWS; FunWebProducts; .NET CLR 1.1.4322)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MyIE2; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FunWebProducts; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; MyIE2)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; ONEWAY NET)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {FF087BE5-1083-4DE5-8F21-637B924CB76E})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; AUTOSIGN W2000 WNT VER03)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4) Gecko/20030529', 'Windows 2000', '1.4', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4a) Gecko/20030401', 'Windows 2000', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; T312461; (R1 1.3))', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; brip1)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; SEARCHALOT)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Feat Ext 18)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.5) Gecko/20031007', 'Windows 95', '1.5', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.7b) Gecko/20040316', 'Windows 2000', '1.7', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; FunWebProducts)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Alexa Toolbar; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Hotbar 4.3.1.0; FunWebProducts)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; el-gr; rv:1.4) Gecko/20030630', 'GNU/Linux', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; brip1)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('SurveyBot/2.3 (Whois Source)', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98) Opera 7.23  [en]', 'Windows 95', '7.23', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; IE 6.05; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.15; Mac_PowerPC)', 'Mac PPC', '5.15', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.0.1) Gecko/20020823 Netscape/7.0', 'Windows XP', '1.0.1', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.0.2) Gecko/20021120 Netscape/7.01', 'Windows XP', '1.0.2', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0; Hotbar 4.4.0.0)', 'Windows NT', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 98; DigExt; FunWebProducts)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {95A9C2FB-E969-47DB-A5F8-4F7D70528FF7})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; T312461; Q312461)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; DigExt; AUTOSIGN W2000 WNT VER03)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; DigExt)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.4b) Gecko/20030516 Mozilla Firebird/0.6', 'Windows XP', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; DigExt; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AIRF)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:0.9.9) Gecko/20020408', 'GNU/Linux', '0.9.9', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; Feat Ext 18)', 'Windows 2000', '5.01', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6) Gecko/20040113 MultiZilla/1.6.3.0d', 'Windows XP', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Crazy Browser 1.0.5; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 98; DigExt; Hotbar 4.3.5.0; FunWebProducts)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; ACN; MyIE2; .NET CLR 1.1.4322)', 'Windows NT', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (compatible; Konqueror/3.2; Linux) (KHTML, like Gecko)', ' Linux', '3.2', KONQUEROR),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows ME) Opera 7.50  [en]', 'uknown OS', '7.50', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; ESB{C9D3416E-AF99-432D-BB0F-629589DD2A96})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Opera/7.11 (Windows NT 5.1; U)  [en]', 'Windows XP', '7.11 (Windows NT 5.1; U)', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; (R1 1.5); .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows NT', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Feat Ext 13)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('CURIValidate', None, None, OTHER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.3) Gecko/20030312', 'Windows XP', '1.3', MOZILLA),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20040309', 'GNU/Linux', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; winweb; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.01; Windows 98; Feat Ext 15)', 'Windows 95', '5.01', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/124 (KHTML, like Gecko) Safari/125', 'Mac PPC', '5.0 (Macintosh; U; PPC Mac OS X; en', SAFARI),
    ('Mozilla/4.0 compatible ZyBorg/1.0 (wn.zyborg@looksmart.net; http://www.WISEnutbot.com)', 'uknown OS', '4.0 compatible ZyBorg/1.0', 5),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; YComp 5.0.2.6)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Opera/7.20 (Windows NT 5.0; U)  [en]', 'Windows 2000', '7.20 (Windows NT 5.0; U)', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Alexa Toolbar)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.23  [el]', 'Windows XP', '7.23', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90; Smart Explorer 6.1)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; Netcraft Web Server Survey)', 'uknown OS', '4.0', 5),
    ('Mozilla/5.0 (compatible; Konqueror/3.1-rc4; i686 Linux; 20020516)', ' i686 Linux; 20020516', '3.1', KONQUEROR),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; UKC VERSION)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows XP) Opera 7.0  [en]', 'uknown OS', '7.0', OPERA),
    ('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows 95', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; SEARCHALOT 11022003)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90; FunWebProducts; iOpus-I-M; .NET CLR 1.0.3705)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.2914)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 1.0.2914)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT))', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Googlebot-Image/1.0 (+http://www.googlebot.com/bot.html)', '', '1.0', GOOGLE),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.2.1) Gecko/20021130', 'Windows XP', '1.2.1', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7b) Gecko/20040314', 'Windows XP', '1.7', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.5) Gecko/20031007 Firebird/0.7', 'Windows 95', '1.5', MOZILLA),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.4) Gecko/20030624', 'Windows XP', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; iOpus-I-M; CLINK)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7b) Gecko/20040316', 'GNU/Linux', '1.7', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90; Alexa Toolbar)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.0.1) Gecko/20020823 Netscape/7.0', 'Windows NT', '1.0.1', MOZILLA),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.5) Gecko/20031007 Firebird/0.7', 'GNU/Linux', '1.5', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0; .NET CLR 1.0.3705)', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; WinNT; en; rv:1.0.2) Gecko/20030311 Beonex/0.8.2-stable', 'Windows NT', '1.0.2', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; {5D5A1B12-0F6C-4483-A2FF-B03498A4570F})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90; Q312461; AT&T CSM6.0; sbcydsl 3.12; YComp 5.0.0.0; .NET CLR 1.0.3705)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AUTOSIGN W2000 WNT VER03; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MyIE2; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows XP) Opera 6.05  [el]', 'uknown OS', '6.05', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; ESB{C46FA41C-A455-4506-A8C0-4B25AFA4C704}; FunWebProducts)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; DVD Owner; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461; MyIE2)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (compatible; Konqueror/3.1; Linux)', ' Linux', '3.1', KONQUEROR),
    ('Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)', 'Windows 95', '1.4', MOZILLA),
    ('Baiduspider+(+http://www.baidu.com/search/spider.htm)', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows 95; DigExt)', 'Windows 95', '5.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.2.1) Gecko/20030225', 'GNU/Linux', '1.2.1', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; X11; Linux i686) Opera 7.23  [en]', 'GNU/Linux', '7.23', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; TUCOWS)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5a) Gecko/20030728 Mozilla Firebird/0.6.1', 'Windows XP', '1.5', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; LRF; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90; (R1 1.3); .NET CLR 1.1.4322)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.0.3705; Alexa Toolbar; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0b; Windows NT 5.0; NetCaptor 7.5.0 Gold; .NET CLR 1.1.4322)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Tucows; YComp 5.0.0.0)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461; .NET CLR 1.0.3705; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.0; el-GR; rv:1.6) Gecko/20040113', 'Windows 2000', '1.6', MOZILLA),
    ('UptimeBot(www.uptimebot.com)', None, None, OTHER),
    ('Xenu Link Sleuth 1.2e', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; ESB{1BAAA30F-BDC9-4E83-AF38-660B1E484271})', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; PPC; 240x320)', 'Mac PPC', '4.01', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0; T312461)', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.50  [en]', 'Windows XP', '7.50', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; H010818; UB1.4_IE6.0_SP1; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SALT 1.0.4223.1 0111 Developer; .NET CLR 1.1.4322; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.0.2) Gecko/20030716', 'GNU/Linux', '1.0.2', MOZILLA),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.4b) Gecko/20030507', 'GNU/Linux', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; FunWebProducts)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; YComp 5.0.0.0)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; winweb)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows 98) Opera 7.02  [en]', 'Windows 95', '7.02', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; NetCaptor 7.2.0; .NET CLR 1.0.3705)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Installed by Symantec Package)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.6) Gecko/20040206 Firefox/0.8', 'Windows NT', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; NetCaptor 7.2.2)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MS FrontPage 6.0)', 'uknown OS', '4.0', 5),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; StumbleUpon.com 1.760)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.22  [en]', 'Windows XP', '7.22', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 5.0; Windows XP) Opera 6.05  [en]', 'uknown OS', '6.05', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.0  [en]', 'Windows XP', '7.0', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows ME) Opera 7.23  [en]', 'uknown OS', '7.23', OPERA),
    ('Java1.3.0', None, None, OTHER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.2; fr-FR; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)', 'Windows NT', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Argentina.com v12b8.1; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; AT&T CSM6.0)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; FunWebProducts; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322; MSN 9.0; MSNbVZ02; MSNmen-us; MSNcOTH)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Win 9x 4.90; en-US; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)', 'Windows ME', '1.4', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FunWebProducts-MyWay; .NET CLR 1.1.4322)', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Creative)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Avant Browser [avantbrowser.com])', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; AskBar 3.00; Hotbar 4.4.2.0)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0) Opera 7.11  [en]', 'Windows 2000', '7.11', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U) Opera 7.23  [en]', 'Windows XP', '7.23', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; Mozilla/4.0 (Compatible; MSIE 6.0; Windows 2000; MCK); Mozilla/4.0 (Compatible; MSIE 6.0; Win; MCK))', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.4.1) Gecko/20031114', 'GNU/Linux', '1.4.1', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0; H010818; UB1800; .NET CLR 1.0.3705)', 'Windows 2000', '5.5', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; (R1 1.3))', 'Windows XP', '6.0', INTERNET_EXPLORER),
    ('Mozilla/6.20  (BEOS; U ;Nav)', None, None, OTHER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; TUCOWS.COM)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; .NET CLR 1.0.3705)', 'Windows 95', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; T312461; YComp 5.0.0.0; .NET CLR 1.0.3705)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 5.5; Windows 95; FunWebProducts)', 'Windows 95', '5.5', INTERNET_EXPLORER),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20040122 Debian/1.6-1', 'GNU/Linux', '1.6', MOZILLA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; www.ASPSimply.com)', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; ESB{59E9535D-AE57-4D68-A91A-F568540A69C8})', 'Windows 2000', '6.0', INTERNET_EXPLORER),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.0.2) Gecko/20030208 Netscape/7.02', 'Windows XP', '1.0.2', MOZILLA),
    ('Opera/9.02 (X11; Linux i686; U; en)', 'Linux', '9.02', OPERA),
    ('Opera/9.02 (Windows 98; U; en)', 'Windows 98', '9.02', OPERA),
    ('Opera/9.02 (Macintosh; PPC Mac OS X; U; en)', 'PPC Mac', '9.02', OPERA),
    ('Opera/9.01 (X11; Linux i686; U; en)', 'Linux', '9.01', OPERA),
    ('Opera/9.01 (Macintosh; Intel Mac OS X; U; fr)', 'Intel Max', '9.01', OPERA),
    ('Opera/9.00 (Macintosh; PPC Mac OS X; U; en)', 'PPC Mac', '9.00', OPERA),
    ('Opera/9.00 (Windows NT 5.0; U; en)', 'Windows 2000', '9.00', OPERA),
    ('Opera/9.00 (Macintosh; PPC Mac OS X; U; en)', 'PPC Mac', '9.00', OPERA),
    ('Mozilla/5.0 (X11; Linux i686; U; en) Opera 9.00', 'Linux', '9.00', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U; en) Opera 9.01', 'Windows XP', '9.01', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U; en) Opera 9.00', 'Windows XP', '9.00', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.10', 'Windows XP', '9.10', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0.7) Gecko/20060728 Firefox/1.5.0.7 Opera 9.10', 'Windows XP', '9.10', OPERA),
    ('Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1b1) Gecko/20060728 Firefox/2.0 Opera 9.20', 'Windows XP', '9.20', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; en) Opera 9.01', 'Windows XP', '9.01', OPERA),
    ('Mozilla/4.0 (compatible; MSIE 6.0; X11; Linux i686; en) Opera 9.00', 'Linux', '9.00', OPERA),
    ('Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Safari/419.3', 'Mac', '420.0', SAFARI),
    ('Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/418.9.1 (KHTML, like Gecko) Safari/419.3', 'Mac', '418.9.1', SAFARI),
    ("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/523.12.9 (KHTML, like Gecko) Version/3.0 Safari/523.12.9", 'Windows', '523.12.9', SAFARI),
    ("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.1+ (KHTML, like Gecko) Version/3.0 Safari/523.12.9", 'Mac', '525.1', SAFARI),
)

def createTest(sig, isSupported, index, os, browser, version):
    def test(self):
        actual = self.script(sig)
        if isSupported:
            expect = "expected supported but it isn't"
        else:
            expect = "found supported when not expecting it"
        self.assertEquals(isSupported, actual, expect)
    testname = 'test_%d %s %s %s' % (index, os, BROWSERNAMES[browser],
                                     '.'.join([str(v) for v in version]))
    setattr(TestBrowserSupportsKupu, testname.strip(), test)

def createTests():
    for id, (sig, os, version, browser) in enumerate(BROWSERS):
        if version:
            version = version.split()[0]
            version = tuple([int(v) for v in version.split('.')])
        else:
            version = ()
        minver = SUPPORTED.get(browser, None)
        supported = minver != None and version >= minver

        # Specifically exclude support for some browsers
        #XXX Hack
        #if 'Safari' in sig:
        #    supported = False

        createTest(sig, supported, id, os, browser, version)

createTests()

from unittest import TestSuite, makeSuite
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserSupportsKupu))
    return suite

if __name__ == '__main__':
    framework()
