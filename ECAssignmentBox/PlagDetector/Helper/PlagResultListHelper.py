# -*- coding: utf-8 -*-
# $Id: PlagResultListHelper.py,v 1.1 2007/07/02 14:40:22 peilicke Exp $
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
#===============================================================================

from Products.ECAssignmentBox.PlagDetector.PlagResult import PlagResult



#===============================================================================
#    PlagResult List Access Methods
#===============================================================================

#===============================================================================
#def getClusters(resultList):
#    """Returns a list of plagirism cluster sets.
#        Note: Only suspected PlagResults are being clustered.
#    
#        @param resultList list containing PlagResult objects
#        @return A list of plagiarism clusters sets [set([id1, id2]), set([id3, id4, id5])]
#    """
#    clusters = []
#    for r in resultList:
#        #if result is not suspected plagiarism
#        if not r.isSuspectPlagiarism():
#            continue
#        #get ids
#        ids = r.getIdentifier()
#        #look if ids are already in a certain cluster
#        inCluster = False
#        for i in xrange(len(clusters)):
#            if clusters[i].__contains__(ids[0]) or clusters[i].__contains__(ids[1]):
#                clusters[i] = clusters[i] | set(ids)
#                inCluster = True
#        if not inCluster:
#            clusters.append(set(ids))
#            
#    return clusters
#===============================================================================

def getClusters(resultList, onlyPositives=True, onlyNonZeroSimilarities=True):
    """Returns a list of plagirism cluster sets.
    
        @param resultList list containing PlagResult objects
        @param onlyPositives [optional] True (default): only suspect PlagResults are clustered, 
                            False: all PlagResults are clustered
        @param onlyNonZeroSimilarities [optional] True(default): only PlagResults with 
                                                    similarities greater zero are clustered
                                                  False: zero similarity PlagResults are
                                                    clustered in their own cluster
        @return A list of plagiarism clusters sets [set([id1, id2]), set([id3, id4, id5])]
    """
    clusters = []
    zeroSimCluster = set([])
    for r in resultList:
        #if onlyPositives and result is not suspected plagiarism
        if onlyPositives and not r.isSuspectPlagiarism():
            continue
        #if onlyNonZeroSimilarities and result's similarity is zero
        if onlyNonZeroSimilarities and r.getSimilarity()==0:
            continue
        #get ids
        ids = r.getIdentifier()
        #look if ids are already in a certain cluster
        if r.getSimilarity() > 0:
            inCluster = False
            for i in xrange(len(clusters)):
                if clusters[i].__contains__(ids[0]) or clusters[i].__contains__(ids[1]):
                    clusters[i] = clusters[i] | set(ids)
                    inCluster = True
            if not inCluster:
                clusters.append(set(ids))
        else:
            #similarity == 0
            zeroSimCluster = zeroSimCluster | set(ids)
    
    #combine clusters if they share similar members
    cnt = 0
    while cnt<len(clusters):
        cnt2 = cnt+1
        while cnt2<len(clusters):
            #if clusters share same members
            if len(clusters[cnt] & clusters[cnt2]) > 0:
                #combine clusters
                clusters[cnt] = clusters[cnt] | clusters[cnt2]
                #delete the second cluster
                clusters.remove(clusters[cnt2])
                continue
            else:
                cnt2 = cnt2 + 1
        cnt = cnt + 1
    
    #if also non zero similarity clusters are wished add the found clusters
    if not onlyNonZeroSimilarities and len(zeroSimCluster) > 0:
        clusters.append(zeroSimCluster)
            
    return clusters

def getClusterNr(id1, id2, clusters):
    """Returns zero if both ids do not belong to the same cluster,
        otherwise it returns the cluster number.
    """
    for i in xrange(len(clusters)):
        c = clusters[i]
        if id1 in c and id2 in c:
            return i
        
    return None

def getIdentifier(resultList):
    """Returns a list with all identifier from the result list.
        
        @param resultList list containing PlagResult objects
        @return A list containing all Identifier owned by the PlagResult objects.
    """
    idSet = set()
    for r in resultList:
        idSet = idSet | set(r.getIdentifier())
    return list(idSet)

