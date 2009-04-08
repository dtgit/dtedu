##############################################################################
#
# Copyright (c) 2003-2008 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Kupu configuration file
"""
import re

# Pattern to match resolveuid links in HTML.
# Match groups:
#    tag: the html tag from the start up to the point where the uid
#    occurs.
#    url: the url containing the uid (stops after the uid: any
#    trailing part such as '/image_thumb' is not included.
#    uid: the uid itself.
UID_PATTERN = re.compile('(?P<tag><(?:a|img|object|param)\\s[^>]*(?:src|href|data|value)\s*=\s*")(?P<url>[^"]*resolveuid/(?P<uid>[^/"#? ]*))', re.DOTALL | re.IGNORECASE)

