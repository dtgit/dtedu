## Script (Python) "importQuiz"
##parameters=file=''
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

"""This script is called when the wiki_edit tab is loaded"""

I18NDOMAIN = context.i18n_domain

if(same_type(file,'') or same_type(file,u'')):
  msg = context.translate(msgid='string_not_file',domain=I18NDOMAIN,\
                          default='Got a string, not a file for read.')
  msg += ' ' + file                        
else:
  ret = context.importQuiz(context,file)
  if ret == True:
    msg = context.translate(msgid='import_wiki_success',domain=I18NDOMAIN,\
                            default='The quiz was successfully imported.')
  else:
    msg = context.translate(msgid='import_wiki_error',domain=I18NDOMAIN,\
                            default='An error occured, could not import quiz!')

target = context.getActionInfo('object/wiki_edit')['url']
context.redirect('%s?portal_status_message=%s' % (target,msg))
