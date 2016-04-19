from urllib2 import urlopen, HTTPError
from bs4 import BeautifulSoup
import zipfile, zlib, datetime, copy, csv
from listOfTestURLS import bigTestList

monthDictionary = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04",
                   "May":"05", "Jun":"06", "Jul":"07", "Aug":"08",
                   "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}


urlsList = []
dupList = []
currentURLList = []
'''
For testing:
mainURL = "/web/*/http://www.okcupid.com/profile?tuid=14361*"
prefixURL = "http://web.archive.org"
fullURL = prefixURL + mainURL
'''


def soupify(url):
    if type(url) == str:
        return BeautifulSoup(urlopen(url).read())
    elif type(url) == file:
        return BeautifulSoup(url.read())

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

def scrapeDateData(urlBSObj):
    '''Finds text giving date profile was archived and appends the date
    to a list of items to be added to the final string for this profile.
    Also returns the year to be stored in a variable for use in other places.'''
    
    dateTag = str(urlBSObj.find_all("td", id="displayMonthEl")[0])
    #print "success 1"

    dateTag = dateTag[dateTag.index("title=") + 7:]
    #print"success 2"

    dateTag = dateTag[:dateTag.index(">") - 1]
    #print "success 3"

    splitDate = dateTag.split(" ")[4:]
    #print "success 4"

    dateDataPoint = monthDictionary[splitDate[0]] + "-" + splitDate[1][:-1]+ "-" + splitDate[2]

    return dateDataPoint

def titleScraper(urlBSObj):
    '''Finds all non-ID'd title tags '''
    allTitles = urlBSObj.find_all("title", id=False)
    #print "allTitles: ", allTitles
    
    
    try:
        title = allTitles[0].contents[0].encode("utf-8")
        titleHoldVar = ""
        i = -1
        while len(titleHoldVar) == 0:
            titleData = title.split("/")
            titleHoldVar = titleData[0].split(" ")[i]
            i -= 1
        titleData[0] = titleHoldVar

        sexuality = titleData[3]
        if ("gay" not in sexuality and "straight" not in sexuality and "bisexual" not in sexuality):
            titleData.insert(3, "")            
        
        return titleData
    except:
        raise Exception

majorDict= {"summary":"", "doing with":"", "really good":"", "first thing":"",
            "favorite":"", "six things":"", "lot of time":"",
            "typical friday":"", "private thing":"", "should message":""}

#############CASE A FUNCTONS##########################

def minorDetailParserA(urlBSObj):
    minorDictAList = ["looking for", "drinks", "education", "smokes", "job", "drugs",
                      "income", "kids", "sign", "pets", "religion", "ethnicity", "languages"]
    minorDictA = {}
    workingDataList = []
    helperList = []
    
    try:
        tagList = urlBSObj.find_all("table", style="color:#1e50c2")
        tdList = tagList[0].find_all("td")
        for td in tdList:
            helperList.append(td.get_text().encode("utf-8"))
        for item in helperList:
            if item[-1] != ":":
                try:
                    workingDataList.append(item)
                except:
                    workingDataList.append("")
        for i in range(len(minorDictAList)):
            minorDictA[minorDictAList[i]] = workingDataList[i]

        workingDataList = [minorDictA["ethnicity"], "", "", "", minorDictA["looking for"],
                           minorDictA["smokes"], minorDictA["drinks"], minorDictA["drugs"],
                           minorDictA["religion"], minorDictA["sign"], minorDictA["education"],
                           '', minorDictA["income"], minorDictA["kids"], minorDictA["pets"],
                           minorDictA["languages"]]                           
    except:
        workingDataList = ["" for i in range(16)]

    finally:
        return workingDataList
     

