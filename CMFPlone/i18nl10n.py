"""
Collection of i18n and l10n utility methods.
"""
import re
import logging

from zope.i18n import translate
from zope.publisher.interfaces.browser import IBrowserRequest

from Acquisition import aq_acquire
from DateTime import DateTime
from DateTime.interfaces import IDateTime

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import log
from Products.CMFPlone.utils import safe_unicode

# get the registered translation service
from Products.PageTemplates.GlobalTranslationService import \
     getGlobalTranslationService

from Products.PlacelessTranslationService.utility import PTSTranslationDomain

# Create a PTS surrogate domain
plonedomain = PTSTranslationDomain('plone')
atctdomain = PTSTranslationDomain('atcontenttypes')
pltdomain = PTSTranslationDomain('plonelanguagetool')
prtdomain = PTSTranslationDomain('passwordresettool')
cmfpwdomain = PTSTranslationDomain('cmfplacefulworkflow')
cmfedomain = PTSTranslationDomain('cmfeditions')

# these are taken from PTS, used for format interpolation
NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_interp_regex = re.compile(r'(?<!\$)(\$(?:%(n)s|{%(n)s}))' %({'n': NAME_RE}))

datetime_formatvariables = ('H', 'I', 'm', 'd', 'M', 'p', 'S', 'Y', 'y', 'Z')
name_formatvariables = ('a', 'A', 'b', 'B')

# unicode aware translate method (i18n)
def utranslate(*args, **kw):
    # safety precaution for cases where we get passed in an encoded string
    return safe_unicode(getGlobalTranslationService().translate(*args, **kw))

# unicode aware localized time method (l10n)
def ulocalized_time(time, long_format=None, context=None,
                    domain='plonelocales', request=None):
    # get msgid
    msgid = long_format and 'date_format_long' or 'date_format_short'

    # NOTE: this requires the presence of two msgids inside the translation catalog
    #       date_format_long and date_format_short
    #       These msgids are translated using interpolation.
    #       The variables used here are the same as used in the strftime formating.
    #       Supported are %A, %a, %B, %b, %H, %I, %m, %d, %M, %p, %S, %Y, %y, %Z, each used as
    #       variable in the msgstr without the %.
    #       For example: "${A} ${d}. ${B} ${Y}, ${H}:${M} ${Z}"
    #       Each language dependend part is translated itself as well.

    # From http://docs.python.org/lib/module-time.html
    #
    # %a    Locale's abbreviated weekday name.  	
    # %A 	Locale's full weekday name. 	
    # %b 	Locale's abbreviated month name. 	
    # %B 	Locale's full month name. 	
    # %d 	Day of the month as a decimal number [01,31]. 	
    # %H 	Hour (24-hour clock) as a decimal number [00,23]. 	
    # %I 	Hour (12-hour clock) as a decimal number [01,12]. 	
    # %m 	Month as a decimal number [01,12]. 	
    # %M 	Minute as a decimal number [00,59]. 	
    # %p 	Locale's equivalent of either AM or PM. 	
    # %S 	Second as a decimal number [00,61]. 	
    # %y 	Year without century as a decimal number [00,99]. 	
    # %Y 	Year with century as a decimal number. 	
    # %Z 	Time zone name (no characters if no time zone exists). 	

    mapping = {}
    # convert to DateTime instances. Either a date string or 
    # a DateTime instance needs to be passed.
    if not IDateTime.providedBy(time):
        try:
            time = DateTime(time)
        except:
            log('Failed to convert %s to a DateTime object' % time,
                severity=logging.DEBUG)
            return None

    if context is None:
        # when without context, we cannot do very much.
        return time.ISO()

    if request is None:
        request = aq_acquire(context, 'REQUEST')

    # get the formatstring
    formatstring = translate(msgid, domain, mapping, request)

    if formatstring is None or formatstring.startswith('date_'):
        # msg catalog was not able to translate this msgids
        # use default setting

        properties=getToolByName(context, 'portal_properties').site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            format=properties.localTimeFormat

        return time.strftime(format)
    
    # get the format elements used in the formatstring
    formatelements = _interp_regex.findall(formatstring)
    # reformat the ${foo} to foo
    formatelements = [el[2:-1] for el in formatelements]

    # add used elements to mapping
    elements = [e for e in formatelements if e in datetime_formatvariables]

    # add weekday name, abbr. weekday name, month name, abbr month name
    week_included = True
    month_included = True

    name_elements = [e for e in formatelements if e in name_formatvariables]
    if not ('a' in name_elements or 'A' in name_elements):
        week_included = False
    if not ('b' in name_elements or 'B' in name_elements):
        month_included = False

    for key in elements:
        mapping[key]=time.strftime('%'+key)

    if week_included:
        weekday = int(time.strftime('%w')) # weekday, sunday = 0
        if 'a' in name_elements:
            mapping['a']=weekdayname_msgid_abbr(weekday)
        if 'A' in name_elements:
            mapping['A']=weekdayname_msgid(weekday)
    if month_included:
        monthday = int(time.strftime('%m')) # month, january = 1
        if 'b' in name_elements:
            mapping['b']=monthname_msgid_abbr(monthday)
        if 'B' in name_elements:
            mapping['B']=monthname_msgid(monthday)

    # translate translateable elements
    for key in name_elements:
        mapping[key] = translate(mapping[key], domain, context=request, default=mapping[key])

    # translate the time string
    return translate(msgid, domain, mapping, request)

def _numbertoenglishname(number, format=None, attr='_days'):
    # returns the english name of day or month number
    # starting with Sunday == 0
    # and January = 1
    # format is either None, 'a' or 'p')
    #   None  means full name (January, February, ...)
    #   'a' means abbreviated (Jan, Feb, ..)
    #   'p' means abbreviated with . (dot) at end (Jan., Feb., ...)
    
    number = int(number)
    if format is not None:
        attr = '%s_%s' % (attr, format)
    
    # get list from DateTime attribute
    thelist = getattr(DateTime, attr)

    return thelist[number]
    
def monthname_english(number, format=None):
    # returns the english name of month with number
    return _numbertoenglishname(number, format=format, attr='_months')

def weekdayname_english(number, format=None):
    # returns the english name of week with number
    return _numbertoenglishname(number, format=format, attr='_days')

def monthname_msgid(number):
    # returns the msgid for monthname
    # use to translate to full monthname (January, February, ...)
    # eg. month_jan, month_feb, ...
    return "month_%s" % monthname_english(number, format='a').lower()
    
def monthname_msgid_abbr(number):
    # returns the msgid for the abbreviated monthname
    # use to translate to abbreviated format (Jan, Feb, ...)
    # eg. month_jan_abbr, month_feb_abbr, ...
    return "month_%s_abbr" % monthname_english(number, format='a').lower()
    
def weekdayname_msgid(number):
    # returns the msgid for the weekdayname
    # use to translate to full weekdayname (Monday, Tuesday, ...)
    # eg. weekday_mon, weekday_tue, ...
    return "weekday_%s" % weekdayname_english(number, format='a').lower()
    
def weekdayname_msgid_abbr(number):
    # returns the msgid for abbreviated weekdayname
    # use to translate to abbreviated format (Mon, Tue, ...)
    # eg. weekday_mon_abbr, weekday_tue_abbr, ...
    return "weekday_%s_abbr" % weekdayname_english(number, format='a').lower()
    
def weekdayname_msgid_short(number):
    # return the msgid for short weekdayname
    # use to translate to 2 char format (Mo, Tu, ...)
    # eg. weekday_mon_short, weekday_tue_short, ...
    return "weekday_%s_short" % weekdayname_english(number, format='a').lower()
