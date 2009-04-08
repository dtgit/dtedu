# -*- coding: utf-8 -*-
# $Id: PlagChecker.py,v 1.1 2007/07/02 14:40:18 peilicke Exp $
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
#This module contains methods to check two strings or a list of strings on 
#plagiarisms. The results are returned as PlagResult objects.
#
#To use the class it is necessary to specify the normalizer and the algorithm
#which should be used for the tests.
#By default uses:
#    normalizer:   NORMAL    -> Normalizer for normal (natrual language) texts.
#    algorithm:    NGRAM     -> Fast Algorithm computing similarities on sets of
#                                3 word phrases. More Information: algNGRAM.py
#===============================================================================

import PlagResult
from Detection import *
from Normalize import *
from errors import NoValidArgumentError, NoValidAlgorithmNameError, NoValidNormalizerNameError



class PlagChecker(object):
    """Class for checking strings on similarity.
	"""
    
    def __init__(self, algName='NGRAM', normalizerName='NORMAL'):
        """Initializes the Class.
        """
        #all Alg Names with their functions
        self.algNames = algNames    # algNames from __init__.py
        #all Norm Names with their functions
        self.normNames = normNames    # normNames from __init__.py
        #set algorithm and normalizer
        self.setAlgorithm(algName)
        self.setNormalizer(normalizerName)
    

    def compare(self, string1, string2, id1="", id2="", mML=3, treshold=None):
        """Compares two strings in their normalized version and returns their similarities as PlagResult object.
        """
        #normalize Strings
        normString1 = self.normalizer(string1)
        normString2 = self.normalizer(string2)
        #compare Strings and return PlagResult
        if treshold:
            #use given treshold
            result = self.alg(normString1, normString2, mML, treshold)
        else:
            #use default treshold
            result = self.alg(normString1, normString2, mML)
        #set Identifier
        if id1=="" and id2=="":
            result.setIdentifier(hash(string1), hash(string2))
        else:
            result.setIdentifier(id1, id2)
        #set Id string length
        result.setIdStringLength(len(normString1.split()), len(normString2.split()))
        #set names of algorithm and normalizer used for comparison
        result.setAlgorithmName(self.algName)
        result.setNormalizerName(self.normalizerName)
        #return the result
        return result
    

    def compareList(self, stringList, idList, mML=3, treshold=None):
        """Compares all strings in the list with each other and
            returns a list with the found similarities as PlagResult
            objects.
        """
        if type(stringList) != type([]):
            raise NoValidArgumentError, 'Input stringList must be of type list.'
        elif type(idList) != type([]):
            raise NoValidArgumentError, 'Input idList must be of type list.'
        elif len(stringList) != len(idList):
            raise AssertionError, 'stringList length must be equal to length of the idList'
        #normalize Strings
        normStringList = map(self.normalizer, stringList)
        #comareStrings
        resultList = []
        for cnt in xrange(0, len(normStringList)):
            s1 = normStringList[cnt]
            for i in xrange(cnt+1, len(normStringList)):
                s2 = normStringList[i]
                if treshold:
                    #use given treshold
                    result = self.alg(s1, s2, mML, treshold)
                else:
                    #use default treshold
                    result = self.alg(s1, s2, mML)
                #set ids
                if idList[cnt] == "" and idList[i] == "":
                    result.setIdentifier(hash(stringList[cnt]), hash(stringList[i]))
                else:
                    result.setIdentifier(idList[cnt], idList[i])
                #set Id string length
                result.setIdStringLength(len(s1.split()), len(s2.split()))
                #set names of algorithm and normalizer used for comparison
                result.setAlgorithmName(self.algName)
                result.setNormalizerName(self.normalizerName)
                #append result to resultlist
                resultList.append(result)
        #return list with PlagResults
        return resultList
    

    def setAlgorithm(self, algName):
        """Sets the algorithm which is used to check for similarities.
        
            Some Options for algName: 
                GSTPRECELT  - Greedy String Tiling
                NGRAM  		- nGram Overlap
                
            For a complete List of available algorithms use getAlgorithmNames().
                
            Example: setAlgorithm('GST')
        """
        if self.algNames.has_key(algName):
            self.alg = self.algNames.get(algName)
            self.algName = algName
        else: #Exception
            raise NoValidAlgorithmNameError(algName, algNames.keys())


    def setNormalizer(self, normalizerName):
        """Sets the normalizer which is used to normalize the input strings.
        
            Some Options for normalizerName: 
                NORMAL  - Normal: for natural language input
                PYTHON  - for Python program code
                
            For a complete List of available Normalizer use getNormalizerNames().
                
            Example: setAlgorithm('NORMAL')
        """
        if self.normNames.has_key(normalizerName):
            self.normalizer  = self.normNames.get(normalizerName)
            self.normalizerName = normalizerName
        else: #Exception
            raise NoValidNormalizerNameError(normalizerName, normNames.keys())


    def getNormalizerNames(self):
        """Returns a list containing all available normalizer ids. These
            can be used to set the normalizer.
        """
        list = normNames.keys()[:]
        list.sort()
        return list


    def getAlgorithmNames(self):
        """Returns a list containing all available algorithm ids. These
            can be used to set the algorithm.
        """
        list = algNames.keys()
        list.sort()
        return list

