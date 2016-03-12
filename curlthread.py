#!/usr/bin/python

# Simple multi-threaded example using Queue + Thread modules

import sys
import time
from Queue import Queue
from threading import Thread
import pycurl

num_threads = 20
domains_queue = Queue()

try:
    domains = open(sys.argv[1]).readlines()
    if len(sys.argv) > 2:
        num_threads = int(sys.argv[2])
except :
    print("Error!!! Usage: %s <file with domains to fetch> [<# of concurrent threads>]" % sys.argv[0])
    raise SystemExit

def query_domain(i, q):
    while True:
        domain = q.get()

        # time.sleep(i+2)
        fp = open(domain + "-curl.out", "wb")
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, "http://" + domain)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.MAXREDIRS, 5)
        #it takes forever to resolve sometimes
#        curl.setopt(pycurl.CONNECTTIMEOUT, 2)
#        curl.setopt(pycurl.TIMEOUT, 4)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.WRITEDATA, fp)
        curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0")
        curl.setopt(pycurl.AUTOREFERER, 1)
        curl.setopt(pycurl.ENCODING, "gzip")
        curl.setopt(pycurl.COOKIEFILE, "")
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        print str(i+1) + " -> Downloading: " + "http://" + domain
        try:
            curl.perform()
        except:
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
        curl.close()
        fp.close()
        sys.stdout.write(".")
        sys.stdout.flush()
        q.task_done()

# Set up some threads to fetch the domains
for i in range(num_threads):
    worker = Thread(target=query_domain, args=(i, domains_queue,))
    worker.setDaemon(True)
    worker.start()

for domain in domains:
    domains_queue.put(domain.rstrip())

print "Main thread waiting"
domains_queue.join()
print "All threads completed"
