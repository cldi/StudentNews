# Readme
URI folder stores the code and workflow information for 
creating URIs for the StudentNews project.



## VIAF Authority Records
viafURI_v2.py will look up VIAF authorities for named entities (people, organizations, places...).

The input is a csv file with one column (named entities only) or two columns (1: entities; 2: type). The types you can choose from are limited to: person (use: person), place (use: place) or organization (use: org). Any other string will do a Contextual Query Language of all fields.

The result is a tab-delimited file with seven or more columns.
1. Col 1: Original search term
2. Col 2: VIAF ID
3. Col 3: Entity type
4. Col 4: Full URL
5. Col 5: Birth date
6. Col 6: Death date
7. Col 7+: Prefered terms for that ID

The dates provided in columns 5 and 6 come from the accompanying date entries. If there is no available date for either birth or death (for whatever reason) there will be zeroes reported for those values.

Currently, there is limited UI built in to the application and requires the easygui package.
To install easygui, type the following in your command line: `easy_install easygui`

Also, if it looks like the application has stalled after asking for a save location, you might have a
file explorer box hidden behind an application window.

## DBpedia Authority Records
dbpediaURIv1_1.py will look up DBpedia authorities for named entities.

The input is a csv file with one column (named entities only) or two columns (1: entities; 2: type). The types you can choose from are limited to: place (use: place), person (use: person) or organization (use: org). Any other string will do a search without specifying a field. You will also be asked to specify the number of returns that you want. If nothing is specified or if anything is entered other than a positive integer, the number of returns will default to 10.

The result is a tab-delimited file with four or more columns.
1. Col. 1: Original search term
2. Col. 2: DBpedia term
3. Col. 3: Full URL
4. Col. 4: Date(s)

The column containing dates (column 4) comes from the text description provided by DBpedia. There is a regex search for any of the following pattern: 1900-01-01;  01 January 1900; or 01 January 1900. Multiple dates (often two) from the same text field are joined together in the same column using a semi-colon (without spaces). If there are no dates available, the column will read either None or empty. (None: no matching patterns found in description; Empty: no text description provided for that entry.)

Also requires easygui  package.

## Full process
main_long.py will look up both VIAF and DBpedia URIs from a set of named entities.

The input is a tab-delimited file with three columns. This format is designed to match the output of the StanfordNER 4-class model (PERSON, LOCATION, ORGANIZATION, MISC) using tabbed entities. This has two advantages: 1) it keeps first and last names together and 2) it keeps the entity in context.

You will be asked to provide a folder with the input files and another folder for the output files. These should be different, otherwise you end up in a infinite loop.

For each input file, you have two output files: 1) VIAF URIs and 2) DBpedia URIs. The output files are very similar to the descriptions provided for each in the above sections.





