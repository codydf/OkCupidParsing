




####THE MOST UPDATED VERSION OF THIS CODE IS THAT ON THE SERVER######








from okc_functions import soupify, yearParser
from urllib2 import urlopen, HTTPError
from bs4 import BeautifulSoup
import zipfile, zlib

'''
This code generates a list of all possible profile URLs from the Wayback Machine and
writes the HTML data from each of those URLs into a zip file.
'''

monthDictionary = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05","Jun":"06",
                   "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}


i = 2
while i < 3:
#while i < 10:
    htmlZipFile = zipfile.ZipFile("HTMLZipFile.zip", mode = "a")
    for j in range(3):
        mainURL = "/web/*/http://www.okcupid.com/profile?tuid=" + str(i) + str(j) + "*"
        #mainURL = "/web/*/http://www.okcupid.com/profile?tuid=14361*"
        urlsList = []
        dupList = []
        prefixURL = "http://web.archive.org"
        fullURL = prefixURL + mainURL

        bigSoup = soupify(fullURL)
        urlClassTags = bigSoup.find_all("td", class_="url")


        for profile in urlClassTags:
            try:
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
                                     
                    yearsSpanned = yearParser(profID, startYear, endYear)          
                    
                    for yearURL in yearsSpanned:
                        yearCalendar = soupify(yearURL)
                        yearCalendar.find_all("div", class_="measure capacity20")

                        for link in yearCalendar.find_all("div", class_="measure opacity20"):
                            dateList = link.get('id').split(" ")                
                            date = dateList[-1] + monthDictionary[dateList[1]] + dateList[2]
                            urlString = prefixURL +"/web/" + date + "000000/http://www.okcupid.com/profile?tuid=" + profID
                            dupList.append((urlString, False))
                finalURLList = urlsList + dupList
            except ValueError:
                pass

        k = 1
        for url in finalURLList:
            year = url[0][27:31]
            htmlFile = open("okcFinalData" + str(i) + "-" + str(k) + "-" + year + ".txt", "w")
            try:
                htmlFile.write(urlopen(url[0]).read())
                htmlFile.close()
            except (HTTPError, ValueError, IOError, RuntimeError, TypeError, NameError) :
                htmlFile. close()
            htmlZipFile.write("okcFinalData" + str(i) + "-" + str(k) + "-" + year + ".txt")
            k += 1
            
        i += 1
        
htmlZipFile.close()
    

print "URL List Generated!"

