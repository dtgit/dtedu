##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
# Run jslint over modified javascript files
import os, sys, glob, time
import cPickle
from Queue import Queue
import threading

COMPILE_COMMAND = "java org.mozilla.javascript.tools.shell.Main %(lint)s --options %(options)s %(file)s"
ERRORS = (IOError, )
if sys.platform=='win32':
    COMPILE_COMMAND = "cscript /NoLogo %(lint)s --options %(options)s %(file)s"
    ERRORS = (IOError, WindowsError)

def lint(name):
    cmd = COMPILE_COMMAND % dict(lint=LINT, file=name, options=OPTIONS)
    stream = os.popen(cmd)
    data = stream.read()
    rc = stream.close()
    return data, rc

def scriptrelative(relative):
    """Find absolute path of file relative to this script"""
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)

LINT = scriptrelative('jslint.js')
OPTIONS = scriptrelative('jslint.opts')
STATUSFILE = scriptrelative('lint.record')

def filelist(*patterns):
    for p in patterns:
        names = glob.glob(scriptrelative(p))
        for n in names:
            yield os.path.normpath(n)

def newfiles(status, *patterns):
    for n in filelist(*patterns):
        mtime = os.stat(n).st_mtime
        if n in status and status[n] == mtime:
            continue
        status[n] = mtime
        yield n

def basetime(marker):
    try:
        mtime = os.stat(marker).st_mtime
    except ERRORS:
        mtime = 0.0
    return mtime

def loadstatus(name):
    try:
        f = open(name, 'rb')
    except ERRORS:
        return {}
    try:
        try:
            data = cPickle.load(f)
        except EOFError:
            return {}
    finally:
        f.close()
    return data

def savestatus(name, status):
    f = open(name, 'wb')
    cPickle.dump(status, f)
    f.close()

# Thread pool code.
class Pool:
    def __init__(self, nThreads):
        self.nThreads = nThreads
        self.requestQueue = Queue()
        self.responseQueue = Queue()
        self.exitcode = 0
        self.thread_pool = [
                threading.Thread(target=self.run)
                for i in range(nThreads)]
        for t in self.thread_pool:
            t.start()

    def run(self):
        for item in iter(self.requestQueue.get, None):
            if not self.exitcode:
                self.responseQueue.put([item, lint(item)])
            else:
                # Error state, just ignore this item
                self.responseQueue.put([item, ("skipped %s" % item, 1)])

    def handleResponse(self, item, data, rc):
        if rc is not None:
            if item in status:
                del status[item]
            self.exitcode = max(self.exitcode, rc)
        print data

    def process(self, items):
        items = list(items)
        for item in items:
             self.requestQueue.put(item)
        for dummy in items:
            item, (data, rc) = self.responseQueue.get()
            self.handleResponse(item, data, rc)

    def shutdown(self):
        # and then to shut down the threads when you've finished:
        for t in self.thread_pool:
            self.requestQueue.put(None)
        for t in self.thread_pool:
             t.join()

if __name__=='__main__':
    status = loadstatus(STATUSFILE)
    exitcode = None
    threads = Pool(4)
    work = newfiles(status, 'common/*.js', 'plone/kupu_plone_layer/*.js')
    threads.process(work)
    threads.shutdown()
    savestatus(STATUSFILE, status)
    sys.exit(exitcode)
