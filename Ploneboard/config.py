"""
$Id: config.py 60683 2008-03-14 12:21:49Z wichert $
"""
PROJECTNAME = "Ploneboard"
SKINS_DIR = 'skins'
I18N_DOMAIN = PROJECTNAME.lower()

# Transform config
EMOTICON_TRANSFORM_ID = 'text_to_emoticons'
EMOTICON_TRANSFORM_MODULE = 'Products.Ploneboard.transforms.text_to_emoticons'
URL_TRANSFORM_MODULE = 'Products.Ploneboard.transforms.url_to_hyperlink'
SAFE_HTML_TRANSFORM_MODULE = 'Products.PortalTransforms.transforms.safe_html'

PLONEBOARD_TRANSFORMSCHAIN_ID = 'ploneboard_chain'
PLONEBOARD_TOOL = 'portal_ploneboard'

REPLY_RELATIONSHIP = 'ploneboard_reply_to'
# This should be configurable ttw
NUMBER_OF_ATTACHMENTS = 5

GLOBALS = globals()

try:
    from Products import SimpleAttachment as SA
    HAS_SIMPLEATTACHMENT = True
    del SA
except ImportError:
    HAS_SIMPLEATTACHMENT = False

