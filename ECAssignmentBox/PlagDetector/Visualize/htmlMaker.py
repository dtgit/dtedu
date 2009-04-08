# -*- coding: utf-8 -*-
# $Id: htmlMaker.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


#===============================================================================
#Author: Christian Dervaric
#
#Description:
#This module contains methods to represent the results of the plagiarism tests, 
#i.e. PlagResult objects, as marked html code.
#===============================================================================

import re
from Products.ECAssignmentBox.PlagDetector.Normalize import *



def resultToHtml(result, s1, s2, startMarkToken="<b>", endMarkToken="</b>"):
    """Returns a list of strings [s1Marked, s2Marked] in which the
        tiles of the result are marked by the markTokens.
        
        Note: Using this method will automatically choose the right way 
        to create the marked HTML Texts. 
        
        To change the way similarities are highlighted, it is possible to set
        the start and end token of the marking using:
        Options; 
            startMarkToken and endMarkToken
                    By Default: startMarkToken = "<b>"
                                endMarkToken = "</b>"
    """
    if result.getNormalizerName() == 'NORMAL':
        return resultToHtml_Normal(result, s1, s2, startMarkToken, endMarkToken)
    else:
        return resultToHtml_Prog(result, s1, s2, startMarkToken, endMarkToken)


def resultToHtmlText(result, s1, s2, markTokens = ["<b>","</b>"]):
    """Creates a complete html file text that can be used to save it to diskspace
        and view it.
    """
    markedTexts = resultToHtml(result, s1, s2, markTokens[0], markTokens[1])
    
    import re
    #replace linebreaks by htmllinebreaks
    text1 = re.sub("\n", "<br/>", markedTexts[0])
    text2 = re.sub("\n", "<br/>", markedTexts[1])
    
    title = "Comparison of %s and %s" % (result.getIdentifier()[0], result.getIdentifier()[1])
    
#    divstyle = "style=\"height: auto; width: auto; overflow: auto\""
    divstyle = "style=\"height: 400px; width: 280px; overflow: auto\""
    
    compPart = "<table>\n"\
               "<tr>\n"\
               "<td>\n<div %s>\n%s\n</div></td>\n"\
               "<td>\n<div %s>\n%s\n</div></td>\n"\
               "</table>\n" % (divstyle, text1, divstyle, text2)
    
    body = "<h1>%s</h1>\n%s\n" % (title, compPart)
    
    htmlText="<html>\n<head>\n<title>\n%s</title>\n</head>\n</html>\n\n<body>%s</body>\n" % (title, body)
    
    return htmlText

def resultToHtml_Normal(result, s1, s2, startMarkToken, endMarkToken, colored=True):
    """Returns a list of strings [s1Marked, s2Marked] in which the
        tiles of the result are marked by the markTokens.
    """
    #recreate normalized strings from orignal strings as lists
    s1NormList = normNormal.normalize(s1).split()
    s2NormList = normNormal.normalize(s2).split()
    
    #if matches should be colored create color generator
    if colored:
        gen = colorGen(len(result.getTiles()))

    #sort tiles in decreasing length > tile=(pos1, pos2, length)
    tiles = result.getTiles()
    tiles.sort(key=lambda x: x[2], reverse=True)
    
    #for each tile, 
    #    look for the substring in the normalized version
    #    create a search pattern out of it
    #    use the pattern to mark the tile in the original string
    for tile in tiles:#result.getTiles():
       tileList = s1NormList[tile[0]:tile[0]+tile[2]]
       pattern = ""
       for s in tileList:
           pattern += s + "\W*?"
       pattern = pattern[:-4]
       
       #if matches should be colored add color to mark tokens
       if colored:
           color = gen.next()
           styleStart = "<span style=\"color:rgb%s\">" % str(color)
           styleEnd = "</span>"
       
       #mark string
       s1 = mark(pattern, s1, styleStart + startMarkToken, endMarkToken + styleEnd)
       s2 = mark(pattern, s2, styleStart + startMarkToken, endMarkToken + styleEnd)
   
    #return marked strings
    return [s1, s2]
           

def mark(pattern, string, startMarkToken, endMarkToken):
    """Marks all substrings in the string which matches the pattern.
    """
    #look for matches
    matches = re.findall(pattern, string, re.I|re.L|re.U) #ignore case
    #create a set of the matches to avoid double entries
    matches = set(matches)
    #mark each match in the string with the predefined markTokens
    for match in matches:
        string = string.replace(match, startMarkToken+match+endMarkToken)
    #return marked string
    return string

def resultToHtml_Prog(result, s1, s2, startMarkToken, endMarkToken, colored=True):
    """Returns a list of strings [s1Marked, s2Marked] in which the
        tiles of the result are marked by the markTokens.
    """
    normalize = normNames.get(result.getNormalizerName())
    s1Norm, lineNrList1 = normalize(s1, returnLinesForEachToken=True)
    s1NormList = s1Norm.split()
    s2Norm, lineNrList2 = normalize(s2, returnLinesForEachToken=True)
    s2NormList = s2Norm.split()
    linesS1 = s1.splitlines(True)
    linesS2 = s2.splitlines(True)

    if colored: 
        gen = colorGen(len(result.getTiles()))

    for tile in result.getTiles():
        if gen:
           color = gen.next()
           styleStart = "<span style=\"color:rgb%s\">" % str(color)
           styleEnd = "</span>"
            
        for i in lineNrList1[tile[0]: tile[0]+tile[2]]:
            linesS1[i] = markLine(linesS1[i], styleStart+startMarkToken, endMarkToken+styleEnd)
        for i in lineNrList2[tile[1]: tile[1]+tile[2]]:
            linesS2[i] = markLine(linesS2[i], styleStart+startMarkToken, endMarkToken+styleEnd)

    return ["".join(linesS1), "".join(linesS2)]

def markLine(line, startMarkToken, endMarkToken):
    """Marks given line using the start- and endMarkToken.
    """
    if line.startswith(startMarkToken) and line.endswith(endMarkToken):
        return line
    return startMarkToken + line + endMarkToken

def isEmptyLine(line):
    """Returns True if the string line only consists of whitespaces [' ','\n','\t', ...]."""
    if len([s for s in line if re.search('\s', s)]) == len(line):
        return True
    else: return False
    
    
def colorGen(numberColors):
    colors = createXDifferentColors(numberColors)
    for c in colors:
        yield c

def createXDifferentColors(x):
    """Returns a list with x different colors.
    """
    x3 = x/3
    colors = []
    for i in xrange(x3):
        colors.append((0,0,(i+1)*255/x3))
    for i in xrange(x3):
        colors.append((0,(i+1)*255/x3,0))
    for i in xrange(x-(2*x3)):
        colors.append(((i+1)*255/(x-(2*x3)),0,0))
    return colors
    
