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
    if searchword is None or searchword == '':
        return "<head><title> TCE-Find </title></head><body><h1> No search word specified! </h1></body>"
    try:
        indexfile = open('/tmp/TCEFind-Index.cache', 'r')
        indexcache = indexfile.read()
        indexfile.close()
    except:
        return "<head><title> TCE-Find </title></head><body><h1> Index cache error! </h1></body>"
    names = indexcache.splitlines()

    # Match in names
    matching = [s for s in names if searchword in s]

    # Build html
    htmlout = "<head><title> TCE-Find - " + searchword + "</title></head><body>"
    if matching == []:
        return htmlout + "<h1> No packages found! </h1></body>"
    for x in matching:
        htmlout += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>\n"
    htmlout += "</body>"
    return htmlout

@app.route("/info", methods=['GET'])
def package_info():
    packagename = request.args.get("package")
    if packagename is None or packagename == '':
        return "<head><title> TCE-Find </title></head><body><h1> No package specified! </h1></body>"
    md5sum = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".md5.txt")
    if md5sum.status_code != 200:
        return "<head><title> TCE-Find - " + packagename + "</title></head><body><h1> Package not found! </h1></body>"
    info = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".info").content.decode("utf-8")
    dep = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".dep")
    depret = ""
    if dep.status_code == 200:
        dep = dep.content.decode("utf-8").splitlines()
        depret = "<h2> Dependency: </h2><br>"
        for x in dep:
            depret += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>"
    return render_template("info.html", info=info, md5sum=md5sum.content.decode("utf-8"), dep=depret, packagename=packagename)

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

if __name__ == '__main__':
    cacheIndex(True)
    _thread.start_new_thread(cacheIndex, (True,))
    app.run()
