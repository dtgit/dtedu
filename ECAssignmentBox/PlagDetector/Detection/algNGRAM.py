# -*- coding: utf-8 -*-
# $Id: algNGRAM.py,v 1.1 2007/07/02 14:40:20 peilicke Exp $
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
#    Resemblance: 0.03
#    Containment: 0.31
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



def run(s1, s2, mML=3, treshold=[0.03, 0.31]):
    """This method runs a comparison on the two given strings s1 and s2 returning
        a PlagResult object containing the similarity value, the similarities as 
        list of tiles and a boolean value indicating suspected plagiarism.
    
        Input:  s1 and s2 : normalized Strings  
        
                Options:
                ========
                    mML      : minimumMatchingLength
                    treshold : could be a single number(Resemblance) 
                                or a list of two numbers(Resemblance 
                                and Containment)
        Output: PlagResult
    """
    #check if the preconditions are fullfilled
    if mML<1: 
        raise OutOfRangeError, 'minimum Matching Length mML needs to be greater than 0'
    if type(treshold) == type([]):
        if len(treshold) != 2:
            raise AssertionError, 'Treshold must be a  single Value (Resemblance) or a list of two Values [Resemblance, Containment]'
        elif not (0 <= treshold[0] <= 1) or not (0 <= treshold[1] <= 1):
            raise OutOfRangeError, 'tresholds values need to be 0<=t<=1'
    elif not (0 <= treshold <= 1): 
        raise OutOfRangeError, 'treshold t needs to be 0<=t<=1'
    if s1 == None or s2 == None: 
        raise NoValidArgumentError, 'input must be of type string not None'
    if type(s1) != type('') or type(s2) != type(''): 
        raise NoValidArgumentError, 'input must be of type string'
    if s1 == '' or s2 == '':
        return PlagResult(hash(s1), hash(s2)) #TODO: Identifierbildung ueberdenken..
    
    #create NGrams for strings
    ngramDict1 = createNGrams(s1, mML)
    ngramDict2 = createNGrams(s2, mML)
    
    #no nGrams found -> return empty initialized PlagResult
    if ngramDict1 == {} or ngramDict2 == {}:
        return PlagResult(hash(s1), hash(s2))
    
    #compute similarity
    simResult = calcSimilarity(set(ngramDict1.keys()), set(ngramDict2.keys()), treshold)
    similarity = simResult[0]
    
    #compute tiles
    tiles = calcTiles(ngramDict1, ngramDict2, simResult[1], mML)
    
    #create PlagResult and set attributes
    result = PlagResult()
    result.setIdentifier(hash(s1), hash(s2))
    result.setTiles(tiles)
    result.setSimilarity(similarity)
    result.setSuspectedPlagiarism(simResult[2])
    result.setIdStringLength(len(s1.split()), len(s2.split()))
    
    #return result of similarity check as PlagResult object
    return result

def createNGrams(string, n, mode = 0):
    """Returns a dictonary with Strings each containing n strings and 
        a list of the occurencies in the original string
        
        Options:
            mode - 0 create word ngrams; 1 create character ngrams
    """
    if mode == 0:
        wordList = string.split()
        sep = ' '
    elif mode == 1:
        wordList = string
        sep = ''
    else:
        raise NoValidArgumentError, "mode must be 0 (word ngrams) or 1 (character ngrams)"
    returnDict = {}
    cnt = 1
    s = ''
    for i in xrange(len(wordList)):
        if i+n>len(wordList):
            break
        for j in xrange(i, i+n):
            s = s + wordList[j] + sep
#        returnList.append(s.strip())
        if returnDict.has_key(s):    # if dict contains key add pos
            list = returnDict.get(s)
            list.append(i)
            #not needed -> returnDict.setdefault(s, list)
        else:                        # otherwise create new dict entry
            returnDict.setdefault(s, [i])
        s = ''
    return returnDict

#===============================================================================
#    Computation of the Similarity
#===============================================================================
def calcSimilarity(A, B, treshold):
    """Calculates Similarity and returns list [similarity, nGramsList]"""
    #compute Containment
    if len(A) > len(B):
        c = calcContainment(A, B)
    else:
        c = calcContainment(B, A)
    #compute Resemblance
    r = calcResemblance(A, B)
    #compute ResultSet with similar NGrams
    resSet = A & B
    
    #if treshold is a list similarity will be tested due to resemblance and
    #to containment otherwise only resemblance will be taken into account
    if type(treshold) == type([]):
        if r >= c:
            sim = r
            suspPlag = sim >= treshold[0]
        else: 
            sim = c
            suspPlag = sim >= treshold[1]
    else: 
        #cbanged: 6.4.07 - use containment instead of resemblance
        #sim = r 
        sim = c
        suspPlag = sim >= treshold
    
    return [sim, resSet, suspPlag]

