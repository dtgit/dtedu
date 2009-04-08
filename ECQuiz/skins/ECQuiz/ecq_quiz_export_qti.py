## Script (Python) "exortTest"
##parameters=
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_quiz_export_qti.py,v 1.4 2007/07/04 01:09:26 wfenske Exp $
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

""" This script will be called when somebody presses 'Export' in the 
    import_export.
"""

REQUEST  = container.REQUEST
RESPONSE = REQUEST.RESPONSE

I18N_DOMAIN = context.i18n_domain

# an arbitrary marker than can be identified using 'is'/'is not'
nullVal = ['foo'] 
ignoreErrors = REQUEST.get('ignore_export_errors', nullVal) is not nullVal

# Call 'ECQuiz.processQTIExport()"
package, errors = context.processQTIExport()
if errors:
    # The uploaded file has errors.
    msg = context.translate(
        msgid   = 'errors_occurred',
        domain  = I18N_DOMAIN,
        default = 'The following error(s) occurred:') \
        + ' ' + context.str(errors)
else:
    msg = ''
msg = msg.replace('\n', ' - ')
msg = msg.strip()

if (msg and (not ignoreErrors)) or (package is None):
    if not msg:
        msg = context.translate(
            msgid   = 'unexpected_export_error',
            domain  = I18N_DOMAIN,
            default = 'An an unexpected has occurred. '
            'The quiz could not be exported.')
    target = context.getActionInfo('object/import_export')['url']
    context.redirect('%s?portal_status_message=%s' % (target, msg))
    # Seems like for some reason I have to put this nonsense here.
    RESPONSE.setHeader('Content-Disposition', 'attachment; filename=error.txt')
    RESPONSE.setHeader('Content-Type', 'text/plain')
    RESPONSE.setHeader('Content-Length', 0)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
else:
    filename = context.pathQuote(context.title_or_id()) + '.' + 'zip'    
    RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
    RESPONSE.setHeader('Content-Type', 'application/zip')
    RESPONSE.setHeader('Content-Length', package.len)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    package.seek(0)
    n=1 << 16
    while package.tell() < package.len:
        blockSize = min(n, package.len - package.tell())
        data = package.read(blockSize)
        RESPONSE.write(data)
    return ''
