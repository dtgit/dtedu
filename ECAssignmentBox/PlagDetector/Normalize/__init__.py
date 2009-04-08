# -*- coding: utf-8 -*-
# $Id: __init__.py,v 1.1 2007/07/02 14:40:25 peilicke Exp $
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

#
#To avoid updating of all modules using the normalizer
#here all normalizer should be added to the __all__ list
#which are then imported by:
#from PlagDetector.Normalize import *
#
#Please also update normNames which is a dictonary used for
#referencing the normalizer in the PlagChecker.py etc.
#

__all__ = ["normNames", "normNormal", "normPython"]

import normNormal, normPython

normNames = {'NORMAL': normNormal.normalize, 
             'PYTHON': normPython.normalize}
