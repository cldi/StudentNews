# =============================================================================
# Code to do the complete process from StanfordNER to URIs from VIAF and DBpedia
# =============================================================================


import requests
import xml.etree.ElementTree as et
import csv
import easygui
import re
import json
import os


# =============================================================================
# Functions 
# =============================================================================

# formats the name for lastname, firstname (if  there are 2 names)
def convertName(name):
    temp = name.split()
    if len(temp) == 1:
        return name
    else:
        return(str(temp[1]) + ", " + str(temp[0]))

# translates the type from the output of the StanfordNER to the requirements
# of the lookup scripts
def convertType(typeString):
    if typeString == "PERSON":
        return "person"
    elif typeString == "LOCATION":
        return "place"
    elif typeString == "ORGANIZATION":
        return "org"
    else:
        return "misc"
    
# build query URL for VIAF
def urlVIAFBuilder(query, entityType='person', maxRecords='all', returnType='json'):
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

# get desired information from the returned VIAF record
def getViafRecord(viafDict):
    viafEntity = []
    viafEntity.append(viafDict.get("record").get("recordData").get("viafID"))
    viafEntity.append(viafDict.get("record").get("recordData").get("Document").get("@about"))
    viafEntity.append(viafDict.get("record").get("recordData").get("nameType"))
    viafEntity.append(viafDict.get("record").get("recordData").get("birthDate"))
    viafEntity.append(viafDict.get("record").get("recordData").get("deathDate"))
    dictNode = viafDict.get("record").get("recordData").get("mainHeadings").get("data")
    if type(dictNode) is dict:
        viafEntity.append(getTextAndSources(dictNode))
    else:
        for item in dictNode:
            viafEntity.append(getTextAndSources(item))
    return viafEntity

# gather the text and the sources and return in one string
def getTextAndSources(node):
    if type(node.get("sources").get("s")) is list:
        value = node.get("text")+"|"+",".join(node.get("sources").get("s"))
    else:
        value = node.get("text")+"|"+node.get("sources").get("s")
    return value

# build query URL for DBpedia
def urlDBPBuilder(query, queryClass="unknown", returns=10):
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
    
def cleanLine(line):
    strippedLine = line.strip()
    if strippedLine[0] == "&":
        temp = re.sub('[&]', '', strippedLine)
        return re.sub('[•!@#]', '', temp)
    return re.sub('[•!@#]', '', strippedLine)

def ner2uri(file):
    entities = []
    preContext = ""
    for line in full_doc:
        if len(line)==3 and len(line[0])==0:
            preContext=line[2]
        elif len(line)==3 and len(line[0])>0 and line[1]=="PERSON":
            entities.append([convertName(line[0]), convertType(line[1]), preContext, line[2]])
            preContext = line[2]
        elif len(line)==3 and len(line[0])>0:
            entities.append([cleanLine(line[0]), convertType(line[1]), preContext, line[2]])
            preContext = line[2]
        elif len(line)==2 and len(line[0])>0:
            entities.append([cleanLine(line[0]), convertType(line[1]), preContext, ""])
            preContext = ""
    return entities

def viafReturns(entities):
    queries = []
    print("Building VIAF queries. Please wait.")  
    for search in entities:
        queries.append([search[0], urlVIAFBuilder(query=search[0], entityType=search[1])])
    
    responses = [] 
    print("Gathering responses from VIAF. Please wait.")   
    for num, item in enumerate(queries, start=1):
        response = requests.get(item[1])
        data = response.content.decode("utf-8")
        responses.append([item[0], data])
        if num%50==0:
            temp = round(num/len(queries)*100)
            print("Processed {}".format(num) + " of " + str(len(queries)) + " (" + str(temp) + "%)")
    
    terms = []
    missing_count = 0
    for item in responses:
        if "records" in json.loads(item[1]).get("searchRetrieveResponse"):    
            record_list = json.loads(item[1]).get("searchRetrieveResponse").get("records")
            for x in record_list:
                terms.append([item[0], getViafRecord(x)])
        else:
            missing_count += 1
    print("There are " + str(missing_count) + " entities that were not found.")
    return terms

def dbpediaReturns(entities, maxHits):
    queries = []
    print("Building DBpedia queries. Please wait.")
    for search in entities:
        queries.append([search[0], urlDBPBuilder(query=search[0], queryClass=search[1], returns=maxHits)])
        
    responses = [] 
    print("Gathering responses from DBpedia. Please wait.")   
    for num, item in enumerate(queries, start=1):
        response = requests.get(item[1])
        data = response.content.decode("utf-8")
        responses.append([item[0], data])
        if num%50==0:
            temp = round(num/len(queries)*100)
            print("Processed {}".format(num) + " of " + str(len(queries)) + " (" + str(temp) + "%)")
        
    terms = []
    missing_count = 0
    for item in responses:
        temp = []
        if len(list(et.fromstring(item[1]))) > 0:
            terms.append([item[0], getdbpRecord(item[1])])
        else:
            missing_count += 1
    print("There are " + str(missing_count) + " entities that were not found.")
    return terms


def writeVIAFReturns(terms, saveloc):
    file = open(saveloc, "w", encoding="utf-8")
    file.write("Query\tViafID\tURL\tEntityType\tBirthDate\tDeathDate\tTerms\n")
    for term in terms:
        file.write(term[0]+"\t")
        for item in term[1]:
            file.write(str(item)+"\t")
        file.write("\n")
    file.close()
    
def writeDBpediaReturns(terms, saveloc):
    file = open(saveloc, "w", encoding="utf-8")
    file.write("Query\tError\tTerm\tURL\tDate(s)\n")
    sep = "\t"
    for term in terms:
        for item in term[1]:
            file.write(term[0]+"\t")
            file.write(sep.join(item))
            file.write("\t")
            file.write("\n")
    file.close()
    
# =============================================================================
# Main code
# =============================================================================

csvfoldername = easygui.diropenbox("Please select the CSV file that contains your data.")
savefoldername = easygui.diropenbox("Where would you like to save the output")

#request to get the max number of returns from the user.
maxHits = easygui.integerbox("How many returns would you like from DBpedia?")

for file in os.listdir(csvfoldername):
    print("Processing: " + file)
    full_doc = csv.reader(open(os.path.join(csvfoldername, file), newline=''), delimiter="\t")
    
    # create list named entities that includes only the lines that have complete dataset
    names_list = ner2uri(full_doc)
    
    # get results for VIAF and DBpedia
    viafTerms = viafReturns(names_list)
    dbpediaTerms = dbpediaReturns(names_list, maxHits)
    
    # build filename
    filenameVIAF = str(file[:-4])+"_VIAF.txt"
    filenameDBP = str(file[:-4])+"_DBpedia.txt"
    
    # write the information to disk
    writeVIAFReturns(viafTerms, saveloc=os.path.join(savefoldername, filenameVIAF))
    writeDBpediaReturns(dbpediaTerms, saveloc=os.path.join(savefoldername, filenameDBP))












