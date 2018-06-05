# =============================================================================
# Code to query DBpedia for named entities.
# 
# =============================================================================

import requests
import xml.etree.ElementTree as et
import csv
import os
import easygui
import re

# =============================================================================
# Default return type is XML. Others: json.
# Classes are: Resource (general), Place, Person, Work, Species, Organization
# but don't include resource as one of the 
# =============================================================================
def urlBuilder(query, queryClass="unknown", returns=10):
    prefix = 'http://lookup.dbpedia.org/api/search/KeywordSearch?'
    #Selects the appropriate QueryClass for the url
    if queryClass == 'place':
        qClass = 'QueryClass=place'
    elif queryClass == 'person':
        qClass = 'QueryClass=person'
    elif queryClass == 'org':
        qClass = 'QueryClass=organization'
    else:
        qClass = 'QueryClass='
    #Sets the QueryString
    qString = "QueryString=" + str(query)
    #sets the number of returns
    qHits = "MaxHits=" + str(returns)
    #full url    
    dbpURL = prefix + qClass + "&" + qString + "&" + qHits
    return dbpURL

#takes a xml doc as STRING and returns an array with the name and the URI
def getdbpRecord(xmlpath):
    root  = et.fromstring(xmlpath)
    dbpRecord = []
    for child in root:
        temp = []
        temp.append(child[0].text)
        temp.append(child[1].text)
        if child[2].text is None:
            temp.append("Empty")
        else:
            temp.append(findDates(child[2].text))
        dbpRecord.append(temp)
    return dbpRecord

#looks for a date with pattern: 1900-01-01 OR 01 January 1900 OR 1 January 1900
def findDates(x):
    pattern = re.compile('\d{4}-\d{2}-\d{2}|\d{2}\s\w{3,9}\s\d{4}|\d{1}\s\w{3,9}\s\d{4}')
    returns = pattern.findall(x)
    if len(returns) > 0:
        return ";".join(returns)
    else:
        return "None"


#%%
# =============================================================================
# Build and send get requests
# =============================================================================
print("Please select the CSV file that contains your data.")
csvfilename = easygui.fileopenbox("Please select the CSV file that contains your data.")
lookups = []
name_list = csv.reader(open(csvfilename, newline=''), delimiter=",")
for name in name_list:
    lookups.append(name)
    
#request to get the max number of returns from the user.
temp = input("Specify the maximum number of returns desired: ")
if temp.isdigit():
    maxHits = temp
else:
    maxHits = 10
queries = []
print("Building queries. Please wait.")
for search in lookups:
    if len(search) == 2:
        queries.append([search[0], urlBuilder(query=search[0], queryClass=search[1], returns=maxHits)])
    else:
        queries.append([search, urlBuilder(query=search, returns=maxHits)])

responses = [] 
print("Gathering responses. Please wait.")   
for item in queries:
    response = requests.get(item[1])
    data = response.content.decode("utf-8")
    responses.append([item[0], data])
    
entities = []
missing_count = 0
for item in responses:
    temp = []
    if len(list(et.fromstring(item[1]))) > 0:
        entities.append([item[0], getdbpRecord(item[1])])
    else:
        missing_count += 1
print("There are " + str(missing_count) + " entities that were not found.")

print("Please select the destination folder for the results of the VIAF lookup.")
savedir = easygui.diropenbox("Please select the destination folder for the results of the VIAF lookup.")
savefile = input("Please type the filename (including extension): ")
file = open(os.path.join(savedir, savefile), "w", encoding="utf-8")
file.write("Number of entities not found: " + str(missing_count) + "\n")
sep = "\t"
for entry in entities:
    file.write(entry[0]+"\t")
    for item in entry:
        file.write(sep.join(item[0]))
        file.write("\t")
    file.write("\n")
file.close()
    








