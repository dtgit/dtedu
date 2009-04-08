import time
import transaction
import sys
import os
from os.path import realpath
import math

from ZODB import DB
from ZODB.FileStorage import FileStorage

from common import Root, Dummy

NUM_ITER = 500

epi_path = '/'.join(realpath(os.getcwd()).split('/')[:-1])
sys.path.insert(0, epi_path)
from ExtendedPathIndex import ExtendedPathIndex

print '\nOpening file storage'

storage = FileStorage(file_name='EPI.fs', create=False, read_only=True)
db = DB(storage)

transaction.begin()
conn = db.open()
root = conn.root()

plone = root['plone']
index = plone.index

start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone', "depth": 2}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)
res1 = res[0].keys()

# Try not touching the /plone set as it contains 200820 entries
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/', "depth": 3, 'startlevel':1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)
res2 = res[0].keys()

if res1 == res2:
    print "Results are the same"
else:
    print "Different results!"

print "\n============================"

print "Navtree query at root"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone', "navtree": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

print "Navtree query at /plone/f-1/f-1-1/f-1-1-1"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone/f-1/f-1-1/f-1-1-1', "navtree": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

print "\n============================"

print "Folder listing at portal root"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone', "depth": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

print "Folder listing at /plone/f-1"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone/f-1', "depth": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

print "\n============================"

print "Breadcrumbs at portal root"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone', "depth": 0,
                                       "navtree": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

print "Breadcrumbs at /plone/f-1/f-1-1/f-1-1-1"
start = time.time()
for i in range(NUM_ITER):
    res = index._apply_index({"path": {'query': '/plone/f-1/f-1-1/f-1-1-1',
                                       "depth": 0, "navtree": 1}})
end = time.time()
print 'Found %s in %s seconds (%s iterations)' % (len(res[0].keys()),
                                                  end-start, NUM_ITER)

transaction.abort()
conn.close()

db.close()
storage.close()
#storage.cleanup() # For removing all files
