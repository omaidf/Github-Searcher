import requests
import json
import colorama
import qprompt
from colorama import Fore, Back, Style
from jira import JIRA
import getpass
from github import Github
import os
import pyminizip
import sys

resulttext = []
total_count = 0

findings = {"results":[]}
# result = findings["result"]

searchkeys = ['db.password','ftp.pass','secret_token','apikey','passwd','passkey','db.pass','API_Key','Ftp_password','Ppcapr_pwd','PGP Private','PGP_Key','Pgpassword','Passphrase','Ppc_psql_pwd','Server.password']


# Create list of variables
# Test Auth
# Grab all results
# Put results into one 

def searchterm(term,searchrepo):
        global total_count
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q=%s:repo:%s" % (term,searchrepo)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        pages = int(searchdata["total_count"])/30
        total_count = int(searchdata["total_count"])
        print "%s possible findings for %s" % (total_count,term)
        # print "%s pages to iterate" % pages
        if pages > 35:
                pages = 35
        if pages == 0:
            scrapeterms(term,searchrepo,pages)
        else:
            for i in range(1,pages):
                    scrapeterms(term,searchrepo,i)

def scrapeterms(term,searchrepo,page):
        global total_count
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q=%s:repo:%s&page=%s" % (term,searchrepo,page)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        results = searchdata["items"]
        for result in results:
                matches = result["text_matches"]
                repo = result["repository"]["full_name"]
                for match in matches:
                        matchedtext = match["matches"]
                        for sterm in matchedtext:
                            if term in match["fragment"]:
                                fragment = "%s" % (match["fragment"])
                                html_url = "%s" % (result["html_url"])
                                for lines in matchedtext:
                                        lineinfo = 'Found "%s" on lines %s.' % (lines["text"],lines["indices"])
                                        result = {'repo':repo,'fragment':fragment,'html_url':html_url,'lineinfo':lineinfo}
                                        findings["results"].append(result)
                                total_count -= 1
                                if total_count == 0:
                                    print ""

def askforrepo():
    print "Example: oomaidf/GithubSearch"
    searchrepo = raw_input("What repository would you like to search :")
    # search = raw_input("What is your search term :")
    for key in searchkeys:
        searchterm(key,searchrepo)

askforrepo()
file = open("findings.json","w") 
file.write(json.dumps(findings)) 
file.close()
print "Wrote results to findings.json!"

# print findings
