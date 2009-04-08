# *- coding: utf-8 -*-
# $Id: PlagVisualizer.py,v 1.1 2007/07/02 14:40:18 peilicke Exp $
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
#This module contains several methods to visualize similarities or the 
#PlagResults.
#===============================================================================

from Visualize import *
from PIL import Image



class PlagVisualizer(object):
    "The class contains several methods to visualize similarities or the PlagResults."
    
    def __init__(self):
        pass

#===============================================================================
#    RESULT TO HTML Methods
#===============================================================================
    def resultToHtml(self, result, s1, s2):
        """Takes the PlagResult object result and the two strings from the 
            comparison.
            Returns a list of strings [s1Marked, s2Marked] in which the
            tiles of the result are marked in HTML.
        """
        return htmlMaker.resultToHtml(result, s1, s2)

    def resultToHtmlText(self, result, s1, s2):
        """Takes the PlagResult object result and the two strings from the 
            comparison.
            Returns a string containing the html file text that can be used to
            manually check the two texts for plagiarism including highlighted
            passages which are linked to each other links.
        """
        return htmlMaker.resultToHtmlText(result, s1, s2)


#===============================================================================
#    DOTPLOT Methods
#===============================================================================
    def resultToDotplot(self, result, showIdNums=False):
        """Creates an PIL-Image object showing a dotplot using the tiles of
            the given PlagResult object result.
            
            Return: PIL Image object
                        
            Options:
            showIdNums:boolean
                ->if set to True shows numbers along the dotplot marking the ids          
        """
        return dotplot.createDotplotFromResult(result, showIdNums)
    
    def stringsToDotplot(self, string1, string2, w=1, k=1, id1="", id2="", showIdNums=False):
        """A Dotplot shows all w/k-matches (window of length w with k matches) 
            between two sequences - here two strings s1 and s2.
        
            For every window of length w with at least k matches a dot is drawn 
            otherwise it will be left blank.
        
            Values w and k should be at least w=k=1 and w>=k.

            Return: PIL Image object
            
            Other Options:
            showIdNums:boolean
                ->if set to True shows numbers along the dotplot marking the ids          
            id1, id2:String    
                ->ids for the strings used for marking purposes in the image
        """
        return dotplot.createDotplotFromStrings(string1, string2, w, k, id1, id2, showIdNums)
    
    def stringListToDotplot(self, stringList, w=1, k=1, idList=[], showIdNums=True):
        """A Dotplot shows all w/k-matches (window of length w with k matches) 
            between two sequences - here two strings s1 and s2.
        
            For every window of length w with at least k matches a dot is drawn 
            otherwise it will be left blank.
        
            Values w and k should be at least w=k=1 and w>=k.
            
            Return: PIL Image object
            
            Other Options:
            showIdNums:boolean
                ->if set to True shows numbers along the dotplot marking the ids          
            id1, id2:String    
                ->ids for the strings used for marking purposes in the image
        """
        return dotplot.createDotplotFromStringList(stringList, w, k, idList, showIdNums)

#===============================================================================
#    TORC Method
#===============================================================================
    def resultsToTorc(self, resultList, colored=False):
        """Takes the result and returns an image showing a Torc indicating the
            similarity relations of the compared texts in the results.
        
            A Torc is a kind of overview which allows the user to recognize the similarity
            relations between different texts. Therefore all texts are arranged on a circle.
            For each relation of similarity between two texts a connecting line is drawn.

            Return: PIL Image object
        """
        return torc.resultsToTorc(resultList, colored)

