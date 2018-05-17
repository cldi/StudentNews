# =============================================================================
# Code to query VIAF and return: 1) VIAF ID, 2) URL and 3) preferred names for
# named entities in student publications. Currently only handles names 
# of people.
# =============================================================================

import requests
import json
import csv

#%%
# =============================================================================
# Default return type is html. Others: json, xml, xhtml.
# Specify the type as a string. At the moment, only json or xml possible.
# =============================================================================
def urlBuilder(query, maxRecords='all', returnType='json'):
    prefix = 'http://www.viaf.org/viaf/search?query='
    queryString = 'local.names+exact+"' + str(query) +'"'
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
    viafEntity.append(viafDict.get("record").get("recordData").get("Document").get("primaryTopic").get("@resource"))
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
lookups = ["Jane Austen", "Trudeau, Justin", "Austen, Jane"]

queries = []
for search in lookups:
    queries.append(urlBuilder(search))

responses = []    
for item in queries:
    response = requests.get(item)
    data = response.content.decode("utf-8")
    responses.append(data)

info = []
for item in responses:
    if "records" in json.loads(item).get("searchRetrieveResponse"):    
        record_list = json.loads(item).get("searchRetrieveResponse").get("records")
        for x in record_list:
            info.append(getViafRecord(x))
    else:
        print("skipping")
