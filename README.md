# Summary
This repository creates a graphical interface to display personal collection entries.

Main window example:
_____________________________________________________________________________________________________________________
![Example](readme%20pictures/main%20example.png)
_____________________________________________________________________________________________________________________
Entry window example:
_____________________________________________________________________________________________________________________
![Entry Example](readme%20pictures/entry%20example.png)
_____________________________________________________________________________________________________________________

Data is sorted into 3 nested groups: tabs -> groups -> entries
This project contains 2 executable files: main.py to run the project, and ExtractExcel.py to build the file system for data.
This project should not be your main way of storing important information. Personal collection information should always have a paper copy.

# What is Needed to Run
This project can run on Windows and Linux (I use a raspberry pi)  
It uses the following libraries:  
pygame  
sys  
pathlib  
openpyxl  
zipfile  
re  
dataclasses  
configparser  
time  

# How to Add Data
This project is designed to work with a specifically formatted Word or Google document. 
This is because it is the format I use to track my collection item information and it is the same document I print out for a paper copy.

Here is an example picture showing how the data should be formatted and any restrictions.
It shows that a group is made every new line with text, and a new entry every image.
The entries in each group must be organized by a 2 wide table with images on the left and associated text on the right.
_____________________________________________________________________________________________________________________
![Format Example](readme%20pictures/EntryGuide.png)
_____________________________________________________________________________________________________________________
To download the data to the program, download the Google Doc as a word, then open the document and ctrlA and ctrlC the whole document.
Open a brand new Excel file next to ExcelExtract.py and paste the document into the top left corner.
_____________________________________________________________________________________________________________________
![Format Example](readme%20pictures/ExcelGuide.png)
_____________________________________________________________________________________________________________________

Make sure the new excel file is the only excel file in the project folder.
Running ExtractExcel.py will take the contents and generate a new folder in database/
Every time ExtractExcel is run, it makes a NEW folder in database.
Each folder in database will correspond  to a tab in the main program.

# Customize Your Program
This program supports customization through sprite upload and a config.txt  
View config.txt to see options for: font size, font color, side bar color, sleep time.  
Program also supports file uploads for the following per each 'tab' folder in the database:  
tab handle (size/dimensions matters) -> tab_handle.png  
tab frame -> tab_handle.png  
background -> background.png  
loading screen -> loading.png  
font -> *.ttf OR *.TTF  
![Format Example](readme%20pictures/file%20custom%20pic.png)
These files are placed directly under the tab number folder (auto generated from data extractor program).
![Format Example](readme%20pictures/filenav%20pic.png)


# Contributions
This project will not be accepting Pull requests.
Please report any bugs in the issues tab on this github page.
