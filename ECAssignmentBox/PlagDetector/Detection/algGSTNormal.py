# -*- coding: utf-8 -*-
# $Id: algGSTNormal.py,v 1.1 2007/07/02 14:40:20 peilicke Exp $
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
#Takes two strings as input and returns a PlagResult object containing the 
#result of the comparison including a similarity value, the identifier of the 
#two strings, and the found similarites as a list of 'tiles' (tile: a tile is
#a tuple (startFirstText, startSecoundText, length) that describes the position
#of the found similarity.
#
#This Algorithm uses nGrams for the comparison. For more Information about the 
#algorihtm please look up the documetation.
#
#Good Tresholds values: 
#         0.5 simple but good indicator value
#
#Behaviour:
#- Input: normal Input -> return correct filled PlagResult
#- Input: other than two Strings -> NoValidArgumentError
#- Input: one of the Strings is empty -> return initialized 'empty' PlagResult
#- Input: two empty Strings -> return initialized 'empty' PlagResult
#- if minimumMatchingLength<1 -> OutOfRangeError
#- if treshold<0 or >1 -> OutOfRangeError 
#===============================================================================

from Products.ECAssignmentBox.PlagDetector.errors import NoValidArgumentError, OutOfRangeError
from Products.ECAssignmentBox.PlagDetector.PlagResult import PlagResult



def run(s1, s2, mML=3, treshold=0.5):
    """Normal Version of GST
    
        Input:  s1 and s2 : normalized Strings  
                mML : minimumMatchingLength
                treshold : a single value between 0 and 1
        Output: PlagResult
    """
    #check if the preconditions are fullfilled
    if mML<1: 
        raise OutOfRangeError, 'minimum Matching Length mML needs to be greater than 0'
    if not (0 <= treshold <= 1): 
        raise OutOfRangeError, 'treshold t needs to be 0<=t<=1'
    if s1 == None or s2 == None: 
        raise NoValidArgumentError, 'input must be of type string not None'
    if type(s1) != type('') or type(s2) != type(''): 
        raise NoValidArgumentError, 'input must be of type string'
    if s1 == '' or s2 == '':
        return PlagResult(hash(s1), hash(s2)) #TODO: Identifierbildung ueberdenken..
    
    #compute tiles
    tiles = []
    tiles = GSTSim(s1, s2, mML)

    #compute similarity
    simResult = calcSimilarity(s1.split(), s2.split(), tiles, treshold)
    similarity = simResult[0]
    if similarity>1: similarity = 1
    
    #create PlagResult and set attributes
    result = PlagResult()
    result.setIdentifier(hash(s1), hash(s2))
    result.setTiles(tiles)
    result.setSimilarity(similarity)
    result.setSuspectedPlagiarism(simResult[1])
    
    #return result of similarity check as PlagResult object
    return result


#================
#===NORMAL_GST===
#================
def GSTSim(s1, s2, minimalMatchingLength):
    """Greedy-String-Tiling Algorithm
    
        More Informations can be found here:
        "String Similarity via Greedy String Tiling and Running 
        Karp-Rabin Matching"
        http://www.pam1.bcs.uwa.edu.au/~michaelw/ftp/doc/RKR_GST.ps
        "YAP3: Improved Detection of Similarities in Computer Program 
        and other Texts"
        http://www.pam1.bcs.uwa.edu.au/~michaelw/ftp/doc/yap3.ps
    """
    #note s1 and s2 are already preprocessed strings
    s1list = s1.split()
    s2list = s2.split()
    s1PosList = range(len(s1list))
    s2PosList = range(len(s2list))
    tiles = set([])
    while 1:
        maxmatch = minimalMatchingLength
        matches = []
        
        for posS1 in s1PosList:    #hier wird nur einmal ueber komplette liste iteriert
        #for posS1 in [i for i in xrange(0, len(s1list)) if s1list[i][0] != '*']: #hier wird erst ueber komplette liste und dann ueber neue liste iteriert
            #if s1list[posS1][0] == '*': continue#testweise
            for posS2 in s2PosList:
                j = 0
                #if not marked or out of bounds
                while (posS1+j < len(s1list) and posS2+j < len(s2list) 
                       and (s1list[posS1+j] == s2list[posS2+j]) 
                       and (s1list[posS1+j][0] != '*') and (s2list[posS2+j][0] != '*')): 
                    j = j+1
                if j == maxmatch:
                    matches.append((posS1, posS2, j))
                elif j>maxmatch:
                    matches = [(posS1, posS2, j)]
                    maxmatch = j
        #mark matched words and add match to tiles
        for posS1, posS2, j in matches:
            for i in xrange(0, maxmatch):
                s1list[posS1+i] = '*' + s1list[posS1+i]
                s2list[posS2+i] = '*' + s2list[posS2+i]
                try:
                    s1PosList.remove(posS1+i)
                except ValueError: pass
                try:
                    s2PosList.remove(posS2+i)
                except ValueError: pass
            tiles = tiles | set([(posS1, posS2, j)])
        #Abbruchbedingung
        if (maxmatch == minimalMatchingLength):
            break
    return list(tiles)
