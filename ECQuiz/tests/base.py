# -*- coding: utf-8 -*-
#
# $Id: base.py,v 1.1 2006/10/27 17:45:01 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

# Let Zope know about the products we require above and beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('DataGridField')
ZopeTestCase.installProduct('ECQuiz')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site, and apply the membrane and borg extension profiles
# to make sure they are installed.
#setupPloneSite(extension_profiles=('membrane:default', 'borg:default'))
setupPloneSite(products=('ECQuiz',))

class ECQTestCase(PloneTestCase):
    """Base class for integration tests for the 'ECQuiz' product.
    This may provide specific set-up and tear-down operations, or
    provide convenience methods.
    """

class ECQFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'ECQuiz'
    product.  This may provide specific set-up and tear-down
    operations, or provide convenience methods.
    """
