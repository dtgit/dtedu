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

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.interface import implements
from zope.formlib.form import Fields
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IMyCTMFolderPortlet(IPortletDataProvider):
    """ Show my courses portlet. """


class Assignment(base.Assignment):
    """ Assignment """

    implements(IMyCTMFolderPortlet)

    title = _('My CTM Folder')


class Renderer(base.Renderer):
    """ Renderer """

    render = ViewPageTemplateFile('myctmfolder.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)

        groups_url = '10.6.0.4:8088/plone'

        user = context.portal_membership.getAuthenticatedMember().getUserName()
        
        #retrieve user password from __ac cookie
        ac = self.request['__ac']
        pwd = decodestring(ac).split(':')[1]

        user_pwd = pwd.decode('hex')

        url = 'http://%s:%s@%s' % (user, user_pwd, groups_url)

        server = xmlrpclib.ServerProxy(url)
        
        results = server.xmlrpc_getCTMFolder(user) 

        
    @property
    def available(self):
        roles = self.context.portal_membership.getAuthenticatedMember().getRoles()
        return ('Contributor' in roles or \
                'Administrator' in roles or 
                'Manager' in roles) and self.numCourses


    def getMyCTMFolder(self):
        return results


    
class AddForm(base.NullAddForm):
    """ Add Form """

    form_fields = Fields(IMyCTMFolderPortlet)

    def create(self):
        return Assignment()
