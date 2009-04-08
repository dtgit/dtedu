# -*- coding: iso-8859-1 -*-
#
# $Id: qti.py,v 1.4 2007/06/27 22:59:11 wfenske Exp $
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

from tools import createObject, setTitle
from xml.dom import minidom
from xml.dom.minidom import parseString
from StringIO import StringIO
from mimetypes import guess_type
import os, os.path
from zipfile import ZipFile

from Products.Archetypes.utils import shasattr

from config import I18N_DOMAIN, PROJECTNAME
FIXME_PROJECTNAME = 'LlsMultipleChoice'
from ECQGroup import ECQGroup
from QuestionTypes.ECQMCQuestion import ECQMCQuestion
from AnswerTypes.ECQMCAnswer import ECQMCAnswer
from QuestionTypes.ECQExtendedTextQuestion import ECQExtendedTextQuestion
from QuestionTypes.ECQScaleQuestion import ECQScaleQuestion
from AnswerTypes.ECQScaleAnswer import ECQScaleAnswer
from tools import createObject, log

# A couple of namespaces used by QTI
NS_IMSCP_V1P1_URI = u'http://www.imsglobal.org/xsd/imscp_v1p1'
NS_IMSMD_V1P2_URI = u'http://www.imsglobal.org/xsd/imsmd_v1p2'
NS_IMSMD = u'imsmd'
NS_XSI_URI = u'http://www.w3.org/2001/XMLSchema-instance'
NS_XSI = u'xsi'
NS_IMSQTI_V2P0_URI = u'http://www.imsglobal.org/xsd/imsqti_v2p0'
NS_IMSQTI_V2P0_URL = u'http://www.imsglobal.org/xsd/imsqti_v2p0.xsd'
NS_IMSQTI = u'imsqti'
NS_IMSSS_URI = u'http://www.imsglobal.org/xsd/imsss'
NS_IMSSS = u'imsss'
NS_LLSMC_URI = u'http://wwwai.cs.uni-magdeburg.de/llsmc/v1.0'
NS_LLSMC = u'llsmc'

# More namespace stuff. The schemas used in the manifest (for export).
MANIFEST_SCHEMA_LOCATIONS = \
            NS_IMSCP_V1P1_URI  + u' http://www.imsglobal.org/xsd/imscp_v1p1.xsd'\
    u'\n' + NS_IMSMD_V1P2_URI  + u' http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd'\
    u'\n' + NS_IMSQTI_V2P0_URI + u' ' + NS_IMSQTI_V2P0_URL

# The path where the assesment items will be located when an ecquiz is
# exported as a QTI package.
EXPORT_ITEM_PATH = u'content'

# Used to mark our own QTI package export format.
MC_TOOL_VERSION = u'1.0'
MC_TOOL_VENDOR = u'WDOK Research Group, Otto-von-Guericke-Universität Magdeburg'

# A number of names of QTI elements.
CHOICE_INTERACTION = u'choiceInteraction'
EXTENDED_TEXT_INTERACTION = u'extendedTextInteraction'
PLACEHOLDER_TEXT = u'placeholderText'
EXPECTED_LENGTH = u'expectedLength'
ASSESSMENT_ITEM = u'assessmentItem'
PROMPT = u'prompt'
ITEM_BODY = u'itemBody'
ORGANIZATIONS = u'organizations'
ORGANIZATION = u'organization'
IDENTIFIER = u'identifier'
IDENTIFIER_REF = u'identifierref'
RESPONSE_IDENTIFIER = u'responseIdentifier'
RESOURCES = u'resources'
RESOURCE = u'resource'
TYPE = u'type'
ITEM = u'item'
FILE = u'file'
METADATA = u'metadata'
QTI_METADATA = u'qtiMetadata'
SEQUENCING = u'sequencing'
RANDOMIZATION_CONTROLS = u'randomizationControls'
RANDOMIZATION_TIMING = u'randomizationTiming'
ON_EACH_NEW_ATTEMPT = u'onEachNewAttempt'
REORDER_CHILDREN = u'reorderChildren'
SELECT_COUNT = u'selectCount'
LIMIT_CONDITIONS = u'limitConditions'
ATTEMPT_LIMIT = u'attemptLimit'
ADAPTIVE = u'adaptive'
TIME_DEPENDENT = u'timeDependent'
TRUE = u'true'
FALSE = u'false'
RESPONSE_DECLARATION = u'responseDeclaration'
CORRECT_RESPONSE = u'correctResponse'
MAPPING = u'mapping'
DEFAULT_VALUE = u'defaultValue'
MAP_ENTRY = u'mapEntry'
MAP_KEY = u'mapKey'
MAPPED_VALUE = u'mappedValue'
OUTCOME_DECLARATION = u'outcomeDeclaration'
VALUE = u'value'
SHUFFLE = u'shuffle'
MAX_CHOICES = u'maxChoices'
SIMPLE_CHOICE = u'simpleChoice'
FEEDBACK_INLINE = u'feedbackInline'
FEEDBACK_BLOCK = u'feedbackBlock'
SHOW_HIDE = u'showHide'
SHOW = u'show'
HIDE = u'hide'
OUTCOME_IDENTIFIER = u'outcomeIdentifier'
INTERACTION_TYPE = u'interactionType'
TITLE = u'title'
IMS_QTI_SCHEMA_VERSION = u'2.0'
TOOL_NAME = u'toolName'
TOOL_VERSION = u'toolVersion'
TOOL_VENDOR = u'toolVendor'
LOM = u'lom'
GENERAL = u'general'
LANG_STRING = u'langstring'
XML_LANG = u'xml:lang'
MANIFEST = u'manifest'
HREF = u'href'

WEIGHT = u'weight'
INSTANT_FEEDBACK = u'instantFeedback'
ONE_QUESTION_PER_PAGE = u'oneQuestionPerPage'
ALLOW_NAVIGATION = u'allowNavigation'
SCORING_FUNCTION = u'scoringFunction'
GRADING_SCALE = u'gradingScale'
GRADING_SCALE_ROW = u'gradingScaleRow'
GRADE = u'grade'
MIN_SCORE = u'minScore'
LAYOUT = u'layout'
TUTOR_GRADED = u'tutorGraded'

# All the interaction types we can import
SUPPORTED_INTERACTION_TYPES = [CHOICE_INTERACTION, EXTENDED_TEXT_INTERACTION]

# The name of the imsmanifest file of a QTI package.
MANIFEST_FILE_NAME = u'imsmanifest.xml'
# The resource type we can import.
IMSQTI_ITEM_XMLV2P0 = u'imsqti_item_xmlv2p0'

# The encoding that will be used in QTI package export.
EXPORT_ENCODING = u'utf-8'

# A list of the HTML elements that are allowed as content of <itemBody> in an
# assessment item.
BLOCK_ELEMENTS = [u'pre', u'h2', u'h3', u'h1', u'h6', u'h4', u'h5', 
    u'p', u'address', u'dl', u'ol', u'hr', u'ul', u'table', u'div']

# A list of the HTML elements that are allowd as content of the <prompt>,
# <simpleChoice> and <feedbackInline> elemnts in an assessment item.
INLINE_ELEMENTS = [u'img', u'br', u'object', u'em', u'a', u'code', 
    u'span', u'sub', u'acronym', u'big', u'tt', u'kbd', u'q', u'i', 
    u'dfn', u'abbr', u'strong', u'sup', u'var', u'small', u'samp', 
    u'b', u'cite']

# Import modes used in importResource(), importAsessmentItem()
DEFAULT = 0
FORCE_TEST = 1
FORCE_GROUP = 2
FORCE_QUESTION = 3

# The prefix for UIDs used during import and export
UID_PREFIX = u'UID-'


def getElementsByTagNameFlat(node, tagName):
    """ Works similar to node.getElementsByTagName(tagName)
        but returns only direct children.
            Also returns children whose localName is tagName minus a possible
        namespace prefix.

        @param node An XML element.
        @param tagName The name of the direct child elements of 'node'
                you want to have.

        @return The direct children of 'node' whose nodeName name is 'tagName' or
            whose localName is tagName minus a possible namespace prefix.
    """
    ret = []
    tagNameSplit = tagName.split(u':')
    if len(tagNameSplit) > 1:
        [nsPrefix, localName] = tagNameSplit
    else:
        nsPrefix = None
        localName = tagName
    for child in node.childNodes:
        if ((child.nodeType == child.ELEMENT_NODE) 
            and ((child.nodeName == tagName) or 
                  (child.localName == localName))):
            ret += [child]
    return ret
    

def getFirstElementByTagNameFlat(node, tagName):
    """ Like getElementsByTagNameFlat(node, tagName), but returns the only the first
        element in the list or None.
    """
    l = getElementsByTagNameFlat(node, tagName)
    if (l):
        return l[0]
    else:
        return None


def filterChildren(element, keepList):
    """ Removes any ELEMENT_NODE children of the XML element 'element' if
        their node name is not in the list of names 'keepList'.

        @param element An XML element.
        @param keepList A list of the names of elements that should be kept.

        @return A reduced clone of the element 'element' with all ELEMENT_NODE
            children removed whose name was not in 'keepList'.
            E.g. if you have element <p>Hello <em>World</em>!<i>How are<em>you</em> today</i></p>
            an call filterChildren(element, ['em']) you will get an element
            <p>Hello <em>World</em>!</p>.
    """
    clone = element.cloneNode(True)
    for child in clone.childNodes:
        if ((child.nodeType == child.ELEMENT_NODE) 
            and (not (child.nodeName in keepList))):
            clone.removeChild(child)
    return clone


def getAttribute(node, attributeName, defaultValue = None):
    """ Return the value of an attribute 'attributeName' of the XML element
        'node' or 'defaultValue' if the element has no such attribute.

        @param node An XML element.
        @param attributeName The name of the attribute you want to have.
        @param defaultValue A default value that is returned if
                node does not have an attribute called 'attributeName'.

        @return If present, the value of the attribute 'attributeName' or
            otherwise 'defaultValue'.
    """
    if (node.hasAttribute(attributeName)):
        return node.getAttribute(attributeName)
    else:
        return defaultValue


def getText(node, defaultValue = None):
    """ Return the text content of an element as a string.

        @param node An XML element.
        @param defaultValue A default value that is returned if
                node does not have any child nodes of type TEXT_NODE.

        @return The concatenation of all the direct TEXT_NODE children of
            'node' or 'defaultValue' if there aren't any.
    """
    text = None
    foundText = False
    for child in node.childNodes:
        if (child.nodeType == child.TEXT_NODE):
            if (foundText):
                text += child.data
            else:
                text = child.data
                foundText = True
    if foundText:
        return text
    else:
        return defaultValue


def contentsToUnicodeString(node):
    """ Render the contents of an XML element to a unicode string.

        @param node An XML element.

        @return A unicode string containing the contents of the element.
            E.g. contentsToUnicodeString() of the <p> element of
            <p>Hello<br/><em>World</em></p> would return
            u'Hello<br/><em>World</em>'.
    """
    text = u''
    for child in node.childNodes:
        text += child.toxml()
    return text


def getElementsByPath(node, path):
    """ Return all the the children in 'node' that match the path given
        in 'path'.

        @param node An XML element.
        @param path A simple path-like expression, e.g. body/p/br

        @return All the child elements of 'node' that match the path.
            E.g. in X-HTML, getElementsByPath(htmlElement, 'body/p')
            would return all the paragraph elements in the body.
    """
    nodeList = [node]
    ret = []
    for elementName in path.split(u'/'):
        childrenListList = map((lambda (node) : (
            getElementsByTagNameFlat(node, elementName))), nodeList)
        nodeList = []
        for childrenList in childrenListList:
            nodeList += childrenList
    return nodeList
    

def getFirstElementByPath(node, path):
    """ Like getElementsByPath(node, path), but returns the only the first
        element in the list or None.
    """
    l = getElementsByPath(node, path)
    if (l):
        return l[0]
    else:
        return None


def stringToZopeId(context, typeName, string, errors):
    """ Try to convert the string 'string' into a Zope ID.

        @param context The context (parent) object, which will contain the
                object that you generate an ID for.
        @param typeName The type of the object you want to create, i.e.
                'Image' or 'File'.
        @param string The string you want to use as an ID.
        @param errors An object with a 'write()' method where error
                mesages can be put, i.e. a StringIO object.

        @return If the string contains non-ASCII characters, the context object
            generates a new ID for the type specified in 'typeName'.
                If 'string' is empty, None will be returned.
    """
    id = [string, None][not string]
    if id:
        try:
            id = str(unicode(id))
        except:
            oldId = id
            id = context.generateUniqueId(typeName)
            errors.write('\n' + context.translate(
                msgid   = 'identifier_unicode_error',
                domain  = I18N_DOMAIN,
                default = 'The identifier "%s" contains non-ASCII characters. '
                    'The item will be imported under the id "%s".') 
                % (context.str(oldId), context.str(id))
            )
    return id


