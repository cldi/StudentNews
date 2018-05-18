# =============================================================================
# Code to query VIAF and return: 1) VIAF ID, 2) URL and 3) preferred names for
# named entities in student publications. Currently only handles names 
# of people.
# =============================================================================

import requests
import json
import csv
import os
import easygui


#%%
# =============================================================================
# Default return type is html. Others: json, xml, xhtml.
# Specify the type as a string. At the moment, only json or xml possible.
# =============================================================================
def urlBuilder(query, entityType='person', maxRecords='all', returnType='json'):
    prefix = 'http://www.viaf.org/viaf/search?query='
    if entityType == 'person':
        queryString = 'local.names+exact+"' + str(query) +'"'
    elif entityType == 'org':
        queryString = 'local.corporateNames+=+"' + str(query) + '"'
    elif entityType == 'place':
        queryString = 'local.geographicNames+=+"' + str(query) + '"'
    else:
        queryString = 'cql.any+=+"' + str(query) + '"'
    if maxRecords == 'all':
        maxRecordsString = ""
    else:
        maxRecordsString = "&maximumRecord="+str(maxRecords)
    # declares the return type
    if returnType == 'json':
        returnString = '&httpAccept=application/json'
    elif returnType == 'xml':
        returnString = '&httpAccept=text/xml'
    else:
        returnString = ''
    viafUrl = prefix + queryString + maxRecordsString + returnString
    return viafUrl

def getViafRecord(viafDict):
    viafEntity = []
    viafEntity.append(viafDict.get("record").get("recordData").get("viafID"))
    viafEntity.append(viafDict.get("record").get("recordData").get("Document").get("@about"))
    dictNode = viafDict.get("record").get("recordData").get("mainHeadings").get("data")
    if type(dictNode) == dict:
        viafEntity.append(dictNode.get("text"))
    else:
        for item in dictNode:
            viafEntity.append(item.get("text"))
    return viafEntity


#%%
# =============================================================================
# Build and send get request (for VIAF)
# =============================================================================

# add different names in lookups (or call a csv file)
print("Please select the CSV file that contains your data.")
csvfilename = easygui.fileopenbox()
lookups = []
name_list = csv.reader(open(csvfilename, newline=''), delimiter=",")
for name in name_list:
    lookups.append(name)

queries = []
print("Building queries. Please wait.")  
for search in lookups:
    if len(search) == 2:
        queries.append(urlBuilder(query=search[0], entityType=search[1]))
    else:
        queries.append(urlBuilder(search))

responses = [] 
print("Gathering responses. Please wait.")   
for item in queries:
    response = requests.get(item)
    data = response.content.decode("utf-8")
    responses.append(data)

entities = []
missing_count = 0
for item in responses:
    if "records" in json.loads(item).get("searchRetrieveResponse"):    
        record_list = json.loads(item).get("searchRetrieveResponse").get("records")
        for x in record_list:
            entities.append(getViafRecord(x))
    else:
        missing_count += 1
print("There are " + str(missing_count) + " entities that were not found.")

print("Please select the destination folder for the results of the VIAF lookup.")
savedir = easygui.diropenbox()
savefile = input("Please type the filename (including extension): ")
file = open(os.path.join(savedir, savefile), "w", encoding="utf-8")
file.write("Number of entities not found: " + str(missing_count) + "\n")
for entry in entities:
    for item in entry:
        file.write(str(item)+"\t")
    file.write("\n")
file.close()








