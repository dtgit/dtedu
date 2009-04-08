# -*- coding: utf-8 -*-
# $Id: algGSTPrechelt.py,v 1.1 2007/07/02 14:40:20 peilicke Exp $
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
from algGST import GSTHashtable, createKRHashValue



def run(s1, s2, mML=3, treshold=0.5):
    """Tuned Version of GST
    
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
    tiles = GSTPrechelt(s1, s2, mML)

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


def GSTPrechelt(s1, s2, minimalMatchingLength):
    """TODO: Beschreibung
    """
    s1List = s1.split()
    s2List = s2.split()
    matches = set([])

    hashList = computeHashList(s1List, minimalMatchingLength)
    
    i = 0
    while (i < len(s2List)-minimalMatchingLength): #for i in xrange(len(s2List)-minimatchingLength):
        h = createKRHashValue(" ".join(s2List[i:i+minimalMatchingLength]))
        #get positions for hashvalue from string s1
        positions = hashList.get(h)
        if positions:
            for pos in positions:
                #check if substrings are equal
                j = 0
                while (pos+j<len(s1List) and i+j<len(s2List) and s1List[pos+j] == s2List[i+j]):
                    j += 1
                #try to extend the match
                if j >= minimalMatchingLength:
                    #match
                    matches = matches | set([(pos, i, j)]) #pos1, pos2, length
                   # foundMatch = True
                else:
                    #no match
                    pass
                    #foundMatch = False
                #insert match
        i += 1
        
    #return matches as List
    return reduceMatches(list(matches))


def computeHashList(s, minimalMatchingLength):
    hashList = GSTHashtable()
    
    for i in xrange(len(s)-minimalMatchingLength):
        hashList.add(createKRHashValue(" ".join(s[i:i+minimalMatchingLength])), i)
    
    return hashList

def reduceMatches(tiles):
    """Tries to reduce tiles in list tiles by removing all tiles that are contained in other lists
        or that are part of two lists.
    """
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
                newLength = tile2[2] + (tile1[0]+tile1[2]) - (tile2[0]+tile2[2])
                return (tile2[0], tile2[1], newLength)
            elif secondTileLarger and d2<=tile1[2]:
                newLength = tile1[2] + (tile2[0]+tile2[2]) - (tile1[0]+tile1[2])
                return (tile1[0], tile1[1], newLength)
    #otherwise:
    return None
#===============================================================================
#Ueberlegung:
#Variante 1:
#jede Runde jeden Match vermerken und schrittweise durchgehen
#
#Variante 2: mehr GST-Natur
#nur den laengsten Match vermerken und dann Sprung zur Stelle nach dem Match
#===============================================================================
#===============================================================================
#def GSTPrechelt(s1, s2, minimalMatchingLength):
#    """TODO: Beschreibung
#    """
#    s1List = s1.split()
#    s2List = s2.split()
#    matches = set([])
#
#    hashList = computeHashList(s1, minimalMatchingLength)
#    
#    i = 0
#    while (i < len(s2List)-minimalMatchingLength) #for i in xrange(len(s2List)-minimatchingLength):
#        h = createKRHashValue(s2List[i:i+minimalMatchingLength])
#        positions = hashList.get(h)
#        if positions:
#            for pos in positions:
#                #check if substrings are equal
#                j = 0
#                while (s1List[pos+j] == s2List[i+j]):
#                    j += 1
#                #try to extend the match
#                if j >= minimalMatchingLength:
#                    #match
#                    matches = matches & (i, pos, j) #pos1, pos2, length
#                    foundMatch = True
#                else:
#                    #no match
#                    foundMatch = False
#                #insert match
#            if Match
#===============================================================================

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
    #Pattern String
    s1list = s1.split()
    patLList = LinkedList()
    for s in s1list:
        patLList.add(node(s)) #every unmarked token is doubly linked with its successor and predecessor
    #Text String
    s2list = s2.split()
    textLList = LinkedList()
    valuePosDict = {}
    valuePosNode = Node(valuePosDict)
    textLList.add(valuePosNode)
    for s in s2list:
        textLList.add(node(s))
#    s1PosList = range(len(s1list))
#    s2PosList = range(len(s2list))
    tiles = set([])
    while 1:
        maxmatch = minimalMatchingLength
        matches = []

        scanpattern(textLList, patLList)
        markarrays(matches)
        #Abbruchbedingung
        if (maxmatch == minimalMatchingLength):
            break
    return list(tiles)

def scanpattern(textLList, patLList):
    """
    """
    for p in patLList:
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

def markarrays(matches):
   #mark matched words and add match to tiles
   for posS1, posS2, j in matches:
       for i in xrange(0, maxmatch):
           #mark token
           s1list[posS1+i] = '*' + s1list[posS1+i]
           s2list[posS2+i] = '*' + s2list[posS2+i]
           #unlink token
           try:
                s1PosList.remove(posS1+i)
           except ValueError: pass
           try:
                s2PosList.remove(posS2+i)
           except ValueError: pass
       tiles = tiles | set([(posS1, posS2, j)])

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


#===============================================================================
#    Helper Class
#===============================================================================
class LinkedList(object):
    "Doubly Linked List"
    
    def __init__(self):
        self.size = 0
        self.head = None
        self.tail = None
        
    def addFirst(self, node):
        if self.head == None:
            self.head = self.tail = node
            node.prev = None
            node.next = None
        else:
            self.insertBefore(self.head, node)
            
    def add(self, node):
        if self.tail == None:
            self.addFirst(node)
            self.size = 1
        else:
            self.insertAfter(self.tail, node)
    
    def insertBefore(self, node, newNode):
        newNode.prev = node.prev
        newNode.next = node
        if node.prev == None: #node is head of list
            self.head = newNode
        else:
            node.prev.next = newNode
        node.prev = newNode
        self.size += 1
        
    def insertAfter(self, node, newNode):
        newNode.prev = node
        newNode.next = node.next
        if node.next == None: #is last node
            self.tail = newNode
        else:
            node.next.prev = newNode
        node.next = newNode
        self.size += 1
    
    def remove(self, node):
        if node.prev == None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next == None:
            self.tail = None
        else:
            node.next.prev = node.prev
        del node
        self.size -= 1
        
    def __iter__(self):
        node = self.head
        while node != None:
            yield node
            node = node.next
            
    def size(self):
        return self.size
    
    def get(self, i):
        if i>self.size or i<0: return None
        cnt = 0
        node = self.head
        while cnt!=i:
            node = node.next
            cnt += 1
        return node

    
class Node(object):
    """Node of doubly linked list."""
    
    def __init__(self, data = None, prev = None, next = None):
        self.data = data
        self.prev = prev
        self.next = next
        
    def setData(self, data):
        self.data = data
        
    def getData(self):
        return self.data
    
    def setPrev(self, prev):
        self.prev = prev
        
    def getPrev(self):
        return self.prev
    
    def setNext(self, next):
        self.next = next
        
    def getNext(self):
        return self.next
