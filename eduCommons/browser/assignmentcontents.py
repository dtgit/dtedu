from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.foldercontents import FolderContentsView, FolderContentsTable
import urllib
from zope.component import getUtility
from Products.eduCommons.utilities.interfaces import IECUtility
from plone.app.content.browser.tableview import Table
from kss.core import KSSView
from zope.app.pagetemplate import ViewPageTemplateFile
from Acquisition import aq_parent, aq_inner
from zope.annotation import IAnnotations
from summarycontents import SummaryContentsTable, SummaryTable, SummaryContentsView




class AssignmentContentsView(FolderContentsView):
    """
    Override contents table to use FindECParent and user query_type parameter instead of review_state.
    """

    def contents_table(self):
	ecutil = getUtility(IECUtility)
	parent = ecutil.FindECParent(self.context)
        path = '/'.join(parent.getPhysicalPath())
        request = self.request
        state = ''
        if request.has_key('state'):
            review_state = request['state']
            state = request['state']
	else:
	    review_state = ''

        table = AssignmentContentsTable(parent, self.request, contentFilter={'path':path,'state':state})
        return table.render()


class AssignmentContentsTable(FolderContentsTable):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        """
        Initialize the table
        """
        super(AssignmentContentsTable, self).__init__(context, request, contentFilter)
        url = self.context.absolute_url()
        view_url = url + '/assignment_contents'
        self.table = SummaryTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)
    
    @property
    def items(self):
        """
        """
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = self.context.browserDefault()


        # This is the customized portion. Takes list of items from the AssignmentState object rather than 
        # the querying the object based on the contentFilter.

        state = self.contentFilter['state']
        assignmentState = AssignmentState(self.context)
        func = getattr(assignmentState,'get' + plone_utils.normalizeString(state).capitalize() )
        listobjects = func()

        # end of customizations

        results = list()
        for i, obj in enumerate(listobjects):
            if i % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])


            #if IAnnotations(obj.getObject()).has_key('eduCommons.clearcopyright'):
            #    cc_status = IAnnotations(obj.getObject())['eduCommons.clearcopyright']
            #else:
            #    cc_status = False
                              

            pathlist = obj.getPath().split('/')

            if len(pathlist) > 1 and obj.portal_type == 'ECAssignment':
                obj_title = '%s (%s)' %(obj.pretty_title_or_id(), pathlist[-2])
            else:
                obj_title = obj.pretty_title_or_id()

            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj_title,
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = self.context.isExpired(obj),
                #cc_status = cc_status,
            ))
        return results

class AssignmentState(object):

    def __init__(self, context): 

        parent = context
        if context.portal_type != 'Course':
            ecutil = getUtility(IECUtility)
            parent = ecutil.FindECParent(context)

        self.context = parent.aq_inner.aq_parent

        self.inpro = []
        self.subm = []
        self.grad = [] 
        self.nonc = []
        hasStarted = []

	assignmentboxes = self.context.portal_catalog.queryCatalog({'path':{'query':'/'.join(self.context.getPhysicalPath()),},'portal_type':'ECAssignmentBox'})
        member = self.context.portal_membership.getAuthenticatedMember().id

        for assignmentbox in assignmentboxes:
            assignments = self.context.portal_catalog.queryCatalog({'path':{'query':assignmentbox.getPath(),},'portal_type':'ECAssignment'})
            for assignment in assignments:
                if assignment.getObject().getOwner().getId() == member:
                    state = assignment.review_state
                    if state == 'inprogress':
                        self.inpro += [assignment]
                        hasStarted = 1
                    elif state == 'submitted':
                        self.subm += [assignment]
                        hasStarted = 1
                    elif state == 'graded':
                        self.grad += [assignment]
                        hasStarted = 1

            if not hasStarted:
                self.nonc += [assignmentbox]
            
            hasStarted = 0

    def getInprogress(self):
        return self.inpro

    def getSubmitted(self):
        return self.subm

    def getGraded(self):
        return self.grad

    def getUnsubmitted(self):
        return self.nonc

    def getTotal(self):
        return self.getInprogress() + self.getSubmitted() + self.getGraded() + self.getUnsubmitted()


