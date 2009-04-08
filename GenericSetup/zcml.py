##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""GenericSetup ZCML directives.

$Id: zcml.py 76859 2007-06-20 19:24:38Z rafrombrc $
"""

from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.interface import Interface

from interfaces import BASE
from registry import _profile_registry
from upgrade import _upgrade_registry

#### genericsetup:registerProfile

class IRegisterProfileDirective(Interface):

    """Register profiles with the global registry.
    """

    name = PythonIdentifier(
        title=u'Name',
        description=u'',
        required=True)

    title = MessageID(
        title=u'Title',
        description=u'',
        required=True)

    description = MessageID(
        title=u'Description',
        description=u'',
        required=True)

    directory = Path(
        title=u'Path',
        description=u"If not specified 'profiles/<name>' is used.",
        required=False)

    provides = GlobalObject(
        title=u'Type',
        description=u"If not specified 'BASE' is used.",
        default=BASE,
        required=False)

    for_ = GlobalObject(
        title=u'Site Interface',
        description=u'If not specified the profile is always available.',
        default=None,
        required=False)


_profile_regs = []
def registerProfile(_context, name, title, description, directory=None,
                    provides=BASE, for_=None):
    """ Add a new profile to the registry.
    """
    product = _context.package.__name__
    if directory is None:
        directory = 'profiles/%s' % name

    _profile_regs.append('%s:%s' % (product, name))

    _context.action(
        discriminator = ('registerProfile', product, name),
        callable = _profile_registry.registerProfile,
        args = (name, title, description, directory, product, provides, for_)
        )


#### genericsetup:upgradeStep

import zope.schema
from upgrade import UpgradeStep
from upgrade import _registerUpgradeStep
from upgrade import _registerNestedUpgradeStep

class IUpgradeStepsDirective(Interface):
    """
    Define multiple upgrade steps without repeating all of the parameters
    """
    source = zope.schema.ASCII(
        title=u"Source version",
        required=False)

    destination = zope.schema.ASCII(
        title=u"Destination version",
        required=False)

    sortkey = zope.schema.Int(
        title=u"Sort key",
        required=False)

    profile = zope.schema.TextLine(
        title=u"GenericSetup profile id",
        required=True)

class IUpgradeStepsStepSubDirective(Interface):
    """
    Subdirective to IUpgradeStepsDirective
    """
    title = zope.schema.TextLine(
        title=u"Title",
        required=True)

    description = zope.schema.TextLine(
        title=u"Upgrade step description",
        required=True)

    handler = GlobalObject(
        title=u"Upgrade handler",
        required=True)

    checker = GlobalObject(
        title=u"Upgrade checker",
        required=False)

class IUpgradeStepDirective(IUpgradeStepsDirective, IUpgradeStepsStepSubDirective):
    """
    Define multiple upgrade steps without repeating all of the parameters
    """


def upgradeStep(_context, title, profile, handler, description=None, source='*',
                destination='*', sortkey=0, checker=None):
    step = UpgradeStep(title, profile, source, destination, description, handler,
                       checker, sortkey)
    _context.action(
        discriminator = ('upgradeStep', source, destination, handler, sortkey),
        callable = _registerUpgradeStep,
        args = (step,),
        )

class upgradeSteps(object):
    """
    Allows nested upgrade steps.
    """
    def __init__(self, _context, profile, source='*', destination='*', sortkey=0):
        self.profile = profile
        self.source = source
        self.dest = destination
        self.sortkey = sortkey
        self.id = None

    def upgradeStep(self, _context, title, description, handler, checker=None):
        step = UpgradeStep(title, self.profile, self.source, self.dest, description,
                           handler, checker, self.sortkey)
        if self.id is None:
            self.id = str(abs(hash('%s%s%s%s' % (title, self.source, self.dest,
                                                 self.sortkey))))
        _context.action(
            discriminator = ('upgradeStep', self.source, self.dest, handler,
                             self.sortkey),
            callable = _registerNestedUpgradeStep,
            args = (step, self.id),
            )

    def __call__(self):
        return ()


#### cleanup

def cleanUp():
    global _profile_regs
    for profile_id in _profile_regs:
        del _profile_registry._profile_info[profile_id]
        _profile_registry._profile_ids.remove(profile_id)
    _profile_regs = []

    _upgrade_registry.clear()


from zope.testing.cleanup import addCleanUp
addCleanUp(cleanUp)
del addCleanUp
