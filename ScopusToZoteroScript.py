from pybliometrics.scopus.utils import config
from pybliometrics.scopus import AffiliationSearch, ScopusSearch
from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
from pyzotero import zotero
import pandas as pd
import time
from functions import *

# There are some code segments commented out, if you want to know the runtime of the
# Script you can un comment them and it will tell you
# For the correct Zotero database line 96 is where you will put in the data for that


# This is requested to be put in by the CrossRef API, when running this script please enter your information
# This allows CroffRef to contact you if something is going wrong with the code
{
  "Crossref-Plus-API-Token": "<<Plus API token, for Plus users only>>",
  "User-Agent": "<<polite user agent; including (First Name) (Last Name): **********@southernct.edu>>",
  "(First Name) (Last Name)": "<<**********@southernct.edu>>"
}

#Gather All Southern Affiliations
query = "AFFIL(Southern Connecticut State University)"
southernAffils = AffiliationSearch(query)
southernAffils.affiliations


#Create dataframes for all data related to southern
pd.set_option('display.max_columns', None)
s = ScopusSearch('AFFIL(Southern Connecticut State University)')
dfSCSU = pd.DataFrame(pd.DataFrame(s.results))
s = ScopusSearch('AFFIL(Connecticut State Colleges and Universities)')
dfCSCU = pd.DataFrame(pd.DataFrame(s.results))


#Creating the list of doi so that they can be added to respective dataframes wether they have a doi or no doi as ones with Doi's can be passed through crossref.
doiCol = dfSCSU['doi']
noDoiDF = pd.DataFrame(columns = dfSCSU.columns)
doiDF =pd.DataFrame(columns = dfSCSU.columns)


#searhes through all the doi's and added them to their respective dataframe the doi or non doi for the Southern Connecticut State University affiliation
start = time.time()
count = 0
for document in doiCol:
    if(document == None):
        noDoiDF = pd.concat([noDoiDF,dfSCSU.iloc[[count]]])
    else:
        doiDF = pd.concat([doiDF,dfSCSU.iloc[[count]]])
    count = count +1
end = time.time()
print("Runtime doiDF/noDoiDF for SCSU: ", end - start)


#searhes through all the doi's and added them to their respective dataframe the doi or non doi for the Connecticut State Colleges and Universities affiliation
start = time.time()
doiCol = dfCSCU['doi']
count = 0
for document in doiCol:
    if(document == None):
        noDoiDF = pd.concat([noDoiDF,dfCSCU.iloc[[count]]])
    else:
        doiDF = pd.concat([doiDF,dfCSCU.iloc[[count]]])
    count = count +1
end = time.time()
print("Runtime doiDF/noDoiDF for CSCU: ", end - start)
noDoiDF.drop_duplicates()
doiDF.drop_duplicates()


# This section searches through the entirety off doi's from Scopus and populates them into a List if they have data in crossRef
doiCol = pd.Series(doiDF['doi'])
crossRefDictionary = []
nameCol = pd.Series(doiDF['description'])
crossRefDictionaryList = []
crossRefBadList = []
count =0
start = time.time()
for doi in doiCol:
    if count <= 150:
        try:
            data = get_entity(doi,EntityType.PUBLICATION,OutputType.JSON)
            crossRefDictionaryList.append(data)
            tempE = data
            checkValue = tempE['type']     
        except:
            crossRefBadList.append(doi)
            noDoiDF = pd.concat([noDoiDF,doiDF.iloc[count]])
        count +=1
end = time.time()
print("Runtime crossRefDictionaryList: ", end - start)


# Gathers All data currently in Zotero to make sure there are no duplicates being populated
start = time.time()
zot = zotero.Zotero('4421509','group','YWq3eh8BBDE9adJY66lDvrzd')
items = zot.everything(zot.top())
end = time.time()
print("items Creation Runtime: ", end - start)
zotTypeList = []


# Makes a list of all of the entry names from Zotero
start = time.time()
zotDoiList = []
for item in items:
    d = item['data']
    tempName = d['title']
    zotDoiList.append(tempName)
end = time.time()
print("Runtime zotDoiList Creation: ", end - start)


# Compares the CrossRef Entries with ones currently in Zotero to make sure no entry with the
# same name will get populated into the database
addZotList = []
startOuter = time.time()
inputDoiLen = len(crossRefDictionaryList)
for n in range(0,inputDoiLen):
    startInner = time.time()
    tempE = crossRefDictionaryList[n]
    try:
        tempName = tempE['title'][0]
        passName = True
    except:
        passName = False
     
    for zDoi in zotDoiList:
        #print("CrossRef: ",tempDoi, " comparing to ", "Zotero: ", zDoi)
        if tempName == zDoi:
            passName = False
    if (passName == True) and (not("mml:math" in tempName)):
        addZotList.append(crossRefDictionaryList[n])
        endInner = time.time()
        #print("Runtime doi compare: ", tempName, ", Time: ",endInner - start, ", Result: Pass")
    else:
        endInner = time.time()
        #print("Runtime doi compare: ", tempName, ", Time: ",endInner - start, ", Result: Fail")
endOuter = time.time()
print("Runtime addZotList: ", endOuter - startOuter)
print("Num of Data from CrossRef to Populate into Zotero: ", len(addZotList))



# Populates the filtered data into the Zotero database using the proper formating
for item in addZotList:
    formatDict(item)