# -*- coding: utf-8 -*-
# $Id: torc.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
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
#A Torc is a kind of overview which allows the user to recognize the similarity
#relations between different texts. Therefore all texts are arranged on a circle.
#For each relation of similarity between two texts a connecting line is drawn.
#===============================================================================

from PIL import Image, ImageDraw, ImageFont
from math import *
from Products.ECAssignmentBox.PlagDetector.errors import NoValidArgumentError
from Products.ECAssignmentBox.PlagDetector.PlagResult import PlagResult
from Products.ECAssignmentBox.PlagDetector.Helper.GraphicsHelper import computeMaxIdLength, getColorForScope
from Products.ECAssignmentBox.PlagDetector.Helper.PlagResultListHelper import getClusters, getClusterNr



def resultsToTorc(resultList, colored=False):
    """Takes the result and returns an image showing a Torc indicating the
        similarity relations of the compared texts in the results.
        
        A Torc is a kind of overview which allows the user to recognize the similarity
        relations between different texts. Therefore all texts are arranged on a circle.
        For each relation of similarity between two texts a connecting line is drawn.
    """
    #check preconditions
    if type(resultList) != type([]):
        raise NoValidArgumentError, 'Input must be of type list'
    elif len(resultList) == 0:
        return None
    else:
        for result in resultList:
            if type(result) != type(PlagResult()):
                raise NoValidArgumentError, 'Input list should only contain values of type PlagResult.'
    #1. get all identifiers of the results
    idSet = set()
    for result in resultList:
        for id in result.getIdentifier():
            idSet.add(id)
    idSet = list(idSet)
    idSet.sort()
            
    #2. create a circle with a size depending on the number of identifier
    font = ImageFont.load_default()
    freespace = computeMaxIdLength(idSet, font)
    margin = 10
    radius = computeRadius(len(idSet)) # computes radius depending on number of ids
    xM = freespace + radius + margin    #middle x pos of circle
    yM = freespace + radius + margin   #middle y pos of circle
    img = Image.new('RGB', (2*xM, 2*yM), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.arc((freespace+margin, freespace+margin, freespace+margin+(2*radius), freespace+margin+(2*radius)), 0, 360, fill = (150, 150, 150))
    
    #3. arrange the ids along the circle and save the coordinates for each id
    distToNextId = 360 / len(idSet)
    angles = range(0, 360, distToNextId)
    idPosDict = {}
    for idNr in xrange(0, len(idSet)):
        # x = xM + r * cos phi und y = yM + r * sin phi
        pos = (xM + (radius * cos(radians(angles[idNr]))), 
               yM + (radius * sin(radians(angles[idNr]))))
        idPosDict.setdefault(idSet[idNr], pos)
    
    # use a truetype font and draw the id names
    for id in idPosDict:
        draw.text(computeFontPos(font, draw, str(id), idPosDict.get(id), xM, yM), 
                  str(id), 
                  font=font,
                  fill = (0, 0, 0))
    
    #4. walk through the results and plot the similarity relations as lines between the Ids
    if colored:
        #TODO: Params von aussen eingeben?
        clusters = getClusters(resultList, onlyPositives=False, onlyNonZeroSimilarities=False)

    for result in resultList:
        if result.isSuspectPlagiarism():
            ids = result.getIdentifier()
            if colored:
                color = getColorForScope(getClusterNr(ids[0], ids[1], clusters), range(len(clusters)))
            else:
                color = (0,0,0)
            draw.line([idPosDict.get(ids[0]), idPosDict.get(ids[1])], fill = color)
        
    del draw #free draw instance
   
    #5. return the image
    return img

def computeRadius(x):
    """ Computes a radius depending on the number of ids x given.
    """
    if x <=6:
        return 50
    else:
        return x*15
    
def computeFontPos(font, draw, idText, pos, xM, yM):
    """Rearranges the ids text position depending on its postion on the circle.
        Returns new id postion -> (x, y)
    """
    newPos = [pos[0], pos[1]]
    textsize = draw.textsize(str(idText), font=font)
    space = 5
    #check x arrangement
    if pos[0] < xM:
        #move id to the left out of the circle
        newPos[0] -= textsize[0]+space
    elif pos[0] > xM:
        newPos[0] += space
    #check y arrangement
    if pos[1] < yM:
        #move id up out of the circle
        newPos[1] -= textsize[1]+space
    elif pos[1] > yM:
        newPos[1] += space
    
    return tuple(newPos)
