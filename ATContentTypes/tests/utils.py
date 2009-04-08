#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from UserDict import UserDict
import ExtensionClass
from Acquisition import Implicit
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from Persistence import Persistent
import os

PACKAGE_HOME = package_home(globals())

class FakeRequestSession(ExtensionClass.Base, UserDict):
    """Dummy dict like object with set method for SESSION and REQUEST
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()
    
    def __init__(self):
        UserDict.__init__(self)
        # add a dummy because request mustn't be empty for test
        # like 'if REQUEST:'
        self['__dummy__'] = None
    
    def __nonzero__(self):
        return True
    
    def set(self, key, value):
        self[key] = value

InitializeClass(FakeRequestSession)
FakeRequestSession()

class DummySessionDataManager(Implicit):
    """Dummy sdm for sessioning
    
    Uses traversal hooks to add the SESSION object as lazy item to the request
    """
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    security.declareObjectPublic()
    
    id = 'session_data_manager'
    
    def __init__(self):
        self.session = FakeRequestSession()
        
    def manage_afterAdd(self, item, container):
        """Register traversal hooks to add SESSION to request
        """
        parent = self.aq_inner.aq_parent
        hook = DummySDMTraverseHook()
        registerBeforeTraverse(parent, hook, 'SessionDataManager', 50)

    def getSessionData(self, create=1):
        """ """
        return self.session
    
    def hasSessionData(self):
        """ """
        return True
    
    def getSessionDataByKey(self, key):
        """ """
        return self.session
    
    def getBrowserIdManager(self):
        """ """
        # dummy
        return self

InitializeClass(DummySessionDataManager)

class DummySDMTraverseHook(Persistent):
    """Traversal hook for dummy sessions
    
    See Products.Sessions.SessionDataManager.SessionDataManagerTraverser
    """
    
    def __call__(self, container, request):
        id = DummySessionDataManager.id
        sdm = getattr(container, id)
        getSessionData = sdm.getSessionData
        request.set_lazy('SESSION', getSessionData)

def Xprint(s):
    """print helper

    print data via print is not possible, you have to use
    ZopeTestCase._print or this function
    """
    ZopeTestCase._print(str(s)+'\n')

from DateTime import DateTime
def dcEdit(obj):
    """dublin core edit (inplace)
    """
    obj.setTitle('Test title')
    obj.setDescription('Test description')
    obj.setSubject('Test subject')
    obj.setContributors(('test user a',))
    obj.setEffectiveDate(DateTime() -1)
    obj.setExpirationDate(DateTime() +2)
    obj.setFormat('text/structured')
    obj.setLanguage('de')
    obj.setRights('GPL')
    
from Products.validation import ValidationChain
EmptyValidator = ValidationChain('isEmpty')
EmptyValidator.appendSufficient('isEmpty')
idValidator = ValidationChain('isValidId')
idValidator.appendSufficient('isEmptyNoError')
idValidator.appendRequired('isValidId')
TidyHTMLValidator = ValidationChain('isTidyHtmlChain')
TidyHTMLValidator.appendRequired('isTidyHtmlWithCleanup')
NotRequiredTidyHTMLValidator = ValidationChain('isTidyHtmlNotRequiredChain')
NotRequiredTidyHTMLValidator.appendSufficient('isEmptyNoError')
NotRequiredTidyHTMLValidator.appendRequired('isTidyHtmlWithCleanup')
URLValidator = ValidationChain('isURL')
URLValidator.appendSufficient('isEmptyNoError')
URLValidator.appendRequired('isURL')
EmailValidator = ValidationChain('isEmailChain')
EmailValidator.appendSufficient('isEmptyNoError')
EmailValidator.appendSufficient('isMailto')
EmailValidator.appendRequired('isEmail')
EmailValidator = ValidationChain('isEmailChain')
EmailValidator.appendSufficient('isEmptyNoError')
EmailValidator.appendRequired('isEmail')
PhoneValidator = ValidationChain('isPhoneChain')
PhoneValidator.appendSufficient('isEmptyNoError')
PhoneValidator.appendRequired('isInternationalPhoneNumber')

PREFIX = os.path.abspath(os.path.dirname(__file__)) 

def input_file_path(file): 
    return os.path.join(PREFIX, 'input', file) 
