try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator, \
         BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False
    
import types
try:
	import transaction
except:
	from Products.Archetypes import transaction

from types import StringTypes
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.debug import log
from Products.Archetypes.BaseUnit import BaseUnit
from Products.CMFPlone.utils import safe_hasattr

from Acquisition import aq_base

from Products.ECLecture.config import *

###############################################################################

def instructor_to_instructors(obj, val, **kwargs):
    log('%s: instructor_to_instructors called for %s' % (ECL_NAME,
                                                         obj.TitleOrId()))
    
    if isinstance(val, StringTypes):
        return [val,]
    else:
        return val

def from_1_1_to_1_2(self, out):
    """
    Migrate from 1.1 to 1.2: We now use a field `instructors' instead
    of `instructor', and it contains a list instead of a string.
    """
    if not haveContentMigrations:
        print >> out, "WARNING: Install contentmigrations to be able to migrate from 1.1 to 1.2"
        return

    class InstructorsMigrator(InlineFieldActionMigrator):
        src_portal_type = src_meta_type = (ECL_META,)

        fieldActions = ({ 'fieldName':    'instructor',
                          'newFieldName': 'instructors',
                          'transform':    instructor_to_instructors,
                          },
                        )

    # Migrate instructor field
    portal = getToolByName(self, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(portal, InstructorsMigrator, query={})
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating from instructor to instructors"
    walker.go()
    
###############################################################################

def migrate(self):
    out = StringIO()
    print >> out, 'Starting %s migration' % ECL_NAME
    from_1_1_to_1_2(self, out)
    print >> out, '%s migrations finished' % ECL_NAME
    return out.getvalue()