#===============================================================================
#def GSTSim(s1, s2, minimalMatchingLength):
#    """Greedy-String-Tiling Algorithm
#    
#        More Informations can be found here:
#        "String Similarity via Greedy String Tiling and Running 
#        Karp-Rabin Matching"
#        http://www.pam1.bcs.uwa.edu.au/~michaelw/ftp/doc/RKR_GST.ps
#        "YAP3: Improved Detection of Similarities in Computer Program 
#        and other Texts"
#        http://www.pam1.bcs.uwa.edu.au/~michaelw/ftp/doc/yap3.ps
#    """
#    #note s1 and s2 are already preprocessed strings
#    s1list = s1.split()
#    s2list = s2.split()
#    tiles = set([])
#    while 1:
#        maxmatch = minimalMatchingLength
#        matches = []
#        
#        for posS1 in range(0, len(s1list)):    #hier wird nur einmal ueber komplette liste iteriert
#        #for posS1 in [i for i in xrange(0, len(s1list)) if s1list[i][0] != '*']: #hier wird erst ueber komplette liste und dann ueber neue liste iteriert
#            if s1list[posS1][0] == '*': continue#testweise
#            for posS2 in xrange(0, len(s2list)):
#                j = 0
#                #if not marked or out of bounds
#                while (posS1+j < len(s1list) and posS2+j < len(s2list) 
#                       and (s1list[posS1+j] == s2list[posS2+j]) 
#                       and (s1list[posS1+j][0] != '*') and (s2list[posS2+j][0] != '*')): 
#                    j = j+1
#                if j == maxmatch:
#                    matches.append((posS1, posS2, j))
#                elif j>maxmatch:
#                    matches = [(posS1, posS2, j)]
#                    maxmatch = j
#        #mark matched words and add match to tiles
#        for posS1, posS2, j in matches:
#            for i in xrange(0, maxmatch):
#                s1list[posS1+i] = '*' + s1list[posS1+i]
#                s2list[posS2+i] = '*' + s2list[posS2+i]
#            tiles = tiles | set([(posS1, posS2, j)])
#        #Abbruchbedingung
#        if (maxmatch == minimalMatchingLength):
#            break
#    return list(tiles)
#===============================================================================

#===============================================================================
#    Computation of the Similarity
#===============================================================================
def calcSimilarity(s1List, s2List, tiles, treshold):
    """Calculates Similarity and returns list [similarity:float, suspectedPlagiarism:bool]"""
    #compute similarity
    similarity = sim(s1List, s2List, tiles)
    
    #check if it is suspected plagiarism
    suspPlag = similarity >= treshold
    
    return [similarity, suspPlag]

def sim(A, B, tiles):
    """Returns similarity value for token of text A and B and the similary tiles covered.
    """
    return float(2 * coverage(tiles)) / float(len(A) + len(B))

def coverage(tiles):
    """Sum of length of all tiles.
    """
    accu = 0
    for tile in tiles:
        accu = accu + tile[2]
    return accu
