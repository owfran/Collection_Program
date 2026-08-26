from pathlib import Path
from zipfile import ZipFile
from docx2python import docx2python


base_dir = Path(__file__).resolve().parent
db_path = base_dir / "database"
doc_path = next(base_dir.glob("*.docx"), None)


def extract_images_by_name(docx_path):
    #Extract images from DOCX ZIP and return dict: {'imageX.png': image bytes}.
    # docx2python only stores placeholders like ----media/imageX.png---- but not the actual image data.
    # So i have to use zipfile to match to a path like word/media/imageX.png
    images = {}
    temp = ZipFile(docx_path, "r")
    for name in temp.namelist():
        print(name)
        if name.startswith("word/media/"):
            filename = name.split("/")[-1]  # finds just the file name example: image1.png
            images[filename] = temp.read(name)
    return images


def extract_group_title(section):
    print(f"extracting group title from {section}")
    """Extracts the actual group title string from a group title section."""
    cell = section[0][0]
    # pick the first non-empty string
    for s in cell:
        if isinstance(s, str) and s.strip(): # checks if s is a string. 
            #then checks if s without whitespace still exists. will not be true if s = '' or '\n'
            return s.strip()
    return None # Returns none value if no text found. This lets me later ignore making new groups on accident.


def is_entry_row(row):
    """
    Detects entry rows like
    ['----media/image1.jpg----'], ['some text', ...]
    """
    if (
        len(row) == 2 # relates to the 2 by X table size from the document.
        and isinstance(row[0], list) # has to be a list to match docx2python expected output.
        and isinstance(row[1], list) # same as above
        #and len(row[0]) == 1 # removed so no error on extra whitespace after image
        and isinstance(row[0][0], str) # ensures the right cell is text
        and row[0][0].startswith("----media/") # check is first cell first part is an image.
    ):
        return True
    return False


def build_tab(docx_path: Path, db_path: Path):
    doc = docx2python(docx_path)
    print("\n")
    print("\nBODY STRUCTURE")
    print(doc.body)

    print("\nIMAGES FOUND")
    print(len(doc.images))
    print("\n")

    images = extract_images_by_name(docx_path)
    doc_name = docx_path.stem
    # make root dir under appropriate number folder.
    j=1
    while (db_path / str(j)).is_dir():
        print (db_path / str(j)) 
        j+=1
    root = db_path / str(j) / doc_name
    root.mkdir(parents=True, exist_ok=True) #create base folder in database

    group_number = 0
    entry_number = 1
    group_dir = None

    # Iterate through sections
    for section in doc.body:
        #print(section)

        print("\n")
        for row in section:

            print(row)

            if not is_entry_row(row): # try to create a group directory if not entry row. Runs first so group_dir can be made first.
                print("not entry row")
                title = extract_group_title(section)
                if title: # only if an actual title is found.
                    group_number += 1   #increases group num for folder gen
                    entry_number = 1    #resets entry num for folder gen
                    group_dir = root / str(group_number) / title
                    group_dir.mkdir(parents=True, exist_ok=True)
                else:
                    None # prevents making empty group folder ot changing group folder is no title is found.

            else: # runs when a entry row is found
                if group_dir is None:
                    continue  # will now create entries if a group_dir is not defined
                
                print("entry row")
                filename = row[0][0]  # "----media/imageX.Y----"
                filename = filename.replace("----media/", "").replace("----", "") # "imageX.Y"
                #print(filename)
                
                image_bytes = images.get(filename)
                if image_bytes is None:
                    raise ValueError("no matching image file")

                # Extract text lines
                # makes a list of non empty text lines from each part of row[1] (right cell of each row of table in docx)
                text_lines = [part.strip() for part in row[1] if part.strip()] 

                # make readable folder name
                entry_name = text_lines[0] if text_lines else "untitled" 

                # make entry directory
                entry_dir = group_dir / str(entry_number) / entry_name
                entry_dir.mkdir(parents=True, exist_ok=True)

                # save image from bytes
                with open(entry_dir / "image.png", "wb") as f:
                    f.write(image_bytes)

                # save text with new line characters
                with open(entry_dir / "text.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(text_lines))
                    # X.join[A,B,C = AXBXC
                    #here it is used to put new line characters between text lines when writing the file.

                entry_number += 1

# run the builder
build_tab(doc_path, db_path)
