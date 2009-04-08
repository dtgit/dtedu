# -*- coding: iso-8859-1 -*-
#
# $Id: ECQMCAnswer.py,v 1.1 2006/08/10 13:16:08 wfenske Exp $
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

from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, SelectionWidget, TextAreaWidget, RichWidget, \
     BaseContent
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget

from Products.ECQuiz.config import *
from Products.ECQuiz.permissions import *
from Products.ECQuiz.tools import log, registerTypeLogged
from Products.ECQuiz.AnswerTypes.ECQCorrectAnswer import ECQCorrectAnswer

class ECQMCAnswer(ECQCorrectAnswer):
    """An answer to a multiple-choice question."""
    
    meta_type = 'ECQMCAnswer'    # zope type name
    portal_type = meta_type      # plone type name
    archetype_name = 'MC Answer' # friendly type name

    # Use the portal_factory for this type.  The portal_factory tool
    # allows users to initiate the creation objects in a such a way
    # that if they do not complete an edit form, no object is created
    # in the ZODB.
    #
    # This attribute is evaluated by the Extensions/Install.py script.
    use_portal_factory = True

    security = ClassSecurityInfo()
    security.declareProtected(PERMISSION_STUDENT, 'getId')
    security.declareProtected(PERMISSION_STUDENT, 'getAnswer')
    

# Register this type in Zope
registerTypeLogged(ECQMCAnswer)
