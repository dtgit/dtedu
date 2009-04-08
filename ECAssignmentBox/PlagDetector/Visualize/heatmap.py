# -*- coding: utf-8 -*-
# $Id: heatmap.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
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
#This module provides two methods which create heatmap charts, i.e. cell charts 
#indicating e.g. intensity or clusters by different coloring the cells. Each 
#cell represents a mapped value for a single plagiarism pair.
#===============================================================================

from PIL import Image, ImageDraw, ImageFont
from Products.ECAssignmentBox.PlagDetector.Helper.PlagResultListHelper import (getClusters,
                                                      getClusterNr,
                                                      getPositiveResults, 
                                                      getIdentifier)
from Products.ECAssignmentBox.PlagDetector.Helper.GraphicsHelper import (createXDifferentColors,
                                          getColorForScope,
                                          computeMaxIdLength, 
                                          rotText)



def createIntensityHeatmap(resultList, scopes=[0.2, 0.4, 0.6, 0.8, 1], recSize = 20, onlyPositiveResults=True):
    """Creates a heatmap chart showing the intensity of plagiarism in for the 
        given results.
    """
    #===create intensity matrix===
    if onlyPositiveResults:
        results = getPositiveResults(resultList)
    else:
        results = resultList
        
    if not results:
        return None
    
    intensityDict = {}
    xDict = {}
    yDict = {}
    for r in results:
        rIds = r.getIdentifier()
        intensityDict.setdefault(tuple(rIds), r.getSimilarity())
        if (not xDict.has_key(rIds[0]) and not yDict.has_key(rIds[1])
            and not yDict.has_key(rIds[0]) and not xDict.has_key(rIds[1])):
            xDict.setdefault(rIds[0], len(xDict))
            yDict.setdefault(rIds[1], len(yDict))
        elif xDict.has_key(rIds[0]) and not yDict.has_key(rIds[1]):
            yDict.setdefault(rIds[1], len(yDict))
        elif not xDict.has_key(rIds[0]) and yDict.has_key(rIds[1]):
            xDict.setdefault(rIds[0], len(xDict))
        elif yDict.has_key(rIds[0]) and not xDict.has_key(rIds[1]):
            xDict.setdefault(rIds[1], len(xDict))
        elif not yDict.has_key(rIds[0]) and xDict.has_key(rIds[1]):
            yDict.setdefault(rIds[0], len(yDict))

    matrix = [[0 for x in xDict] for y in yDict]
    
    xLabelList = xDict.keys()
    xLabelList.sort()
    yLabelList = yDict.keys()
    yLabelList.sort()
    for y in xrange(len(yLabelList)):
        for x in xrange(len(xLabelList)):
            xL = xLabelList[x]
            yL = yLabelList[y]
            val = intensityDict.get((xL, yL))
            if not val:
                val = intensityDict.get((yL, xL))
            matrix[y][x] = val

    #===init===
	font = ImageFont.load_default()

    #color init
    colorImgFG = (0,0,0)
    colorImgBG = (255,255,255)
    colorChartBG = (230, 230, 230)
    colorGrid = (100,100,100)

    #create heatmap img   
    img = createHeatmapChart(matrix,
                             xLabelList, 
                             yLabelList, 
                             recSize = recSize, 
                             font = font)
    
    maxX = img.size[0]
    maxY = img.size[1]
    
    #add legend
    legendimg = createLegend(scopes, maxY, font, colorImgBG, colorImgFG)
    newImg = Image.new("RGB", (maxX+legendimg.size[0], maxY))
    newImg.paste(img, (0,0))
    newImg.paste(legendimg, (img.size[0]+1, 0))
    
    #clean up
    del font
    
    #return img
    return newImg

def createClusterHeatmap(resultList, recSize = 20, onlyPositiveResults=True):
    """Creates a heatmap chart showing the clusters found in the given results.
    """
    #===create cluster matrix===
    if onlyPositiveResults:
        #get all postive Results
        results = getPositiveResults(resultList)
    else:
        results = resultList
        
    if not results:
        return None

    #extract ids and clusters
    ids = getIdentifier(results)
    ids.sort()
    clusters = getClusters(results)
    print str(clusters)
    #create matrix
    matrix = [[0 for x in ids] for y in ids]
    
    for y in xrange(len(ids)):
        for x in xrange(len(ids)):
            xL = ids[x]
            yL = ids[y]
            if x!=y:
                val = getClusterNr(xL, yL, clusters)
            else: val = None
            matrix[y][x] = val

    #===init===
	font = ImageFont.load_default()
    scopes = [(i+0.5) for i in xrange(len(clusters)+1)]
    print scopes
    #color init
    colorImgFG = (0,0,0)
    colorImgBG = (255,255,255)
    colorChartBG = (230, 230, 230)
    colorGrid = (100,100,100)

    #create heatmap img   
    img = createHeatmapChart(matrix,
                             ids, 
                             ids,
                             scopes = scopes,
                             recSize = recSize, 
                             font = font)
    
    maxX = img.size[0]
    maxY = img.size[1]
    
    #add legend
