import okc_functions as okcFunctions
from urllib2 import urlopen, HTTPError
from bs4 import BeautifulSoup
import zipfile, zlib, csv, copy
from datetime import datetime
'''
The form of the resulting list of data points for each profile will be:

[Date, Profile Name, Age, Gender, Sexuality, Location, Ethnicity, Height,
Body Type, Diet, Looking For, Smokes, Drinks, Drugs, Religion, Sign, Education,
Job, Income, Kids, Pets, Languages, Self-Summary, Doing With Life, Really Good At,
First Things People Notice, Favorites, 6 Things Couldn't Live Without,
Spend A Lot of Time Thinking About, Typical Friday Night, Most Private Thing,
Should Message Me If]

'''

'''
The complete string of data for each profile will be stored inside (parentheses).
Within the string, each separate data point will be contained in 'single quotes'
and each will be separated by a comma, and thus can be split at " ', ' " indices.

'''


finalDataList = []
htmlZipFile = zipfile.ZipFile("[INSERT ZIPFILE NAME HERE]", mode="r")
htmlFileList = htmlZipFile.namelist()

for htmlFile in htmlFileList:
    try:
        beautSoupConvertedURL = BeautifulSoup(htmlZipFile.read(htmlFile))
        urlDate = okcFunctions.scrapeDateData(beautSoupConvertedURL)
        finalDataList.append([beautSoupConvertedURL, urlDate])
    except (HTTPError, UnboundLocalError, IndexError):
        pass


print "PART 1 OVER!"

finalCSVList = []

for profileDataList in finalDataList:
    try:
        finalCSVList.append(okcFunctions.caseFunctionTries(profileDataList))
    except:
        finalCSVList.append([])


print "PART 2 OVER!"

finalFile = open("[INSERT FINAL FILE NAME HERE].csv", "w")
print "FINAL CSV OPENED"
finalCSV = csv.writer(finalFile, delimiter = ",", quoting = csv.QUOTE_ALL)
print "CSV WRITER OK"

for profileDataList in finalCSVList:  
    if len(profileDataList) > 1: 
        finalCSV.writerow(profileDataList)


finalFile.close()


print "JOB COMPLETE!"
    




#############################################################################
