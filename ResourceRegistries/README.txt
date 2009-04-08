ResourceRegistries

  A registry for linked Stylesheet files and Javascripts.

  This registry is mainly aimed at solving the following usecases:

  - Enable product authors to register stylesheets with their product
    installers without having to resort to override either header.pt or
    ploneCustom.css creating potential conflicts with other products.

  - Enable more componentialization of the stylesheets provided with Plone
    (and other products) without having to increase the number of http
    requests for a Plone page.

  - Enable condition checking on stylesheets. Great for variable
    look-and-feel for groups/roles/folders/departments/content-types/etc

  - Enable inline dynamic stylesheets. For those style rules that should
    vary for each request. Mainly used for things like header-bar-
    backgroundimages, department colors etc.

  - Enable developers to activate/deactivate their styles in a simpler way

  - Enable compression to safe bandwidth and download time

Usage

  ResourceRegistries 1.3 requires CMF 1.6 or later.  (Intrepid users can
  probably get it working w/ CMF 1.5.5 w/ GenericSetup installed.)

  The CSSRegistry and JSRegistry is configured through the ZMI. it can be found
  in the ZMI of your plonesite as 'portal_css' and 'portal_javascript'.

  Add links to stylesheets that exist in your skins paths, by ids;  like
  'plone.css', 'ploneCustom.css' etc.

  Linked stylesheets take some parameters:

  id -- The id mentioned above. the Zope id of the stylesheet to be used.

  expression -- A CMF expression to be evaluated to check if the stylesheet
  should be included in output or not.

  media -- The media for which the stylesheet should apply, normally empty or
  'all'. other possible values are 'screen', 'print' etc.

  rel -- Link relation. defaults to 'stylesheet', and should almost always
  stay that way. For designating alternative stylesheets.

  title -- the title for alternate stylesheets

  rendering -- How to link the stylesheet from the html page:

      - 'import' - the default. normal css import

      - 'link' - works better for old browsers and is needed for alternate
                 stylesheets

      - 'inline' - render the stylesheet inline instead of linking it
                   externally.
                   Shouldn't be used at all!
                   It isn't possible to create sites which validate if you do.
                   For more information see:
                   http://developer.mozilla.org/en/docs/Properly_Using_CSS_and_JavaScript_in_XHTML_Documents

  compression -- Whether and how much the resource should be compressed:

      - 'none' - the original content will not be changed

      - 'safe' - the content will be compressed in a way which should be safe
                 for any workarounds for browser bugs. Conditional code for
                 Internet Explorer is preserved since ResourceRegistries
                 1.2.3 and 1.3.1.

      - 'full' - the content will be compressed with some additional rules.
                 For css all comments and most newlines are removed, this may
                 break special browser hacks, so use with care.
                 For javascript this encodes variables with special prefixes
                 according to the rules described here (Special Characters):
                 http://dean.edwards.name/packer/usage/
                 The source code needs to be written according to those rules,
                 otherwise it's more than likely that it will break.

      - 'safe-encode' - only available for javascript
      - 'full-encode' - only available for javascript
                 Additionally encodes keywords. This heavily compresses the
                 javascript, but it needs to be decoded on the fly in the
                 browser on each load. Depending on the size of the scripts
                 this could lead to timeouts in Firefox.
                 Use with special care!

  If several stylesheets listed directly after each other in the registry have
  the same parameters and expression, they will be concatenated into a larger,
  composite, stylesheet on rendering. - This can be useful for splitting
  stylesheets into smaller components for overrideing, while preserving
  cacheability and minimising the number of http-requests to Plone.

  This tool was started at the excellent SnowSprint 2005 - Organised by
  Telesis in the Austrian Alps. Thanks, Jodok! :)

Credits

    Florian Schulze -- Independent
    
    Laurence Rowe -- Independent

    Geir B�kholt -- "Plone Solutions":http://www.plonesolutions.com

    Matt Hamilton -- "Netsight Internet Solutions":http://www.netsight.co.uk

Plone Solutions AS

  "http://www.plonesolutions.com":http://www.plonesolutions.com

  "info@plonesolutions.com":mailto:info@plonesolutions.com

Netsight Internet Solutions

  "http://www.netsight.co.uk":http://www.netsight.co.uk/

  "info@netsight.co.uk":mailto:info@netsight.co.uk
