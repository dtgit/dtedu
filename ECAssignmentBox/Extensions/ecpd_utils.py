# -*- coding: utf-8 -*-
# $Id: ecpd_utils.py,v 1.1 2007/07/02 14:40:16 peilicke Exp $
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA# -*- coding: utf-8 -*-

#
# Authors: Christian Dervaric
#          Sascha Peilicke
#
# Contains external methods to access the PlagDetector library.
#

from StringIO import StringIO
from Products.ECAssignmentBox.PlagDetector.PlagChecker import PlagChecker
from Products.ECAssignmentBox.PlagDetector.PlagVisualizer import PlagVisualizer
from Products.ECAssignmentBox.PlagDetector.Helper.PlagResultListHelper import getClusters




def getNormalizerNames(self):
	"""Returns a list with all available normalizer names.
	"""
	names = PlagChecker().getNormalizerNames()
	if not names:
		return []
	return names


def getAlgorithmNames(self):
	"""Returns a list with all available algorithm names.
	"""
	names = PlagChecker().getAlgorithmNames()
	if not names:
		return []
	return names


def compareList(self, strList, idList, normName, algName, mML, treshold):
	"""Takes list of strings and a corresponding list of
			ids and computes the similarities between the
			strings.
	"""
	if not mML:
		mML = 3
	checker = PlagChecker(algName, normName)
	#search for similarities
	results = checker.compareList(strList, idList, mML, treshold)
	#return results of comparison
	return results


def createDotplot3(self, assignment1, assignment2, REQUEST=None):
	"""Creates a dotplot image for viewing purposes.
	"""
	vis = PlagVisualizer()
	image = vis.stringsToDotplot(str(assignment1.getFile()),str(assignment2.getFile()),
			id1=assignment1.pretty_title_or_id(),id2=assignment2.pretty_title_or_id(),
			showIdNums=True)
	imageData = StringIO()
	image.save(imageData, 'JPEG')

	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def createDotplot(self, assignment1, assignment2, REQUEST=None):
	"""Creates a dotplot image for viewing purposes.
	"""
	vis = PlagVisualizer()
	image = vis.stringsToDotplot(str(assignment1),str(assignment2),
			id1="Id1",id2="Id2",showIdNums=True)
	imageData = StringIO()
	image.save(imageData, 'JPEG')

	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def createDotplot2(self, assignment1, assignment2):
	"""Creates a dotplot image for viewing purposes.
	"""
	vis = PlagVisualizer()
	image = vis.stringsToDotplot(str(assignment1.getFile()),str(assignment2.getFile()),
			id1=assignment1.pretty_title_or_id(),id2=assignment2.pretty_title_or_id(),
			showIdNums=True)	
	imageData = StringIO()
	image.save(imageData, 'JPEG')
	id = "dotplotImg"
	if hasattr(self, id):
		self.manage_delObjects([id])
		self.manage_addImage(id, imageData.getvalue(), content_type="image/jpeg")
	return id


def createTorc(self, REQUEST=None):
	"""Creates a torc using the given results. Showing the similarity
			relations between all suspected plagiarism pairs.
	"""
	#get REQUEST
	if not REQUEST:
		REQUEST = self.REQUEST
	#get PlagResults
	session = REQUEST.SESSION
	if session.has_key('results'):
		results = session['results']
	if results == []: 
		return None

	#compute image
	image = PlagVisualizer().resultsToTorc(results, colored=True)
	#return image for displaying purposes
	imageData = StringIO()
	image.save(imageData, 'JPEG')

	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def createIntensityHeatmap(self):
	"""Creates a torc using the given results. Showing the similarity
			relations between all suspected plagiarism pairs.
	"""
	#get REQUEST
	REQUEST = self.REQUEST
	#get PlagResults
	session = REQUEST.SESSION
	if session.has_key('results'):
		results = session['results']
	if results == []: 
		return None
	#compute image
	image = PlagVisualizer().resultsToIntensityHeatmap(results)
	imageData = StringIO()
	image.save(imageData, 'JPEG')
	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def createClusterHeatmap(self, REQUEST=None):
	"""Creates a torc using the given results. Showing the similarity
			relations between all suspected plagiarism pairs.
	"""
	if not REQUEST:
		REQUEST = self.REQUEST
	#get PlagResults
	session = REQUEST.SESSION
	if session.has_key('results'):
		results = session['results']
	if results == []: return None

	#compute image
	image = PlagVisualizer().resultsToClusterHeatmap(results)
	imageData = StringIO()
	image.save(imageData, 'JPEG')

	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def createDotplotDirectCompare(self, selectedResults="", paths=""):
	"""TODO: Beschreibung
	"""
	#check preconditions
	if not selectedResults and not paths:
		return None

	#INIT
	REQUEST = self.REQUEST

	objs = self.objectValues()
	assignment_texts = []
	identifier = []
	for o in objs:#objects:
		try:
			assignment_texts.append(str(o.getFile()))
			identifier.append(o.pretty_title_or_id())
		except:
			pass

	#computing lists with ids and texts
	if not selectedResults:
		#USING SELECTED ASSIGNMENTS
		idList = paths.split()
		strList = [assignment_texts[identifier.index(id)] for id in idList]
	else:
		#USING SELECTED RESULTS
		selectedResults=selectedResults.split()
		idList = set([])
		for selres in selectedResults:
			ids = selres.split(',')
			for id in ids:
				idList.add(id)
		idList = list(idList)
		strList = [assignment_texts[identifier.index(id)] for id in idList]

	#compute Dotplot image and return
	return createDotplotFromLists(strList, idList, REQUEST);


