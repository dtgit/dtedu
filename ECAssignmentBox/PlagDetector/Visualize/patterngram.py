# -*- coding: utf-8 -*-
# $Id: patterngram.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
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
#This module contains methods to create Categorical Patterngrams and Composite
#Categorical Patterngrams, from the paper "Using Visualization to Detect 
#Plagiarism in Computer Science Classes" from Randy L. Ribler and Marc Abrams, 
#2000.
#===============================================================================

from PIL import Image, ImageDraw, ImageFont
from Products.ECAssignmentBox.PlagDetector.Normalize import *
from Products.ECAssignmentBox.PlagDetector.Detection.algNGRAM import createNGrams
from Products.ECAssignmentBox.PlagDetector.errors import NoValidNormalizerNameError, NoValidArgumentError
from Products.ECAssignmentBox.PlagDetector.Helper.GraphicsHelper import rotText



#Constants
WORD = 0
CHAR = 1

#===============================================================================
#    Categorical Patterngram
#===============================================================================
def createCategoricalPatterngram(basefile, ensemble, klength, normName, mode=CHAR):
    """Creates a Categorical Patterngram as PIL Image object. It "shows
        the degree of similarity that exists between one file [(the base 
        file)] and the rest of the ensemble of files." (Rib00)
    
        basefile - the single file in the 'one-to-many' comparison
        ensemble - the set of files used for the comparison
        klength  - the length of the used ngrams
        normName - the name of the normalizer used to normalize the texts
        mode     - default: CHAR (=1); WORD (=0)
    
        "[A] categorical patterngram [...] [is] a visualization
        that displays, for each character position x in the the base
        file, the number of ensemble files that contain the k-length
        n-gram that begins at that position. A point is plotted at
        coordinate (x,y) if the k-length n-gram beginning at character
        x in the base file occurs at any location in y files of the 
        ensemble." (Rib00)
        
        Rib00 - "Using Visualization to Detect Plagiarism in Computer Science Classes",
        Randy L. Ribler, Marc Abrams, 2000
    """
    #check preconditions
    if type(basefile) != type(""):
        raise NoValidArgumentError, "basefile must be of type string"
    elif type(ensemble) != type([]):
        raise NoValidArgumentError, "ensemble must be of type list"
    elif type(klength) != type(1):
        raise NoValidArgumentError, "klength must be of type integer"
    elif klength<=0:
        raise NoValidArgumentError, "klength must be greater zero"
    elif not normName in normNames:
        raise NoValidNormalizerNameError(normName)
    
    #get Normalizer
    normalize = normNames.get(normName)
    
    #===init base file===
    #normalize base file
    normBase = normalize(basefile) 
    #create ngrams
    nGramDict = createNGrams(normBase, klength, mode=mode)
    #create array for base file ngrams to cnt occurencies in ensemble files
    if mode == WORD:
        occSize = len(normBase.split())-klength+1
    else:
        occSize = len(normBase)-klength+1
    nGramOccurencies = [0 for x in xrange(occSize)]
    
    #===check ensemble files===
    for text in ensemble:
#===============================================================================
#    for y in xrange(len(ensemble)):
#        text = ensemble[y]
#        if text == basefile:
#            subNr = y
#===============================================================================
        if text == basefile:
            continue
        #normalize text
        normText = normalize(text)
        #create ngrams
        textNGrams = createNGrams(text, klength, mode=mode)
        #check for common ngrams
        commonNGrams = set(nGramDict.keys()) & set(textNGrams.keys())
        #increase array for common ngrams
        for ngram in commonNGrams:
            for i in nGramDict.get(ngram):
                nGramOccurencies[i] += 1
        
    #===create CP Image===
    #init
    colorBG = (255, 255, 255)
    colorFG = (0, 0, 0)
    colorSelf = (0, 0, 200)
    colorInfrequently = (200, 0, 0)
    colorFrequently = (0, 200, 0)
    infrequent = 3
    maxNb = reduce(returnGreater, nGramOccurencies)
    ydist = 10
    maxY = (maxNb+2)*ydist
    img = Image.new("RGB", (len(nGramOccurencies), maxY), colorBG)
    draw = ImageDraw.Draw(img)
    
    #compute max nb files
    for x in xrange(len(nGramOccurencies)):
        yCoord = nGramOccurencies[x]+1
        y = maxY - (ydist*(yCoord))
        if yCoord == 1:
            color = colorSelf
        elif yCoord<=infrequent:
            color = colorInfrequently
        else: color = colorFrequently
        draw.line((x, y-(ydist-6), x, y+(ydist-6)), fill=color)
    
    #===paste img to chart pattern===
    img = createChart(img, maxNb+1, ydist, "N-gram starting character", "Nb of files containing n-gram", "Submission "+" (k="+str(klength)+")")
    
    #clean up
    del draw
    
    #return CP chart image
    return img

