#!/usr/bin/python

# Simple multi-threaded example using Queue + Threat modules

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
        print str(i+1) + " -> Downloading: " + domain
        time.sleep(i+2)
        q.task_done()

# Set up some threads to fetch the domains
for i in range(num_threads):
    worker = Thread(target=query_domain, args=(i, domains_queue,))
    worker.setDaemon(True)
    worker.start()

for domain in domains:
    domains_queue.put(domain)

print "Main thread waiting"
domains_queue.join()
print "All threads completed"
