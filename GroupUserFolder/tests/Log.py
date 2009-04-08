# -*- coding: utf-8 -*-
## GroupUserFolder
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
One can override the following variables :

LOG_LEVEL : The log level, from 0 to 5.
A Log level n implies all logs from 0 to n.
LOG_LEVEL MUST BE OVERRIDEN !!!!!


LOG_NONE = 0            => No log output
LOG_CRITICAL = 1        => Critical problems (data consistency, module integrity, ...)
LOG_ERROR = 2           => Error (runtime exceptions, ...)
LOG_WARNING = 3         => Warning (non-blocking exceptions, ...)
LOG_NOTICE = 4          => Notices (Special conditions, ...)
LOG_DEBUG = 5           => Debug (Debugging information)


LOG_PROCESSOR : A dictionnary holding, for each key, the data processor.
A data processor is a function that takes only one parameter : the data to print.
Default : LogFile for all keys.
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: Log.py 33402 2006-11-11 12:26:18Z shh42 $
__docformat__ = 'restructuredtext'



LOG_LEVEL = -1

LOG_NONE = 0
LOG_CRITICAL = 1
LOG_ERROR = 2
LOG_WARNING = 3
LOG_NOTICE = 4
LOG_DEBUG = 5

from sys import stdout, stderr, exc_info
import time
import thread
import threading
import traceback
import os
import pprint
import string

LOG_STACK_DEPTH = [-2]

def Log(level, *args):
    """
    Log(level, *args) => Pretty-prints data on the console with additional information.
    """
    if LOG_LEVEL and level <= LOG_LEVEL:
        if not level in LOG_PROCESSOR.keys():
            raise ValueError, "Invalid log level :", level

        stack = ""
        stackItems = traceback.extract_stack()
        for depth in LOG_STACK_DEPTH:
            stackItem = stackItems[depth]
            stack = "%s%s:%s:" % (stack, os.path.basename(stackItem[0]), stackItem[1],)
        pr = "%8s %s%s: " % (
            LOG_LABEL[level],
            stack,
            time.ctime(time.time()),
            )
        for data in args:
            try:
                if "\n" in data:
                    data = data
                else:
                    data = pprint.pformat(data)
            except:
                data = pprint.pformat(data)
            pr = pr + data + " "

        LOG_PROCESSOR[level](level, LOG_LABEL[level], pr, )

def LogCallStack(level, *args):
    """
    LogCallStack(level, *args) => View the whole call stack for the specified call
    """
    if LOG_LEVEL and level <= LOG_LEVEL:
        if not level in LOG_PROCESSOR.keys():
            raise ValueError, "Invalid log level :", level

        stack = string.join(traceback.format_list(traceback.extract_stack()[:-1]))
        pr = "%8s %s:\n%s\n" % (
            LOG_LABEL[level],
            time.ctime(time.time()),
            stack
            )
        for data in args:
            try:
                if "\n" in data:
                    data = data
                else:
                    data = pprint.pformat(data)
            except:
                data = pprint.pformat(data)
            pr = pr + data + " "

        LOG_PROCESSOR[level](level, LOG_LABEL[level], pr, )



def FormatStack(stack):
    """
    FormatStack(stack) => string

    Return a 'loggable' version of the stack trace
    """
    ret = ""
    for s in stack:
        ret = ret + "%s:%s:%s: %s\n" % (os.path.basename(s[0]), s[1], s[2], s[3])
    return ret


def LogException():
    """
    LogException () => None

    Print an exception information on the console
    """
    Log(LOG_NOTICE, "EXCEPTION >>>")
    traceback.print_exc(file = LOG_OUTPUT)
    Log(LOG_NOTICE, "<<< EXCEPTION")


LOG_OUTPUT = stderr
def LogFile(level, label, data, ):
    """
    LogFile : writes data to the LOG_OUTPUT file.
    """
    LOG_OUTPUT.write(data+'\n')
    LOG_OUTPUT.flush()

logFile = LogFile

import logging

CUSTOM_TRACE = 5
logging.addLevelName('TRACE', CUSTOM_TRACE)

zLogLevelConverter = {
    LOG_NONE: CUSTOM_TRACE,
    LOG_CRITICAL: logging.CRITICAL,
    LOG_ERROR: logging.ERROR,
    LOG_WARNING: logging.WARNING,
    LOG_NOTICE: logging.INFO,
    LOG_DEBUG: logging.DEBUG,
    }

def LogzLog(level, label, data, ):
    """
    LogzLog : writes data though Zope's logging facility
    """
    logger = logging.getLogger('GroupUserFolder')
    logger.log(zLogLevelConverter[level], data + "\n", )



LOG_PROCESSOR = {
    LOG_NONE: LogzLog,
    LOG_CRITICAL: LogzLog,
    LOG_ERROR: LogzLog,
    LOG_WARNING: LogzLog,
    LOG_NOTICE: LogzLog,
    LOG_DEBUG: LogFile,
    }


LOG_LABEL = {
    LOG_NONE: "",
    LOG_CRITICAL: "CRITICAL",
    LOG_ERROR:    "ERROR   ",
    LOG_WARNING:  "WARNING ",
    LOG_NOTICE:   "NOTICE  ",
    LOG_DEBUG:    "DEBUG   ",
    }