def returnGreater(x, y):
    """Returns the greater parameter."""
    if x>y: return x
    else: return y

#===============================================================================
#    Composite Categorical Patterngram
#===============================================================================
def createCompositeCategoricalPatterngram(basefile, ensemble, klength, normName, mode=CHAR):
    """Creates a Composite Categorical Patterngram as PIL Image object. It "shows
        which particular files are similar." (Rib00)
    
        basefile - the single file in the 'one-to-many' comparison
        ensemble - the set of files used for the comparison
        klength  - the length of the used ngrams
        normName - the name of the normalizer used to normalize the texts
        mode     - default: CHAR (=1); WORD (=0)
    
        A composite categorical patterngram is a visualization that displays, 
        for each character position x in the the base file, which file of the 
        ensemble files also contain the k-length n-gram that begins at that 
        position. "A point is plotted at (x,y) if the k-length n-gram beginning 
        at x in the base file occurs one or more times in file y." (Rib00)
        
        Rib00 - "Using Visualization to Detect Plagiarism in Computer Science Classes",
        Randy L. Ribler, Marc Abrams, 2000
    """
    #check preconditions
    if type(basefile) != type(""):
        raise NoValidArgumentError, "basefile must be of type string"
    elif type(ensemble) != type([]):
        raise NoValidArgumentError, "ensemble must be of type list"
    elif type(klength) != type(1):
        raise NoValidArgumentError, "klength must be of type integer"
    elif klength<=0:
        raise NoValidArgumentError, "klength must be greater zero"
    elif not normName in normNames:
        raise NoValidNormalizerNameError(normName, normNames)
    
    #get Normalizer
    normalize = normNames.get(normName)
    
    #===init base file===
    #normalize base file
    normBase = normalize(basefile) 
    #create ngrams
    nGramDict = createNGrams(normBase, klength, mode)

    #===create CPP Image===
    #init
    colorBG = (255, 255, 255)
    colorFG = (0, 0, 0)
    colorSelf = (0, 0, 200)
    colorInfrequently = (200, 0, 0)
    colorFrequently = (0, 200, 0)
    infrequent = 2
    ydist = 10
    if mode == WORD:
        maxX = len(normBase.split())-klength+1
    else:
        maxX = len(normBase)-klength+1
    maxY = (len(ensemble)+1)*ydist
    img = Image.new("RGB", (maxX, maxY), colorBG)
    draw = ImageDraw.Draw(img)
    subNr = ''
    
    #===check ensemble files===
    for y in xrange(len(ensemble)): # +2?
        text = ensemble[y]
        yPos = maxY - (ydist*(y+1))
        #if text is basefile mark with colorSelf in img
        if text == basefile:
            subNr = y+1
            for x in xrange(maxX):
                draw.line((x, yPos-(ydist-6), x, yPos+(ydist-6)), fill=colorSelf)
        #else 
        #for each text compute ngrams
        #compute common ngrams
        #draw corresponding lines for each common ngram colored aufter its
        #frequency
        else:
            #normalize text
            normText = normalize(text)        
            #create ngrams
            textNGrams = createNGrams(normText, klength, mode)
            #check for common ngrams
            commonNGrams = set(nGramDict.keys()) & set(textNGrams.keys())
            #draw for each common ngram the appropriate marking
            for ngram in commonNGrams:
                #for each position of the common ngram draw right marking
                for i in nGramDict.get(ngram):
                    #get occurencies of the ngram in the text
                    cntNgram = len(textNGrams.get(ngram))
                    #choose color for occurency
                    if cntNgram <= infrequent:
                        color = colorInfrequently
                    else:
                        color = colorFrequently
                    #draw line
                    draw.line((i, yPos-(ydist-6), i, yPos+(ydist-6)), fill=color)
                    
    #===paste img to chart pattern===
    img = createChart(img, len(ensemble), ydist, "N-gram starting character", "File number", "Submission nb: "+str(subNr)+" (k="+str(klength)+")")

    return img

