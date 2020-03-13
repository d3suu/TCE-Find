from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def webform():
    return render_template('searchform.html')

@app.route('/search', methods=['GET'])
def parse_search():
    searchword = request.args.get("searchword")
    if searchword is None or searchword == '':
        return render_template('error.html', error="No search word specified!")
    try:
        indexfile = open('/tmp/TCEFind-Index.cache', 'r')
        indexcache = indexfile.read()
        indexfile.close()
    except:
        return render_template('error.html', error="Index cache error!")
    names = indexcache.splitlines()

    # Match in names
    matching = [s for s in names if searchword in s]

    # Build html
    htmlout = "<head><title> TCE-Find - " + searchword + "</title></head><body>"
    if matching == []:
        return render_template('error.html', error="No packages found!")
    for x in matching:
        htmlout += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>\n"
    htmlout += "</body>"
    return htmlout

@app.route("/info", methods=['GET'])
def package_info():
    packagename = request.args.get("package")
    if packagename is None or packagename == '':
        return render_template('error.html', error="No package specified!")
    md5sum = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".md5.txt")
    if md5sum.status_code != 200:
        return render_template('error.html', error="Package not found!")
    info = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".info").content.decode("utf-8")
    dep = requests.get("http://distro.ibiblio.org/tinycorelinux/11.x/x86/tcz/" + packagename + ".dep")
    depret = ""
    if dep.status_code == 200:
        dep = dep.content.decode("utf-8").splitlines()
        depret = "<h2> Dependency: </h2><br>"
        for x in dep:
            depret += "<a href=\"/info?package=" + x + "\">" + x + "</a><br>"
    return render_template("info.html", info=info, md5sum=md5sum.content.decode("utf-8"), dep=depret, packagename=packagename)

if __name__ == '__main__':
    app.run()
