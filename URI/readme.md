# Readme
URI folder stores the code and workflow information for 
creating URIs for the StudentNews project.



## VIAF Authority Records
viafURI_v2.py will look up VIAF authorities for named entities (people, organizations, places...).

The input is a csv file with one column (named entities only) or two columns (1: entities; 2: type). The types you can choose from are limited to: person (use: person), place (use: place) or organization (use: org). Any other string will do a Contextual Query Language of all fields.

The result is a tab-delimited file with three or more columns.
1. Col 1: VIAF ID
2. Col 2: full URL
3. Col 3+: prefered terms for that ID

Currently, there is limited UI built in to the application and requires the easygui package.
To install easygui, type the following in your command line: `easy_install easygui`

Also, if it looks like the application has stalled after asking for a save location, you might have a
file explorer box hidden behind an application window.

## DBpedia Authority Records
dbpediaURI.py will look up DBpedia authorities for named entities.

The input is a csv file with one column (named entities only) or two columns (1: entities; 2: type). The types you can choose from are limited to: place (use: place), person (use: person) or organization (use: org). Any other string will do a search without specifying a field. You will also be asked to specify the number of returns that you want. If nothing is specified or if anything is entered other than a positive integer, the number of returns will default to 10.

The results are similar to VIAF lookup above, except that there are only two columns: full URL and prefered term.

You also need easygui package installed.

