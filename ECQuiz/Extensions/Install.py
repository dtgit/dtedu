# -*- coding: iso-8859-1 -*-
#
# $Id: Install.py,v 1.2 2006/10/19 19:54:19 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""The install script for this Product.  I'm not sure how it's
supposed to work but at least it's working if this file is called
'Install.py', contains a function 'install(self)' and is located in a
directory called 'Extensions'.
"""

from Products.Archetypes.public import process_types, listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.migrations.migration_util import addLinesToProperty
from StringIO import StringIO

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import log

from Products.ECQuiz.ECQResult import ECQResult
from Products.ECQuiz.ECQGroup import ECQGroup
from Products.ECQuiz.QuestionTypes.ECQMCQuestion import ECQMCQuestion
from Products.ECQuiz.QuestionTypes.ECQScaleQuestion import ECQScaleQuestion
from Products.ECQuiz.QuestionTypes.ECQExtendedTextQuestion \
     import ECQExtendedTextQuestion
from Products.ECQuiz.ECQAbstractGroup   import ECQAbstractGroup
from Products.ECQuiz.ECQuiz import ECQuiz
from Products.ECQuiz.AnswerTypes.ECQMCAnswer import ECQMCAnswer
from Products.ECQuiz.AnswerTypes.ECQScaleAnswer import ECQScaleAnswer


def install_dependencies(self, out):
    """Checks wether or not depending products are installed. If not,
    try to install them.
    """
    missing = []
    
    qi = getToolByName(self, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if qi.isProductInstallable(product):
            if not qi.isProductInstalled(product):
                qi.installProduct(product)
        else:
            missing.append(product)

    if missing:
        s = ', '.join([("`%s'" % p) for p in missing])
        print >> out, "Missing dependencies: %s." % s
        raise Exception('Missing dependencies: %s.' % s)
    else:
        print >> out, "success."


def install_workflows(self, out):
    wf_tool = getToolByName(self, 'portal_workflow')

    for wfId, wfTitle in ((ECMCR_WORKFLOW_ID, ECMCR_WORKFLOW_TITLE),
                          (ECMCT_WORKFLOW_ID, ECMCT_WORKFLOW_TITLE),
                          (ECMCE_WORKFLOW_ID, ECMCE_WORKFLOW_TITLE),
                          ):
        if wfId in wf_tool.objectIds():
            wf_tool._delObject(wfId)
    
        wf_tool.manage_addWorkflow(id=wfId,
                                   workflow_type='%s (%s)' % (wfId, wfTitle))
    
    ecmce_types = [c.meta_type for c in (ECQAbstractGroup,
                                         ECQGroup,
                                         ECQMCQuestion,
                                         ECQMCAnswer,
                                         ECQScaleQuestion,
                                         ECQScaleAnswer,
                                         ECQExtendedTextQuestion,
                                         )]
    wf_tool.setChainForPortalTypes(ecmce_types, ECMCE_WORKFLOW_ID)

    wf_tool.setChainForPortalTypes((ECQResult.meta_type,),
                                   ECMCR_WORKFLOW_ID)
    wf_tool.setChainForPortalTypes((ECQuiz.meta_type,),
                                   ECMCT_WORKFLOW_ID)
    
    # in case the workflows have changed, update all workflow-aware objects
    wf_tool.updateRoleMappings()
    
    print >> out, "success."


def install(self):
    """Installs the Product."""
    
    out = StringIO()

    def descr(step):
        #return
        out.write("%s ... " % step)
    
    try:
        # install depending products
        descr('Installing Dependencies')
        install_dependencies(self, out)
        
        # out.write("QUESTION_TYPES = " + unicode(QUESTION_TYPES) + "\n")
        # out.write("ANSWER_TYPES = " + unicode(ANSWER_TYPES) + "\n")
        
        # Call Archetypes' install functions
        descr('Installing Types')
        installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

        # Make some settings for types, currently:
        #
        # - Hide types from the potal_navigation tree (controlled by
        #   navigation_exclude = True in the class definition)
        #
        # - Enable the portal_factory (controlled by
        #   use_portal_factory = True in the class definition)
        #
        navtree_props = self.portal_properties.navtree_properties
        unlisted      = getattr(navtree_props, 'metaTypesNotToList', ())
        factory_tool  = getToolByName(self, 'portal_factory')
        factory_types = []
        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME), PROJECTNAME)
        
        for i in range(0, len(content_types)):
            meta_type = ftis[i]['meta_type']
            
            exclude            = getattr(content_types[i],
                                         'navigation_exclude', False)
            use_portal_factory = getattr(content_types[i],
                                         'use_portal_factory', False)
            
            if exclude:
                if meta_type not in unlisted:
                    addLinesToProperty(navtree_props, 'metaTypesNotToList',
                                       meta_type)
            if use_portal_factory:
                factory_types.append(meta_type)

        factory_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)
        
        print >> out, "success."
        
        descr('Installing Skins')
        install_subskin(self, out, GLOBALS)
        print >> out, "success."

        # Install workflows
        descr('Installing Workflows')
        install_workflows(self, out)
        
        # Install the multiple choice tool
        descr('Installing Tool')
        from Products.ECQuiz.ECQTool \
             import ECQTool as Tool

        if hasattr(self, Tool.id):
            self.manage_delObjects([Tool.id])
            out.write('Deleting old %s; make sure you repeat '
                      'customizations.\n' % Tool.id)
        addTool = self.manage_addProduct[PROJECTNAME].manage_addTool

        addTool(Tool.meta_type)
        # set title of tool:
        tool = getToolByName(self, Tool.id)
        tool.title = Tool.meta_type
        print >> out, "Added %s to the portal root folder." % tool.title

        out.write("\n")
        out.write("Successfully installed %s." % PROJECTNAME)
    except Exception, e:
        log("install() failed: " + str(e) + "\n")
        out.write("\n")
        out.write("Failed to install %s:\n\n  %s" % (PROJECTNAME, str(e)))
        #raise Exception(out.getvalue())
    return out.getvalue()
