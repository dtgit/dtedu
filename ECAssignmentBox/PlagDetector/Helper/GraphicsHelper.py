# -*- coding: utf-8 -*-
# $Id: GraphicsHelper.py,v 1.1 2007/07/02 14:40:22 peilicke Exp $
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
#This module provides several methods to access informations that are contained
#in a list of PlagResult objects.
#It also cintains several methods to suppor creating the visualizations.
#===============================================================================

#===============================================================================
#    Helper Methods for Visualizations
#===============================================================================

from PIL import Image, ImageFont, ImageDraw

def computeMaxIdLength(idSet, font):
    """Computes the maximal length of an id and returns it."""
    #max length of texts per default set to 50 pixel
    maxLength = 50
    #search for biggest textsize
    for id in idSet:
        textsize = font.getsize(str(id))
        if maxLength < textsize[0]:
            maxLength = textsize[0]

    #return maximal length        
    return maxLength

def rotText(text, font, colorBG=(255, 255, 255), colorFG=(0,0,0)):
    """Dreht den text um 90 grad entgegen den Uhrzeigersinn 
        und gibt ihn als PIL image object wieder.
    """
    tsize = font.getsize(text)
    img = Image.new("RGB", (tsize[0]+20, tsize[1]+20), colorBG)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10) , text, fill=colorFG, font=font)
    img = img.rotate(90)
    return img.crop((10, 10, 10+tsize[1], 10+tsize[0]))

def getColorForScope(val, scopes, defaultcolor=(255,255,255)):
    """Returns a int RGB color (r, g, b) for a given value according
        to the given scopes.
    
        val - value which is compard to values in scopes and
                corresponding scope color is returned
        scope - a list defining scopes, e.g. [0.2,0.4,0.6,0.8,1]
        defaultcolor - returned if val == None 
                        or if val is out of scope
    """
    if val == None:
        return defaultcolor
    colors = createXDifferentColors(len(scopes))
    for i in xrange(len(scopes)):
        if val<=scopes[i]:
            return colors[i]
        
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

