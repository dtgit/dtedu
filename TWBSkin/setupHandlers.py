##################################################################################
#    Copyright (C) 2004-2007 Utah State University, All rights reserved.          
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]


from zope.component import getUtility, getMultiAdapter
from Products.CMFCore.interfaces import ISkinsTool
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from plone.app.portlets.portlets import classic

def importFinalSteps(context):
    site = context.getSite()
    setupBaseProperties(site)
    customizeActionTitles(site)


def setupBaseProperties(site):
    # Setup custom properties for skin
    stool = site.portal_skins

#    if 'custom' in stool.keys():
#        if 'base_properties' in stool.custom.keys():
#            stool.custom.manage_delObjects('base_properties')

    site.portal_properties.site_properties.manage_changeProperties(disable_folder_sections=True)


def customizeActionTitles(site):
    """ Customize the titles for Zip import/export and IMS import/export  """
    portal_actions = site.portal_actions

    folder_buttons = portal_actions.folder_buttons
    for button in folder_buttons.listActions():
        if button.title == 'Import':
            button.title = 'Zip Import'
        elif button.title == 'Export':
            button.title = 'Zip Export'

    object = portal_actions.object
    for ob in object.listActions():
        if ob.title == 'IMS':
            ob.title = 'IMS Import/Export'
