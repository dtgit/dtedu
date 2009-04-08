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

"""This script is called when the wiki_edit tab is loaded."""

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE
I18NDOMAIN = context.i18n_domain

filename = context.pathQuote(context.title_or_id()) + '.txt'
package = context.exportQuiz(context,filename)

if package is None:
    target = context.getActionInfo('object/wiki_edit')['url']
    msg = context.translate(msgid='export_wiki_error',domain=I18NDOMAIN,\
                            default='An error occured, the quiz could not be exported!')
    context.redirect('%s?portal_status_message=%s' % (target,msg))
else:
    RESPONSE.setHeader('Content-Disposition','attachment; filename=' + filename)
    RESPONSE.setHeader('Content-Type','text/plain')
    RESPONSE.setHeader('Content-Length',package.len)
    RESPONSE.setHeader('Accept-Ranges','bytes')
    package.seek(0)
    s = ''
    while package.tell() < package.len:
       s += package.read()
    return s  
