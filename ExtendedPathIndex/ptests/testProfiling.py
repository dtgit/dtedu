from common import Dummy
import os
import sys
from os.path import realpath
import hotshot, hotshot.stats

epi_path = '/'.join(realpath(os.getcwd()).split('/')[:-1])
sys.path.insert(0, epi_path)
from ExtendedPathIndex import ExtendedPathIndex

index = ExtendedPathIndex( 'path' )


def profile(prof_name, method, args=(), kwargs={}, times=100):
        def run_multiple(method, args, kwargs):
            for i in range(times):
               r = method(*args, **kwargs)
            return r
        prof = hotshot.Profile(prof_name)
        result = prof.runcall(run_multiple, method, args, kwargs)
        prof.close()
        print prof_name
        stats = hotshot.stats.load(prof_name)
        # Print calls ordered by time
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(15)
        return result

def createContent(index, f1=9, f2=50, f3=10):
    count = 0
    for i in range(f1):
        meth1 = index.search
        args = ()
        kwargs = {"path": '/plone/f-0/f-0-0/f-0-0-0',
                  "navtree": 1,
                  "depth": 1}
        prof_id = 'profile_EPI_%s.prof'%count
        result = profile(prof_id, meth1, args, kwargs)
        print 'num of results: %s'%len(result.keys())
        f1id = 'f-%d' % i
        folder1 = Dummy("/plone/%s" % f1id)
        count += 1
        index.index_object(count, folder1)

        for j in range(f2):
            f2id = 'f-%d-%d' % (i, j)
            folder2 = Dummy("/plone/%s/%s" % (f1id, f2id))
            count += 1
            index.index_object(count, folder2)

            for k in range(f3):
                f3id = 'f-%d-%d-%d' % (i, j, k)
                folder3 = Dummy("/plone/%s/%s/%s" % (f1id, f2id, f3id))
                count += 1
                index.index_object(count, folder3)

                for m in range(100):
                    docid = 'f-%d-%d-%d-%d' % (i, j, k, m)
                    doc = Dummy("/plone/%s/%s/%s/%s" % (f1id, f2id, f3id, docid))
                    count += 1
                    index.index_object(count, doc)
    prof_id = 'profile_EPI_%s.prof'%count
    result = profile(prof_id, meth1, args, kwargs)
    print 'num of results: %s'%len(result.keys())
    print 'Created %s entries' % count

createContent(index)