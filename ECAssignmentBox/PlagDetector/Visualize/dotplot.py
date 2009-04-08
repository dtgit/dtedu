# -*- coding: utf-8 -*-
# $Id: dotplot.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
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
#A Dotplot shows all w/k-matches (window of length w with k matches) 
#between two sequences.
#        
#For every window of length w with at least k matches a dot is drawn 
#otherwise it will be left blank.
#
#===============================================================================

from PIL import Image, ImageDraw, ImageFont
from Products.ECAssignmentBox.PlagDetector.errors import NoValidArgumentError
from Products.ECAssignmentBox.PlagDetector.PlagResult import PlagResult
from Products.ECAssignmentBox.PlagDetector.Helper.GraphicsHelper import computeMaxIdLength, rotText



def createDotplotFromResult(result, showIds=False):
    """Creates a dotplot from the result (PlagResult) of a similarity check.
    
        It uses the tiles of the PlagResult. Therefore it does not need w/k
        parameters.
    """
    #check preconditions
    if type(result) != type(PlagResult()):
        raise NoValidArgumentError, 'Input must be of type PlagResult.'
    if result == None:
        raise NoValidArgumentError, 'Input must be of type PlagResult not None.'
    
    maxX = result.getIdStringLength()[0]
    maxY = result.getIdStringLength()[1]
    
    #create image (B/W)
    img = Image.new("L", (maxX, maxY), 255)
    
    tiles = result.getTiles()
    
    for tile in tiles:
        for i in range(0, tile[2]):
            img.putpixel((tile[0]+i, tile[1]+i), 0)   
            
    if showIds:
        img = addIds(img, result.getIdentifier(), result.getIdStringLength())
        
    return img
    
    
def createDotplotFromStrings(s1, s2, w=1, k=1, id1="", id2 ="", showIdNums = False):
    """A Dotplot shows all w/k-matches (window of length w with k matches) 
        between two sequences - here two strings s1 and s2.
        
        For every window of length w with at least k matches a dot is drawn 
        otherwise it will be left blank.
        
        Values w and k should be at least w=k=1.
         
        Parts of this function are based on a file found here:
        lectures.molgen.mpg.de/Algorithmische_Bioinformatik_WS0405/zettel/1/dotplot.py
         
        (It's a solution of an assignment for a Bio-Informatics course.)
    """
    #check preconditions
    if s1 == None or s2 == None:
        raise NoValidArgumentError, 'Input must be of type string not None'
    elif type(s1) != type("") or type(s2) != type(""):
        raise NoValidArgumentError, 'Input must be of type string'
    
    s1list = s1.split()#s1.strip()
    s2list = s2.split()#s2.strip()

    m = len(s1list)
    n = len(s2list)

    # Create a (m - w + 1)x(n - w + 1) matrix initialized with 0s.
    dotplot = [[0 for j in range(n - w + 1)] for i in range(m - w + 1)]

    # For each position (i,j) in the matrix, count the
    # number of matches in a window of length w.
    for i in range(m - w + 1):
        for j in range(n - w + 1):
            count = 0
            for l in range(w):
                if s1list[i + l] == s2list[j + l]: count += 1
            dotplot[i][j] = (count >= k and 1 or 0)

    #create result image (b/w)
    img = Image.new("L", (m-w+1, n-w+1), 255)
    for row in xrange(0, m-w+1):
        for col in xrange(0, n-w+1):
            if dotplot[row][col] == 1:
                img.putpixel((row, col), 0)
    
    if showIdNums:
        img = addIds(img, [id1, id2], [m, n])
    
    #return image
    return img