#===============================================================================
#    legendimg = createLegend(scopes, maxY, font, colorImgBG, colorImgFG)
#    newImg = Image.new("RGB", (maxX+legendimg.size[0], maxY))
#    newImg.paste(img, (0,0))
#    newImg.paste(legendimg, (img.size[0]+1, 0))
#===============================================================================
    
    #clean up
    del font
    
    #return img
#    return newImg
    return img


#===============================================================================
#    Creation of the Heatmap Chart
#===============================================================================
def createHeatmapChart(matrix, xLabels, yLabels, scopes = [0.2, 0.4, 0.6, 0.8, 1], 
                       recSize = 20, colorBG = (255, 255, 255), colorFG = (0, 0, 0), 
                       colorChartBG = (230, 230, 230), colorGrid = (100, 100, 100),
					   font = ImageFont.load_default()):
    """Creates a heatmap chart for the given values in the matrix labeled with the labels
        given in xDict and yDict TODO:
        
        options:
            - scopes - list of values that describe the scopes for the matrix values,
                        e.g. scopes = [0.2, 0.4, 0.6, 0.8, 1] (default)
            - font - font used
            - recSize - size of a single indicator rectangle in the heatmap
            - colorBG - background color of the chart as rgb value (default: (255, 255, 255))
            - colorFG - foreground color of the chart as rgb value (default: (0, 0, 0))
            - colorChartBG - background color of the chart as rgb value (default: (230, 230, 230))
            - colorGrid - color of the grid as rgb value (dafault: (100, 100, 100)); if set to
                            "None" no grid will be drawn
    """
    #===init===
    #margin to left and bottom
    margin = 5
    #maximal identifier length 
    maxIdLength = computeMaxIdLength(set(xLabels+yLabels), font)
    #size of the img
    maxX = margin + maxIdLength + ((len(xLabels)+2) * recSize)
    maxY = margin + maxIdLength + (len(yLabels)+2) * recSize
    #lower left corner fo the chart
    offset = (margin+maxIdLength+4, maxY-maxIdLength-margin)
    
    #===create img===
    img = Image.new("RGB", (maxX, maxY), colorBG)
    draw = ImageDraw.Draw(img)
    
    #draw chart background
    draw.rectangle((offset, (offset[0]+((len(xLabels)+1)*recSize), offset[1]-((len(yLabels)+1)*recSize))), fill=colorChartBG)
    
    #draw heatmap
    for row in xrange(len(matrix)):
        for col in xrange(len(matrix[0])):
            pos = (offset[0]+col*recSize, offset[1]-row*recSize, offset[0]+(col+1)*recSize, offset[1]-(row+1)*recSize)
            fill = getColorForScope(matrix[row][col], scopes, colorChartBG)
            draw.rectangle(pos, fill=fill)
    
    #draw grid
    #x-axis
    for i in xrange(len(yLabels)+1):
        yPos = offset[1]-((i+1)*recSize)
        draw.line(((offset[0], yPos), (offset[0]+recSize*(len(xLabels)+1), yPos)), fill=colorGrid)
    #y-axis
    for i in xrange(len(xLabels)+1):
        draw.line(((offset[0]+(i+1)*recSize, offset[1]), (offset[0]+(i+1)*recSize, offset[1]-recSize*(len(yLabels)+1))), fill=colorGrid)
    
    #draw axes
    #x-axis
    draw.line((offset, (offset[0]+recSize*(len(xLabels)+1), offset[1])), fill=colorFG)
    for i in xrange(len(xLabels)):
        draw.line(((offset[0]+recSize/2+i*recSize, offset[1]-2),(offset[0]+recSize/2+i*recSize, offset[1]+2)), fill=colorFG)
    #y-axis
    draw.line((offset, (offset[0], offset[1]-recSize*(len(yLabels)+1))), fill=colorFG)
    for i in xrange(len(yLabels)):
        draw.line(((offset[0]-2, offset[1]-(recSize/2+i*recSize)),(offset[0]+2, offset[1]-(recSize/2+i*recSize))), fill=colorFG)
    
    #draw ids
    for i in xrange(len(yLabels)):
        name = yLabels[i]
        pos = i
        draw.text((margin, offset[1]-((pos+1)*recSize)), name, font=font, fill=colorFG)
    for i in xrange(len(xLabels)):
        name = xLabels[i]
        pos = i
        img.paste(rotText(name, font=font, colorBG=colorBG, colorFG=colorFG), (offset[0]+(recSize/5)+((pos)*recSize), offset[1]+2))

    #clean up
    del draw

    #return heatmap chart img
    return img


    