def getChildrenWithId(context, id):
    """ Search a folderisch Zope object and return all the direct children
        (this function is not recursive) with the specified id.

        @param context A folderish Zope object.
        @param id A Zope id.

        @return A list of all the children of "context" with the id "id".
    """
    if ((not id) or (type(id) not in [str, unicode])):
        return []
    else:
        idIsUID = id.startswith(UID_PREFIX)
        if idIsUID:
            idMinusUID = id[len(UID_PREFIX) : ]
        return  [ obj for obj in context.listFolderContents() 
                    if ((obj.getId() == id) or 
                        (
                            idIsUID and hasattr(obj, 'UID') 
                            and (obj.UID() == idMinusUID)
                        )) ]


def isIdUsed(context, id, errors):
    """ Checks wether an object with the id "id" is a direct child of the
        folderish Zope object "context".

        @param context A folderish Zope object.
        @param id A Zope id.
        @param errors A string IO object. If the id is already in use, an
            error log entry will be made.

        @return True if the id is already in use, False otherwise.
    """
    if getChildrenWithId(context, id):
        errors.write('\n' + (context.translate(
            msgid   = 'item_exists', 
            domain  = I18N_DOMAIN, 
            default = 'An item named "%s" already exits.') 
            % (context.str(id))))
        return True # The id is already in use
    else:
        return False # The id is new


def readFromZip(context, zipFileObject, fileName, errors):
    """ Reads file from a Python ZipFile object and returns its contents.
        Normally, this would simply be zipFileObject.read(fileName), but
        this may fail if the file name is encoded using a code page
        unexpected by the ZipFile class, e.g. cp850, a common one on
        Windows machines.

        So what we do is try some code pages out and take what we can get.

        @param context Some object from the ECQuiz product.
                It is only needed to call some scripts, e.g. 'unicodeDecode'.
        @param zipFileObject A Python ZipFile object.
        @param fileName The name of the file you want to extract.
        @param errors A string IO object where errors can be logged.

        @return The file's contents or None if all attempts have failed.
    """
    contents = None
    firstException = None
    try:
        # Read the resource from the zip file
        contents = zipFileObject.read(fileName)
    except Exception, e:
        firstException = e

    if contents is None:
        # Try some different encodings for the file name
        uFileName = None
        try: # Convert to unicode
            uFileName = context.unicodeDecode(fileName)
        except UnicodeError:
            pass
        if uFileName:
            # cp850 and cp437 are commonly used code pages
            charSetList = ['cp850', 'cp437', 'cp1252', 'latin-1', 'utf-8']
            # Get Plone's 'default_charset'
            siteCharSet = context.getCharset()
            if siteCharSet:
                charSetList += [siteCharSet]
            for charSet in charSetList:
                try:
                    contents = zipFileObject.read(uFileName.encode(charSet))
                    # If we get here, we read something and can stop trying
                    break
                except:
                    # Probably wrong code page
                    pass

    if contents is None:
        # No luck
        errors.write('\n' + (context.translate(
            msgid   = 'extraction_error', 
            domain  = I18N_DOMAIN, 
            default = 'Cannot extract the file "%s". An error occurred: %s') 
                % (context.str(fileName), context.str(firstException))))

    return contents


def writeToZip(context, zipFileObject, fileName, contents, errors):
    """ Writes a file to a Python ZipFile object using. The file name
        will be encoded using "EXPORT_ENCODING".

        @param context Some object from the ECQuiz product.
                It is only needed to call some scripts, e.g. 'unicodeDecode'.
        @param zipFileObject A Python ZipFile object.
        @param fileName The name of the file you want to write.
        @param contents The contents of said file.
        @param errors A string IO object where errors can be logged.
    """
    fileName = context.unicodeDecode(fileName).encode(EXPORT_ENCODING)
    zipFileObject.writestr(fileName, contents)


def xhtmlExport(parentElem, xhtmlContent):
    DIV = u'div'
    docText = u'<%s>%s</%s>' % (DIV, xhtmlContent, DIV)
    docText = docText.encode(EXPORT_ENCODING)
    try:
        doc = parseString(docText)
    except:
        doc = None
    if doc: # We got well formed XML
        div = doc.documentElement
        appendElements = []
        for child in div.childNodes:
            if ((   # Child is a block element 
                    (child.nodeType == child.ELEMENT_NODE) and (child.nodeName
                        in BLOCK_ELEMENTS)
                ) or (# Child is a text node that contains only whitespace
                    (child.nodeType == child.TEXT_NODE) and (not 
                        child.data.strip())
                )
            ):
                appendElements += [child]
            else: # We don't have all block elements -> we append the text 
                # wrapped in a <div>
                appendElements = [div]
                break
    else: # Malformed XML
        doc = minidom.Document()
        div = doc.appendChild(doc.createElement(DIV))
        div.appendChild(doc.createTextNode(xhtmlContent))
        appendElements = [div]
    for elem in appendElements:
        parentElem.appendChild(elem)
    # Destroy the temporary XML doc
    if doc:
        doc.unlink()
    

def xhtmlImport(context, element, keepList, errors, toolInfo=None):
    """
        @param element An XML element.
        @param keepList A list of the names of elements that should be kept.
        @param errors A string IO object where errors can be logged.
    """
    element = filterChildren(element, keepList)
    return contentsToUnicodeString(element)


def getBoolVal(parent, elemName):
    retVal = None
    
    elem = getFirstElementByTagNameFlat(parent, elemName)
    if elem:
        v = getText(elem).strip()
        if v == TRUE:
            retVal = True
        elif v == FALSE:
            retVal = False
    
    return retVal


def getStrVal(parent, elemName):
    retVal = None
    
    elem = getFirstElementByTagNameFlat(parent, elemName)
    if elem:
        v = getText(elem)
        if v:
            v = v.strip()
        if v:
            retVal = v
    
    return retVal


def importMCQuestion(abstractGroup,
                     choiceInteractionElement,
                     correctResponseValueList,
                     errors,
                     id=None, 
                     toolInfo=None):
    """Creates an ECQMCQuestion from a QTI <choiceInteraction> and
    imports it into `abstractGroup'.

        @param abstractGroup An instanc of
            ECQAbstractGroup, i.e. a ECQuiz or a
            ECQGroup. The <choiceInteraction> element will be imported
            into that container.
        @param choiceInteractionElement An XML <choiceInteraction> node.
        @param correctResponseValueList A list of identifiers of the answers
            that are correct. (This list is not contained in the
            <choiceInteraction> element but in the <assessmentItem> that
            contains it. That's why we have to get it as a parameter.)
        @param errors A string IO object where errors can be logged.
        @param toolInfo The program that has produced the XML code. It only matters
            if it is this product or not.

        @return A list of objects that have been added to the quiz.

        Side effects:
            If successful, the item will be imported in "abstractGroup".
    """
    addedObjects = []
    context = abstractGroup
    """ Expected children:
            <xsd:sequence>
                <xsd:group ref="prompt" minOccurs="0" maxOccurs="1"/>
                <xsd:element ref="simpleChoice" minOccurs="1" maxOccurs="unbounded"/>
            </xsd:sequence>

        processed:
            prompt
            simpleChoice

        Expected attributes:
            <xsd:attributeGroup name="choiceInteraction.AttrGroup">
                <xsd:attributeGroup ref="bodyElement.AttrGroup"/>
                <xsd:attribute name="responseIdentifier" type="identifier.Type" use="required"/>
                <xsd:attribute name="shuffle" type="boolean.Type" use="required"/>
                <xsd:attribute name="maxChoices" type="integer.Type" use="required"/>
            </xsd:attributeGroup>
    """
    if ((choiceInteractionElement.nodeType != choiceInteractionElement.ELEMENT_NODE) 
        or (choiceInteractionElement.localName != CHOICE_INTERACTION)):
        errors.write('\n' + context.translate(
            msgid   = 'no_choiceInteraction',
            domain  = I18N_DOMAIN,
            default = 'Expected a <%s> element. Got "%s".') 
            % (context.str(CHOICE_INTERACTION),
               context.str(choiceInteractionElement.toxml())))
        return addedObjects

    ## Create a new question ##
    
    # Handle Attributes
#     id = getAttribute(choiceInteractionElement, RESPONSE_IDENTIFIER, u'')
    if (not id) or (type(id) not in [str, unicode]):
        id = None
    if id and isIdUsed(context, id, errors):
        return addedObjects

    # Create the Question object
    typeName = ECQMCQuestion.portal_type
    id = stringToZopeId(context, typeName, id, errors)
    q = createObject(context, typeName, id=id)
    addedObjects += [q]

    # Import randomOrder
    choiceInteractionShuffle = getAttribute(choiceInteractionElement, 
        SHUFFLE, TRUE).strip()
    q.setRandomOrder(choiceInteractionShuffle.lower() == TRUE)

    # Import allowMultipleSelection
    choiceInteractionMaxChoices = getAttribute(choiceInteractionElement, 
        MAX_CHOICES, u'0').strip()
    try:
        choiceInteractionMaxChoices = int(choiceInteractionMaxChoices)
    except:
        choiceInteractionMaxChoices = 0
    q.setAllowMultipleSelection(choiceInteractionMaxChoices != 1)

    # (numberOfRandomAnswers is imported from the manifest via
    # `importFromOrganization')

    # Process 'prompt' elements
    promptList = choiceInteractionElement.getElementsByTagName(PROMPT)
    if len(promptList) > 1:
        errors.write('\n' + context.translate(
            msgid   = 'too_many_elements',
            domain  = I18N_DOMAIN,
            default = 'Expected at most one <%s> element. Skipping the following <%s> elements.') 
                % (context.str(PROMPT), context.str(PROMPT)))

    # Set the question text to the contents of <prompt> (if present).
    if (promptList):
        q.setQuestion(xhtmlImport(context,
                                  promptList[0],
                                  INLINE_ELEMENTS,
                                  errors, 
                                  toolInfo=toolInfo).strip())

    # Process 'simpleChoice' elements
    simpleChoiceList = choiceInteractionElement.getElementsByTagName(
                           SIMPLE_CHOICE)
    for simpleChoice in simpleChoiceList:
        """ Expected children:
                Text, inline and 'feedbackInline' elements

            Expected attributes:
                <xsd:attributeGroup ref="bodyElement.AttrGroup"/>
                <xsd:attribute name="identifier" type="identifier.Type" use="required"/>
                <xsd:attribute name="fixed" type="boolean.Type" use="optional"/>
        """
        simpleChoiceIdentifier = simpleChoice.getAttribute(IDENTIFIER).strip()
        if not isIdUsed(q, simpleChoiceIdentifier, errors):
            # Create a new answer
            typeName = ECQMCAnswer.portal_type
            id = stringToZopeId(q, typeName, simpleChoiceIdentifier, errors)
            a = createObject(q, typeName, id=id)
            
            if (simpleChoiceIdentifier):
                setTitle(a, simpleChoiceIdentifier)
            a.setCorrect(simpleChoiceIdentifier in correctResponseValueList)
            
            # Set the answer text to the contents of the
            # <simpleChoice> element.
            a.setAnswer(xhtmlImport(context, simpleChoice, 
                INLINE_ELEMENTS + BLOCK_ELEMENTS, errors, toolInfo=toolInfo).strip())
            # Process <feedbackInline> elements (--> comments)
            feedbackInlineList = \
                simpleChoice.getElementsByTagName(FEEDBACK_INLINE)
            comment = u''
            for feedbackInline in feedbackInlineList:
                if (feedbackInline.getAttribute(SHOW_HIDE).lower() == SHOW):
                    comment += xhtmlImport(context, feedbackInline, 
                        INLINE_ELEMENTS, errors, toolInfo=toolInfo).strip() + u'\n'
            # Process <feedbackBlock> elements (also --> comments)
            feedbackBlockList = \
                simpleChoice.getElementsByTagName(FEEDBACK_BLOCK)
            for feedbackBlock in feedbackBlockList:
                if (feedbackBlock.getAttribute(SHOW_HIDE).lower() == SHOW):
                    comment += xhtmlImport(context,
                                           feedbackBlock, 
                                           BLOCK_ELEMENTS,
                                           errors,
                                           toolInfo=toolInfo).strip()
                    comment += u'\n'
            # Set the comment to the contents of the <feedbackInline>
            # + <feedbackBlock> elements
            comment =comment.strip()
            if (comment):
                a.setComment(comment)
    return addedObjects

  
