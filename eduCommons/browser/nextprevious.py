from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from Products.ATContentTypes.interface.folder import IATFolder


from plone.memoize.instance import memoize

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.eduCommons.utilities.interfaces import IECUtility



class ATFolderNextPrevious(object):
    """Let a folder act as a next/previous provider. This will be 
    automatically found by the @@plone_nextprevious_view and viewlet.
    """


    implements(INextPreviousProvider)
    adapts(IATFolder)

    def __init__(self, context):
        self.context  = context
        
        sp = getToolByName(self.context, 'portal_properties').site_properties
        self.view_action_types = sp.getProperty('typesUseViewActionInListings', ())

        self.ecutil = getUtility(IECUtility)
        self.ecparent = self.ecutil.FindECParent(context)


    def getNextItem(self, obj):
        relatives = self.itemRelatives(obj)
        return relatives["next"]
        
    def getPreviousItem(self, obj):
        relatives = self.itemRelatives(obj)
        return relatives["previous"]

    @property
    def enabled(self):
        return self.context.getNextPreviousEnabled()

    @memoize
    def itemRelatives(self, obj):
        """Get the relative next and previous items
        """
        folder = self.context
        cur_item   = obj
        catalog  = getToolByName(self.context, 'portal_catalog')

        previous = None
        next     = None

        if cur_item.exclude_from_nav() == True:
            return {'next':next, 'previous':previous}

        # Get course objs in nav 
        path = {'path':{'query':'/'.join(self.ecparent.getPhysicalPath())+'/'},
                'getExcludeFromNav':False,
                'sort_on':'getObjPositionInCourse'}
        brains = self.context.portal_catalog.searchResults(path)
        nav_objs = [nobj for nobj in brains if not getattr(nobj.aq_explicit, 'exclude_from_nav', True)]

        #determine item 'position' in nav_objs
        position = 0
        for n_obj in nav_objs:
            if n_obj.id != cur_item.id:
                position += 1
            elif n_obj.id == cur_item.id:
                break

        # Get the previous item
        if (position - 1) >= 0:
            prev_brain = nav_objs[position - 1]
            if prev_brain and len(prev_brain) > 0:
                previous = self.buildNextPreviousItem(prev_brain)


        # Get the next item
        if (position + 1) < len(nav_objs):
            next_brain = nav_objs[position + 1]
            if next_brain and len(next_brain) > 0:
                next   = self.buildNextPreviousItem(next_brain)


        nextPrevious = {
            'next'      : next,
            'previous'  : previous,
            }

        return nextPrevious
        


    def buildNextPreviousItem(self, brain):
        return {'id'          : brain.getId,
                'url'         : self.getViewUrl(brain),
                'title'       : brain.Title,
                'description' : brain.Description,
                'portal_type' : brain.portal_type,
                }

    def getViewUrl(self, brain):
        """create link and support contents that requires /view 
        """
        item_url = brain.getURL()
    
        if brain.portal_type in self.view_action_types:
            item_url += '/view'
    
        return item_url

    def saveAndExit(self):
        """ Save the current url and then move to the social networking site """
        url = self.context.getURL()
        mtool = self.context.portal_membership
        mtool.getAuthenticatedMember().bookmark_url = url
        self.request.response.redirect('http://www.teacherswithoutborders.org/')

        
    def saveAndCont(self):
        url = self.context.getURL()
        mtool = self.context.portal_membership
        mtool.getAuthenticatedMember().bookmark_url = url
        self.request.response.redirect(self.getNextItem(self.context))




