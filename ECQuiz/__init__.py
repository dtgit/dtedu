# -*- coding: iso-8859-1 -*-
#
# $Id: __init__.py,v 1.1 2006/08/10 13:16:06 wfenske Exp $
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

""" This file is needed in order to make Zope import this directory.
    All the following statements will be executed and finally 
    the 'initialize' function will be called.
"""

from Products.ECQuiz.tools import log
# mark start of Product initialization in log file
# for details on 'log' see Products.ECQuiz.config
log('------------------------------------------------------------------\n')

import os, os.path

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.validation.validators.validator import RegexValidator

from Products.ECQuiz.XMLValidator import XMLValidator

# some global constants (in ALL_CAPS) and functions
from Products.ECQuiz.config import *
from Products.ECQuiz.tools import *
from Products.ECQuiz.permissions import *

from Products.GenericSetup import profile_registry
from Products.GenericSetup import BASE, EXTENSION
from Products.CMFPlone.interfaces import IPloneSiteRoot


module = ''

# register the validator 'isPositiveInt' in the Zope environment and log whether the registration worked
registerValidatorLogged(RegexValidator, 'isPositiveInt', r'^[1-9]\d*$')

# import self defined types and register them in Zope
# (the registration of the classes contained in each file
# is done via 'registerType(ClassName)' statements in the file)
try:
    # import all answer types
    #   1. import the directory ANSWER_DIR 
    #      (can only work if there is an __init__.py in the directory)
    __import__(ANSWER_DIR, GLOBALS, locals())
    #   2. import all files in the list ANSWER_TYPES (for this to work it 
    # is not necessary to write one file per class and name the 
    # file after the class)
    for entry in ANSWER_TYPES:
        module = ANSWER_DIR + '.' + str(entry)
        __import__(module, GLOBALS, locals())
        log('Worked: importing module "%s"\n' % module)
    # import all question types
    #   1. import the directory QUESTION_DIR
    __import__(QUESTION_DIR, GLOBALS, locals())
    #   2. import all files in the list QUESTION_TYPES
    for entry in QUESTION_TYPES:
        module = QUESTION_DIR + '.' + str(entry)
        __import__(module, GLOBALS, locals())
        log('Worked: importing module "%s"\n' % module)
    # import 'ECQAbstractGroup', 'ECQuiz', 'ECQGroup'
    import ECQAbstractGroup
    import ECQuiz
    import ECGroup
    import ECQResult
    import ECQResultWorkflow
    import ECQFolder
    import ECQGroup
    import ECQReference
except Exception, e:
    # log any errors that occurred
    log('Failed: importing module "' + module + '": ' + unicode(e) + '\n')

""" Register the skins directory (where all the page templates, the
    '.pt' files, live) (defined in Products.ECQuiz.config)
"""
registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    """ The 'initialize' function of this Product.
        It is called when Zope is restarted with these files in the Products 
        directory. (I'm not sure what it does or if it is neccessary 
        at all. Best leave it alone.)
    """
    log('Start: "initialize()"\n')
    try:
        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME),
            PROJECTNAME)
        
        utils.ContentInit(
            PROJECTNAME + ' Content',
            content_types      = content_types,
            permission         = PERMISSION_ADD_MCTEST,
            extra_constructors = constructors,
            fti                = ftis,
        ).initialize(context)
        
        log('\tWorked: "ContentInit()"\n')

        # Add permissions to allow control on a per-class basis
        for i in range(0, len(content_types)):
            content_type = content_types[i].__name__
            if ADD_CONTENT_PERMISSIONS.has_key(content_type):
                context.registerClass(meta_type    = ftis[i]['meta_type'],
                                      constructors = (constructors[i],),
                                      permission   = ADD_CONTENT_PERMISSIONS[content_type])

        from ECQTool import ECQTool

        utils.ToolInit(
            ECQTool.meta_type,
            tools = (ECQTool,),
            product_name = PROJECTNAME,
            icon = 'ECQTool.png',
            ).initialize(context)




	if profile_registry is not None:
            profile_registry.registerProfile('default',
                                     'ECQuiz',
                                     'Extension profile for ECQuiz',
                                     'profiles/default',
                                     'ECQuiz',
                                     EXTENSION,
                                     for_=IPloneSiteRoot)  

        #~ parsers.initialize(context)
        #~ renderers.initialize(context)
        log('Worked: "initialize()"\n')
    except Exception, e:
        # Log any errors that occurred in 'initialize()'
        log('Failed: "initialize()": ' + str(e) + '\n')
    # Mark end of Product initialization in log file.
    log('------------------------------------------------------------------\n')