def importExtendedTextInteraction(abstractGroup, 
                                  extendedTextInteraction,
                                  errors,
                                  id=None, 
                                  toolInfo=None):
    """Creates a ECQExtendedTextQuestion from a QTI
    <extendedTextInteraction> and imports it into
    [abstractGroup].

    @param abstractGroup

        An instanc of ECQAbstractGroup, i.e. a
        ECQuiz or a ECQGroup.  The
        <choiceInteraction> element will be imported into that
        container.

    @param extendedTextInteraction

        An XML <extendedTextInteraction> node.

    @param errors

        A string IO object where errors can be logged.

    @param toolInfo

        The program that has produced the XML code. It only matters if
        it is this product or not.

    @return

        A list of objects that have been added to the quiz.

    Side effects:

        If successful, the item will be imported in
        [abstractGroup].
    """
    addedObjects = []
    context = abstractGroup

    ## Create a new question ##

    # Handle Attributes
#     id = getAttribute(extendedTextInteraction, RESPONSE_IDENTIFIER, u'')
    if ((not id) or (type(id) not in [str, unicode])):
        id = None
    if id and isIdUsed(context, id, errors):
        return addedObjects

    # Create a new Question object
    typeName = ECQExtendedTextQuestion.portal_type
    id = stringToZopeId(context, typeName, id, errors)
    q = createObject(context, typeName, id=id)
    addedObjects += [q]

    # Process 'prompt' elements
    promptList = extendedTextInteraction.getElementsByTagName(PROMPT)
    if len(promptList) > 1:
        errors.write('\n' + context.translate(
            msgid   = 'too_many_elements',
            domain  = I18N_DOMAIN,
            default = 'Expected at most one <%s> element. '
                      'Skipping the following <%s> elements.') 
                     % (context.str(PROMPT), context.str(PROMPT)))

    # Set the question text to the contents of <prompt> (if present).
    if promptList:
        q.setQuestion(xhtmlImport(context,
                                  promptList[0],
                                  INLINE_ELEMENTS,
                                  errors, 
                                  toolInfo=toolInfo).strip())

    # Set [answerTemplate]
    answerTemplate = extendedTextInteraction.getAttribute(PLACEHOLDER_TEXT)
    answerTemplate = answerTemplate.strip()
    if answerTemplate:
        q.setAnswerTemplate(answerTemplate)

    # Set [expectedLength]
    expectedLength = extendedTextInteraction.getAttribute(EXPECTED_LENGTH)
    try:
        expectedLength = int(expectedLength.strip())
    except:
        errors.write('\n' + context.translate(
            msgid   = 'invalid_expected_length',
            domain  = I18N_DOMAIN,
            default = 'The expected length "%s" is invalid.'
            ) % context.str(expectedLength))
        expectedLength = None
    if expectedLength is not None:
        q.setExpectedLength(expectedLength)
    
    return addedObjects


def importScaleQuestion(abstractGroup,
                        choiceInteractionElement,
                        mapping,
                        errors,
                        id=None, 
                        toolInfo=None):
    """Creates an ECQScaleQuestion from a QTI <choiceInteraction> and
    imports it into `abstractGroup'.

        @param abstractGroup An instanc of
            ECQAbstractGroup, i.e. a ECQuiz or a
            ECQGroup. The <choiceInteraction> element will be imported
            into that container.
        @param choiceInteractionElement An XML <choiceInteraction> node.
        @param mapping A dictionary that maps an answer's identifier to a score.
        @param errors A string IO object where errors can be logged.
        @param toolInfo The program that has produced the XML code. It only matters
            if it is this product or not.

        @return A list of objects that have been added to the quiz.

        Side effects:
            If successful, the item will be imported in "abstractGroup".
    """
    addedObjects = []
    context = abstractGroup
    """ Expected children:
            <xsd:sequence>
                <xsd:group ref="prompt" minOccurs="0" maxOccurs="1"/>
                <xsd:element ref="simpleChoice" minOccurs="1" maxOccurs="unbounded"/>
            </xsd:sequence>

        processed:
            prompt
            simpleChoice

        Expected attributes:
            <xsd:attributeGroup name="choiceInteraction.AttrGroup">
                <xsd:attributeGroup ref="bodyElement.AttrGroup"/>
                <xsd:attribute name="responseIdentifier" type="identifier.Type" use="required"/>
                <xsd:attribute name="shuffle" type="boolean.Type" use="required"/>
                <xsd:attribute name="maxChoices" type="integer.Type" use="required"/>
            </xsd:attributeGroup>
    """
    if ((choiceInteractionElement.nodeType != choiceInteractionElement.ELEMENT_NODE) 
        or (choiceInteractionElement.localName != CHOICE_INTERACTION)):
        errors.write('\n' + context.translate(
            msgid   = 'no_choiceInteraction',
            domain  = I18N_DOMAIN,
            default = 'Expected a <%s> element. Got "%s".') 
            % (context.str(CHOICE_INTERACTION),
               context.str(choiceInteractionElement.toxml())))
        return addedObjects

    ## Create a new question ##
    
    # Handle Attributes
    if (not id) or (type(id) not in [str, unicode]):
        id = None
    if id and isIdUsed(context, id, errors):
        return addedObjects

    # Create the Question object
    typeName = ECQScaleQuestion.portal_type
    id = stringToZopeId(context, typeName, id, errors)
    q = createObject(context, typeName, id=id)
    addedObjects += [q]

    # Import randomOrder
    choiceInteractionShuffle = getAttribute(choiceInteractionElement, 
        SHUFFLE, TRUE).strip()
    q.setRandomOrder(choiceInteractionShuffle.lower() == TRUE)

    # (numberOfRandomAnswers is imported from the manifest via
    # `importFromOrganization')
    
    # Process 'prompt' elements
    promptList = choiceInteractionElement.getElementsByTagName(PROMPT)
    if len(promptList) > 1:
        errors.write('\n' + context.translate(
            msgid   = 'too_many_elements',
            domain  = I18N_DOMAIN,
            default = 'Expected at most one <%s> element. Skipping the following <%s> elements.') 
                % (context.str(PROMPT), context.str(PROMPT)))

    # Set the question text to the contents of <prompt> (if present).
    if promptList:
        q.setQuestion(xhtmlImport(context,
                                  promptList[0],
                                  INLINE_ELEMENTS,
                                  errors, 
                                  toolInfo=toolInfo).strip())

    # Process 'simpleChoice' elements
    simpleChoiceList = choiceInteractionElement.getElementsByTagName(
                           SIMPLE_CHOICE)
    for simpleChoice in simpleChoiceList:
        """ Expected children:
                Text, inline and 'feedbackInline' elements

            Expected attributes:
                <xsd:attributeGroup ref="bodyElement.AttrGroup"/>
                <xsd:attribute name="identifier" type="identifier.Type" use="required"/>
                <xsd:attribute name="fixed" type="boolean.Type" use="optional"/>
        """
        simpleChoiceIdentifier = simpleChoice.getAttribute(IDENTIFIER).strip()
        if not isIdUsed(q, simpleChoiceIdentifier, errors):
            # Create a new answer
            typeName = ECQScaleAnswer.portal_type
            id = stringToZopeId(q, typeName, simpleChoiceIdentifier, errors)
            a = createObject(q, typeName, id=id)

            # Set title and score
            if simpleChoiceIdentifier:
                setTitle(a, simpleChoiceIdentifier)
                a.setScore(mapping[simpleChoiceIdentifier])
            
            # Set the answer text to the contents of the
            # <simpleChoice> element.
            a.setAnswer(xhtmlImport(context, simpleChoice, 
                INLINE_ELEMENTS + BLOCK_ELEMENTS, errors, toolInfo=toolInfo).strip())
            
            # Set the comment (extracted from <feedbackInline> and
            # <feedbackBlock> elements)
            feedbackInlineList = \
                simpleChoice.getElementsByTagName(FEEDBACK_INLINE)
            comment = u''
            for feedbackInline in feedbackInlineList:
                if feedbackInline.getAttribute(SHOW_HIDE).lower() == SHOW:
                    comment += xhtmlImport(context, feedbackInline, 
                        INLINE_ELEMENTS, errors, toolInfo=toolInfo).strip() + u'\n'
            # Process <feedbackBlock> elements (also --> comments)
            feedbackBlockList = \
                simpleChoice.getElementsByTagName(FEEDBACK_BLOCK)
            for feedbackBlock in feedbackBlockList:
                if (feedbackBlock.getAttribute(SHOW_HIDE).lower() == SHOW):
                    comment += xhtmlImport(context,
                                           feedbackBlock, 
                                           BLOCK_ELEMENTS,
                                           errors,
                                           toolInfo=toolInfo).strip()
                    comment += u'\n'
            # Set the comment to the contents of the <feedbackInline>
            # + <feedbackBlock> elements
            comment =comment.strip()
            if comment:
                a.setComment(comment)
    return addedObjects


def importChoiceInteraction(context, 
                            choiceInteraction,
                            errors,
                            id=None,
                            toolInfo=None):
    itemBody = choiceInteraction.parentNode
    asmtItem = itemBody.parentNode
    
    correctResponses = []
    mapping = {}
    
    respDecls = asmtItem.getElementsByTagName(RESPONSE_DECLARATION)
    for respDecl in respDecls:
        """ Expected children of <responseDeclaration>:
        <xsd:group ref="variableDeclaration.ContentGroup"/>
        <xsd:element ref="correctResponse" minOccurs="0" maxOccurs="1"/>
        <xsd:element ref="mapping" minOccurs="0" maxOccurs="1"/>
        <xsd:element ref="areaMapping" minOccurs="0" maxOccurs="1"/>
        
        processed:
        correctResponse
        mapping
        """
        valueList = getElementsByPath(respDecl, u'correctResponse/value')
        for value in valueList:
            """Expecting Text"""
            correctResponses.append(getText(value, u'').strip())
        
        mapEntries = getElementsByPath(respDecl, u'mapping/mapEntry')
        for m in mapEntries:
            try:
                k = m.getAttribute(MAP_KEY)
                v = m.getAttribute(MAPPED_VALUE)
                mapping[k.strip()] = float(v)
            except:
                pass

    if correctResponses:
        return importMCQuestion(
            context, 
            choiceInteraction,
            correctResponses, 
            errors,
            id=id,
            toolInfo=toolInfo)
    else:
        return importScaleQuestion(
            context,
            choiceInteraction,
            mapping,
            errors,
            id=id,
            toolInfo=toolInfo)


