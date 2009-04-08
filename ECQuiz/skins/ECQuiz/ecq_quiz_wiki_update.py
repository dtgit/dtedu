## Script (Python) "updateQuiz"
##parameters=wikiTextarea
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright © 2006 Otto-von-Guericke-Universität Magdeburg
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

"""This script is called when the user pressed the update button 
in the wiki_edit tab"""

I18N_DOMAIN = context.i18n_domain

target = context.getActionInfo('object/wiki_edit')['url']

ret = context.updateQuiz(context,wikiTextarea)
if ret == True:
  msg =  context.title_or_id()
  msg += context.translate( msgid='update_wiki_success',domain = I18N_DOMAIN,\
                            default = ' was successfully updated!')
else:
  msg = 'Error: ' + ret
#  msg =  context.title_or_id()
#  msg += context.translate( msgid='update_wiki_error',domain = I18N_DOMAIN,\
#                            default = ' could not be updated, you may have syntax errors!')

context.redirect('%s?portal_status_message=%s' % (target,msg))
