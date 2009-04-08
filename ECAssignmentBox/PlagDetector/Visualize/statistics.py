# -*- coding: utf-8 -*-
# $Id: statistics.py,v 1.1 2007/07/02 14:40:27 peilicke Exp $
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
#...TODO:Beschreibung statistics.py
#===============================================================================

##from PIL import Image
##from pychart import *
##from PlagDetector.errors import NoValidNameError, NoValidArgumentError
##theme.get_options()
##
##def statRelationSubmissionToPlagiarism(resultList, mode="Bar"):
##    """Returns an Image(PIL) object showing a chart representing
##        the relation from submissions to plagiarism.
##        
##        resultList - list of PlagResults
##        mode - "Bar" creates a bar plot (default)
##             - "Pie" creates a pie plot
##    """
##    #check preconditions
##    if type(mode) != type(""):
##        raise NoValidArgumentError, "Mode must be of type string (mode = ('Bar' or 'Pie'))"
##    elif mode != 'Bar' and mode != 'Pie':
##        raise NoValidNameError(mode, ['Bar', 'Pie'])
##    elif type(resultList) != type([]):
##        raise NoValidArgumentError, "resultList must be of type list"
##    
##    #extract needed data
##    idSet = set()
##    plagSet = set()
##    for r in resultList:
##        print r
##        ids = r.getIdentifier()
##        if r.isSuspectPlagiarism():
##            plagSet = plagSet | set(ids)
##        idSet = idSet | set(ids)
##    
##
##    #===draw chart===
##    #create own canvas
##    canvas.init("tmp.png", "png")
##
##    #create bar chart
##    if mode=="Bar":
##        data = [["All", len(idSet)], ["Plagiarism", len(plagSet)]]
##        print "DEBUG: ", len(idSet), len(plagSet)
##        #create area
##        ar = area.T(x_coord = category_coord.T(data, 0), y_range = (0, None),
##                x_axis = axis.X(label=""),
##                y_axis = axis.Y(label="Number Of Submissions"))
##        #add plot -> bar plot
##        ar.add_plot(bar_plot.T(data = data, label = "Submissions"))
##    elif mode=="Pie":
##        data = [["Non-Plagiarism", len(idSet)-len(plagSet)], ["Plagiarism", len(plagSet)]]
##        #create area
##        ar = area.T(size=(150,150), legend=legend.T(),
##            x_grid_style = None, y_grid_style = None)
##
##        #add plot -> pie plot
##        ar.add_plot(pie_plot.T(data=data, arc_offsets=[0,10],
##                  shadow = (2, -2, fill_style.gray50),
##                  label_offset = 25,
##                  arrow_style = arrow.a3))
##
##    #draw chart to canvas
##    ar.draw()
##
##    canvas.close()
##    
##    #load chart and return img
##    return retrieveImg()
##
##def statOverview(resultList):
##    """Returns an Image(PIL) object showing a chart representing
##        an overview containing:
##         - number of submissions, 
##         - number of plagiarism,
##         - number of plagiarism clusters
##        
##        resultList - list of PlagResults
##    """
##    #check preconditions
##    if type(resultList) != type([]):
##        raise NoValidArgumentError, "resultList must be of type list"
##    
##    #extract needed data
##    idSet = set()
##    plagSet = set()
##    for r in resultList:
##        print r
##        ids = r.getIdentifier()
##        if r.isSuspectPlagiarism():
##            plagSet = plagSet | set(ids)
##        idSet = idSet | set(ids)
##    clusters = extractClusterFromResults(resultList)
##
##    #===draw chart===
##    #create own canvas
##    canvas.init("tmp.png", "png")
##
##    #create bar chart
###    data = [("All Submissions", len(idSet)), ("Plagiarism", len(plagSet)), ("Clusters", len(clusters))]
##    data = [("All Submissions", 94), ("Plagiarism", 7), ("Clusters", 2)]
##    print "DEBUG: ", len(idSet), len(plagSet)
##    #create area
##    ar = area.T(x_coord = category_coord.T(data, 0), y_range = (0, None),
##            x_axis = axis.X(label=""),
##            y_axis = axis.Y(label="Value"))
##    #add plot -> bar plot
##    ar.add_plot(bar_plot.T(data = data))
##
##    #draw chart to canvas
##    ar.draw()
##
##    canvas.close()
##    
##    #load chart and return img
##    return retrieveImg()
##
##def statOverview2(resultList):
##    """Returns an Image(PIL) object showing a chart representing
##        an overview containing:
##         - number of submissions, 
##         - number of plagiarism,
##         - number of plagiarism clusters
##        
##        resultList - list of PlagResults
##    """
##    #check preconditions
##    if type(resultList) != type([]):
##        raise NoValidArgumentError, "resultList must be of type list"
##    
##    #extract needed data
##    idSet = set()
##    plagSet = set()
##    for r in resultList:
##        print r
##        ids = r.getIdentifier()
##        if r.isSuspectPlagiarism():
##            plagSet = plagSet | set(ids)
##        idSet = idSet | set(ids)
##    clusters = extractClusterFromResults(resultList)
##
##    #===draw chart===
##    #create own canvas
##    canvas.init("tmp.png", "png")
##
##    #create bar chart
##    data = [("Overview", len(idSet), len(plagSet),len(clusters))]
##    print "DEBUG: ", len(idSet), len(plagSet)
##    #create area
##    chart_object.set_defaults(area.T, size=(150, 120), y_range= (0, None), x_coord = category_coord.T(data, 0))
##    chart_object.set_defaults(bar_plot.T, data = data)
##    ar = area.T(#x_coord = category_coord.T(data, 0), y_range = (0, None),
##            x_axis = axis.X(label=""),
##            y_axis = axis.Y(label="Value"))
##    #add plot -> bar plot
##    #ar.add_plot(bar_plot.T(data = data))
##    ar.add_plot(bar_plot.T(label="All Submissions", cluster=(0,3)),
##                bar_plot.T(label="Suspected Plagiarism", hcol=2, cluster=(1,3)),
##                bar_plot.T(label="Plagiarism Clusters", hcol=3, cluster=(2,3)))
##
##    #draw chart to canvas
##    ar.draw()
##
##    canvas.close()
##    
##    #load chart and return img
##    return retrieveImg()
##
##
###===============================================================================
###    Helper Functions
###===============================================================================
##def retrieveImg():
##    """Gets Image written by statistic method to tmp.png and returns an PIL
##        image object.
##    """
##    #load chart and return img
##    img = Image.open("tmp.png", mode="r")
##    return img
##
##
##def extractClusterFromResults(resultList):
##    """Returns a list of plagirism cluster sets.
##    """
##    clusters = []
##    for r in resultList:
##        #if result is suspected plagiarism
##        if r.isSuspectPlagiarism():
##            #get ids
##            ids = r.getIdentifier()
##            #look if ids are already in a certain cluster
##            inCluster = False
##            for i in xrange(len(clusters)):
##                if clusters[i].__contains__(ids[0]) or clusters[i].__contains__(ids[1]):
##                    clusters[i] = clusters[i] | set(ids)
##                    inCluster = True
##            if not inCluster:
##                clusters.append(set(ids))
##                
##    return clusters
##
###===============================================================================
###    Test
###===============================================================================
##if __name__ == '__main__':
##    A = "dies ist nur ein kleiner test und ich hab dich so lieb"
##    B = "ich hab dich so lieb ach ja und dies ist nur ein kleiner test kleiner test yeah mah bin ich toll wah oder so ne"
##    s5 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\ndef mah():\n    s= 1+2\n    return s\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
##    s6 = 'print \'hello\'\n\ndef mah():    return \'nok\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
##    s7 = 'print \'hello\'\n\ndef test1(s):\n    s = test2(s)\n    if s == \'Muster\':\n        return s\n    else:\n        return \'\'\n\n#lala\ndef test2(s):\n    if s==\'\':\n        return \'\'\n    elif len(s) > 5:\n        s = \'muha\'\n    else:\n        return \'Muster\'\n\n    return s\n\n'
##    nonplag = "Ja mei wat is dat denn fuer a schmarrn ^^"
##
##
##    stringList = [A, B, s5, s6, s7, nonplag]
##    idList = ["student01", "student02", "student03", "student04", "student05", "student06"]
##    from PlagDetector.PlagChecker import PlagChecker
##    checker = PlagChecker()
##    resultList = checker.compareList(stringList, idList, 3)
##    img = statRelationSubmissionToPlagiarism(resultList)
##    img.show()
##    img = statRelationSubmissionToPlagiarism(resultList, mode="Pie")
##    img.show()
##    img = statOverview(resultList)
##    img.show()
##    img = statOverview2(resultList)
##    img.show()
##    
##    list = extractClusterFromResults(resultList)
##    print list