def importAssessmentItem(abstractGroup, string, errors, id=None, 
    importMode=DEFAULT, toolInfo=None):
    """Import a QTI <assessmentItem> into [abstractGroup].

    If there is more than one <choiceInteraction> element, a
    ECQGroup will be created which will contain an 'MC Question'
    for each <choiceInteraction> element. Otherwise the
    <assessmentItem> will be imported as a single MC Question.

    @param abstractGroup

        An instanc of ECQAbstractGroup, i.e. a
        ECQuiz or a ECQGroup.  The <assessmentItem>
        will be imported into that container.

    @param string

        A string containing the XML representation of the
        <assessmentItem>.

    @param errors

        A string IO object where errors can be logged.

    @return

        A list of objects that have been added to the quiz.

    Side effects:

        If successful, the item will be imported in
        [abstractGroup].
    """
    addedObjects = []
    context = abstractGroup

    if ((not id) or (type(id) not in [str, unicode])):
        id = None
    if id and isIdUsed(context, id, errors):
        return addedObjects

    if type(string) not in [str, unicode]:
        # The file could not be read.
        errors.write('\n' + context.translate(
            msgid   = 'expected_string', 
            domain  = I18N_DOMAIN, 
            default = 'Input must be str or unicode, not %s.') 
            % context.str(type(string)))
        return addedObjects

    try:
        if isinstance(string, unicode):
            string = string.encode(u'utf-8')
        doc = parseString(string)
    except Exception, e:
        errors.write('\n' + context.translate(
            msgid   = 'parse_error',
            domain  = I18N_DOMAIN,
            default = 'A parse error occurred in "%s": %s') 
            % (context.str(string), context.str(e)))
        return addedObjects

    try:
        if (doc.documentElement.localName == ASSESSMENT_ITEM):
            assessmentItem = doc.documentElement
        else:
            errors.write('\n' + (context.translate(
                msgid   = 'no_qti',
                domain  = I18N_DOMAIN,
                default = 'Invalid QTI document. The name of the root element has to '
                    'be "%s", not "%s".') % (ASSESSMENT_ITEM, doc.documentElement.localName)))
            doc.unlink()
            return addedObjects

        """ Expected children of <assessmentItem>
                <xsd:element ref="responseDeclaration" minOccurs="0" maxOccurs="unbounded"/>
                <xsd:element ref="outcomeDeclaration" minOccurs="0" maxOccurs="unbounded"/>
                <xsd:element ref="templateDeclaration" minOccurs="0" maxOccurs="unbounded"/>
                <xsd:element ref="templateProcessing" minOccurs="0" maxOccurs="1"/>
                <xsd:element ref="stylesheet" minOccurs="0" maxOccurs="unbounded"/>
                <xsd:element ref="itemBody" minOccurs="0" maxOccurs="1"/>
                <xsd:element ref="responseProcessing" minOccurs="0" maxOccurs="1"/>
                <xsd:element ref="modalFeedback" minOccurs="0" maxOccurs="unbounded"/>

            processed:
                responseDeclaration
                itemBody
        """

        # Which function does the <assessmentItem> 'identifier' attribute have?
        
        # assessmentItemIdentifier =
        # assessmentItem.getAttribute('identifier').strip()
        
        assessmentItemTitle = getAttribute(assessmentItem, TITLE)
        # Should be either 'single' or 'multiple'
        # assessmentItemTitleCardinality =
        # getAttribute(assessmentItem, u'cardinality')

        itemBodyList = assessmentItem.getElementsByTagName(ITEM_BODY)
        if (len(itemBodyList) != 1):
            errors.write('\n' + context.translate(
                msgid   = 'no_item_body',
                domain  = I18N_DOMAIN,
                default = 'Expected exactly one <%s> element.')
                         % context.str(ITEM_BODY))
            doc.unlink()
            return addedObjects

        itemBody = itemBodyList[0]
        # The text and HTML contents of the <itemBody> become the
        # 'Directions' of the question group or part of the question
        # text if we have only one <???Interaction> child.
        directions = xhtmlImport(context, itemBody, BLOCK_ELEMENTS, errors, 
                                 toolInfo=toolInfo).strip()
        if importMode in [FORCE_TEST, FORCE_GROUP]:
            if importMode == FORCE_TEST:
                # "context" should be a ECQuiz instance.
                # We don't have to create anything.
                containerObj = context
            else: # importMode == FORCE_GROUP
                # "context" should be a ECQuiz instance and we
                # have to create a new ECQGroup.
                typeName = ECQGroup.portal_type
                id = stringToZopeId(context, typeName, id, errors)
                qGroup = createObject(context, typeName, id=id)
                addedObjects += [qGroup]
                containerObj = qGroup
            if (assessmentItemTitle):
                setTitle(containerObj, assessmentItemTitle)
            containerObj.setDirections(directions)
        else: # (importMode in [DEFAULT, FORCE_QUESTION])

            # Each choiceInteraction element will become an `MC
            # Question' or a `Scale Question'
            choiceInteractionList = \
                itemBody.getElementsByTagName(CHOICE_INTERACTION)
            extendedTextInteractionList = \
                itemBody.getElementsByTagName(EXTENDED_TEXT_INTERACTION)
            if ((not choiceInteractionList) and
                (not extendedTextInteractionList)):

                types = ["<%s>" % context.str(t)
                         for t in SUPPORTED_INTERACTION_TYPES]
                types = ', '.join(types)
                errors.write('\n' + context.translate(
                    msgid   = 'no_interaction',
                    domain  = I18N_DOMAIN,
                    default = 'Did not find any elements of type %s.')
                             % types)
                doc.unlink()
                return addedObjects

            # OK, we got some <???Interaction> elements.  If we have
            # more than one, we create a new ECQGroup.  Otherwise
            # we import it as a single Question.
            if (len(choiceInteractionList) +
                len(extendedTextInteractionList)
                > 1):
                # More than one <???Interaction> element
                typeName = ECQGroup.portal_type
                id = stringToZopeId(context, typeName, id, errors)
                qGroup = createObject(context, typeName, id=id)
                addedObjects += [qGroup]
                if (assessmentItemTitle):
                    setTitle(qGroup, assessmentItemTitle)
                qGroup.setDirections(directions)
                for choiceInteraction in choiceInteractionList:
                    addedObjects += importMCQuestion(
                                        qGroup, 
                                        choiceInteraction,
                                        correctResponseValueList,
                                        errors,
                                        id=id,
                                        toolInfo=toolInfo)
                
                for extendedTextInteraction in extendedTextInteractionList:
                    addedObjects += importExtendedTextInteraction(
                                        qGroup,
                                        extendedTextInteraction,
                                        errors,
                                        id=id,
                                        toolInfo=toolInfo)
            else:
                # One <???Interaction> element --> Import it directly
                # into the quiz
                if choiceInteractionList:
                    newQuestionList = importChoiceInteraction(
                                          context,
                                          choiceInteractionList[0],
                                          errors,
                                          id=id,
                                          toolInfo=toolInfo)
                elif extendedTextInteractionList:
                    newQuestionList = importExtendedTextInteraction(
                                          context, 
                                          extendedTextInteractionList[0], 
                                          errors,
                                          id=id,
                                          toolInfo=toolInfo)
                else:
                    newQuestionList = []
                
                # Test if anything could be imported.
                if newQuestionList:
                    addedObjects += newQuestionList
                    # At this point, we know the list contains exactly
                    # one question.
                    newQuestion = newQuestionList[0]
                    # There was only one question, so the title of the
                    # <???Item> is the title of the question.
                    if assessmentItemTitle:
                        setTitle(newQuestion, assessmentItemTitle)
                    if directions:
                        # Archetypes' TextField accessor always returns a
                        # "coded" string (*not* a Unicode string), cf.
                        # Archetypes/Field.py. Therefore we must convert
                        # it to a Unicode string.
                        questionText = unicode(newQuestion.getQuestion(
                            encoding=u'utf-8'), u'utf-8')
                        # Add the HTML contents of the <itemBody> to
                        # the question text
                        newQuestion.setQuestion(directions
                                                + u' '
                                                + questionText)
    except Exception, e:
        errors.write('\n' +
                     context.translate(
                         msgid   = 'unexpected_error',
                         domain  = I18N_DOMAIN,
                         default = 'An unexpected error has occurred '
                                   'in "%s": %s')
                     % (context.str('importAssessmentItem()'), context.str(e)))
        doc.unlink()
        return addedObjects

    doc.unlink()
    return addedObjects # (Success)


def importPackage(multipleChoiceTest, zipFileObject, errors):
    """Import a QTI package that is contained in a Python ZipFile
    object into 'multipleChoiceTest'.

    @param multipleChoiceTest

        The ECQuiz that the package is to be imported in.

    @param zipFileObject

        A Python ZipFile object that contains a QTI package.

    @param errors

        A string IO object where errors can be logged.

    @return

        A list of objects that have been added to the quiz.

    Side effects:

        If successful, the package will be imported in
        'multipleChoiceTest'.
    """
    addedObjects = []
    context = multipleChoiceTest
    try:
        ### Read & parse the manifest file ###
        try:
            fileNameList = [context.unicodeDecode(f.filename)
                            for f in zipFileObject.filelist]
        except:
            errors.write('\n' + context.translate(
                msgid   = 'expected_zip', 
                domain  = I18N_DOMAIN, 
                default = 'Input must be ZipFile, not %s.') 
                % context.str(type(zipFileObject)))
            return addedObjects
        # Find the manifest file

        manifestFnList = [fn for fn in fileNameList
                          if fn.lower() == MANIFEST_FILE_NAME]
        if not manifestFnList: # No manifest
            errors.write('\n' + (context.translate(
                msgid   = 'no_manifest', 
                domain  = I18N_DOMAIN, 
                default = 'The package must contain a manifest file '
                          'called "%s".') 
                % context.str(MANIFEST_FILE_NAME)))
            return addedObjects
        elif len(manifestFnList) > 1: # More than one manifest
            errors.write('\n' + (context.translate(
                msgid   = 'multiple_manifest', 
                domain  = I18N_DOMAIN, 
                default = 'The package contains more than one file '
                          'called "%s".') 
                % context.str(MANIFEST_FILE_NAME)))
            return addedObjects

        # Extract the manifest from the zip
        
        # If reading fails, "readFromZip" will report that in "errors"
        manifestContents = readFromZip(context,
                                       zipFileObject,
                                       manifestFnList[0],
                                       errors)
        if manifestContents is None: # 'readFromZip()' failed
            return addedObjects

        # Create the xml document object
        try:
            if isinstance(manifestContents, unicode):
                manifestContents = manifestContents.encode(u'utf-8')
            manifestDo = parseString(manifestContents)
        except Exception, e:
            errors.write('\n' + context.translate(
                msgid   = 'parse_error', 
                domain  = I18N_DOMAIN, 
                default = 'A parse error occurred in "%s": %s') 
                % (context.str(MANIFEST_FILE_NAME), context.str(e)))            
            return addedObjects

        manifest = manifestDo.documentElement

        ### Parse some information in the manifest ###
        # Extract the title of the quiz
        testTile = getFirstElementByPath(manifest, METADATA + u'/' + LOM 
            + u'/' + GENERAL + u'/' + TITLE + u'/' + LANG_STRING)
        if (testTile):
            setTitle(context, getText(testTile, u'').strip())

        # Get the <resource> elements
        resourceList = manifest.getElementsByTagName(RESOURCE)

        ### Check whether this package has been createcd by this
        ### product ###
        isLlsMCPackage = False
        qtiMetadata = getFirstElementByPath(manifest,
                                            METADATA + u'/' + QTI_METADATA)
        if qtiMetadata:
            expectedValueList = [(TOOL_NAME, FIXME_PROJECTNAME), 
                (TOOL_VERSION, MC_TOOL_VERSION), (TOOL_VENDOR, MC_TOOL_VENDOR)]
            valuesVerified = True
            # Check if <toolName>, <toolVersion>, <toolVendor> match
            for elementName, expectedValue in expectedValueList:
                element = getFirstElementByTagNameFlat(qtiMetadata, elementName)
                if not element:
                    #log("1: no element: %s\n" % elementName)
                    valuesVerified = False
                    break
                else:
                    elementText = getText(element, u'').strip()
                    if elementText != expectedValue.strip():
#                         log("2: expected:%s\n        got:%s\n"
#                             % (expectedValue.strip(),
#                                context.str(elementText)))
                        valuesVerified = False
                        break
            if valuesVerified:
                # Get the <organization>
                organization = getFirstElementByPath(manifest, ORGANIZATIONS + 
                    u'/' + ORGANIZATION)
                if organization:
                    if getElementsByTagNameFlat(organization, ITEM):
                        # We also got an <organization> element and it has
                        # an <item> child. This must be one of our packages.
                        isLlsMCPackage = True
                    else:
                        #log("3: no element: %s\n" % ITEM)
                        None
                else:
                    #log("4: no organization\n")
                    None

        ### Import the <resource> elements accordingly ###
        if isLlsMCPackage:
            toolInfo = {
                TOOL_NAME    : FIXME_PROJECTNAME, 
                TOOL_VERSION : getText(getFirstElementByTagNameFlat(
                                           qtiMetadata, 
                                           TOOL_VERSION)).strip(), 
                TOOL_VENDOR  : getText(getFirstElementByTagNameFlat(
                                           qtiMetadata, 
                                           TOOL_VENDOR)).strip(),
                }
            addedObjects += importFromOrganization(multipleChoiceTest,
                                                   zipFileObject, 
                                                   organization,
                                                   resourceList,
                                                   toolInfo,
                                                   errors)
        else:
            # Iterate over the <resource> elements and try to import
            # everything as best we can.
            for resource in resourceList:
                addedObjects += importResource(multipleChoiceTest,
                                               zipFileObject, 
                                               resource,
                                               errors)
                    
        manifestDo.unlink()
        return addedObjects
    except Exception, e:
        errors.write('\n' + context.translate(
                                msgid   = 'unexpected_error',
                                domain  = I18N_DOMAIN,
                                default = 'An unexpected error has '
                                          'occurred in "%s": %s'
                            )
                     % (context.str('importPackage()'), context.str(e)))
        manifestDo.unlink()
        return addedObjects


def importBool(elemName, setter, parent):
    val = getBoolVal(parent, elemName)
    if val is not None:
        setter(val)

def importStr(elemName, setter, parent):
    val = getStrVal(parent, elemName)
    if val is not None:
        setter(val)