def majorDetailParserA(urlBSObj):
    majDictA = copy.copy(majorDict)
    tagList_b = urlBSObj.find_all("b")
    tagList_s = urlBSObj.find_all("script")
    for tag in tagList_s:
        if "six things" in tag.get_text().lower().encode("utf-8"):
            majDictA["six things"] = tag.next_sibling.next_sibling.next_sibling.next_sibling.get_text().encode("utf-8")
    for i in majDictA.keys():
            for tag in tagList_b:
                    if i in tag.get_text().lower().encode("utf-8"):
                        try:
                            tagPar = tag.parent
                            parParList = tagPar.parent.contents
                            majDictA[i] = parParList[8].get_text().encode("utf-8")
                        
                        except (IndexError, AttributeError):
                            try:
                                majDictA[i] = tag.next_sibling.next_sibling.next_sibling.next_sibling.get_text().encode("utf-8")
                                
                            except (IndexError, AttributeError):
                                try:
                                    tagList_f = urlBSObj.find_all("font", class_="usertext")
                                    majDictA[i] = tagList_f[1].get_text().encode("utf-8")
                                except:
                                    print tag
                            
                    else:
                        pass
            
    return [majDictA["summary"], majDictA["doing with"],majDictA["really good"],
            majDictA["first thing"],majDictA["favorite"],majDictA["six things"],
            majDictA["lot of time"], majDictA["typical friday"], majDictA["private thing"],
            majDictA["should message"]]

    
def allDetailParserA(urlBSObj):
    try:
        return (minorDetailParserA(urlBSObj) + majorDetailParserA(urlBSObj))
    except:
        print "allDetailParserA ERROR"
        raise Exception


#############CASE B FUNCTIONS#########################

def minorDetailParserB(urlBSObj):
    minorDictBList = ["looking for", "drinks", "education", "smokes", "job", "drugs",
                      "income", "kids", "sign", "pets", "religion", "ethnicity", "languages"]
    minorDictB = {}
    try:
        tagList = urlBSObj.find_all("div", class_="detail")
        for i in range(len(tagList)):
            try:
                contentsStr = tagList[i].get_text().encode("utf-8")[(tagList[i].get_text().encode("utf-8").index(":") + 2):]
                minorDictB[minorDictBList[i]] = contentsStr
            except:
                minorDictB[i] = ""

    except:
        return ["" for i in range(16)]

    finally:
        for key in minorDictBList:
            if key not in minorDictB:
                minorDictB[key] = ""
                
        return [minorDictB["ethnicity"], "", "", "", minorDictB["looking for"],
                minorDictB["smokes"], minorDictB["drinks"], minorDictB["drugs"],
                minorDictB["religion"], minorDictB["sign"], minorDictB["education"],
                "", minorDictB["income"], minorDictB["kids"], minorDictB["pets"],
                minorDictB["languages"]]
        

