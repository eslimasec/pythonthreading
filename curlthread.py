#!/usr/bin/env python

# Multi-threaded web page & headers grabber using Queue + Thread modules

import sys
from Queue import Queue
from threading import Thread
import pycurl
import StringIO
import traceback

domains_queue = Queue()
num_threads = 20

try:
    domains = open(sys.argv[1]).readlines()
    if len(sys.argv) > 2:
        num_threads = int(sys.argv[2])
except :
    print("Error!!! Usage: %s <file with sites fetch> [<# of concurrent threads>]" % sys.argv[0])
    sys.exit()

def query_domain(i, q):
    while True:
        domain = q.get()

        fp_html = open(domain + ".html", "wb")
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, "http://" + domain)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.MAXREDIRS, 5)
        #sometimes it takes forever to resolve but eventually occurs
#        curl.setopt(pycurl.CONNECTTIMEOUT, 2)
#        curl.setopt(pycurl.TIMEOUT, 4)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.WRITEDATA, fp_html)
        curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0")
        curl.setopt(pycurl.AUTOREFERER, 1)
        curl.setopt(pycurl.ENCODING, "gzip")
        curl.setopt(pycurl.COOKIEFILE, "")
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        #using stringio trick to obtain the buffer provided by the call back function from headerfunction
        headers_io = StringIO.StringIO()
        curl.setopt(pycurl.HEADERFUNCTION, headers_io.write)
        print str(i+1) + " -> Downloading: " + "http://" + domain
        try:
            curl.perform()
        except:
            #traceback.print_exc(file=sys.stderr)
	    fp_error = open(domain + ".error", "wb")
	    error = traceback.format_exc().splitlines()
	    fp_error.write(error[-1] + '\n')	
	    fp_error.close()
        curl.close()
        fp_html.close()
        fp_headers = open(domain + ".headers", "wb")
        fp_headers.write(headers_io.getvalue())
        fp_headers.close
        # sys.stdout.write(".")
        # sys.stdout.flush()
        q.task_done()

# Set up some threads to fetch the domains
for i in range(num_threads):
    worker = Thread(target=query_domain, args=(i, domains_queue,))
    worker.setDaemon(True)
    worker.start()

for domain in domains:
    domains_queue.put(domain.rstrip())

domains_queue.join()
print "All threads completed"
