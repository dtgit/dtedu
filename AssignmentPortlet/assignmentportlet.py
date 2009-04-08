from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.eduCommons.browser.assignmentcontents import AssignmentState


class IAssignmentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IAssignmentPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Assignment Portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('assignmentportlet.pt')

    def __init__(self, context, request, view, manager, data):
        self.context = context
        super(Renderer, self).__init__(self.context, request, view, manager, data)
        self.mtool = self.context.portal_membership

        self.assignmentstate = AssignmentState(self.context)
        self.inprogress = len(self.assignmentstate.getInprogress())
        self.submitted = len(self.assignmentstate.getSubmitted())
        self.graded = len(self.assignmentstate.getGraded())
        self.unsubmitted = len(self.assignmentstate.getUnsubmitted())
        self.total = len(self.assignmentstate.getTotal())

    @property
    def available(self):
        return 'CTMParticipant' in self.mtool.getAuthenticatedMember().getGroups() and not self.context.isTemporary()

    def getInprogressCount(self):
        return self.inprogress

    def getSubmittedCount(self):
        return self.submitted

    def getGradedCount(self):
        return self.graded

    def getUnsubmittedCount(self):
        return self.unsubmitted

    def getTotalCount(self):
        return self.total

    def getStatePercent(self, state):
        """ Grab states for each object based on a filter """

        func = getattr(self, 'get%sCount' %state,  None)
        val = func()

        try:
            return str(float(val)/self.getTotalCount() * 100) + '%'
        except ZeroDivisionError:
            return '0%'

    def getCtmUrl(self):
	mtool = self.context.portal_membership.getAuthenticatedMember()
	if mtool.getProperty('ctmbookmark'):
	    return mtool.getProperty('ctmbookmark')
	else:
	    return ''

    def getCtmCohort(self):
	mtool = self.context.portal_membership.getAuthenticatedMember()
	if mtool.getProperty('ctmcohort'):
	    return mtool.getProperty('ctmcohort')
	else:
	    return ''


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IAssignmentPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IAssignmentPortlet)
