from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time
import _thread

app = Flask(__name__)

@app.route('/')
def webform():
    return render_template('searchform.html')

@app.route('/search', methods=['GET'])
def parse_search():
    searchword = request.args.get("searchword")
    #page = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/")
    #if(page.status_code != 200):
    #    return "ibiblio error!"
    #soup = BeautifulSoup(page.content, 'html.parser')
    indexfile = open('/tmp/TCEFind-Index.cache', 'r')
    indexcache = indexfile.read()
    indexfile.close()
    soup = BeautifulSoup(indexcache, 'html.parser')
    links = soup.find_all('a')
    links = links[4:] # Remove directory links
    
    # Make list of package names
    names = []
    for x in links:
        if x.get_text()[-4:] == '.tcz':
            names.append(x.get_text())

    # Match in names
    matching = [s for s in names if searchword in s]

    # Build html
    htmlout = "<head><title> TCE-Find - " + searchword + "</title></head><body>"
    for x in matching:
        htmlout += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>\n"
    htmlout += "</body>"
    return htmlout

@app.route("/info", methods=['GET'])
def package_info():
    packagename = request.args.get("package")
    info = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".info").content.decode("utf-8")
    md5sum = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".md5.txt").content.decode("utf-8")
    dep = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".dep")
    depret = ""
    if dep.status_code == 200:
        dep = dep.content.decode("utf-8").splitlines()
        depret = "<h2> Dependency </h2><br>"
        for x in dep:
            depret += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>"
    return render_template("info.html", info=info, md5sum=md5sum, dep=depret, packagename=packagename)

def cacheIndex(do_once):
    if do_once:
        index = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/").content.decode("utf-8")
        cachefile = open('/tmp/TCEFind-Index.cache', 'w')
        cachefile.write(index)
        cachefile.close()
    else:
        while True:
            time.sleep(30*60)
            cacheIndex(True)

if __name__ == '__main__':
    cacheIndex(True)
    _thread.start_new_thread(cacheIndex, (True,))
    app.run()
