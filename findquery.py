import requests
import json
import colorama
from colorama import Fore, Back, Style

def searchterm(term):
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q='%s'" % (term)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        pages = int(searchdata["total_count"])/30
        print "%s pages to iterate" % pages
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
                                print Fore.RED + "MATCHED CODE: \n%s" % (match["fragment"])
                                print Fore.YELLOW + "CODE LOCATION: \n%s \n" % (result["html_url"])
                                for lines in matchedtext:
                                        print Fore.GREEN + 'Found "%s" on the lines %s.' % (lines["text"],lines["indices"])
                                print '\n'
                                print (Style.RESET_ALL)

search = raw_input("What is your search term :")
searchterm(search)