def importSelectCount(obj, organizationItem, errors):
    randomizationControls = getFirstElementByPath(
        organizationItem, SEQUENCING + u'/' + RANDOMIZATION_CONTROLS)
    if not randomizationControls:
        return
    
    selCnt = getAttribute(randomizationControls, SELECT_COUNT, None)
    if selCnt is not None:
        selCnt = selCnt.strip()
        try:
            selCnt = int(selCnt)
            # selectCount is specified to be non-negative
            if selCnt < 0:
                raise ValueError('expected non-negative integer, got %d'
                                 % selCnt)
        except:
            errors.write('\n' + obj.translate(
                msgid   = 'invalid_select_count',
                domain  = I18N_DOMAIN,
                default = 'The select count "%s" is invalid.'
                ) % obj.str(selCnt))
            selCnt = None

        if selCnt is not None:
            for name in ('setNumberOfRandomQuestions',
                         'setNumberOfRandomAnswers',):
                if shasattr(obj, name):
                    setter = getattr(obj, name)
                    setter(selCnt)
                    break

def importReorderChildren(obj, organizationItem, errors):
    randomizationControls = getFirstElementByPath(
        organizationItem, SEQUENCING + u'/' + RANDOMIZATION_CONTROLS)
    if not randomizationControls:
        return
    
    reorderChildren = getAttribute(randomizationControls, 
        REORDER_CHILDREN, TRUE).strip()
    obj.setRandomOrder(reorderChildren.lower() == TRUE)

def importFromOrganization(multipleChoiceTest, zipFileObject, organization, 
                           resourceList, toolInfo, errors):
    """
    """
    addedObjects = []
    context = multipleChoiceTest
    # Import resources according to the info in <organizations>
    mcTestItem = getFirstElementByTagNameFlat(organization, ITEM)
    if mcTestItem:
        mcTestChildren = getElementsByTagNameFlat(mcTestItem, ITEM)
        qGroupItemList = [item for item in mcTestChildren
                          if getElementsByTagNameFlat(item, ITEM)]
        for containerItem in [mcTestItem] + qGroupItemList:
            # Get the <resource> that this <item> refers to via its
            # 'identifierref' attribute.
            containerResource = findResource(
                context, containerItem, resourceList, errors)
            if containerResource:
                # Set [containerImportMode] and [qItemList]
                if containerItem is mcTestItem:
                    qItemList = [item for item in mcTestChildren
                                 if item not in qGroupItemList]
                    containerImportMode = FORCE_TEST
                else:
                    qItemList = getElementsByTagNameFlat(containerItem, ITEM)
                    containerImportMode = FORCE_GROUP
                
                # Import the <resource> for the ECQuiz/ECQGroup
                importedObjects = importResource(
                                      multipleChoiceTest, 
                                      zipFileObject,
                                      containerResource,
                                      errors, 
                                      importMode=containerImportMode,
                                      toolInfo=toolInfo)
                addedObjects += importedObjects
    
                # Get "containerObj", the object that has been created from
                # "containerResource"
                if containerItem is mcTestItem:
                    containerObj = multipleChoiceTest
                else:
                    importedGroups = \
                        [o for o in importedObjects
                         if o.portal_type == ECQGroup.portal_type]
                    if importedGroups:
                        containerObj = importedGroups[0]
                    else:
                        # Nothing has been created. Maybe it's because
                        # a ECQGroup with that id already
                        # existed.
                        containerResourceId = containerResource.getAttribute(
                            IDENTIFIER)
                        # First: Get the children with the same id as the
                        # <resource> element
                        childrenWithResourceId = getChildrenWithId(
                            multipleChoiceTest, containerResourceId)
                        # Second: Keep only those that are ECQGroups
                        questionGroupsWithResourceId = \
                            [o for o in childrenWithResourceId 
                             if o.portal_type == ECQGroup.portal_type]
                        # Third: If the list is not empty, take the first
                        # element of the list.
                        if questionGroupsWithResourceId:
                            containerObj = questionGroupsWithResourceId[0]
                        else:
                            # No resource with that name existed. I'm giving
                            # up.
                            containerObj = None
                if containerObj:
                    # import [numberOfRandomQuestions]
                    importSelectCount(containerObj, containerItem, errors)

                    # import [isRandomOrder] Note:
                    # "randomizationControls" for questions is not
                    # imported because this information is also stored
                    # in the "suffle" attribute of the
                    # "<choiceInteraction>" element of the
                    # "<assessmentItem>".
                    importReorderChildren(containerObj, containerItem, errors)
                    
                    # Import all the <resource>s referenced by the
                    # <item>s that are children of "containerItem".
                    for qItem in qItemList:
                        # Get the referenced <resource>.
                        questionResource = findResource(context, 
                            qItem, resourceList, errors)
                        if questionResource:
                            # Import it as a question.
                            importedObjects = importResource(containerObj, 
                                zipFileObject, questionResource, errors, 
                                importMode=FORCE_QUESTION, toolInfo=toolInfo)
                            qObject = importedObjects and importedObjects[0]

                            if qObject:
                                # import [numberOfRandomAnswers]
                                importSelectCount(qObject, qItem, errors)

                                # import the points (if present)
                                if shasattr(qObject, 'points'):
                                    weight = getFirstElementByTagNameFlat(
                                        qItem, NS_LLSMC + u':' + WEIGHT)
                                    points = None
                                    if weight:
                                        weight = getText(weight).strip()
                                        try:
                                            points = int(weight)
                                        except:
                                            errors.write('\n' + context.translate(
                                                msgid   = 'invalid_weight',
                                                domain  = I18N_DOMAIN,
                                                default = 'The weight "%s" is invalid.'
                                                ) % context.str(weight))
                                    if points is not None:
                                        qObject.setPoints(points)

                                # import [tutorGraded]
                                if shasattr(qObject, 'tutorGraded'):
                                    importBool(TUTOR_GRADED, qObject.setTutorGraded,
                                              qItem)

                                # import [choiceLayout]
                                if shasattr(qObject, 'choiceLayout'):
                                    importStr(LAYOUT, qObject.setChoiceLayout,
                                              qItem)
                            
                            # append the new objects to 'addedObjects'
                            addedObjects += importedObjects
                            
        mcTestSequencing = getFirstElementByTagNameFlat(organization,
            SEQUENCING)
        if mcTestSequencing:
            # Import [allowRepetition]
            #
            # <imsss:limitConditions attemptLimit="1"/>
            mcTestLimitConditions = getFirstElementByTagNameFlat(
                mcTestSequencing, LIMIT_CONDITIONS)
            if mcTestLimitConditions:
                attemptLimit = mcTestLimitConditions.getAttribute(
                    ATTEMPT_LIMIT).strip()
                try:
                    attemptLimit = int(attemptLimit)
                except:
                    attemptLimit = None
                if attemptLimit is not None:
                    multipleChoiceTest.setAllowRepetition(attemptLimit < 1)
            
            # import [instantFeedback]
            #
            # <llsmc:instantFeedback>true</llsmc:instantFeedback>
            importBool(INSTANT_FEEDBACK, multipleChoiceTest.setInstantFeedback,
                       mcTestSequencing)
            
            # import [onePerPage]
            #
            # <llsmc:oneQuestionPerPage>true</llsmc:oneQuestionPerPage>
            importBool(ONE_QUESTION_PER_PAGE, multipleChoiceTest.setOnePerPage,
                       mcTestSequencing)
            
            # import [onePerPageNav]
            #
            # <llsmc:oneQuestionPerPage>true</llsmc:oneQuestionPerPage>
            importBool(ALLOW_NAVIGATION, multipleChoiceTest.setOnePerPageNav,
                       mcTestSequencing)
            
        # import [scoringFunction]
        #
        # <llsmc:scoringFunction>guessing</llsmc:scoringFunction>
        importStr(SCORING_FUNCTION, multipleChoiceTest.setScoringFunction,
                  organization)

        # <llsmc:gradingScale>
        importGradingScale(multipleChoiceTest, organization, errors)
    else:
        #FIXME: write some error message to the log
        pass
    return addedObjects


def importGradingScale(mcTest, organization, errors):
    """Import the grading scale from an <organization> element.
    """
    context = mcTest
    
    scaleElem = getFirstElementByTagNameFlat(organization, GRADING_SCALE)
    if not scaleElem:
        return
    
    scale = []
    rows = getElementsByTagNameFlat(scaleElem, GRADING_SCALE_ROW)
    for row in rows:
        lastRow = row is rows[-1]
        grade = getStrVal(row, GRADE)
        score = getStrVal(row, MIN_SCORE) or ''

        # Check if input is valid
        if grade is None:
            msg = instance.translate(
                msgid   = 'error_empty',
                domain  = I18N_DOMAIN,
                default = 'The <%s> element must not be empty. Skipping '
                'invalid <%s> element.',) % (GRADE, GRADING_SCALE_ROW)
            errors.write('\n' + msg)
            continue
        else:
            grade = context.str(grade)

        if score and lastRow:
            msg = context.translate(
                msgid   = 'minimum_score_not_empty_qti',
                domain  = I18N_DOMAIN,
                default = 'The minimum score column of the last row of '
                'the <%s> element must be empty. Ignoring last score.') \
                % GRADING_SCALE
            errors.write('\n' + msg)
            score = ''

        if not lastRow:
            score = context.str(score)
            if score.endswith('%'):
                testScore = score[:-1].strip()
            else:
                testScore = score
            try:
                testScore = float(testScore)
            except ValueError:
                msg = context.translate(
                    msgid   = 'invalid_minimum_score_qti',
                    domain  = I18N_DOMAIN,
                    default = 'Not a percentage or an absolute value: %s. '
                    'Skipping invalid <%s> element.',) \
                    % (score, GRADING_SCALE_ROW)
                errors.write('\n' + msg)
                continue
            
        # Input is valid
        scale.append({'grade' : grade,
                      'score' : score,
                      })

    mcTest.getField('gradingScale').set(mcTest, scale)


def findResource(context, organizationItem, resourceList, errors):
    identifierref = organizationItem.getAttribute(IDENTIFIER_REF)
    if (not identifierref):
        return None
    matches = [res for res in resourceList 
        if res.getAttribute(IDENTIFIER) == identifierref]
    if (not matches):
        errors.write('\n' + context.translate(
                        msgid   = 'unresolved_reference',
                        domain  = I18N_DOMAIN,
                        default = 'There is no resource with the identifier "%s".'
                            'The item cannot be imported.'
                    ) % context.str(identifierref))
        return None
    if (len(matches) > 1):
        errors.write('\n' + context.translate(
                        msgid   = 'ambiguous_reference',
                        domain  = I18N_DOMAIN,
                        default = 'There is more than one resource with '
                            'the identifier "%s". Only the first one will '
                            'be imported.'
                    ) % context.str(identifierref))
    return matches[0]


def importResource(context, zipFileObject, resource, errors, 
    importMode=DEFAULT, toolInfo=None):
    addedObjects = []

    resourceIdentifier = resource.getAttribute(IDENTIFIER).strip() or None
    resourceType = resource.getAttribute(TYPE)
    # Decide what to do with this kind of ressource
    if resourceType != IMSQTI_ITEM_XMLV2P0:
        # We don't know how to handle this kind of resource
        errors.write('\n' + context.translate(
            msgid   = 'unsupported_resource_type', 
            domain  = I18N_DOMAIN, 
            default = 'Unsupported resource type "%s". Skipping resource "%s".') 
            % (context.str(resourceType), context.str(resourceIdentifier)))
        return addedObjects

    # We can handle this kind of resource
    resourceFileName = resource.getAttribute(HREF)
    # Extract the title of the resource
    resourceTitleElem = getFirstElementByPath(resource, METADATA 
        + u'/' + LOM + u'/' + GENERAL + u'/' + TITLE + u'/' + LANG_STRING)
    if resourceTitleElem:
        resourceTitle = getText(resourceTitleElem).strip()
    else:
        resourceTitle = context.translate(
            msgid   = 'untitled_resource',
            domain  = I18N_DOMAIN,
            default = 'Untitled resource')

    if importMode in [DEFAULT, FORCE_QUESTION]:
        # In this case, import the resource as a question
        # Try to gather the 'interaction type' of the item
        interactionType = getFirstElementByPath(resource, METADATA
            + u'/' + QTI_METADATA + u'/' + INTERACTION_TYPE)
        if interactionType:
            interactionType = getText(interactionType, u'').strip()
            if interactionType not in SUPPORTED_INTERACTION_TYPES:
                # unsupported interaction type
                errors.write('\n' + (context.translate(
                    msgid   = 'unsupported_interaction_type',
                    domain  = I18N_DOMAIN,
                    default = 'Unsupported interaction type "%s". '
                              'Skipping item "%s (%s)".')
                    % (context.str(interactionType),
                       context.str(resourceTitle),
                       context.str(resourceFileName))))
                return addedObjects
        else: # Resource has no 'interaction type'
            errors.write('\n' + (context.translate(
                msgid   = 'no_interaction_type',
                domain  = I18N_DOMAIN,
                default = 'Resource specifies no interaction type. '
                          'Skipping item "%s (%s)".')
                % (context.str(resourceTitle), context.str(resourceFileName))))
            return addedObjects

    # Read the actual resource (a QTI assessmentItem) from the zip file
    # If reading fails, "readFromZip" will report that in "errors"
    resourceContents = readFromZip(context, zipFileObject, resourceFileName,
                                   errors)
    if resourceContents is not None: # The resource could be extracted
        # Import the assessmentItem
        addedObjects += importAssessmentItem(context, 
            resourceContents, errors, id=resourceIdentifier, 
            importMode=importMode, toolInfo=toolInfo)
        # Find and import referenced files
        fileList = resource.getElementsByTagName(FILE)
        for file in fileList:
            # The file name is specified in the 'href' attribute
            fileName = file.getAttribute(HREF)
            # Apparently, the resource itself is also specified in the list of
            # referenced files.
            # In that case do nothing. We've already handeled it above.
            if (fileName != resourceFileName):
                addedObjects += importFileResource(context, 
                    zipFileObject, fileName, resourceFileName, errors)

    return addedObjects