#===============================================================================
#    Chart holding the CPs and CPPs
#===============================================================================
def createChart(img, yLevel, ydist, xlabel, ylabel, header,
		font=ImageFont.load_default()):
    """Creates the chart environment and pastes the given img onto it.
        
        Returns PIL image object showing a patterngram
    """
    #init
    colorBG=(255, 255, 255)
    colorFG=(0, 0, 0)
    margin = 50
    #create image
    chartImg = Image.new("RGB", (img.size[0]+(2*margin), img.size[1]+(2*margin)), colorBG)
    #paste image to chart
    chartImg.paste(img, (margin+1, margin+1))

    draw = ImageDraw.Draw(chartImg)
    
    #draw border
    borderY2 = img.size[1]+margin+1
    draw.rectangle(((margin, margin), (img.size[0]+margin+1, borderY2)), outline=colorFG)
    #x-label
    labelSize = computeLabelDist(img.size[0], mode=0)
    for x in xrange(img.size[0]):
        if x%100==0: 
            s = 4
        elif x%50==0: 
            s = 3
        elif x%10==0: 
            s = 2
        elif x%5==0: 
            s = 1
        else: 
            s = 0
        #draw upper border
        draw.line((x+margin, margin, x+margin, margin-s), fill=colorFG)
        #draw lower border
        draw.line((x+margin, borderY2, x+margin, borderY2+s), fill=colorFG)
        #draw labels
        if x%labelSize==0:
            label = str(x)
            pos = (margin + x - (font.getsize(label)[0]/2), borderY2+5)
            draw.text(pos, label, fill=colorFG, font=font)
    #y-label
    labelSize = computeLabelDist(yLevel, mode=1)
    for y in xrange(yLevel+1):
        if y%5==0:
            s = 3
        else:
            s = 1
        ypos = borderY2 - (y * ydist)
        #left border
        draw.line((margin-s, ypos, margin, ypos), fill=colorFG)
        #right border
        draw.line((margin+1+img.size[0], ypos, margin+1+img.size[0]+s, ypos), fill=colorFG)
        #draw labels
        if y%labelSize==0 and y!=0:
            label = str(y)
            pos = (margin - (font.getsize(label)[0]+4), borderY2-(y*ydist)-(font.getsize(label)[1]/2))
            draw.text(pos, label, fill=colorFG, font=font)
    
    #===draw labels===
    #xlabel
    draw.text((margin+(img.size[0]/2)-(font.getsize(xlabel)[0]/2), borderY2+(margin/2)), xlabel, fill=colorFG, font=font)
    #header
    draw.text((margin+(img.size[0]/2)-(font.getsize(header)[0]/2), margin/2), header, fill=colorFG, font=font)
    #ylabel
    yLabelImg = rotText(ylabel, font)
    chartImg.paste(yLabelImg, ((margin/2)-(yLabelImg.size[0]/2), margin+(img.size[1]/2)-(yLabelImg.size[1]/2)))
    
    #clean up
    del yLabelImg
    del draw
    del font
    
    #return created chart image
    return chartImg

#===============================================================================
#    Helper Methods
#===============================================================================
def computeLabelDist(length, mode):
    """Computes an appropriate Label distance to label an axis.
    """
    if mode == 0:
        if length<=10:
            return 5
        elif length <= 50:
            return 10
        elif length <= 100:
            return 25
        else:
            return 50
    elif mode == 1:
        if length<5:
            return 1
        else:
            return 5
    
    return None


#===============================================================================
#    Self Test
#===============================================================================
if __name__ == '__main__':
    print "CP and CPP Test\n==============="
    
    s1 = "dies ist nur ein kleiner test und ich hab dich so lieb"
    s2 = "ich hab dich so lieb ach ja und dies ist nur ein kleiner test kleiner test yeah mah bin ich toll wah oder so ne"
    s3 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\ndef mah():\n    s= 1+2\n    return s\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    s4 = 'print \'hello\'\n\ndef mah():    return \'nok\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    s5 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
    nonplag = "Ja mei wat is dat denn fuer a schmarrn ^^"
    minimal = "dich so lieb mau kau schuschu whoowhoo nur ein kleiner test"
    nurzuA = "dies ist nur test und ich"
    
    img = createCategoricalPatterngram(s1, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 3, "NORMAL", CHAR)
    img.show()

    img = createCategoricalPatterngram(s3, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 3, "NORMAL", CHAR)
    img.show()
    
    img = createCompositeCategoricalPatterngram(s4, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 3, "NORMAL", CHAR)
    img.show()
    
    img = createCompositeCategoricalPatterngram(s4, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 1, "NORMAL", CHAR)
    img.show()

    img = createCompositeCategoricalPatterngram(s4, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 10, "NORMAL", CHAR)
    img.show()

    img = createCompositeCategoricalPatterngram(s4, [s1, s2, s3, s4, s5, nonplag, minimal, nurzuA], 6, "NORMAL", CHAR)
    img.show()