def createDotplotFromStringList(strList, w=1, k=1, idList=[], showIdNums = False):
    """Creates an image with dotplots of the comparisons of each string in the 
        given String list strList.
    """
    #check preconditions
    if strList == None:
        raise NoValidArgumentError, 'Input must be a string list not None'
    elif type(strList) != type([]):
        raise NoValidArgumentError, 'Input must be of type list'
    else:
        for s in strList:
            if type(s) != type(""):
                raise NoValidArgumentError, 'Input list should only contain strings'

    #if only two strings are in list use createDotplotFromStrings
    if len(strList) == 2:
        return createDotplotFromStrings(strList[0], strList[1], w, k, idList[0], idList[1], showIdNums)

    #list with string lists
    sList = [s.split() for s in strList]
    
    #compute maxLength of image
    maxLength = reduce(lambda x, y: x -w + 1 + y + 1 , [len(s) for s in sList]) - 1 #added -w+1

    #compute sizes for each string list in sList
    sizes = [0]
    for lNr in xrange(0, len(sList)):
        list = [len(sList[listNr])-w+1 for listNr in xrange(0, lNr+1)] #added -w+1
        sizes.append(reduce(lambda x, y: x+y+1, list))
        
    #create image (B/W)
    img = Image.new("L", (maxLength, maxLength), 255)
    
    #draw borders to seperate the single dotplots
    for s in sizes[1:-1]:
        for x in xrange(0, maxLength):
            img.putpixel((x, s-1), 100)
            img.putpixel((s-1, x), 100)
    
    #draw the dotplots
    for l1Nr in xrange(0, len(sList)):
        for l2Nr in xrange(0, len(sList)):
            l1 = sList[l1Nr]
            l2 = sList[l2Nr]
            for s1Nr in xrange(0, len(l1)-w+1):    #added -w+1
                for s2Nr in xrange(0, len(l2)-w+1):    #added -w+1
                    count = 0
                    for l in range(w):
                        if l1[s1Nr+l] == l2[s2Nr+l]: count += 1
                    if count >= k:
                        img.putpixel((s1Nr+sizes[l1Nr], s2Nr+sizes[l2Nr]), 0)

    if showIdNums:
        img = addIds(img, idList, [len(s) for s in sList])

    #return image
    return img


#===============================================================================
#    HELPER FUNCTIONS
#===============================================================================
def addIds(img, idList, strLengthList, font=None):
    """Adds ids to the given image and returns it.
    
        Options: font - ImageFont   => if no font is set, 16pt Arial is used
    """
    #check preconditions
    if type(idList) != type([]) or type(strLengthList) != type([]):
        raise NoValidArgumentError, 'idList and strLengthList must be of type list []'
    elif len(idList) != len(strLengthList):
        raise AssertionError, 'idList and strLengthList must have the same size'
    elif len(idList)<2 or len(strLengthList)<2:
        raise AssertionError, 'idList and strLengthList must have a length > 2'
    
    #if no font is set use default font (Arial)
    if not font:
		font = ImageFont.load_default()

    #compute textsize for used font
    textsize = font.getsize("00")
    marginSpace = 10
    maxIdLength = computeMaxIdLength(set(idList), font)

    #create new Image (containing the ids + the old img with dotplots)
    if len(idList) == 2:
        x = img.size[0] + textsize[0] + (marginSpace*2)
        if x<(maxIdLength+(2*marginSpace)+textsize[0]):
            x = maxIdLength+(2*marginSpace)+textsize[0]
        #add extra space below for id legend
        y = img.size[1] + textsize[1] + (marginSpace*2) + ((marginSpace+textsize[1])*2)
        offset = (textsize[0]+marginSpace, textsize[1]+marginSpace)
    else:
        #add extra space for ids
        x = img.size[0] + textsize[0] + maxIdLength + (marginSpace*2)
        y = img.size[1] + textsize[1] + (marginSpace*2)
        offset = (textsize[0]+maxIdLength+marginSpace, textsize[1]+marginSpace)
        
    newImg = Image.new("L", (x, y), 255)
    #create a new draw instance on the new img
    draw = ImageDraw.Draw(newImg)
    
    #special case: two ids
    if len(idList) == 2:        
        #first id is above
        draw.text((textsize[0]+marginSpace+(strLengthList[0]/2), marginSpace/2), '1', font=font)
        #second id is to the left
        draw.text((marginSpace/2, textsize[1]+marginSpace+(strLengthList[1]/3)), '2', font=font)
        #draw id legend below
        draw.text((marginSpace, offset[1]+img.size[1]+marginSpace), "1 "+idList[0], font=font)
        draw.text((marginSpace, offset[1]+img.size[1]+(marginSpace*2)+textsize[1]), "2 "+idList[1], font=font)
    #more than 2 ids
    else:
        for n in xrange(0, len(strLengthList)):
            if n == 0:
                l = 0
            elif n == 1:
                l = strLengthList[0]
            else : l = reduce(lambda x, y: x+y, [strLengthList[i] for i in xrange(0, n)])
            xspace = l + strLengthList[n]/2
            yspace = l + strLengthList[n]/3
            #first id is above
            draw.text((offset[0]+xspace, marginSpace/2), str(n+1), font=font)
            #second id is to the left
            draw.text((marginSpace/2, offset[1]+yspace), str(n+1)+" "+idList[n], font=font)#str(n+1), font=font)            
        
    #add borders
    draw.rectangle([(offset[0]-2, offset[1]-2), (offset[0]+img.size[0]+1, offset[1]+img.size[1]+1)], fill=150)
    
    #paste image with dotplot on "id img"
    newImg.paste(img, (offset[0]-1, offset[1]-1))

    #release drawing instance
    del draw
    
    #return img
    return newImg
