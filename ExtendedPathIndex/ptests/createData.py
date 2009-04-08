import transaction
import sys
import os
from os.path import realpath
import math

from ZODB import DB
from ZODB.FileStorage import FileStorage

from common import Root, Dummy


epi_path = '/'.join(realpath(os.getcwd()).split('/')[:-1])
sys.path.insert(0, epi_path)
from ExtendedPathIndex import ExtendedPathIndex
LIMIT = 500
DEPTHLIMIT = 5


storage = FileStorage(file_name='EPI.fs', create=True)
db = DB(storage)

transaction.begin()
conn = db.open()
root = conn.root()

index = ExtendedPathIndex( 'path' )

# Based on Pan Junyong's code
# this is synthetic and not evenly distributed
def buildTree(index, f1=20, f2=20, f3=1):
    count = 0
    for i in range(f1):
        f1id = 'f-%d' % i
        folder1 = Dummy("/plone/%s" % f1id)
        count += 1
        index.index_object(count, folder1)

        for j in range(f2):
            transaction.commit(1)
            f2id = 'f-%d-%d' % (i, j)
            folder2 = Dummy("/plone/%s/%s" % (f1id, f2id))
            count += 1
            index.index_object(count, folder2)

            for k in range(f3):
                f3id = 'f-%d-%d-%d' % (i, j, k)
                folder3 = Dummy("/plone/%s/%s/%s" % (f1id, f2id, f3id))
                count += 1
                index.index_object(count, folder3)

                for m in range(500):
                    docid = 'f-%d-%d-%d-%d' % (i, j, k, m)
                    doc = Dummy("/plone/%s/%s/%s/%s" % (f1id, f2id, f3id, docid))
                    count += 1
                    index.index_object(count, doc)
    print 'Created %s entries' % count

buildTree(index, 20,20)

plone = Root('plone')
plone.index = index
root['plone'] = plone

transaction.commit()
conn.close()

db.close()
storage.close()
#storage.cleanup() # For removing all files
