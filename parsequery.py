import requests
import json
import colorama
import qprompt
from colorama import Fore, Back, Style
from jira import JIRA
import getpass
from github import Github


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
                repo = result["repository"]["full_name"]
                for match in matches:
                        matchedtext = match["matches"]
                        for sterm in matchedtext:
                            if term in match["fragment"]:
                                fragment = "MATCHED CODE: \n%s" % (match["fragment"])
                                html_url = "CODE LOCATION: \n%s \n" % (result["html_url"])
                                for lines in matchedtext:
                                        lineinfo = 'Found "%s" on the lines %s.' % (lines["text"],lines["indices"])
                                makeissue(repo,fragment,html_url,lineinfo)

def makeissue(repository,fragment,html_url,lineinfo):
    print Fore.RED + fragment
    print (Style.RESET_ALL)
    body = """
    The Cyber Defense Center found cleartext credentials in this repository.

    %s


    %s

    %s
    """ % (fragment,html_url,lineinfo)
    if qprompt.ask_yesno("Is this a valid result?", dft="n"):
        print "Creating Github Issue...."
        g = Github(base_url="https://github.$ENTERPRISE.com/api/v3", login_or_token="")
        repo = g.get_repo(repository)
        createissue = repo.create_issue(title="Security: Cleartext Credentials Found", body=body)
        jiracomment = "Created issue #%s for %s repository" % (createissue.number,repository)
        print jiracomment
        jira = JIRA('https://jira.$ENTERPRISE.com',basic_auth=(jirausername,jirapassword))
        issue = jira.issue("ATTACKPT-62")
        jira.add_comment(issue, jiracomment)
        qprompt.pause()
        qprompt.clear()
    qprompt.clear()

jirausername = raw_input("JIRA Username:")
jirapassword = getpass.getpass("JIRA Password:")
search = raw_input("What is your search term :")
searchterm(search)