def importFileResource(multipleChoiceTest, zipFileObject, fileName, 
    assessmentItemFileName, errors):
    """ Import referenced files from a QTI package that is contained in a
        Python ZipFile object into 'multipleChoiceTest'.

        @param multipleChoiceTest The ecquiz that the file is to be
        imported in.
        
        @param zipFileObject Python ZipFile object that contains a QTI
        package.

        @param fileName The name of the file that you want to import.

        @param assessmentItemFileName The file name of the
        assessmentItem that references the file.

        @param errors A string IO object where errors can be logged.

        @return A list of objects that have been added to the test.

        Side effects:
        
            If successful, the file will be imported in
            'multipleChoiceTest'.  New folders may be generated. The
            file itself will be added as an Image or a File to
            'multipleChoiceTest'.
    """
    addedObjects = []
    context = multipleChoiceTest
    try:
        # Read the contents from the ZipFile
        # If reading fails, "readFromZip" will report that in "errors"
        contents = readFromZip(context, zipFileObject, fileName, errors)
        if (contents is None): # 'readFromZip()' failed
            return addedObjects
        try:
            # Create a StringIO object from the contents of the file
            fileStringIO = StringIO(contents)
        except Exception, e:
            errors.write('\n' + (context.translate(
                msgid   = 'read_error', 
                domain  = I18N_DOMAIN, 
                default = 'Cannot read the file "%s". An error occurred: %s') 
                    % (context.str(fileName), context.str(e))))
            return addedObjects
        try:
            """ We can't preserve the file stuctur of the package since e.g.
                an assesmentItem might be located in some folder but the question or
                question group that it is transformed into will become a child of the test.
                So we have to try to find out in which path to actually import the file.
                E.g. if the path of the assesmentItem is 'example' and
                and the path of the file is 'example/images', we want to
                import it in the folder 'images'.
            """
            filePath = fileName.split(u'/')[:-1]
            assessmentItemPath = assessmentItemFileName.split(u'/')[:-1]
            # The first path component (folder) where filePath and assessmentItemPath differ
            diffIndex = 0
            for i in range(min(len(filePath), len(assessmentItemPath))):
                if (filePath[i] == assessmentItemPath[i]):
                    diffIndex += 1
                else: # The paths are different
                    break
            # Keep only the relative path to the referencing assesmentItem
            filePath = filePath[diffIndex : ]
            # The container where the file will be put
            container = context
            for path in filePath:
                # Find out if we already have such a folder in the quiz
                existingFolders = [folder for folder in container.listFolderContents() 
                    if folder.getId() == path]
                if (existingFolders): # Yep, folder exists
                    folderObj = existingFolders[0]
                else: # No --> create the folder
                    newId = container.invokeFactory('Folder', id=path, title=path)
                    if ((newId is None) or (newId == '')):
                        newId = path
                    folderObj = getattr(container, newId, None)
                    if (folderObj):
                        addedObjects += [folderObj]
                if (not folderObj):
                    # Folder creation probably failed. Nothing we can do.
                    break
                # The new container will be the folder we found or just 
                # created
                container = folderObj

            # localName of 'example/images/test.png' will be 'test.png'
            localName = context.str(fileName.split('/')[-1])
            # Try to guess the MIME type of the file
            mimeType = guess_type(localName)[0]
            # type/subtype of the MIME type
            type = ''
            subtype = ''
            if (mimeType):
                [type, subtype] = mimeType.split('/')
            else:
                mimeType = ''
            # Use the Plone object type that best fits the MIME type
            # I.e. import images as 'Image'. Otherwise use 'File'
            typeName = ['File', 'Image'][type.lower() == 'image']
            # The id of the file has to be the file name so that references 
            # in the assesmentItem don't break.
            id = localName
            # Check if file already exists
            if ([obj for obj in container.listFolderContents() 
                if obj.getId() == id]):
                # id is in use --> Skip the file
                reducedFn = localName
                filePath.reverse()
                for path in filePath:
                    reducedFn = context.str(path) + context.str('/') \
                                + reducedFn
                errors.write('\n' + (context.translate(
                    msgid   = 'file_exists', 
                    domain  = I18N_DOMAIN, 
                    default = 'A file named "%s" already exits.') \
                              % context.str(reducedFn)))
            else: # File can be imported
                # Zope IDs must be strings!
                id = stringToZopeId(container, typeName, id, errors)
                newId = container.invokeFactory(typeName, id=id, 
                    title=localName, file=fileStringIO)
                if not newId:
                    newId = id
                fileObject = getattr(container, newId, None)
                if fileObject:
##                    # Set mime type
##                    if mimeType: # i.e. if we have a mimeType
##                       fileObject.setContentType(mimeType)
                    # Add to 'addedObjects'
                    addedObjects += [fileObject]                    
                    
        except Exception, e:
            log('Failed: create "%s": %s\n' % (str(fileName), str(e)))
            errors.write('\n' + context.translate(
                msgid   = 'file_unexpected_error',
                domain  = I18N_DOMAIN,
                default = 'Could not import file "%s". An unexpected error has occurred: %s'
                ) % (context.str(fileName), context.str(e)))
            return addedObjects
        return addedObjects
    except Exception, e:
        errors.write('\n' + context.translate(
                                msgid   = 'unexpected_error',
                                domain  = I18N_DOMAIN,
                                default = 'An unexpected error has occurred in "%s": %s'
                            ) % (context.str('importFileResource()'), context.str(e)))
        return addedObjects


def findFiles(folderishObject, basePath, errors):
    """ Return a list of tuples (path-to-file-object, file-object) for
        every cmf-File and cmf-Image in 'folderishObject'. This function
        works recursively.

        @param folderishObject A folderish object, i.e. one that supports
                'folderishObject.listFolderContents()'.
        @param basePath A path that all the returned 'paths-to-file-object'
                will start with.
        @param errors A string IO object where errors can be logged.

        @return A list of tuples (path-to-file-object, file-object) for
            every cmf-File and cmf-Image in 'folderishObject'.
    """
    fileList = []
    contents = folderishObject.listFolderContents()
    for cmfFile in [cmfFile for cmfFile in contents
                    if cmfFile.Type() in ['File', 'Image']]:
        title = cmfFile.getId().strip()
        fileList += [(basePath + '/' + title, cmfFile)]
    for folder in [folder for folder in contents
                   if folder.Type() in ['Folder']]:
        folderName = folder.getId().strip()
        fileList += findFiles(folder, basePath + '/' + folderName, errors)
    return fileList


def setImsmdTitle(metadataElem, zopeObj):
    """ Set the title of a <metadata> element in an imsmanifest.

        @param metadataElem An xml <metadata> element.
        @param zopeObj A Zope object with the title.

        @return The same <metadata> element, but with some new children.
            This will look something like

            <metadata>
              <lom>
                <general>
                  <title>
                    <langstring xml:lang="de">Titel</langstring>
                  </title>
                </general>
              </lom>
            </metadata>

            Only with namespaces.
    """
    doc = metadataElem.ownerDocument
    lom = metadataElem.appendChild(
        doc.createElementNS(NS_IMSMD_V1P2_URI, NS_IMSMD + u':' + LOM))
    general = lom.appendChild(
        doc.createElementNS(NS_IMSMD_V1P2_URI, NS_IMSMD + u':' + GENERAL))
    title = general.appendChild(
        doc.createElementNS(NS_IMSMD_V1P2_URI, NS_IMSMD + u':' + TITLE))
    langstring = title.appendChild(
        doc.createElementNS(NS_IMSMD_V1P2_URI, NS_IMSMD + u':' + LANG_STRING))
    lang = zopeObj.Language()
    # if the object is language neutral, [lang] will be the empty string
    if lang:
        langstring.setAttribute(XML_LANG, zopeObj.unicodeDecode(lang))
    zopeObjTitle = zopeObj.unicodeDecode(zopeObj.Title().strip())
    langstring.appendChild(doc.createTextNode(zopeObjTitle))

def exportRandomizationControls(obj, organizationItem, errors):
    """Set <imsss:randomizationControls> for randomizable objects"""
    doc = organizationItem.ownerDocument
    
    sequencing = organizationItem.appendChild(
        doc.createElementNS(NS_IMSSS_URI,
                            NS_IMSSS + u':' + SEQUENCING))
    randomizationControls = sequencing.appendChild(
        doc.createElementNS(NS_IMSSS_URI,
                            NS_IMSSS + u':' + RANDOMIZATION_CONTROLS))
    if obj.isRandomOrder():
        randomizationControls.setAttribute(RANDOMIZATION_TIMING,
                                           ON_EACH_NEW_ATTEMPT)
        reorderChildren = TRUE
    else:
        reorderChildren = FALSE
    randomizationControls.setAttribute(REORDER_CHILDREN, reorderChildren)

    for name in ('getNumberOfRandomQuestions',
                 'getNumberOfRandomAnswers',):
        if shasattr(obj, name):
            getter = getattr(obj, name)
            value = getter()
            # only non-negative integers are allowed
            if value >= 0:
                randomizationControls.setAttribute(SELECT_COUNT,
                                                   unicode(value))

