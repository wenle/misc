#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import os
import os.path
import time

def downloadPage(path, fileName, url, params):
    data = urllib.urlencode(params)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    if(not os.path.exists(path)):
       os.makedirs(path) 
    filePath = os.path.join(path, fileName)
    if(os.path.exists(filePath)):
        print "file %s already downloaded, skip" % fileName
        return
    with open(filePath, "w") as f:
        f.write(response.read())
    time.sleep(1)

# first page uses different url pattern then later pages
def downloadFirstPage():
    url = "http://beijinglawyers.chinalawinfo.com/case/Result.asp?SFlag=11"
    values = {"Para1Type" : "1", "HidPara5IDs" : "11,13", "otherPara6":"0401", "Range" : "1", "doSearch.x" : "41", "doSearch.y" : "10"}
    print "downloading the first page ..."
    downloadPage("/var/tmp/cases", "1.html", url, values);

def downloadLaterPage(pageNo):
    url = "http://beijinglawyers.chinalawinfo.com/case/Result.asp?SFlag=13&Para1Type=1&DispLeft=0&DispWord=&CheckFlag=0&KeyWord="
    pageSelect=pageNo-1
    values = {"page" : str(pageNo), "PageSelect" : str(pageSelect), "preWhere" : "48%28%7C7B%522B%3D%25%23%30%30%32%25%23%25%2C%25%23%30%30%33%25%23%25%2C%25%23%30%30%34%25%23%25%29%20%41%4E%44%20%28%28%6570%636E%6765%6E90%3D%25%23%62%30%32%37%23%25%29%20%4F%52%20%28%6570%636E%6765%6E90%3D%25%23%62%30%32%38%23%25%29%29"}
    print "downloading the %sth page ..." % pageNo
    downloadPage("/var/tmp/cases", str(pageNo)+".html", url, values);

def download(fromPage, toPage):
    for pageNo in range(fromPage,toPage+1):
        if(pageNo == 1):
            downloadFirstPage();
        elif(pageNo > 1):
            downloadLaterPage(pageNo)        

def extractGids(fileName):
    gids = []
    with open(fileName, "r") as f:
        for line in f.readlines():
            index = line.find("?Gid=")
            if(index > 0):
                endIndex = line.find("&KeyWord")
                startIndex = index + 5
                gid = line[startIndex:endIndex]
                gids.append(gid)
    return gids

def downloadCaseTxt(gid):
    path = "/var/tmp/cases-txt"
    if(not os.path.exists(path)):
        os.makedirs(path)
    url = "http://beijinglawyers.chinalawinfo.com/case/download_n.asp?db=fnl&gid=%s&istxt=1"%gid
    print "download txt file from %s" % url
    f = urllib2.urlopen(url)
    fileName = f.info().getheader("Content-Disposition").split("=")[1].decode("gb2312")
    fullName = os.path.join(path, fileName)
    print "file name: %s"%fullName
    with open(fullName, "w") as txt:
        txt.write(f.read())
    time.sleep(1)
    return url

# download html file of list page
download(1,99)

gids = []
for i in range(1,100):
    gids.extend(extractGids("/var/tmp/cases/%s.html"%i))
failures = {}
url = ""
for gid in gids:
    try:
        url = downloadCaseTxt(gid)
    except Exception, e:
	print str(e)
        failures[gid] = url
if failures:
    print "failure records:"
    for gid in failures:
        print gid, failures[gid]

#import httplib
#conn = httplib.HTTPConnection("http://beijinglawyers.chinalawinfo.com")
#conn.request("HEAD", "/case/download_n.asp?db=fnl&gid=125789055&istxt=1")
#res=conn.get