def calcContainment(A, B):
    """Calculates containment similarity for sets A and B, 
        i.e. "the extent to which set B is contained in 
        set A"[lyon01].
    
        "A might be derived from concatenated potential 
        source material from the web, a large set. Set 
        B might be derived from a single student essay, 
        a small set." [lyon01]
        See also: 
        [lyon01]"Detecting Short Passages of Similar Text in Large Document Collections"
        citeseer.ist.psu.edu/lyon01detecting.html
        and
        http://www.dcs.shef.ac.uk/nlp/meter/Documents/papers/reuse_acl2002.pdf
    """
    resSet = (A & B)
    res = float(len(resSet)) / float(len(B))
    return res

def calcResemblance(A, B):
    """Calculates resemblance similarity for sets A and B. 
    
        A and B are the trigram sets derived by two texts 
        of comparable length.
        See also: 
        "Detecting Short Passages of Similar Text in Large Document Collections"
        citeseer.ist.psu.edu/lyon01detecting.html
        and
        http://www.dcs.shef.ac.uk/nlp/meter/Documents/papers/reuse_acl2002.pdf
    """
    intersectionSet = (A & B)
    unionSet = (A | B)
    res = float(len(intersectionSet)) / float(len(unionSet))
    return res

#===============================================================================
#    Computation of tiles
#===============================================================================
def calcTiles(dict1, dict2, resSet, mML):
    """Calculates the tiles from the given dictionaries and the resSet.
        Returns a list of tiles describing matches between the two compared texts.
        
        Definition tile:
            tile := [startPostionInText1, startPostionInText2, LengthOfMatch]
    """
    tiles = []
    for ngram in resSet:
        list1 = dict1.get(ngram)
        list2 = dict2.get(ngram)
        #walk through lists and create tiles
        tiles = tiles + [(p1, p2, mML) for p1 in list1 for p2 in list2]
#        print "NGRAM:", ngram, [(p1, p2, mML) for p1 in list1 for p2 in list2]
    #connect tiles to bigger tiles if possible
    cnt = 0
    newTilefound = False
    while len(tiles) > cnt:
        tile1 = tiles[cnt]
        i = cnt+1
        while i < len(tiles): #for i in range(cnt, len(tiles)):
            tile2 = tiles[i]
            newTile =  connectTiles(tile1, tile2)
            if newTile:    # if new tile was found
#                if newTile[0] <= 123 and 123<=newTile[0]+newTile[2]:
#                    print newTile
                tiles.remove(tile1)
                tiles.remove(tile2)
                tiles.append(newTile)
                #tile 1 was deleted so break and get new tile1
                newTilefound = True
                break
            else:
                i = i + 1
        if not newTilefound:
            cnt = cnt + 1 
        else: newTilefound = False
#    print tiles
    return tiles

def connectTiles(tile1, tile2):
    """ Connects two tiles (p11, p12, l1) (p21, p22, l2) using the follwing 
        rules:
        
        1. both first positions are greater or smaller than the first postions
            in the second tuple
            otherwise: return None
        2. the distances between the positions needs to be equal 
            |p11-p21| == |p12-p22|
            otherwise: return None
        3. the distances are smaller or equal than the length 
            d <= l1 or l2
            otherwise: return None
    """
    #rule: 1
    firstTileLarger = (tile1[0]>tile2[0] and tile1[1]>tile2[1])
    secondTileLarger = (tile1[0]<tile2[0] and tile1[1]<tile2[1])
    if firstTileLarger or  secondTileLarger:
        #rule: 2
        d1 = abs(tile1[0]-tile2[0])
        d2 = abs(tile1[1]-tile2[1])
        if d1 == d2:
            #rule 3:
            if firstTileLarger and d1<=tile2[2]:
                diff = (tile1[0]+tile1[2]) - (tile2[0]+tile2[2])
                if diff <= 0: diff = 0
                newLength = tile2[2] + diff
                return (tile2[0], tile2[1], newLength)
            elif secondTileLarger and d2<=tile1[2]:
                diff = (tile2[0]+tile2[2]) - (tile1[0]+tile1[2])
                if diff <= 0: diff = 0
                newLength = tile1[2] + diff
                return (tile1[0], tile1[1], newLength)
    #otherwise:
    return None
