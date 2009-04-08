# -*- coding: iso-8859-1 -*-
#
# $Id: tools.py,v 1.1 2006/08/10 13:16:06 wfenske Exp $
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

from Acquisition import *
from config import PROJECTNAME
import os
import re
try:
    from ZODB.Transaction import get_transaction
except:
    from transaction import get as get_transaction
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content.base import registerATCT
from Products.validation import validation


def log(msg):
    """ Logs the message 'msg' to a logfile named something like
        'ECQuizError.log' which is located in the same
        directory as this script. This can be very helpful when
        you debug because there is no debugger in Plone/Zope.
    """
    return
    f = open(os.path.dirname(__file__) + '/' + PROJECTNAME + "Error.log", "a")
    f.write(msg)
    f.close()


class MyStringIO:
    
    def __init__(self):
        self.string = ''
        
    def write(self, s):
        self.string += s
        
    def read(self):
        return self.string
        
    def seek(self, i):
        return


def registerTypeLogged(klass):
    klassName = str(klass)
    for c in ["<class 'Products.%s." % PROJECTNAME, "'>"]:
        klassName = klassName.replace(c, '')
    try:
        registerType(klass)
        log('Worked: registerType(%s)\n' %klassName)
    except Exception, e:
        log('Failed: registerType(%s): %s\n' %(klassName, str(e)))
        raise e


def registerATCTLogged(klass):
    klassName = str(klass)
    for c in ["<class 'Products.%s." % PROJECTNAME, "'>"]:
        klassName = klassName.replace(c, '')
    try:
        registerATCT(klass, PROJECTNAME)
        log('Worked: registerType(%s)\n' %klassName)
    except Exception, e:
        log('Failed: registerType(%s): %s\n' %(klassName, str(e)))
        raise e


def registerValidatorLogged(klass, *args, **kwargs):
    klassName = str(klass)
    for c in ["Products.%s." % PROJECTNAME]:
        klassName = klassName.replace(c, '')
    try:
        validation.register(klass(*args, **kwargs))
        log('Worked: validation.register(%s(*%s, **%s))\n'
            % (klassName, repr(args), repr(kwargs)))
    except Exception, e:
        log('Failed: validation.register(%s(*%s, **%s)): %s\n'
            %(klassName, repr(args), repr(kwargs), str(e)))
        raise e


def getParent(obj):
    """ Returns the Plone-Object (e.g. a folder) containing 'obj' """
    try:
        parent = obj.parent
    except:
        parent = aq_parent(obj)
    if parent is None:
        txt = "getParent(%s) failed. parent is None.\n" % str(obj)
        log(txt)
        raise Exception(txt)
    else:
        return parent


def filterBy(idList, objList, getIdFun):
    """ Return the list of objects whose ids are in "idList"
        The objects are returned in the order they appear in "idList "
        (NOT in the order they appear in "objList").
        If there is no object in "objList" for an id from "idList",
        an exception will occur.
    """
    returnedObjects = []
    for id in idList:
        newObjs = filter((lambda obj : getIdFun(obj) == id) , objList)
        returnedObjects.extend(newObjs)
    return returnedObjects
    

def filterById(idList, objList):
    return filterBy(idList, objList, (lambda obj : obj.getId()))
        

def filterByUID(idList, objList):
    return filterBy(idList, objList, (lambda obj : obj.UID()))



def evalFunString(funString, funName, argList):
    """ Compiles the Python function definition in 'funString' and
        calls the function 'funName' with the arguments in the list
        'argList'. The return-value of this call is returned.
    """
    codeObj = compile(funString, '<string>', 'exec')
    #~ r = re.compile(ur"\A\s*def\s+(?P<functionName>[^(]+)")
    #~ functionName = r.search(funString).group("functionName")
    exec(codeObj)
    #~ return apply(eval(functionName), argList)
    return apply(eval(funName), argList)


def isNumeric(number):
    return (type(number) in [int, long, float])
    

def makeTransactionUnundoable():
    transaction = get_transaction()
    transaction.setUser(' ')


def createObject(context, typeName, id=None):
    """Creates a new article/object via Python code and returns the
    new object.

    (The code is actually from 'createObject.cpy' (the script that is
    called when you add a new article).)"""
    
    if id is None:
        id=context.generateUniqueId(typeName)
    
    if typeName is None:
        raise Exception, 'Type name not specified'
    
    if context.portal_factory.getFactoryTypes().has_key(typeName):
        o = context.restrictedTraverse('portal_factory/' + typeName + '/' + id)
    else:
        newId = context.invokeFactory(id=id, type_name=typeName)
        if newId is None or newId == '':
            newId = id
        o=getattr(context, newId, None)
    
    if o is None:
        raise Exception

    o = context.portal_factory.doCreate(o, id)
    o.reindexObject()
    
    return o

def setTitle(obj, newTitle):
    # Sets the title of 'obj' to 'newTitle' and calls 
    # 'obj.reindexObject()' which forces an update of the view of the folder 
    # that contains 'obj' (or something to that effect).
    obj.setTitle(newTitle)
    try:
        obj.reindexObject()
    except AttributeError:
        pass

from Products.Archetypes.Field import StringField
from Products.Archetypes.Widget import IdWidget
def hideIdField(schema):
    hiddenIdField = StringField('id',
        default=None,
        widget=IdWidget(
            visible={'view' : 'invisible'},
            macro='empty_widget'
        ),
    )
    schema.replaceField('id', hiddenIdField)
    return schema
