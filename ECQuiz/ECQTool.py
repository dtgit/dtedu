# -*- coding: iso-8859-1 -*-
#
# $Id: ECQTool.py,v 1.2 2006/09/19 16:09:54 mxp Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject, getToolByName
import re
import cgi
import urllib
from OFS.Folder import Folder
from datetime import datetime

HAS_FIVE_TS = True
try:
    from Products.Five.i18n import FiveTranslationService
    from Products import PlacelessTranslationService
except ImportError:
    HAS_FIVE_TS = False
    from Products.PageTemplates.GlobalTranslationService import \
         getGlobalTranslationService

from config import *
from permissions import *
from tools import makeTransactionUnundoable

class ECQTool(UniqueObject, Folder):
    """Various utility methods."""

    id = 'ecq_tool'
    portal_type = meta_type = 'ECQuiz Tool'
    
    security = ClassSecurityInfo()

    # manage options
    manage_options = (
        (Folder.manage_options[0],)
        + Folder.manage_options[2:]
        )

    def __init__(self):
        """
        """
        pass

    def getContentLang(self, object, domain=I18N_DOMAIN):
        if HAS_FIVE_TS:
            # Returns a PTSWrapper
            service = PlacelessTranslationService.getTranslationService()
        else:
            # Returns a PTSWrapper
            service = getGlobalTranslationService()

        # Get the actual PlacelessTranslationService
        service = service.load(object)

        availableTranslations = service.getLanguages(domain)
        
        if object.Language() in availableTranslations:
            return object.Language()

        requestLang = self.getAcceptLanguages(object, availableTranslations)
        if requestLang:
            return requestLang
        
        props = getToolByName(object,'portal_properties').site_properties
        return props.default_language

    def getAcceptLanguages(self, object, available):
        acceptable = object.REQUEST.get('HTTP_ACCEPT_LANGUAGE')
        langcode = re.compile(r'^[^;]+')
        
        if acceptable:
            acceptable = acceptable.split(',')
            acceptable = [langcode.match(elt).group(0) for elt in acceptable]
            lang = [l for l in acceptable if l in available]
            if lang: return lang[0]
        return None

    def localizeNumber(self, format, value):
        """
        A simple method for localized formatting of decimal numbers,
        similar to locale.format().
        """

        result = format % value
        fields = result.split(".")
        decimalSeparator = self.translate(msgid = 'fraction_delimiter',
                                          domain = I18N_DOMAIN,
                                          default = '.')
        if len(fields) == 2:
            result = fields[0] + decimalSeparator + fields[1]
        elif len(fields) == 1:
            result = fields[0]
        else:
            raise ValueError, "Too many decimal points in result string"

        return result

    def localizeTimeDelta(self, diff):
        """
        Return the difference between two times in a localizable format.
        """
        try:
            fmt = self.translate(msgid   ='time_delta_fmt',
                                 domain  = I18N_DOMAIN,
                                 default = '%H:%M:%S')
            return (datetime(2000, 1, 1) + diff).strftime(str(fmt))
        except:
            return 'error'

    security.declarePublic('getFullNameById')
    def getFullNameById(self, id):
        """
        Returns the full name of a user by the given ID.
        """
        
        mtool = self.portal_membership
        member = mtool.getMemberById(id)
        error = False

        if not member:
            return id
        
        try:
            sn        = member.getProperty('sn')
            givenName = member.getProperty('givenName')
        except:
            error = True

        if error or (not sn) or (not givenName):
            fullname = member.getProperty('fullname', '')
            
            if fullname == '':
                return id
            
            if fullname.find(' ') == -1:
                return fullname
            
            sn = fullname[fullname.rfind(' ') + 1:]
            givenName = fullname[0:fullname.find(' ')]
            
        return sn + ', ' + givenName

    security.declarePublic('cmpByName')
    def cmpByName(self, candidateIdA, candidateIdB):
        return cmp(self.getFullNameById(candidateIdA),
                   self.getFullNameById(candidateIdB))

    #security.declareProtected(PERMISSION_STUDENT, 'makeTransactionUnundoable')
    # FIXME: permissions
    security.declarePublic('makeTransactionUnundoable')
    def makeTransactionUnundoable(self):
        makeTransactionUnundoable()

    security.declarePublic('parseQueryString')
    def parseQueryString(self, *args, **kwargs):
        return cgi.parse_qs(*args, **kwargs)

    security.declarePublic('parseQueryString')
    def urlencode(self, *args, **kwargs):
        return urllib.urlencode(*args, **kwargs)

    
    security.declarePublic('userHasOneOfRoles')
    def userHasOneOfRoles(self, user, roles, obj):
        userId = user.getId()
        localRoles = obj.get_local_roles_for_userid(userId)
        contextRoles = user.getRolesInContext(obj)
        for role in roles:
            if (user.has_role(role) or
                (role in localRoles) or
                (role in contextRoles)):
                return True
        return False

                       
InitializeClass(ECQTool)
