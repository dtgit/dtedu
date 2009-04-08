# -*- coding: utf-8 -*-
# $Id: XMLHelper.py,v 1.1 2007/07/02 14:40:22 peilicke Exp $
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
#This module contains methods to transform a PlagResult object to XMl and the
#other way around.
#===============================================================================

from Products.ECAssignmentBox.PlagDetector.PlagResult import PlagResult



#===============================================================================
#    XML IO
#===============================================================================
def resultToXML(result):
    """Returns a XML representation of the PlagResult object.
        
        @param result A PlagResult object.
        @return A XML string representation of the given PlagResult object.
    """
    tilesString = ""
    for tile in result.getTiles():
        tilesString += """    <Tile posId1="%d" posId2="%d" length="%d" />""" % tile
        
    xmlDoc = u"""<?xml version="1.0" encoding="utf-8"?>"""\
                 """<PlagResult>"""\
                 """  <Identifier Id1="%s" Id2="%s" />"""\
                 """  <Algorithm>%s</Algorithm>"""\
                 """  <Normalizer>%s</Normalizer>"""\
                 """  <Similarity>%f</Similarity>"""\
                 """  <SuspectedPlagiarism>%s</SuspectedPlagiarism>"""\
                 """  <Tiles>%s</Tiles>"""\
                 """  <IdStringLength lengthId1="%d" lengthId2="%d" />"""\
                 """</PlagResult>""" % (str(result.getIdentifier()[0]), 
                                        str(result.getIdentifier()[1]),
                                        result.getAlgorithmName(),
                                        result.getNormalizerName(),
                                        result.getSimilarity(),
                                        str(result.isSuspectPlagiarism()),
                                        tilesString,
                                        result.getIdStringLength()[0],
                                        result.getIdStringLength()[1]
                                        )
    xmlDoc.encode("utf-8")
    from xml.dom import minidom
    domObject = minidom.parseString(xmlDoc)
    root = domObject.documentElement
    return domObject.toprettyxml()

def resultFromXML(xmlString):
    """Returns a PlagResult object from the given XML representation.
    
        @param xmlString XML representation (whole file with a single PlagResult)
        @return A PlagResult object of the given XML representation.
    """
    from xml.dom import minidom
    dom_object = minidom.parseString(xmlString)
    
    #get all PlagResult tags in the XML representation
    list = dom_object.getElementsByTagName("PlagResult")
    
    #get the first PlagResult tag
    plagResultTag = list[0]
    
    #create a PlagResult object
    plagResult = PlagResult()
    
    #read attributes from XML and fill PlagResult
    plagResult.setIdentifier(plagResultTag.getElementsByTagName("Identifier")[0].getAttribute("Id1"), 
                             plagResultTag.getElementsByTagName("Identifier")[0].getAttribute("Id2"))
    plagResult.setAlgorithmName(plagResultTag.getElementsByTagName("Algorithm")[0].firstChild.data)
    plagResult.setNormalizerName(plagResultTag.getElementsByTagName("Normalizer")[0].firstChild.data)
    plagResult.setSimilarity(float(plagResultTag.getElementsByTagName("Similarity")[0].firstChild.data))
    plagResult.setSuspectedPlagiarism(bool(plagResultTag.getElementsByTagName("SuspectedPlagiarism")[0].firstChild.data))
    tileTags = plagResultTag.getElementsByTagName("Tiles")[0].getElementsByTagName("Tile")
    tiles = []
    for tileTag in tileTags:
        tile = (int(tileTag.getAttribute("posId1")), 
                int(tileTag.getAttribute("posId2")), 
                int(tileTag.getAttribute("length")))
        tiles.append(tile)
    plagResult.setTiles(tiles)
    plagResult.setIdStringLength(int(plagResultTag.getElementsByTagName("IdStringLength")[0].getAttribute("lengthId1")), 
                             int(plagResultTag.getElementsByTagName("IdStringLength")[0].getAttribute("lengthId2")))
    

    return plagResult

#===============================================================================
#    Test
#===============================================================================
if __name__ == '__main__':
    print "Start Test - Transfrom PlagResult to XML and Back"
    #create Test PlagResult
    plagResult = PlagResult("Test1", "Test2")
    plagResult.setAlgorithmName("NGRAM")
    plagResult.setNormalizerName("NORMAL")
    plagResult.setSimilarity(0.65)
    plagResult.setSuspectedPlagiarism(True)
    plagResult.setIdStringLength(52, 45)
    plagResult.setTiles([(3,5,4),(12,23,5),(34,2,3)])
    
    #test transfrom to xml and back should result in the same PlagResult object
    result = resultFromXML(resultToXML(plagResult))
    
    assert plagResult.__eq__(plagResult), "plagResult changed through transformation to xml and back"
    print "End Test - Transfrom PlagResult to XML and Back"
