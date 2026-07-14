from pathlib import Path
import openpyxl
import zipfile
import re

base_dir = Path(__file__).resolve().parent
db_path = base_dir / "database"

# cell = ws.cell(row=row_idx, column=col_idx)
# value = cell.value
# .strip() can remove new line characters

def write_text_to_entry(excel_name,new_entry_folder,row_start,ws,ws_max):
    row_num = row_start
    row_val_A = ws.cell(row=row_num, column=1).value
    row_val_B = ws.cell(row=row_num, column=2).value
    file_path = new_entry_folder / "new_file.txt"
    with open(file_path, 'w', encoding='utf-8') as new_entry_file:
        new_entry_file.write(f"{row_val_B}\n") # writes the cell next to image as a minimum requirement
        row_num += 1
        row_val_A = ws.cell(row=row_num, column=1).value
        row_val_B = ws.cell(row=row_num, column=2).value
        while (row_val_B is not None) and (not str(row_val_A).startswith("#")): # stops when colB has an empty value, or when colA is another image(start of other entry)
            if (row_num) > ws_max:
                break
            new_entry_file.write(f"{row_val_B}\n") #after check passes
            row_num += 1
            row_val_A = ws.cell(row=row_num, column=1).value
            row_val_B = ws.cell(row=row_num, column=2).value
        print(f"last text for this entry on line: {row_num-1}")
            
    

def generate_subsection(excel_name,section_path,starting_row,subsections_track,ws, starting_num_picture,ws_max) -> int:
    num_path = (section_path / str(subsections_track)) # making folder inside section folder that is just the number path.
    num_path.mkdir(parents=True, exist_ok=True)   # this is done to make it possible to load data in order that it appeard in excel. 
    
    row_track = starting_row #first row of the section
    val = ws.cell(row=row_track, column=1).value #this rows value will be used for folder name
    clean_name = str(val).strip() 
    clean_name = re.sub(r'[/\\()]', '', clean_name)
    subsection_name = clean_name.strip(' .') #cleaned up name
    # does not check if name already used. Just hoping people dont make section names identical (why split up a section?)
    subsection_path = num_path / subsection_name
    subsection_path.mkdir(parents=True, exist_ok=True) # path at this point is: main / database / section / subsection number / subsection name

    #begin loop untill end of subsection (until col1 val is text. See the if statement in generate_section())
    row_track = starting_row + 1 # sets pos to right after subsection name
    row_val = ws.cell(row=row_track, column=1).value
    num_of_pics_in_section = 0
    entries_made = 0

    
    # starts at name of section. has to moke until it finds the next section.
    while row_val is None or str(row_val).startswith("#"):
        #print(f" total pictures in excel = {num_of_pics_in_section}")
        # move until image is found. simply require that entry starts with an image, text next to and below it will contribute to the entry.
        # if nothing found no problems occur.
        # load image first
        if str(row_val).startswith("#"): # finds a new image. Time to start a new entry folder.
            
            entry_name_val = ws.cell(row=row_track, column=2).value
            clean_entry_name = str(entry_name_val).strip() 
            clean_entry_name = re.sub(r'[/\\()]', '', clean_entry_name)
            entry_name = clean_entry_name.strip(' .')

            entries_made += 1
            new_entry_folder = subsection_path / str(entries_made) / f"{entry_name}"
            if new_entry_folder.is_dir():
                print("this name already exists: making new name")
                check = 2
                while new_entry_folder.is_dir():
                    new_entry_folder = subsection_path / f"{entry_name}{check}"
                    check+=1
            print(f"{entry_name} in {new_entry_folder}")
            new_entry_folder.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(excel_name, "r") as archive:
                available_files = archive.namelist()
                png_name = f"xl/media/image{starting_num_picture + num_of_pics_in_section}.png" # reverse modulo formula and skip index 0 and kip index 1 (image 1 is example)
                jpg_name = f"xl/media/image{starting_num_picture + num_of_pics_in_section}.jpeg"  # Excel stores jpg internally as .jpeg
                if png_name in available_files:
                    image_filename = png_name
                    img_ext = "png"
                elif jpg_name in available_files: #found out some of my images are .jpg
                    image_filename = jpg_name
                    img_ext = "jpg"
                else:
                    print(f"failed to find proper image extension of {entry_name}")
                
                image_dest_path = new_entry_folder / f"image_{starting_num_picture + num_of_pics_in_section}.{img_ext}"
                with open(image_dest_path, "wb") as f:
                    f.write(archive.read(image_filename))
                    num_of_pics_in_section += 1

            # on this indent? start code to get text
            write_text_to_entry(excel_name,new_entry_folder,row_track,ws,ws_max)

        

        row_track += 1
        #print(row_track)
        row_val = ws.cell(row=row_track, column=1).value
        if row_track > ws_max:
            break

    return (num_of_pics_in_section)


def generate_section(excel_name,section_path):
    section_path.mkdir(parents=True, exist_ok=True) # make new section folder inside of database
    wb = openpyxl.load_workbook(excel_name)
    ws = wb.active
    ws_max = ws.max_row
    row_track = 1
    starting_num_picture = 1
    subsections_track = 1 # keep track of how many subsections there are. important index to make subsections into number folders in the order they appear in excel.
    while row_track <= ws_max: # main logic to go through every row until max row is hit
        row_val = ws.cell(row=row_track, column=1).value
        if row_val is not None and str(row_val).strip() and not str(row_val).startswith("#"): # checks for text not image
            print(f"Cell has valid text: {row_val}")
            starting_num_picture += generate_subsection(excel_name,section_path,row_track,subsections_track,ws,starting_num_picture,ws_max)
            #starting_num_picture will keep track of how may pictures have been gone through in excels zipped data. 
            subsections_track += 1
        row_track+=1
    print("done")
    print(f"total_pictures in excel: {starting_num_picture-1}") # -1 because my poor tracking
    



first_excel = next(base_dir.glob('*.xlsx'), None)

if first_excel is None:
    print("No .xlsx files found.")
else:
    excel_name = first_excel.name

    i=1
    while (db_path / str(i)).is_dir():
        print (db_path / str(i)) 
        i+=1
    section_path = db_path / str(i) /first_excel.stem
    print(f"Grabbing data from: {excel_name}")
    print(f"Loading data into: {section_path}")
    generate_section(excel_name,section_path)
    