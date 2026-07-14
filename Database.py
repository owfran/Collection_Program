import pygame 
import sys 
from pathlib import Path
from dataclasses import dataclass

base_dir = Path(__file__).resolve().parent
db_path = base_dir / "database"

@dataclass #each entry is a folder with 1 image and 1 picture
class Entry:
    img_path: Path = None
    txt_path: Path = None
    
    @classmethod
    def load_from_folder(cls, folder_path: Path) -> "Entry": # entry_path
        img = next((f for f in folder_path.iterdir() if f.suffix.lower() in {'.png', '.jpg', '.jpeg'}), None)
        txt = next((f for f in folder_path.iterdir() if f.suffix.lower() == '.txt'), None)
        return cls(img_path=img, txt_path=txt)
    

@dataclass
class Section:
    subsections_paths: list[Path]       # list of paths to each subsection
    subsections_names: list[str]        # list of names of subsections
    subsections_len: int                # total number of subsections
    subsections_each_len: list[int]     # list of the lengths(number of entries) of each subsection in the section
    entry_folder: list[Entry]           # list of all entries in section as Entry classes, odd numbered subsections will be ended with None value
    entry_folder_len: int

    @classmethod
    def load_section_from_folder(cls, section_path: Path) -> "Section":
        # part 1 : find subsection paths
        subsections_paths = []
        i = 1
        while True: # section dir follows a few rules. num_dir always starts at 1 and never skips numbers. There is eactly 1 dir under a num_dir
            num_dir = section_path / str(i)
            if not num_dir.is_dir(): #finds last num folder, checks before trying to make new subsection path
                break
            sub_folder = next(d for d in num_dir.iterdir() if d.is_dir())
            subsections_paths.append(sub_folder)
            i += 1

        # part 2 : get subsection names
        subsections_names = [d.name for d in subsections_paths]

        # part 3 : get number of subsections
        subsections_len = len([d for d in (section_path).iterdir() if d.is_dir()])

        # part 4 : get list of number of entries in each subsection
        subsections_each_len = []
        for sub_dir in subsections_paths:
            subsections_each_len.append(len([d for d in (sub_dir).iterdir() if d.is_dir()]))

        #-------------------------------------------------------------
        # part 5 : make a list of every entry folder in the section
        # odd numbered sections should add a None vlaue at the end
        entry_folder = []
        sub_num = 0
        for sub_dir in subsections_paths: # for each subsection directory
            #if subsections_each_len[subnum] == 0:  #empty subsections need to h
            i = 1 # ? here stop and test wether empty sub section folders can exist
            while True: 
                if subsections_each_len[sub_num] == 0: # happens when no entries exist in sub_dir, make 2 None entrie and add them.
                    entry_folder.append(None)
                    entry_folder.append(None)
                    subsections_each_len[sub_num] = 2 # change number of entry count to 2 for the 2 None vaalues added
                    break

                num_dir = sub_dir / str(i)
                if not num_dir.is_dir(): # afte last existing entry is grabbed, make extra None value and update len if odd numbered
                    if subsections_each_len[sub_num] % 2 == 1: # is odd
                        entry_folder.append(None)
                        subsections_each_len[sub_num] = subsections_each_len[sub_num] + 1
                    break

                inner_folder = next(d for d in num_dir.iterdir() if d.is_dir())
                entry = Entry.load_from_folder(inner_folder)
                entry_folder.append(entry)

                i += 1
            sub_num +=1
        
        # part 6 : length of entry folder
        entry_folder_len = len(entry_folder)
        return cls(subsections_paths,subsections_names,subsections_len,subsections_each_len,entry_folder,entry_folder_len)
    

@dataclass 
class Database:
    sections: list[Section]     # list of all sections
    sections_len: int           # total number of sections
    
    @classmethod
    def load_database(cls, db_path: Path) -> "Database":
        sections = []
        i = 1
        while True: # section dir follows a few rules. num_dir always starts at 1 and never skips numbers. There is eactly 1 dir under a num_dir
            num_dir = db_path / str(i)
            if not num_dir.is_dir(): #finds last num folder, checks before trying to make new subsection path
                break
            sub_folder = next(d for d in num_dir.iterdir() if d.is_dir())
            sections.append(Section.load_section_from_folder(sub_folder))
            i += 1
        sections_len = len(sections)
        return cls(sections,sections_len)
        

DB = Database.load_database(db_path)
#print("\nPrinting Database:")
#print(DB)