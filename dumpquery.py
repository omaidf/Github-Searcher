import requests
import json
import colorama
from colorama import Fore, Back, Style
import sys

if len(sys.argv) !=2:
    print('Usage: python dumpquery.py file.txt')

    print('Function: Read lines from file. Parse Github & dump links that match line.')
    sys.exit(0)

def searchterm(term):
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q='%s'" % (term)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        pages = int(searchdata["total_count"])/30
        # print "%s pages to iterate" % pages
        if pages > 35:
                pages = 35
        for i in range(1,pages):
                scrapeterms(term,i)

def scrapeterms(term,page):
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q='%s'&page=%s" % (term,page)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        results = searchdata["items"]
        for result in results:
                matches = result["text_matches"]
                for match in matches:
                        matchedtext = match["matches"]
                        for sterm in matchedtext:
                            if term in match["fragment"]:
                                # print Fore.RED + "MATCHED CODE: \n%s" % (match["fragment"])
                                print result["html_url"]
                                # for lines in matchedtext:
                                        # print Fore.GREEN + 'Found "%s" on the lines %s.' % (lines["text"],lines["indices"])
                                # print '\n'
                                print (Style.RESET_ALL)


def readfile():
    readfile = sys.argv[1]
    with open(readfile) as f:
        for line in f:
            searchterm(line)

readfile()