def majorDetailParserB(urlBSObj):
    majDictB = copy.copy(majorDict)
    tagList= urlBSObj.find_all("div", class_="essaytitle")
    for i in majDictB.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictB[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")                           
                else:
                    pass
            
    return [majDictB["summary"], majDictB["doing with"],majDictB["really good"],
            majDictB["first thing"],majDictB["favorite"],majDictB["six things"],
            majDictB["lot of time"], majDictB["typical friday"], majDictB["private thing"],
            majDictB["should message"]]
    

def allDetailParserB(urlBSObj):
    try:
        return (minorDetailParserB(urlBSObj) + majorDetailParserB(urlBSObj))
    except:
        print "allDetailsParserB ERROR"
        raise Exception

#############CASE C FUNCTIONS#########################

def minorDetailParserC(urlBSObj):
    try:
        workingDataList = []
        detailTable = urlBSObj.find(id="userFactsText")
        detailList = detailTable.find_all("li")
        for detail in detailList:
            info = detail.get_text().encode("utf-8")
            info = info[info.index(":")+1 :]
            workingDataList.append(info)
    except:
        workingDataList = ["" for i in range(13)]
        
    finally:
        workingDataList.insert(2, "")
        workingDataList.insert(2, "")
        workingDataList.insert(11, "")
        return workingDataList

def majorDetailParserC(urlBSObj):
    majDictC = copy.copy(majorDict)
    tagList= urlBSObj.find_all("h1")
    for i in majDictC.keys():
            #print i
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    #print "one"
                    if i == "summary":
                        #print "two"
                        majDictC[i] = tag.next_sibling.next_sibling.next_sibling.next_sibling\
                                          .next_sibling.next_sibling.next_sibling.next_sibling.get_text().encode("utf-8")                    
                    else:
                        #print "three"
                        majDictC[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")
                    break 
                else:
                    majDictC[i] = ""
            
            
    return [majDictC["summary"], majDictC["doing with"],majDictC["really good"],
            majDictC["first thing"],majDictC["favorite"],majDictC["six things"],
            majDictC["lot of time"], majDictC["typical friday"], majDictC["private thing"],
            majDictC["should message"]]

def allDetailParserC(urlBSObj):
    try:
        return (minorDetailParserC(urlBSObj) + majorDetailParserC(urlBSObj))
    except:
        print "allDetailParserC ERROR"
        raise Exception


#############CASE D FUNCTIONS#########################

def minorDetailParserD(urlBSObj):
    minorDictD = {"ethnicity":"", "height":"", "looking for":"", "smokes":"", "drinks":"",
                  "drugs":"", "religion":"", "sign":"", "education":"",
                  "job":"", "income":"", "kids":"", "pets":"", "languages":""}
    workingDataList = []
    try:        
        detailDiv = urlBSObj.find_all("div", class_="hr profileBasicsDetailsHR")[0]        
        for detail in minorDictD:
            for tag in detailDiv.next_siblings:
                if detail in tag.lower().encode("utf-8"):
                    minorDictD[detail] = tag.next_sibling.encode("utf-8")

    except:
        pass

    finally:
        return [minorDictD["ethnicity"], minorDictD["height"], "", "", minorDictD["looking for"],
                minorDictD["smokes"], minorDictD["drinks"], minorDictD["drugs"],
                minorDictD["religion"], minorDictD["sign"], minorDictD["education"],
                minorDictD["job"], minorDictD["income"], minorDictD["kids"], minorDictD["pets"],
                minorDictD["languages"]]        

def majorDetailParserD(urlBSObj):

    majDictD = copy.copy(majorDict)
    tagList= urlBSObj.find_all("h2")
    for i in majDictD.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictD[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")                           
                else:
                    pass

    return [majDictD["summary"], majDictD["doing with"],majDictD["really good"],
            majDictD["first thing"],majDictD["favorite"],majDictD["six things"],
            majDictD["lot of time"], majDictD["typical friday"], majDictD["private thing"],
            majDictD["should message"]]
        

def allDetailParserD(urlBSObj):
    try:
        return (minorDetailParserD(urlBSObj) + majorDetailParserD(urlBSObj))
    except:
        print "allDetailParserD ERROR"
        raise Exception

#############CASE E FUNCTIONS#########################

def minorDetailParserE(urlBSObj):
    return minorDetailParserD(urlBSObj)   
    

def majorDetailParserE(urlBSObj):
    majDictE = copy.copy(majorDict)
    tagList= urlBSObj.find_all("h2")
    for i in majDictE.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictE[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")                            
                else:
                    pass
    return [majDictE["summary"], majDictE["doing with"],majDictE["really good"],
            majDictE["first thing"],majDictE["favorite"],majDictE["six things"],
            majDictE["lot of time"], majDictE["typical friday"], majDictE["private thing"],
            majDictE["should message"]]

def allDetailParserE(urlBSObj):
    try:
        return (minorDetailParserE(urlBSObj) + majorDetailParserE(urlBSObj))
    except:
        print "allDetailParserD ERROR"
        raise Exception


#############CASE F FUNCTIONS#########################

def minorDetailParserF(urlBSObj):
    workingDataList = []
    tagList = urlBSObj.find_all("dd", class_=None)

    for tag in tagList[:14]:
        try:
            workingDataList.append(tag.get_text().encode("utf-8"))
        except:
            workingDataList.append("")

    workingDataList.insert(2, "")
    workingDataList.insert(2, "")
    return workingDataList

def majorDetailParserF(urlBSObj):
    majDictF = copy.copy(majorDict)
    tagList= urlBSObj.find_all("h2")
    for i in majDictF.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictF[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")                           
                else:
                    pass

    return [majDictF["summary"], majDictF["doing with"],majDictF["really good"],
            majDictF["first thing"],majDictF["favorite"],majDictF["six things"],
            majDictF["lot of time"], majDictF["typical friday"], majDictF["private thing"],
            majDictF["should message"]]
        
def allDetailParserF(urlBSObj):
    try:
        return (minorDetailParserF(urlBSObj) + majorDetailParserF(urlBSObj))
    except:
        print "allDetailParserF ERROR"
        raise Exception


##############CASE G FUNCTIONS########################

def minorDetailParserG(urlBSObj):
    workingDataList = []
    tagList = urlBSObj.find_all("dd")
    for tag in tagList[2:]:
        try:
            workingDataList.append(tag.get_text().encode("utf-8"))
        except:
            workingDataList.append("")
    workingDataList.insert(2, "")
    return workingDataList

def majorDetailParserG(urlBSObj):
    majDictG = copy.copy(majorDict)
    tagList= urlBSObj.find_all("h2", class_="essay_title")
    for i in majDictG.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictG[i] = tag.next_sibling.get_text().encode("utf-8")                           
                else:
                    pass

    return [majDictG["summary"], majDictG["doing with"],majDictG["really good"],
            majDictG["first thing"],majDictG["favorite"],majDictG["six things"],
            majDictG["lot of time"], majDictG["typical friday"], majDictG["private thing"],
            majDictG["should message"]]


def allDetailParserG(urlBSObj):
    try:
        return (minorDetailParserG(urlBSObj) + majorDetailParserG(urlBSObj))
    except:
        print "allDetailParserG ERROR"
        raise Exception


##############CASE H FUNCTIONS########################

def minorDetailParserH(urlBSObj):
    workingDataList = []
    tagList = urlBSObj.find_all("dt", class_=None)
    for tag in tagList[1:]:
        try:
            workingDataList.append(tag.next_sibling.next_sibling.get_text().encode("utf-8"))
        except:
            workingDataList.append("")
    workingDataList.insert(4, "")
    return workingDataList

def majorDetailParserH(urlBSObj):
    majDictH = copy.copy(majorDict)
    tagList= urlBSObj.find_all("a", class_="essay_title")
    for i in majDictH.keys():
            for tag in tagList:
                if i in tag.get_text().lower().encode("utf-8"):
                    majDictH[i] = tag.next_sibling.next_sibling.get_text().encode("utf-8")                          
                else:
                    pass

    return [majDictH["summary"], majDictH["doing with"],majDictH["really good"],
            majDictH["first thing"],majDictH["favorite"],majDictH["six things"],
            majDictH["lot of time"], majDictH["typical friday"], majDictH["private thing"],
            majDictH["should message"]]


def allDetailParserH(urlBSObj):
    try:
        return (minorDetailParserH(urlBSObj) + majorDetailParserH(urlBSObj))
    except:
        print "allDetailParserH ERROR"
        raise Exception

##############CASE I FUNCTIONS########################

def minorDetailParserI(urlBSObj):
    workingDataList = []
    tagList = urlBSObj.find_all("span", class_="dd")
    for tag in tagList:
        try:
            workingDataList.append(tag.get_text().encode("utf-8"))
        except:
            workingDataList.append("")
    
    workingDataList.insert(2, "")
    workingDataList.insert(2, "")
    return workingDataList

def majorDetailParserI(urlBSObj):
    majDictI = copy.copy(majorDict)
    tagListSpan = urlBSObj.find_all("span", class_=None)
    tagListRibbon = urlBSObj.find_all("h3", class_="ribbon")
    for i in majDictI.keys():
        try:
            for tag1 in tagListSpan:
                if i in tag1.get_text().lower().encode("utf-8"):
                    majDictI[i] = tag1.next_sibling.get_text().encode("utf-8")                         
                else:
                    pass
        except:
            try:
                for tag2 in tagListRibbon:
                    if i in tag2.get_text().lower().encode("utf-8"):
                        majDictI[i] = tag2.next_sibling.next_sibling.get_text().encode("utf-8")
                    else:
                        pass
            except:
                print "still fuqqed"
                

    return [majDictI["summary"], majDictI["doing with"],majDictI["really good"],
            majDictI["first thing"],majDictI["favorite"],majDictI["six things"],
            majDictI["lot of time"], majDictI["typical friday"], majDictI["private thing"],
            majDictI["should message"]]

def allDetailParserI(urlBSObj):
    try:
        return (minorDetailParserI(urlBSObj) + majorDetailParserI(urlBSObj))
    except:
        print "allDetailParserI ERROR"
        raise Exception        
'''    
yearCaseDict = {"2004":[allDetailParserA], "2005":[allDetailParserA],
                "2006":[allDetailParserA, allDetailParserB, allDetailParserC],
                "2007":[allDetailParserC, allDetailParserD],
                "2008":[allDetailParserD, allDetailParserE, allDetailParserF, allDetailParserG],
                "2009":[allDetailParserG, allDetailParserI, allDetailParserF, allDetailParserH],
                "2010":[allDetailParserG, allDetailParserH], "2011":[allDetailParserH, allDetailParserG],
                "2012":[allDetailParserH],"2013":[allDetailParserH], "2014":[allDetailParserH],
                "2015":[allDetailParserH]}
'''
def caseFunctionTries(profileDataList):
#Initially profileDataList is a list of the form [BeautSoupObj, DateStr]
    yearCaseDict = {"2004":[allDetailParserA], "2005":[allDetailParserA],
                "2006":[allDetailParserA, allDetailParserB, allDetailParserC],
                "2007":[allDetailParserC, allDetailParserD],
                "2008":[allDetailParserD, allDetailParserE, allDetailParserF, allDetailParserG],
                "2009":[allDetailParserG, allDetailParserI, allDetailParserF, allDetailParserH],
                "2010":[allDetailParserG, allDetailParserH], "2011":[allDetailParserH, allDetailParserG],
                "2012":[allDetailParserH],"2013":[allDetailParserH], "2014":[allDetailParserH],
                "2015":[allDetailParserH]}
    currentURL_BSObj = profileDataList.pop(0)

    try:
        profileDataList += titleScraper(currentURL_BSObj)
    except (IndexError, UnicodeEncodeError, Exception):
        return []

    parserCaseList = yearCaseDict[profileDataList[0][-4:]]
    origProfDataList = profileDataList
    bestMatch = ([],0)    
    while len(parserCaseList) > 0:
        count = 0
        profileDataList = origProfDataList
        currentParserFunction = parserCaseList.pop(0) 
    
        try:
            parseResult = currentParserFunction(currentURL_BSObj)
            if len(parseResult) == 26:
                
                for item in parseResult:
                    if item != "":
                        count += 1
                if count > bestMatch[1]:
                    bestMatch = (profileDataList + parseResult, count)
            
        except (IndexError, UnicodeEncodeError, Exception):
            pass
        
    if len(bestMatch[0]) > 0:        
        return bestMatch[0]
    else:
        return []
        #print "CFT EXCEPTION!"
        #raise Exception
 
print "okc_functions loaded"