#===============================================================================
#    Heatmap Methods
#===============================================================================
    def resultsToIntensityHeatmap(self, resultList, scopes=[0.2, 0.4, 0.6, 0.8, 1], recSize = 20, onlyPositiveResults=True):
        """Creates an intensty heatmap chart. Showing all positive results in a chart 
            colored rectangles indicate the grade of plagirism between the plagiriarim
            texts.
            
            options:
                scopes - a list of numbers defining scopes in following way
                            e.g. [0.2, 0.4, 0.6, 0.8, 1] (default) would define the
                            scopes 0<=x<=0.2, 0.2<x<=0.4, ... ,0.8<x<=1
                            Each scope gets its own color in the heatmap.
                recSize - int value that expresses the size in pixel of a single heatmap 
                            cell
                onlyPositiveResults - If set to True only positive results will be used
                                        to create the heatmap. If no positive result is
                                        found None will be returned.
            
            Return: PIL Image Object
        """
        return heatmap.createIntensityHeatmap(resultList, 
                                              scopes = scopes, 
                                              recSize = recSize, 
                                              onlyPositiveResults=onlyPositiveResults)

    def resultsToClusterHeatmap(self, resultList, recSize = 20, onlyPositiveResults=True):
        """Creates a cluster heatmap chart. Showing all clusters of plagiarized results by
            positive results in a chart 
            colored rectangles indicate the grade of plagirism between the plagiriarim
            texts.
            
            options:
                recSize - int value that expresses the size in pixel of a single heatmap 
                            cell
                onlyPositiveResults - If set to True only positive results will be used
                                        to create the heatmap. If no positive result is
                                        found None will be returned.
            
            Return: PIL Image Object
        """
        return heatmap.createClusterHeatmap(resultList, 
                                            recSize = recSize, 
                                            onlyPositiveResults=onlyPositiveResults)

#===============================================================================
#    Patterngrams
#===============================================================================
    def stringsToCategoricalPatterngram(self, basefile, ensemble, klength, normName, mode=1):
        """Creates a Categorical Patterngram as PIL Image object. It "shows
            the degree of similarity that exists between one file [(the base 
            file)] and the rest of the ensemble of files." (Rib00)
        
            basefile - the single file in the 'one-to-many' comparison
            ensemble - the set of files used for the comparison
            klength  - the length of the used ngrams
            normName - the name of the normalizer used to normalize the texts
        
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
        return patterngram.createCategoricalPatterngram(basefile, ensemble, klength, normName, mode)

    def stringsToCompositeCategoricalPatterngram(self, basefile, ensemble, klength, normName, mode=1):
        """Creates a Composite Categorical Patterngram as PIL Image object. It "shows
            which particular files are similar." (Rib00)
        
            basefile - the single file in the 'one-to-many' comparison
            ensemble - the set of files used for the comparison
            klength  - the length of the used ngrams
            normName - the name of the normalizer used to normalize the texts
        
            A composite categorical patterngram is a visualization that displays, 
            for each character position x in the the base file, which file of the 
            ensemble files also contain the k-length n-gram that begins at that 
            position. "A point is plotted at (x,y) if the k-length n-gram beginning 
            at x in the base file occurs one or more times in file y." (Rib00)
            
            Rib00 - "Using Visualization to Detect Plagiarism in Computer Science Classes",
            Randy L. Ribler, Marc Abrams, 2000
        """
        return patterngram.createCompositeCategoricalPatterngram(basefile, ensemble, klength, normName, mode)

#===============================================================================
#    Statistic Methods
#===============================================================================
    def resultsToStatistic(self, resultList, statName=None):
        """TODO: For now only one overview statistic is available which will be
            returned as PIL image object.
            The Overview shows the total number of texts, the number of possible
            plagiarism texts and the number of plagiarism clusters.
        """
        try:
            return statistics.statOverview2(resultList)
        except NameError, ImportError:
            return None
        
    
#===============================================================================
#    HELPER FUNCTIONS
#===============================================================================
    def writeImageToFile(self, img, filename):
        """Writes the given img to to specified place (filename=path+filename) on
            the hard disk.
            The format will be taken from the file extension. Formats available are
            amongst others: png, jpeg, bmp
            For detailed informations please check out Python Imaging Library 
            documentation.
            -> http://www.pythonware.com/library/pil/handbook/index.htm
        """
        try:
            img.save(filename)
        except IOError:
            print "Writing img to disk failed.\n Error Message:\n" + IOError.message