def createLegend(scopes, imgheight, font, colorBG=(240,240,240), colorFG=(0,0,0)):
    """Creates a lengend for the scopes. 
    
        color <> scope
    """
    #compute new img font size
    fsize = font.getsize("T")
    fh = fsize[1] * (len(scopes)+1) * 2
    if fh > imgheight:
        fh = imgheight / ((len(scopes)+1) * 2)
        font = ImageFont.truetype(font.getname()[0]+".ttf", fh)
        fsize = font.getsize("T")
    imgwidth = 80
    margin = 3
    img = Image.new("RGB", (imgwidth, imgheight), colorBG)
    draw = ImageDraw.Draw(img)
    
    draw.text((margin, margin), "Legend:", fill=colorFG, font=font)
    
    colors = createXDifferentColors(len(scopes))
    offset = (margin, margin+fsize[1])
    for i in xrange(len(scopes)):
        #draw color
        draw.rectangle((offset[0]+margin, 
                        offset[1]+(fsize[1]*(i+1)*1.5),
                        offset[0]+margin+fsize[1],
                        offset[1]+(fsize[1]*(i+1)*1.5)+fsize[1]), fill=colors[len(scopes)-(i+1)])
        #draw text
        draw.text((offset[0]+2*margin+fsize[1], 
                        offset[1]+(fsize[1]*(i+1)*1.5)), 
                        text=" <= " + str(scopes[len(scopes)-(i+1)]),
                        fill=colorFG, font=font)
#===============================================================================
#    offset = (margin, imgheight-margin)
#    for i in xrange(len(scopes)):
#        #draw color
#        draw.rectangle((offset[0]+margin, 
#                        offset[1]-(fsize[1]*(i+1)*1.5),
#                        offset[0]+margin+fsize[1],
#                        offset[1]-(fsize[1]*(i+1)*1.5)+fsize[1]), fill=colors[i])
#        #draw text
#        draw.text((offset[0]+2*margin+fsize[1], 
#                        offset[1]-(fsize[1]*(i+1)*1.5)), 
#                        text=" <= " + str(scopes[i]),
#                        fill=colorFG, font=font)
#===============================================================================
        
    #clean up
    del draw
    
    #return image
    return img

#===============================================================================
#    Test
#===============================================================================
if __name__ == '__main__':
    A = "dies ist nur ein kleiner test und ich hab dich so lieb"
    B = "ich hab dich so lieb ach ja und dies ist nur ein kleiner test kleiner test yeah mah bin ich toll wah oder so ne"
    s5 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\ndef mah():\n    s= 1+2\n    return s\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    s6 = 'print \'hello\'\n\ndef mah():    return \'nok\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    s7 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    nonplag = "Ja mei wat is dat denn fuer a schmarrn ^^"
    minimal = "dich so lieb mau kau schuschu whoowhoo nur ein kleiner test"
    nurzuA = "dies ist nur test und ich"

    stringList = [A, B, nurzuA]
    idList = ["student01", "student02", "student03"]
    from PlagDetector.PlagChecker import PlagChecker
    checker = PlagChecker()
    resultList = checker.compareList(stringList, idList, 3)
    for r in resultList:
        print r

#===============================================================================
#    img = createIntensityHeatmap(resultList)
#    img.show()
#===============================================================================
    img = createClusterHeatmap(resultList)
    img.show()


    stringList = [A, B, s5, s6, s7, nonplag, minimal]
    idList = ["student01", "student02", "student03", "student04", "student05", "student06", "student07"]
    from PlagDetector.PlagChecker import PlagChecker
    checker = PlagChecker()
    resultList = checker.compareList(stringList, idList, 3)
    for r in resultList:
        print r

#===============================================================================
#    img = createIntensityHeatmap(resultList)
#    img.show()
#===============================================================================
    img = createClusterHeatmap(resultList)
    img.show()

    stringList = [A, B, s5, s6, s7, nonplag, minimal, A, B, s5, s6, s7, nonplag, minimal]
    idList = ["student01", "student02", "student03", "student04", "student05", "student06", "student07",
              "student08", "student09", "student10", "student11", "student12", "student13", "student14"]
    from PlagDetector.PlagChecker import PlagChecker
    checker = PlagChecker()
    resultList = checker.compareList(stringList, idList, 3)
#===============================================================================
#    for r in resultList:
#        print r
#===============================================================================
    for r in [r for r in resultList if r.isSuspectPlagiarism()]:
        print r

    img = createIntensityHeatmap(resultList)
    img.show()
    img = createClusterHeatmap(resultList)
    img.show()

    
#===============================================================================
#    img = rotText("student07", font=ImageFont.truetype("Vera.ttf", 16))
#    img.show()
#===============================================================================
    
#===============================================================================
#    blankimg = Image.new("L", (100, 100), 255)
#    blankimg.paste(img, (50, 50))
#    blankimg.show()
#===============================================================================
#    img = createIntensityHeatmap(resultList)
#    img.show()
#===============================================================================
#    legend = createLegend([0.2,0.4,0.6,0.8,1], 200, font=ImageFont.truetype("Vera.ttf", 14))
#    legend.show()
#===============================================================================
