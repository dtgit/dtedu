#!/usr/bin/env python
"""Converts a i18n layout to a locales layout

Author: Christian Heimes
License: ZPL 2.1
"""
import os
import os.path
import re
import glob

RE_DOMAIN = re.compile(r"\"Domain: ?([a-zA-Z-_]*)\\n\"")
RE_LANGUAGE = re.compile(r"\"Language-[cC]ode: ?([a-zA-Z-_]*)\\n\"")

base = '.'
i18n = os.path.join(base, 'i18n')
locales = os.path.join(base, 'locales')
po_files = glob.glob(os.path.join(i18n, '*.po'))
pot_files = glob.glob(os.path.join(i18n, '*.pot'))

def getLocalsPath(lang, domain):
    po = '%s.po' % domain
    path = os.path.join(locales, lang, 'LC_MESSAGES')
    return path, po

def svnAdd(path):
    path = path.split(os.sep)
    for l in range(len(path)):
        l+=1
        p = os.path.join(*path[:l])
        if not os.path.isdir(os.path.join(p, '.svn')):
            os.system("svn add %s" % p)

for po in po_files:
    fd = open(po, 'r')
    header = fd.read(5000) # 5,000 bytes should be fine 
    fd.close()
 
    domain = RE_DOMAIN.findall(header)
    lang = RE_LANGUAGE.findall(header)
    if domain and lang:
        domain = domain[0]
        lang = lang[0]
    else:
        print "Failed to get metadata for %s" % po
        continue

    po_path, new_po = getLocalsPath(lang, domain)
    if not os.path.isdir(po_path):
        os.makedirs(po_path)

    src = po
    dst = os.path.join(po_path, new_po)
    svnAdd(po_path)
    os.system("svn mv %s %s" % (src, dst))
    print "Copied %s - %s" % (po_path, new_po)

for pot in pot_files:
    os.system("svn mv %s %s" % (pot, locales))
    print "Copied %s" % pot

