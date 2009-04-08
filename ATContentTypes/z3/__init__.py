# This module is purely for BBB, it is deprecated, do not import from here
import logging
# A * import because we want to mimic the original
from Products.ATContentTypes.interface import *

logger = logging.getLogger('ATContentTypes')
logger.log(logging.WARNING, '%s \n%s',
           'Deprecation Warning',
           'Products.ATContentTypes.z3 is deprecated. The z3 interfaces are '
           'now in the interface module.',)