def createDotplotFromLists(strList, idList, REQUEST):
	"""Takes two lists - one for the texts and one containing the corresponding
			ids for each text and computes the Dotplot image and returns it.
	"""
	if not strList or not idList:
		REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
		msg = 'createDotplotDirectCompare has failed.'\
			  'selectedResults: %s objects: %s assignments: &s'\
			  'strList: %s idList: %s' % (str(selectedResults), str(objects), str(assignments), str(strList), str(idList))
		return REQUEST.RESPONSE.write(msg)

	#compute image
	image = PlagVisualizer().stringListToDotplot(strList, idList=idList)
	imageData = StringIO()
	image.save(imageData, 'JPEG')
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def resultToHtml(self, result, t1, t2):
	"""Computes html texts for the given result and texts t1 and t2
			in which all similarities are marked.
			returns a list [markedText1, markedText2]
	"""        
	vis = PlagVisualizer()
	return vis.resultToHtml(result, t1, t2)        


def stringsToCP(self, basefile=""):
	REQUEST = self.REQUEST
	#get Infos
	basefile = fromUTF8toISOEncoding(basefile)
	objects = self.objectValues()
	ensemble = [str(o.getFile()) for o in objects]
	for i in xrange(len(ensemble)):
		ensemble[i] = fromUTF8toISOEncoding(ensemble[i])
	klength = 7
	normName = "NORMAL"
	if not (basefile and ensemble and klength and normName): return None

	#compute image
	vis = PlagVisualizer()
	#TODO: rename to categoriCal
	image = vis.stringsToCategoricalPatterngram(basefile, ensemble, klength, normName)
	imageData = StringIO()
	fmt = 'JPEG'
	image.save(imageData, fmt)

	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def stringsToCPP(self, basefile=""):
	REQUEST = self.REQUEST
	#get Infos
	basefile = fromUTF8toISOEncoding(basefile)
	objects = self.objectValues()
	ensemble = [str(o.getFile()) for o in objects]
	for i in xrange(len(ensemble)):
			ensemble[i] = fromUTF8toISOEncoding(ensemble[i])
	klength = 7
	normName = "NORMAL"
	if not (basefile and ensemble and klength and normName): return None
	#compute image
	vis = PlagVisualizer()
	#TODO: categoriCal
	image = vis.stringsToCompositeCategoricalPatterngram(basefile, ensemble, klength, normName)
	imageData = StringIO()
	fmt = 'JPEG'
	image.save(imageData, fmt)

	if not REQUEST:
		REQUEST = self.REQUEST
	REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
	return REQUEST.RESPONSE.write(imageData.getvalue())


def fromUTF8toISOEncoding(string):
	"""Returns the string in the 'iso-8859-15' encoding.
	"""
	try:
		iso_file = unicode(string, 'utf8').encode('iso-8859-15')
		return iso_file
	except UnicodeDecodeError:
		return string


def getPlagiarismGroups(self, results):
	"""Returns a list of lists each containing all PlagResults
			of a plagiarism group.
	"""
	#get Identifier for each cluster
	clusters = getClusters(results, onlyPositives=False, onlyNonZeroSimilarities=True)
	groups = [[] for c in clusters]
	
	for r in results:
		#get ids
		ids = r.getIdentifier()
		#look to which cluster the result belongs
		for i in xrange(len(clusters)):
			if clusters[i].__contains__(ids[0]) or clusters[i].__contains__(ids[1]):
				groups[i].append(r)
				break
	return groups


def getSimilarity(self, plagResult):
	return plagResult.getSimilarity()


def getIdentifier(self, plagResult):
	return plagResult.getIdentifier()


def containsIdentifier(self, plagResult, id):
	return plagResult.containsIdentifier(id)


def isSuspectPlagiarism(self, plagResult):
	return plagResult.isSuspectPlagiarism()