def getPositiveResults(resultList):
    """Returns a list with all positive PlagResult objects from the result list.
    
        @param resultList list containing PlagResult objects
        @return A list containing only positive, i.e. suspected, PlagResult objects.
    """
    return [r for r in resultList if r.isSuspectPlagiarism()]

#===============================================================================
#    Test
#===============================================================================
if __name__ == '__main__':
    print "Start Tests - PlagResultList helper methods"
    #create Test PlagResult1
    plagResult = PlagResult("Test1", "Test2")
    plagResult.setAlgorithmName("NGRAM")
    plagResult.setNormalizerName("NORMAL")
    plagResult.setSimilarity(0.65)
    plagResult.setSuspectedPlagiarism(True)
    plagResult.setIdStringLength(52, 45)
    plagResult.setTiles([(3,5,4),(12,23,5),(34,2,3)])
    #create Test PlagResult2
    plagResult2 = PlagResult("Test3", "Test4")
    plagResult2.setAlgorithmName("NGRAM")
    plagResult2.setNormalizerName("NORMAL")
    plagResult2.setSimilarity(0.45)
    plagResult2.setSuspectedPlagiarism(False)
    plagResult2.setIdStringLength(152, 145)
    plagResult2.setTiles([(3,5,4),(12,23,5),(34,2,3)])
    #create Test PlagResult3
    plagResult3 = PlagResult("Test5", "Test6")
    plagResult3.setAlgorithmName("NGRAM")
    plagResult3.setNormalizerName("NORMAL")
    plagResult3.setSimilarity(0.75)
    plagResult3.setSuspectedPlagiarism(True)
    plagResult3.setIdStringLength(132, 125)
    plagResult3.setTiles([(3,5,4),(12,23,5),(34,2,3)])
    #create Test PlagResult3
    plagResult4 = PlagResult("Test3", "Test6")
    plagResult4.setAlgorithmName("NGRAM")
    plagResult4.setNormalizerName("NORMAL")
    plagResult4.setSimilarity(0)
    plagResult4.setSuspectedPlagiarism(False)
    plagResult4.setIdStringLength(112, 115)
    plagResult4.setTiles([(3,5,4),(12,23,5),(34,2,3)])

    #list of PlagResult objects
    resultList = [plagResult, plagResult2, plagResult3, plagResult4]
    
    #test1 getClusters
    clusters = getClusters(resultList)
    assert [set(['Test1', 'Test2']), set(['Test5', 'Test6'])].__eq__(clusters), "clusters onlyPositives=True are not correct computed" + str(clusters)
    clusters = getClusters(resultList, onlyNonZeroSimilarities=False)
    assert [set(['Test1', 'Test2']), set(['Test5', 'Test6'])].__eq__(clusters), "clusters onlyPositives=True nonZeros=False are not correct computed" + str(clusters)
    clusters = getClusters(resultList, onlyPositives=False)
    assert [set(['Test1', 'Test2']), set(['Test3', 'Test4']), set(['Test5', 'Test6'])].__eq__(clusters), "clusters onlyPositives=False are not correct computed" + str(clusters)
    clusters = getClusters(resultList, onlyPositives=False, onlyNonZeroSimilarities=False)
    assert [set(['Test1', 'Test2']), set(['Test3', 'Test4']), set(['Test5', 'Test6']), set(['Test3', 'Test6'])].__eq__(clusters), "clusters onlyPositives=False and nonZeros=False are not correct computed" + str(clusters)
    #test2 getIdentifier
    ids = getIdentifier(resultList)
    assert set(["Test1", "Test2", "Test3", "Test4", "Test5", "Test6"]).__eq__(set(ids)), "ids are not correct computed" + str(ids)
    #test3 getPositiveResults
    posResults = getPositiveResults(resultList)
    assert [plagResult, plagResult3].__eq__(posResults), "posResults are not correct computed" + str(posResults)
    
    print "End Test - PlagResultList helper methods"
