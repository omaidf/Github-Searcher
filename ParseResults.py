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

def makeissue(repository,fragment,html_url,lineinfo):
    f = open("findings.txt","a+")
    print fragment
    print "\n"
    body = """
    Code Fragment:
    %s\n
    Code Location:\n
    %s
    Lines:\n
    %s
    """ % (fragment,html_url,lineinfo)
    if qprompt.ask_yesno("Is this a valid result?", dft="n"):
        f.write(body)
        qprompt.clear()
        f.close()
    qprompt.clear()
    f.close()

def startfile():
    print "Loading File..."
    results = sys.argv[1]
    with open(results, 'r') as f:
        resultdata =  json.load(f)
        print "%s Findings Found" % len(resultdata["results"])
        for result in resultdata["results"]:
            makeissue(result["repo"],result["fragment"],result["html_url"],result["lineinfo"])
        # print "Logging into JIRA..."
        # jirlogin()

if len(sys.argv) !=2:
    print('Usage: python ParseResults.py findings.json')
    sys.exit(0)

startfile()