def exportPackage(multipleChoiceTest, errors):
    """ Exports a Quiz as a QTI package.


        @param multipleChoiceTest The ECQuiz instance
                of course.
        @param errors A string IO object where errors can be logged.

        @return A file-like object (a StringIO instance, to be exact) that
                contains a zip archive.
    """

    context = multipleChoiceTest
    package = StringIO()
    zipObj = ZipFile(package, 'w')

    manifestDoc = minidom.Document()
    manifest = manifestDoc.appendChild(manifestDoc.createElement(MANIFEST))
    """ The attributes of the manifest
        <manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
            xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:imsqti="http://www.imsglobal.org/xsd/imsqti_v2p0"
            identifier="MANIFEST-85D76736-6D19-9DC0-7C0B-57C31A9FD390"
            xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd
            http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd
            http://www.imsglobal.org/xsd/imsqti_v2p0 http://www.imsglobal.org/xsd/imsqti_v2p0.xsd">
    """
    manifest.setAttribute(u'xmlns', NS_IMSCP_V1P1_URI)
    manifest.setAttribute(u'xmlns:' + NS_IMSMD, NS_IMSMD_V1P2_URI)
    manifest.setAttribute(u'xmlns:' + NS_XSI, NS_XSI_URI)
    manifest.setAttribute(u'xmlns:' + NS_IMSQTI, NS_IMSQTI_V2P0_URI)
    manifest.setAttribute(u'xmlns:' + NS_IMSSS, NS_IMSSS_URI)
    manifest.setAttribute(u'xmlns:' + NS_LLSMC, NS_LLSMC_URI)
    manifest.setAttributeNS(NS_XSI_URI, NS_XSI + u':schemaLocation', MANIFEST_SCHEMA_LOCATIONS)
    manifest.setAttribute(IDENTIFIER, u'MANIFEST-' + multipleChoiceTest.UID())

    # metadata: schema, schemaVersion, toolName, toolVersion, toolVendor
    """
        <schema>IMS QTI</schema> 
        <schemaversion>2.0</schemaversion> 
        <imsqti:qtiMetadata>
            <imsqti:toolName>LlsMultipleChoice</imsqti:toolName> 
            <imsqti:toolVersion>1.0</imsqti:toolVersion> 
            <imsqti:toolVendor>WDOK Research Group, Otto-von-Guericke-Universität Magdeburg</imsqti:toolVendor> 
        </imsqti:qtiMetadata>
    """
    metadata = manifest.appendChild(manifestDoc.createElement(METADATA))
    schema = metadata.appendChild(manifestDoc.createElement(u'schema'))
    schema.appendChild(manifestDoc.createTextNode(u'IMS QTI'))
    schemaversion = metadata.appendChild(manifestDoc.createElement(
        u'schemaversion'))
    schemaversion.appendChild(manifestDoc.createTextNode(
        IMS_QTI_SCHEMA_VERSION))
    qtiMetadata = metadata.appendChild(
        manifestDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI + u':'
                                    + QTI_METADATA))
    toolName = qtiMetadata.appendChild(
        manifestDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI + u':'
                                    + TOOL_NAME))
    toolName.appendChild(manifestDoc.createTextNode(
        context.unicodeDecode(FIXME_PROJECTNAME)))
    toolVersion = qtiMetadata.appendChild(
        manifestDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI + u':'
                                    + TOOL_VERSION))
    toolVersion.appendChild(manifestDoc.createTextNode(MC_TOOL_VERSION))
    toolVendor = qtiMetadata.appendChild(
        manifestDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI + u':'
                                    + TOOL_VENDOR))
    toolVendor.appendChild(manifestDoc.createTextNode(MC_TOOL_VENDOR))

    # metadata cont.: title
    setImsmdTitle(metadata, multipleChoiceTest)

    # The <organizations> element
    """
      <organizations>
        <organization identifier="ORGANIZATION-1">
          <title>Default Organization</title>
    
          <item identifier="TEST-1" identifierref="RESOURCE-0">
            <item identifier="ITEM-1" identifierref="RESOURCE-1">
              <title>Ungrouped item</title>
            </item>
    
            <item identifier="QGROUP-1" identifierref="RESOURCE-2">
              <item identifier="QGROUP-1-ITEM-1" identifierref="RESOURCE-3"/>
              <item identifier="QGROUP-1-ITEM-2" identifierref="RESOURCE-4"/>
      
              <!-- Sequencing definition for the containing item -->
              <!-- Meaning: The items of the question group      -->
              <!-- appear in fixed order                         -->
              <imsss:sequencing>
                <imsss:randomizationControls reorderChildren="false"/>
              </imsss:sequencing>
            </item>
    
            <!-- Sequencing definition for the containing item  -->
            <!-- Meaning: The items of the test                 -->
            <!-- appear in random order                         -->
            <imsss:sequencing>
              <imsss:randomizationControls
                     randomizationTiming="onEachNewAttempt"
                     reorderChildren="true"/>
            </imsss:sequencing>
          </item>
    
          <!-- Sequencing definition for the whole organization -->
          <!-- Meaning: This test can only be taken once        -->
          <imsss:sequencing>
            <imsss:limitConditions attemptLimit="1"/>
          </imsss:sequencing>
        </organization>
      </organizations>
    """
    organizations = manifest.appendChild(
        manifestDoc.createElement(ORGANIZATIONS))
    organization = organizations.appendChild(
        manifestDoc.createElement(ORGANIZATION))
    organization.setAttribute(IDENTIFIER, u'ORGANIZATION-1')
    title = organization.appendChild(manifestDoc.createElement(TITLE))
    titleText = 'Default Organization'
    title.appendChild(manifestDoc.createTextNode(
        context.unicodeDecode(titleText)))

    def exportBool(elemName, value, parent):
        elem = parent.appendChild(
            manifestDoc.createElementNS(
                NS_LLSMC_URI, NS_LLSMC + u':' + elemName))
        if value:
            text = TRUE
        else:
            text = FALSE
        elem.appendChild(manifestDoc.createTextNode(text))

    def exportStr(elemName, value, parent):
        elem = parent.appendChild(
            manifestDoc.createElementNS(
                NS_LLSMC_URI, NS_LLSMC + u':' + elemName))
        text = multipleChoiceTest.unicodeDecode(value)
        if text:
            elem.appendChild(manifestDoc.createTextNode(text))

    # The <resources> element
    resources = manifest.appendChild(manifestDoc.createElement(RESOURCES))

    ### Export the quiz, question groups and questions ###
    
    # This list will hold tuples of objects with a "isRandomOrder()" method 
    # and the <item> elements that have been generated for them.
    # It will be used to set:
    #
    # <imsss:sequencing>
    #   <imsss:randomizationControls
    #          randomizationTiming="onEachNewAttempt"
    #          reorderChildren="true"/>
    # </imsss:sequencing>
    quizItem = None
    
    questionContainerList = [multipleChoiceTest] \
        + multipleChoiceTest.getQuestionGroups()
    for containerCounter in range(len(questionContainerList)):
        # Create the assessmentItem
        questionContainer = questionContainerList[containerCounter]
        containerName = u'container' + unicode(containerCounter)
        path = EXPORT_ITEM_PATH + u'/' + containerName + u'.xml'
        containerAI, containerResource = \
            exportAssessmentItem(questionContainer, path, errors)
        if containerAI is not None:
            writeToZip(context, zipObj, path, containerAI, errors)
            resources.appendChild(containerResource)
            # Expand the <organization> element
            containerItem = manifestDoc.createElement(ITEM)
            if questionContainer is multipleChoiceTest:
                # The Quiz
                quizItem = containerItem
                organization.appendChild(containerItem)
                containerItemIdentifier = u'TEST-' \
                                          + unicode(containerCounter+1)
                # Export files
                if (containerResource):
                    fileList = findFiles(multipleChoiceTest,
                                         EXPORT_ITEM_PATH, errors)
                    for cmfFileTuple in fileList:
                        path = cmfFileTuple[0]
                        cmfFile = cmfFileTuple[1]
                        writeToZip(context, zipObj, path,
                                   cmfFile.manage_FTPget(), errors)
                        containerFile = containerResource.appendChild(
                            manifestDoc.createElement(FILE))
                        containerFile.setAttribute(HREF,
                                                   context.unicodeDecode(path))
            elif quizItem:
                # An ECQGroup
                quizItem.appendChild(containerItem)
                containerItemIdentifier = u'CONTAINER-' \
                                          + unicode(containerCounter)
            containerItem.setAttribute(IDENTIFIER, containerItemIdentifier)
            containerResourceIdentifier = containerResource.getAttribute(
                IDENTIFIER)
            if (containerResourceIdentifier):
                containerItem.setAttribute(IDENTIFIER_REF,
                                           containerResourceIdentifier)
            containerResource.ownerDocument.unlink()
        
        # Export the contained questions
        questionList = questionContainer.getAllQuestions()
        for questionCounter in range(len(questionList)):
            question = questionList[questionCounter]
            fileName = containerName + u'_question' \
                       + unicode(questionCounter) + u'.xml'
            path = EXPORT_ITEM_PATH + u'/' + fileName
            questionAI, questionResource = \
                exportAssessmentItem(question, path, errors)
            if questionAI is not None:
                writeToZip(context, zipObj, path, questionAI, errors)
                resources.appendChild(questionResource)
                # Expand the <organization> element
                questionItem = containerItem.appendChild(
                    manifestDoc.createElement(ITEM))
                questionItem.setAttribute(
                    IDENTIFIER, containerItemIdentifier
                    + u'-ITEM-' + unicode(questionCounter+1))
                questionResourceIdentifier = questionResource.getAttribute(
                    IDENTIFIER)
                if (questionResourceIdentifier):
                    questionItem.setAttribute(IDENTIFIER_REF,
                                              questionResourceIdentifier)
                # Export the points of the question
                points = None
                try:
                    pointsTmp = question.getPoints()
                    if type(pointsTmp) == int:
                        points = unicode(pointsTmp)
                except:
                    pass
                if points is not None:
                    weight = questionItem.appendChild(
                        manifestDoc.createElementNS(
                        NS_LLSMC_URI, NS_LLSMC + u':' + WEIGHT))
                    weight.appendChild(manifestDoc.createTextNode(points))

                if shasattr(question, 'isRandomOrder'):
                    # export [isRandomOrder] etc.
                    exportRandomizationControls(question, questionItem,
                                                errors)
                if shasattr(question, 'choiceLayout'):
                    exportStr(LAYOUT, question.getChoiceLayout(),
                              questionItem)
                if shasattr(question, 'tutorGraded'):
                    exportBool(TUTOR_GRADED, question.isTutorGraded(),
                               questionItem)
                questionResource.ownerDocument.unlink()
                
        # export [isRandomOrder] etc. if it's a group (we can't export
        # [isRandomOrder] etc. for the quiz itself here because
        # sequencing information must come after all the other
        # elements)
        if (containerAI is not None) and \
               (questionContainer is not multipleChoiceTest):
            exportRandomizationControls(questionContainer, containerItem,
                                        errors)

    # export [isRandomOrder] etc. if it's the quiz
    if quizItem:
        exportRandomizationControls(multipleChoiceTest, quizItem,
                                    errors)

    ### export the sequencing information ###

    # <organization>: repetition
    organizationSequencing = organization.appendChild(
        manifestDoc.createElementNS(NS_IMSSS_URI, NS_IMSSS
                                    + u':' + SEQUENCING))
    organizationLimitConditions = organizationSequencing.appendChild(
        manifestDoc.createElementNS(NS_IMSSS_URI, NS_IMSSS
                                    + u':' + LIMIT_CONDITIONS))
    organizationAttemptLimit = [u'1', u'0'][
        multipleChoiceTest.isAllowRepetition()]
    organizationLimitConditions.setAttribute(ATTEMPT_LIMIT,
                                             organizationAttemptLimit)
    
    # <llsmc:instantFeedback>
    exportBool(INSTANT_FEEDBACK, multipleChoiceTest.isInstantFeedback(),
               organizationSequencing)
    
    # <llsmc:oneQuestionPerPage>
    exportBool(ONE_QUESTION_PER_PAGE, multipleChoiceTest.isOnePerPage(),
               organizationSequencing)
    
    # <llsmc:allowNavigation>
    exportBool(ALLOW_NAVIGATION, multipleChoiceTest.isOnePerPageNav(),
               organizationSequencing)
    
    # <llsmc:scoringFunction>
    exportStr(SCORING_FUNCTION, multipleChoiceTest.getScoringFunction(),
              organization)

    # <llsmc:gradingScale>
    if multipleChoiceTest.haveGradingScale():
        scale = organization.appendChild(
            manifestDoc.createElementNS(
                NS_LLSMC_URI, NS_LLSMC + u':' + GRADING_SCALE))
        for d in multipleChoiceTest.getGradingScale():
            row = scale.appendChild(
                manifestDoc.createElementNS(
                    NS_LLSMC_URI, NS_LLSMC + u':' + GRADING_SCALE_ROW))
            for k, n in (('grade', GRADE), ('score', MIN_SCORE),):
                exportStr(n, d[k].strip(), row)

    manifestContents = context.unicodeDecode(
        manifestDoc.toprettyxml()).encode(EXPORT_ENCODING)
    manifestDoc.unlink()
    writeToZip(context, zipObj, MANIFEST_FILE_NAME, manifestContents, errors)
    zipObj.close()
    package.seek(0)
    return package


