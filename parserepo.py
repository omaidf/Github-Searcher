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

def searchterm(term,searchrepo):
        global total_count
        url = "https://github.$ENTERPRISE.com/api/v3/search/code?q=%s:repo:%s" % (term,searchrepo)
        headers = {'Accept':'application/vnd.github.v3.text-match+json'}
        search = requests.get(url,headers=headers)
        searchdata = json.loads(search.content)
        pages = int(searchdata["total_count"])/30
        total_count = int(searchdata["total_count"])
        print "%s possible findings" % total_count
        print "%s pages to iterate" % pages
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
                                fragment = "MATCHED CODE: \n%s" % (match["fragment"])
                                html_url = "CODE LOCATION: \n%s \n" % (result["html_url"])
                                for lines in matchedtext:
                                        lineinfo = 'Found "%s" on the lines %s.' % (lines["text"],lines["indices"])
                                total_count -= 1
                                if total_count == 0:
                                    print "All findings analyzed! Creating JIRA...."
                                    createjira()
                                else:
                                    makeissue(repo,fragment,html_url,lineinfo)


def createjira():
        title = "%s Repository Security" % (searchrepo)
        auth_jira = JIRA('https://jira.$ENTERPRISE.com',basic_auth=(jirausername,jirapassword))
        issue_dict = {
        'project': 'CTM',
        'summary': title,
        'description': 'Please contact MIR for attachment password',
        'issuetype': {'name': 'Security'},
        'duedate': '2019-09-17'}
        new_issue = auth_jira.create_issue(fields=issue_dict)
        print "Created: https://jira.$ENTERPRISE.com/browse/%s" % (new_issue.key)
        f= open("findings.txt","w+")
        f.writelines(["%s\n" % item  for item in resulttext])
        f.close()
        pyminizip.compress("findings.txt", None, "findings.zip", "password1", 0)
        auth_jira.add_attachment(issue=new_issue.key, attachment='findings.zip')
        os.remove("findings.txt")
        os.remove("findings.zip")
        print "Uploaded findings to %s" % (new_issue.key)
        sys.exit()


def makeissue(repository,fragment,html_url,lineinfo):
    print Fore.RED + fragment

    print (Style.RESET_ALL)
    body = """
    %s

    %s

    %s
    """ % (fragment,html_url,lineinfo)
    if qprompt.ask_yesno("Is this a valid result?", dft="n"):
        resulttext.append(body)
        qprompt.pause()
        qprompt.clear()
    qprompt.clear()

jirausername = raw_input("JIRA Username:")
jirapassword = getpass.getpass("JIRA Password:")
testauth = JIRA('https://jira.$ENTERPRISE.com',basic_auth=(jirausername,jirapassword))
searchrepo = raw_input("What repository would you like to search :")
search = raw_input("What is your search term :")
searchterm(search,searchrepo)