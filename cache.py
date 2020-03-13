import time
from bs4 import BeautifulSoup
import requests
import os
import sys

def cacheIndex(do_once):
    if do_once:
        index = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/")
        if(index.status_code != 200):
            print("ibiblio error!")
            return # Basically, use last known cache
        soup = BeautifulSoup(index.content, 'html.parser')
        links = soup.find_all('a')
        links = links[4:] # Remove directory links
        out = ""
        for x in links:
            if x.get_text()[-4:] == '.tcz':
                out += x.get_text() + "\n"
        cachefile = open('/tmp/TCEFind-Index.cache', 'w')
        cachefile.write(out)
        cachefile.close()
    else:
        while True:
            time.sleep(30*60)
            cacheIndex(True)

if __name__ == "__main__":
    pid = str(os.getpid())
    pidfile = "/tmp/TCECache.pid"
    pidftmp = open(pidfile, 'w')
    pidftmp.write(pid)
    pidftmp.close()
    cacheIndex(False)