def exportAssessmentItem(obj, exportFileName, errors):
    """ This is about what we want to output for a multiple choice question

        <assessmentItem xmlns="http://www.imsglobal.org/xsd/imsqti_v2p0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.imsglobal.org/xsd/imsqti_v2p0 http://www.imsglobal.org/xsd/imsqti_v2p0.xsd"
            identifier="choice" title="Unattended Luggage" adaptive="false" timeDependent="false">
            <responseDeclaration identifier="RESPONSE" cardinality="single" baseType="identifier">
                <correctResponse>
                    <value>ChoiceA</value>
                </correctResponse>
            </responseDeclaration>
            <!--outcomeDeclaration identifier="SCORE" cardinality="single" baseType="integer">
                <defaultValue>
                    <value>0</value>
                </defaultValue>
            </outcomeDeclaration-->
            <itemBody>
                <p>Look at the text in the picture.</p>
                <p>
                    <img src="additionalContent/images/sign.png" alt="NEVER LEAVE LUGGAGE UNATTENDED"/>
                </p>
                <choiceInteraction responseIdentifier="RESPONSE" shuffle="false" maxChoices="1">
                    <prompt>What does it say?</prompt>
                    <simpleChoice identifier="ChoiceA">You must stay with your luggage at all times.</simpleChoice>
                    <simpleChoice identifier="ChoiceB">Do not let someone else look after your luggage.</simpleChoice>
                    <simpleChoice identifier="ChoiceC">Remember your luggage when you leave.</simpleChoice>
                </choiceInteraction>
            </itemBody>
            <!--responseProcessing template="http://www.imsglobal.org/question/qti_v2p0/rptemplates/match_correct"
                templateLocation="http://www.imsglobal.org/question/qti_v2p0/rptemplates/match_correct.xml"/-->
        </assessmentItem>
    """

    ### Create the <assessmentItem> ###
    aiDoc = minidom.Document()
    ai = aiDoc.appendChild(aiDoc.createElement(ASSESSMENT_ITEM))
    # Set the namespaces
    ai.setAttribute(u'xmlns', NS_IMSQTI_V2P0_URI)
    ai.setAttribute(u'xmlns:' + NS_XSI, NS_XSI_URI)
    ai.setAttributeNS(NS_XSI_URI, NS_XSI + u':schemaLocation',
                      NS_IMSQTI_V2P0_URI + u' ' + NS_IMSQTI_V2P0_URL)
    # Write the title
    title = obj.unicodeDecode(obj.Title().strip())    
    ai.setAttribute(TITLE, title)
    ai.setAttribute(IDENTIFIER, UID_PREFIX + obj.unicodeDecode(obj.UID()))
    ai.setAttribute(ADAPTIVE, FALSE)       # Adaptive tests are not supported
    ai.setAttribute(TIME_DEPENDENT, FALSE) # Time-dependent tests are not supported
    itemBody = ai.appendChild(aiDoc.createElement(ITEM_BODY))

    ### Create a <resource> element for the the manifest ###
    man_resourceDoc = minidom.Document()
    man_resource = man_resourceDoc.appendChild(
        man_resourceDoc.createElement(RESOURCE))
    # the resource gets the same identifier as the assessmentItem it references
    man_resource.setAttribute(IDENTIFIER, ai.getAttribute(IDENTIFIER))
    man_resource.setAttribute(TYPE, IMSQTI_ITEM_XMLV2P0)
    uExportFileName = obj.unicodeDecode(exportFileName)
    man_resource.setAttribute(HREF, uExportFileName)
    # metadata
    man_metadata = man_resource.appendChild(
        man_resourceDoc.createElement(METADATA))
    # imsmd metadata
    setImsmdTitle(man_metadata, obj)
    # file href points to the assessmentItem
    man_fileNode = man_resource.appendChild(
        man_resourceDoc.createElement(FILE))
    man_fileNode.setAttribute(HREF,  uExportFileName)
    ### End of <resource> element ###

    if obj.portal_type in ['ECQuiz', ECQGroup.portal_type]:
        # Write the directions
        directionsText = obj.unicodeDecode(obj.getDirections().strip())
        # Attention: <itemBody> allows only block elements as content.
        xhtmlExport(itemBody, directionsText)
    elif obj.portal_type == ECQMCQuestion.portal_type:
        responseDeclaration = aiDoc.createElement(RESPONSE_DECLARATION)
        ai.insertBefore(responseDeclaration, itemBody)
        
        responseDeclaration.setAttribute(IDENTIFIER, u'RESPONSE')
        responseDeclaration.setAttribute(u'cardinality', [
            u'single', u'multiple'][obj.isAllowMultipleSelection()])

        correctResponse = responseDeclaration.appendChild(
            aiDoc.createElement(CORRECT_RESPONSE))

        # Create a (dummy) outcomeDeclaration to declare an outcome
        # identifier, which is required for feedback blocks.
        outcomeDeclaration = aiDoc.createElement(OUTCOME_DECLARATION)
        ai.insertBefore(outcomeDeclaration, itemBody)

        outcomeDeclaration.setAttribute(IDENTIFIER, u'OUTCOME')
        outcomeDeclaration.setAttribute(u'cardinality', u'single')

        # Write the question text
        # Attention: <itemBody> allows only block elements as content.
        questionText = obj.unicodeDecode(obj.getQuestion().strip())
        xhtmlExport(itemBody, questionText)

        choiceInteraction = itemBody.appendChild(aiDoc.createElement(
            CHOICE_INTERACTION))
        choiceInteraction.setAttribute(RESPONSE_IDENTIFIER, 
            responseDeclaration.getAttribute(IDENTIFIER))
        choiceInteraction.setAttribute(SHUFFLE, [FALSE, TRUE][
            obj.isRandomOrder()])
        choiceInteraction.setAttribute(MAX_CHOICES, [u'1', u'0'][
            obj.isAllowMultipleSelection()])

        # Export the answers
        answerList = obj.listFolderContents()
        for answerCounter in range(len(answerList)):
            """
                <simpleChoice identifier="MGH001A">
                    George W Bush 
                    <feedbackInline outcomeIdentifier="FEEDBACK" identifier="MGH001A" showHide="show">No, he is the President of the USA.</feedbackInline>
                </simpleChoice>
            """
            answer = answerList[answerCounter]
            simpleChoice = choiceInteraction.appendChild(aiDoc.createElement(
                SIMPLE_CHOICE))
            # The answer text
            answerText = obj.unicodeDecode(answer.getAnswer().strip())
            # <simpleChoice> can have block and inline elements as content
            xhtmlExport(simpleChoice, answerText)
            # The identifier
            answerIdentifier = u'Choice' + unicode(answerCounter)
            simpleChoice.setAttribute(IDENTIFIER, answerIdentifier)
            # Correct
            if (answer.isCorrect()):
                value = correctResponse.appendChild(aiDoc.createElement(VALUE))
                value.appendChild(aiDoc.createTextNode(answerIdentifier))
            # The comment
            commentText = answer.getComment().strip()
            if (commentText):
                commentText = obj.unicodeDecode(commentText)
                # Attention: <feedbackInline> allows only inline elements and
                # text as content.
                # Attention: <feedbackBlock> allows only block elements as
                # content.
                feedbackBlock = simpleChoice.appendChild(
                    aiDoc.createElement(FEEDBACK_BLOCK))
                xhtmlExport(feedbackBlock, commentText)
                feedbackBlock.setAttribute(IDENTIFIER, u'Feedback_' + answerIdentifier)
                feedbackBlock.setAttribute(OUTCOME_IDENTIFIER, u'OUTCOME')
                feedbackBlock.setAttribute(SHOW_HIDE, SHOW)

        ### Expand the <resource> element ###
        # imsqti metadata
        man_qtiMetadata = man_metadata.appendChild(
            man_resourceDoc.createElementNS(NS_IMSQTI_V2P0_URI,
                                            NS_IMSQTI + u':' + QTI_METADATA))
        man_interactionType = man_qtiMetadata.appendChild(
            man_resourceDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI
                                            + u':' + INTERACTION_TYPE))
        man_interactionType.appendChild(
            man_resourceDoc.createTextNode(CHOICE_INTERACTION))
    elif obj.portal_type == ECQExtendedTextQuestion.portal_type:
        # Write the question text
        # Attention: <itemBody> allows only block elements as content.
        questionText = obj.unicodeDecode(obj.getQuestion().strip())
        xhtmlExport(itemBody, questionText)

        extendedTextInteraction = itemBody.appendChild(aiDoc.createElement(
            EXTENDED_TEXT_INTERACTION))
        extendedTextInteraction.setAttribute(RESPONSE_IDENTIFIER,
                                             u'RESPONSE')
        
        answerTemplate = obj.unicodeDecode(obj.getAnswerTemplate().strip())
        extendedTextInteraction.setAttribute(PLACEHOLDER_TEXT,
                                             answerTemplate)
        
        expectedLength = unicode(obj.getExpectedLength())
        extendedTextInteraction.setAttribute(EXPECTED_LENGTH,
                                             expectedLength)
        
        ### Expand the <resource> element ###
        # imsqti metadata
        man_qtiMetadata = man_metadata.appendChild(
            man_resourceDoc.createElementNS(
                NS_IMSQTI_V2P0_URI,
                NS_IMSQTI + u':' + QTI_METADATA))
        man_interactionType = man_qtiMetadata.appendChild(
            man_resourceDoc.createElementNS(
                NS_IMSQTI_V2P0_URI,
                NS_IMSQTI + u':' + INTERACTION_TYPE))
        man_interactionType.appendChild(
            man_resourceDoc.createTextNode(EXTENDED_TEXT_INTERACTION))
    elif obj.portal_type == ECQScaleQuestion.portal_type:
        responseDeclaration = aiDoc.createElement(RESPONSE_DECLARATION)
        ai.insertBefore(responseDeclaration, itemBody)
        
        responseDeclaration.setAttribute(IDENTIFIER, u'RESPONSE')
        responseDeclaration.setAttribute(u'cardinality', u'single')

        # This mapping will hold the scores of the answers:
        #
        # * The keys are the IDENTIFIER-attributes of the
        #   corresponding <simpleChoice> element.
        #
        # * The values are the scores.
        mapping = responseDeclaration.appendChild(
            aiDoc.createElement(MAPPING))
        mapping.setAttribute(DEFAULT_VALUE, unicode(0))

        # Create a (dummy) outcomeDeclaration to declare an outcome
        # identifier, which is required for feedback blocks.
        outcomeDeclaration = aiDoc.createElement(OUTCOME_DECLARATION)
        ai.insertBefore(outcomeDeclaration, itemBody)
        
        outcomeDeclaration.setAttribute(IDENTIFIER, u'OUTCOME')
        outcomeDeclaration.setAttribute(u'cardinality', u'single')

        # Write the question text
        # Attention: <itemBody> allows only block elements as content.
        questionText = obj.unicodeDecode(obj.getQuestion().strip())
        xhtmlExport(itemBody, questionText)

        choiceInteraction = itemBody.appendChild(aiDoc.createElement(
            CHOICE_INTERACTION))
        choiceInteraction.setAttribute(RESPONSE_IDENTIFIER, 
            responseDeclaration.getAttribute(IDENTIFIER))
        choiceInteraction.setAttribute(SHUFFLE, [FALSE, TRUE][
            obj.isRandomOrder()])
        choiceInteraction.setAttribute(MAX_CHOICES, u'1')

        # Export the answers
        answerList = obj.listFolderContents()
        for answerCounter in range(len(answerList)):
            answer = answerList[answerCounter]
            simpleChoice = choiceInteraction.appendChild(aiDoc.createElement(
                SIMPLE_CHOICE))
            # The answer text
            answerText = obj.unicodeDecode(answer.getAnswer().strip())
            # <simpleChoice> can have block and inline elements as content
            xhtmlExport(simpleChoice, answerText)
            # The identifier
            answerIdentifier = u'Choice' + unicode(answerCounter)
            simpleChoice.setAttribute(IDENTIFIER, answerIdentifier)
            # The comment
            commentText = answer.getComment().strip()
            if commentText:
                commentText = obj.unicodeDecode(commentText)
                # Attention: <feedbackInline> allows only inline elements and
                # text as content.
                # Attention: <feedbackBlock> allows only block elements as
                # content.
                feedbackBlock = simpleChoice.appendChild(
                    aiDoc.createElement(FEEDBACK_BLOCK))
                xhtmlExport(feedbackBlock, commentText)
                feedbackBlock.setAttribute(
                    IDENTIFIER, u'Feedback_' + answerIdentifier)
                feedbackBlock.setAttribute(OUTCOME_IDENTIFIER, u'OUTCOME')
                feedbackBlock.setAttribute(SHOW_HIDE, SHOW)
            # The score
            kv = mapping.appendChild(aiDoc.createElement(MAP_ENTRY))
            kv.setAttribute(MAP_KEY, answerIdentifier)
            kv.setAttribute(MAPPED_VALUE, unicode(answer.getScore()))

        ### Expand the <resource> element ###
        # imsqti metadata
        man_qtiMetadata = man_metadata.appendChild(
            man_resourceDoc.createElementNS(NS_IMSQTI_V2P0_URI,
                                            NS_IMSQTI + u':' + QTI_METADATA))
        man_interactionType = man_qtiMetadata.appendChild(
            man_resourceDoc.createElementNS(NS_IMSQTI_V2P0_URI, NS_IMSQTI
                                            + u':' + INTERACTION_TYPE))
        man_interactionType.appendChild(
            man_resourceDoc.createTextNode(CHOICE_INTERACTION))
    else:
        errors.write('\n' + obj.translate(
                msgid   = 'export_assessment_item_type_error',
                domain  = I18N_DOMAIN,
                default = 'Cannot export item "%s". Unsupported type "%s".'
            ) % (obj.str(obj.title_or_id()), obj.str(
            obj.portal_type)))
        aiDoc.unlink()
        man_resourceDoc.unlink()
        return None, None
    # Success    
    aiText = obj.unicodeDecode(aiDoc.toxml()).encode(EXPORT_ENCODING)
    aiDoc.unlink()
    return aiText, man_resource
