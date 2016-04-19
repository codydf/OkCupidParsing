from urllib2 import urlopen
from lxml import etree
from bs4 import BeautifulSoup

monthDictionary = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}

mainURL = "/web/*/http://www.okcupid.com/profile?tuid=14367*"
urlsList = []
dupList = []
prefixURL = "http://web.archive.org"
fullURL = prefixURL + mainURL

print fullURL

def soupify(url):
    return BeautifulSoup(urlopen(url).read())

def yearParser(profileID, start, end):
    currentYear = int(start)
    endYear = int(end)
    yearURL = ""
    yearURLList = []
    while currentYear <= endYear:
        urlYearSnip = str(currentYear) + 10*("0") + "*"
        yearURL = prefixURL + "/web/" + urlYearSnip + "/http://www.okcupid.com/profile?tuid=" + profileID
        yearURLList.append(yearURL)
        currentYear += 1
    
    return yearURLList

bigSoup = soupify(fullURL)
urlClassTags = bigSoup.find_all("td", class_="url")

print "urlClassTags"
print urlClassTags

for profile in urlClassTags:
    isUnique = (profile.parent.find_all("td", class_="uniques")[0].contents == [u'1'])
    url = profile.a.get("href")
    profileCount = (prefixURL + url, isUnique)
    if isUnique:
        urlsList.append(profileCount)
    else:
        date = ""
        startYear = str(profile.parent.find_all("td", class_="dateFrom")[0].contents[0])[-4:]
        endYear = str(profile.parent.find_all("td", class_="dateTo")[0].contents[0])[-4:]
  

        urlString = str(profile.a.contents[0])
    

        profID = urlString[urlString.index("=") + 1:]
      
        if startYear != endYear:
            yearsSpanned = yearParser(profID, startYear, endYear)
        else:
            yearsSpanned = [startYear]
        
        for yearURL in yearsSpanned:
            yearCalendar = soupify(yearURL)
            yearCalendar.find_all("div", class_="measure capacity20")

            for link in yearCalendar.find_all("div", class_="measure opacity20"):
                dateList = link.get('id').split(" ")                
                date = dateList[-1] + monthDictionary[dateList[1]] + dateList[2]
                print date
                print "AXE"
                urlString = prefixURL +"/web/" + date + "000000/http://www.okcupid.com/profile?tuid=" + profID
                dupList.append((urlString, False))

    finalURLList = urlsList + dupList

    

for url in finalURLList:
    masterList = []
    soupyURL = soupify(url[0])
    #print soupyURL.prettify()
    allTitles = soupyURL.find_all("title", id=False)
    print allTitles
    if "/" in str(allTitles[0].contents[0]):
        titleData = str(allTitles[0].contents[0]).split(" ")
        for dataPoint in titleData:
            if "OKC" not in dataPoint and dataPoint != "/":
                masterList.append(dataPoint)
    else:
        pass


    print masterList
    

    
    

print "SUCCESS!!!!!"
