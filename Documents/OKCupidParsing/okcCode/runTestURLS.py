from urllib2 import urlopen, HTTPError
from bs4 import BeautifulSoup
import zipfile, zlib, datetime, copy, csv
from listOfTestURLS import bigTestList
from okc_functions import *

def runDatIsh(url):
    soup = soupify(url)
    ud = scrapeDateData(soup)
    dl = [soup, ud]
    return dl

testList = copy.copy(bigTestList)
print len(testList)
for i in range(len(testList)):
    testList[i] = runDatIsh(testList[i])
    


finalCSVList = []
for profileDataList in testList:
    try:
        finalCSVList.append(caseFunctionTries(profileDataList))
    except:
        finalCSVList.append([])

for i in finalCSVList:
    print len(i)
    #print "----"
