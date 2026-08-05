# runs with python 3.12.10 interpreter
import pygame 
import sys 
from pathlib import Path
import Database
import configparser
import time
"""
Structure:
A 'tab'/'section' is the highest level object, created from the data loader program. At least 1 is required to boot the program.
A 'group'/'subsection' is the middle level object. It is displayed inside a tab as a container for entries inside it.
A 'entry' is the lowest level object. It must live inside of a group and contains the data to
display its own 'info panel', showing its associated image and text.

The main function has 3 main parts:
    Initial loading of variables.
    Events manager.
    Drawing (when applicable).

The events manager uses mouse input to determine tab changes, scrolling through entry images to find an entry, and 
clicking to open the entry info panel.

Sleeping loop starts based on a sleep timer reaching its user defined maximum value. Timer reset by mouse down and mouse up actions.
"""
# TO DO
# customize loading screen
# currently doesnt letter or pillar box. Probably wont change due to 16:9 and 16:10 (minimal stretch) monitors being the focus group anyways.

# future verions TO DO
# customizability & prefromance update (tabs and tab loading. adds a config.txt. adds folder for user images)
# Word Doc support update
# geographic support update 
# executibles update

pygame.init()
base_dir = Path(__file__).resolve().parent

monitor_info = pygame.display.Info()

print(f"Monitor size: {monitor_info.current_w}x{monitor_info.current_h}")

# base game run in 1920 x 1080. Surface is the pimary blit/draw location. screen is someitmes blited directly , like during the tab change animation.
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Paleo_Database")
surface = pygame.Surface((1920,1080))

# power button image in top left for touchscreen use.
enable_power_button = True
if enable_power_button:
    power_button_image = pygame.image.load(str(base_dir / "assets" / "power.png")).convert_alpha()

# Controls scrolling image size and spacing.
img_size = 400
img_gap = 50
img_space = img_size + img_gap


clock = pygame.time.Clock()

#----------------------------------------- user config functs

default_font_color = (50,50,50)
default_font_size = 40
default_bar_color = (50,50,50)

def user_font_colors(tab_count):
    config = configparser.ConfigParser()
    config.read('config.txt')
    font_colors = config["Settings"]["font_colors"].strip()
    tuples = []

    if font_colors == "" or font_colors.lower() == "none":
        # tuples empty if no input
        print("No font colors provided.")
    else:
        # parsing user's input list based on end of a tuple ), or ) ,
        for item in font_colors.split("),"): #split by formated values
            item = item.replace("(", "").replace(")", "").strip()
            #each tuple inside user input (x,y,z) -> x,y,z
            # raise errors for user
            if item == "":
                raise ValueError("Empty tuple detected in 'font_colors'")
            # splits tuple into its parts to detect if != 3 before adding to tuples[]
            parts = item.split(",")
            if len(parts) != 3:
                raise ValueError(f"Tuple '{item}' does not contain exactly 3 values")

            #adds each tuple element to a new tuple nums only if passing all error checks. Then adds to tuples[]
            nums = tuple(int(x) for x in parts)
            tuples.append(nums)

    result = []
    # adds user input values to result until it runs out of user input or reaches tab count, then finishes with default values.
    for i in range(tab_count):
        if i<len(tuples):
            result.append(tuples[i])
        else:
            result.append(default_font_color)
    return(result)


def user_font_sizes(tab_count):
    config = configparser.ConfigParser()
    config.read('config.txt')
    font_sizes = config["Settings"]["font_sizes"].strip()
    vals = []

    if font_sizes == "" or font_sizes.lower() == "none":
        print("No font sizes provided.")
    else:
        for item in font_sizes.split(","):
            if item == "":
                raise ValueError("Empty tuple detected in 'font_sizes'")
            vals.append(int(item))

    result = []
    for i in range(tab_count):
        if i<len(vals):
            result.append(vals[i])
        else:
            result.append(default_font_size)

    return(result)

def user_bar_color():
    config = configparser.ConfigParser()
    config.read('config.txt')
    rgb = config["Settings"]["bar_color"].strip()
    if rgb == "" or rgb.lower() == "none":
        print("No bar color provided.")
        return(default_bar_color)
    else:
        rgb = rgb.replace("(", "").replace(")", "").strip()
        parts = rgb.split(",")
        if len(parts) != 3:
            raise ValueError(f"Tuple '{item}' does not contain exactly 3 values")
        nums = tuple(int(x) for x in parts)
        return(nums)

def user_tab_overlap_px():
    config = configparser.ConfigParser()
    config.read('config.txt')
    val = config["Settings"]["overlapping_pxs"].strip()
    val = int(val)
    return(val)

def user_sleep_time():
    time = 0
    enabled = False
    config = configparser.ConfigParser()
    config.read('config.txt')
    val = config["Settings"]["sleep_time"].strip()
    if val == "" or val.lower() == "none":
        None
    else:
        enabled = True
        time = int(val)
    return enabled, time

#--------------------------------------- tab functs
def get_tab_hitboxes(tab_count,tab_images,drawing_order,tab_overlap_px,tab_space_between): # returns a list of hitboxes. need tab images to dynamically assign based on image size.
    list_hitboxes = []
    min_pos = 20
    #tab frame should ALWAYS be draw at x=160
    y_pos_tracker = min_pos
    for i in range(tab_count):
        size = tab_images[drawing_order[i]][0].get_size() # tab_images[x,0] is the tabs handle. returns (width, height)
        #new_hitbox = pygame.Rect(left,top,width,height)
        new_hitbox = pygame.Rect(160-size[0]+tab_overlap_px, y_pos_tracker, size[0], size[1])
        list_hitboxes.append(new_hitbox)
        y_pos_tracker += size[1] + tab_space_between
    return(list_hitboxes)



def draw_tab(tab_count,tab_images,tab_hitboxes,drawing_order): # draws tab images and at the order they are in the list
    #selected and top image should be LAST
    # when new tabs are selected, tab images and tab hitboxes need to be reordered.
    #screen.blit(img, rect)
    #example drawing order might be [2,0,1,3,4]
    for i in range(tab_count-1,0,-1):
        j = drawing_order[i]
        #print(i,j)
        surface.blit(tab_images[j][0],tab_hitboxes[i]) #draws handles first
    surface.blit(tab_images[drawing_order[0]][1],(160,0)) # draws frame of active tab (last in list)
    surface.blit(tab_images[drawing_order[0]][0],tab_hitboxes[0]) # draws handle of active tab last to overlap.

def get_backgrounds(tab_count):# returns a list of background images.
    result = []
    for i in range(tab_count):
        test_path = base_dir / "database" / str(i+1) /"background.png"
        if test_path.is_file():
            result.append(pygame.transform.scale(pygame.image.load(test_path),(1720,1080)).convert())
            print(f"assigning custom background.png image to tab{i+1}")
        else:
            print(f"assigning defualt background.png image to tab{i+1}")
            result.append(pygame.transform.scale(pygame.image.load(str(base_dir / "assets" / "background.png")),(1720,1080)).convert())
    return(result)

def get_tab_images(tab_count):# returns list [[tab_handle.png,tab_frame.png], ...]. each item in tab_images is a list contaning the handle and the frame
    result = []
    result_sec = []
    #pygame.image.load(str(base_dir / "assets" / "loading_screen.png")).convert_alpha()
    for i in range(tab_count):
        # assign custom or defult tab handle image
        test_path = base_dir / "database" / str(i+1) /"tab_handle.png"
        if test_path.is_file():
            result_sec.append(pygame.image.load(test_path).convert_alpha())
            print(f"assigning custom tab_handle.png image to tab{i+1}")
        else:
            print(f"assigning defualt tab_handle.png image to tab{i+1}")
            result_sec.append(pygame.image.load(str(base_dir / "assets" / "tab_handle.png")).convert_alpha())
        # assign custom or defult tab frame image
        # tab_frame images are scaled to fit 1760 x 1080
        test_path = base_dir / "database" / str(i+1) /"tab_frame.png"
        if test_path.is_file():
            result_sec.append(pygame.transform.scale(pygame.image.load(test_path),(1760,1080)).convert_alpha())
            print(f"assigning custom tab_frame.png image to tab{i+1}")
        else:
            result_sec.append(pygame.transform.scale(pygame.image.load(str(base_dir / "assets" / "tab_frame.png")),(1760,1080)).convert_alpha())
            print(f"assigning defualt tab_frame.png image to tab{i+1}")
        result.append(result_sec)
        result_sec = []
    return(result)

def get_tab_loading_screens(tab_count):# returns list [[tab_handle.png,tab_frame.png], ...]. each item in tab_images is a list contaning the handle and the frame
    result = []
    for i in range(tab_count):
        test_path = base_dir / "database" / str(i+1) /"loading.png"
        if test_path.is_file():
            result.append(pygame.transform.scale(pygame.image.load(test_path),(1760,1080)).convert_alpha())
            print(f"assigning custom loading.png image to tab{i+1}")
        else:
            print(f"assigning defualt loading.png image to tab{i+1}")
            result.append(pygame.transform.scale(pygame.image.load(str(base_dir / "assets" / "loading.png")),(1760,1080)).convert_alpha())
    return(result)

    
def get_tab_fonts(tab_count,font_sizes):# returns a list font objects.
    result = []
    for i in range(tab_count):
        test_path = base_dir / "database" / str(i+1)
        fonts_found = [f for f in test_path.iterdir() if f.suffix.lower() == ".ttf"]

        if fonts_found:
            # fonts_found[0] is a Path object. convert it to a string for Pygame
            detected_font = str(fonts_found[0])
            result.append(pygame.font.Font(detected_font, font_sizes[i]))
            print(f"assigning custom font to tab{i+1} with size {font_sizes[i]}")
        else:
            detected_font = str(base_dir / "assets" / "game_font.ttf")
            result.append(pygame.font.Font(detected_font, font_sizes[i]))
            print(f"assigning default font to tab{i+1} with size {font_sizes[i]}")
    return(result)
            

def animated_tab_change(tab_images,drawing_order,old_order,tab_overlap_px,tab_space_between,loading_screen,bar_color):

    tab_count = len(drawing_order)
    # get staring y pos in order of old_order
    starting_ys = []
    min_pos = 20
    y_pos_tracker = min_pos
    for i in range(tab_count):
        size = tab_images[old_order[i]][0].get_size()
        starting_ys.append(y_pos_tracker)
        y_pos_tracker += size[1] + tab_space_between

    # get ending y pos in order of drawing_order / new order
    ending_ys = []
    y_pos_tracker = min_pos
    for i in range(tab_count):
        size = tab_images[drawing_order[i]][0].get_size()
        ending_ys.append(y_pos_tracker)
        y_pos_tracker += size[1] + tab_space_between

    #elemant to prevent drawing to entire screen every frame
    element_surface = pygame.Surface((200, 1080))

    #draw active tab frame first
    surface.blit(loading_screen, (190,0))
    active_id = drawing_order[0]
    surface.blit(tab_images[active_id][1], (160, 0))
    screen.blit(surface, (0, 0))

    frames = 10
    # animation loop
    for frame in range(frames):
        pygame.draw.rect(element_surface, bar_color, (0, 0, 180, 1080)) # color bar
        # draw each tab
        for j in range(tab_count):
            tab_num = old_order[j]
            start_index = old_order.index(tab_num)
            start_y = starting_ys[start_index]

            end_index = drawing_order.index(tab_num)
            end_y = ending_ys[end_index]

            current_y = int(start_y + (end_y - start_y) * (frame / frames)) # y value per image per frame

            # draw handle
            handle_img = tab_images[tab_num][0]
            size = handle_img.get_size()
            x_pos = 160 - size[0] + tab_overlap_px
            element_surface.blit(handle_img, (x_pos, current_y))

        # draw active tab frame last then active tab handle
        active_id = drawing_order[0]
        element_surface.blit(tab_images[active_id][1], (160, 0))
        # late night code looks bad.
        tab_num = drawing_order[0]
        start_index = old_order.index(tab_num)
        start_y = starting_ys[start_index]
        end_index = drawing_order.index(tab_num)
        end_y = ending_ys[end_index]
        current_y = int(start_y + (end_y - start_y) * (frame / frames))
        handle_img = tab_images[tab_num][0]
        size = handle_img.get_size()
        x_pos = 160 - size[0] + tab_overlap_px
        element_surface.blit(handle_img, (x_pos, current_y))

        screen.blit(element_surface, (0, 0))

        pygame.display.flip()

        clock.tick(30)

    surface.fill((255,255,255))
    surface.blit(loading_screen, (190,0))
    pygame.draw.rect(surface, bar_color, (0, 0, 180, 1080)) # color bar

    


#---------------------------- subsection / group functs
def subs_draws_pos(section): #returns a list of every group name drawing x position. Runs only when tab changed or start.
    x_pos = []
    xmax = 230 # starting value is 220.
    for i in range(len(section.subsections_each_len)):
        x_pos.append(xmax)
        xmax = xmax + ((section.subsections_each_len[i]*img_space/2))
    return(x_pos)

def draw_subsections(subsection_text,scroll,sub_draw_x_pos,color): # draws group labels from list based on scroll value and label x position.
    for i in range(len(sub_draw_x_pos)):
        if abs(scroll - sub_draw_x_pos[i])<2600: # 2600 is just a random number above 1920, avoid drawing names far away from what can be seen.
            surface.blit(subsection_text[i],(sub_draw_x_pos[i]-scroll,980))
            pygame.draw.rect(surface,color,(sub_draw_x_pos[i]-scroll - 30, 980, 5, 100))


#--------------------------- entry functs
# x usable space 190 to 1890.  y usable space 20 to 1060
# pictures img_size x img_size. first picture at 220,40.

def create_or_replace_hitboxes(scroll): #  returns a list of pygame.rect objects as hitboxes.
    hitboxes = []
    for i in range(12):
        x_val = (220+((i//2) * img_space)-(scroll % img_space))
        y_val = 40 + (img_space * (i %2 ))
        hitboxes.append(pygame.Rect(x_val, y_val, img_size, img_size))
    return(hitboxes)

def get_entry_for_hitbox_clicked(hitboxes,mouse_pos,section,scroll,section_images_loaded): # returns an entry if its image was clicked.
    subset_index = None
    for i in range(12):
        if hitboxes[i].collidepoint(mouse_pos):
            subset_index = i
            # section_images_loaded[(scroll // img_space)*2] returns the first image on screen(from scroll) of the loaded images.
            clicked_entry_index = section_images_loaded[((scroll // img_space)*2) + subset_index] 
            #written this weird way because the section images list is padded with extra tailing None values that wont give index errors and just return None.
            if clicked_entry_index != None:
                clicked_entry = section.entry_folder[((scroll // img_space)*2) + subset_index]
                return clicked_entry
            else:
                return None
    return None #if no htibox clicked

def get_info_panel_text(info_panel_entry,font_size): # returns a list of text segments dynamically sized to wrap based on font size.
    # Takes an Entry object and uses its text file path to get text.
    # container width = target character count × font size × multiplier
    max_width = 970
    multiplier = .6 # experimental value
    max_characters = round(max_width / (font_size * multiplier))

    file_path = info_panel_entry.txt_path
    final_lines = []
    with open(file_path, "r", encoding='utf-8') as file:
        for line in file:
            # Remove trailing newline characters
            current_chunk = line.rstrip("\n")
            # split up the line while it exceeds the character limit
            #if not it just adds to the list of text
            while len(current_chunk) > max_characters:
                # find the last space within the max character limit
                space_index = current_chunk.rfind(" ", 0, max_characters)
                # if no space exists before the limit, keep the whole line
                if space_index == -1:
                    break
                final_lines.append(current_chunk[:space_index]) #saves up to index
                current_chunk = current_chunk[space_index + 1 :] # continue on with the rest. +1 to skip the space itself
            # append remaning, or the original line
            final_lines.append(current_chunk)
    return final_lines

def draw_panel_text(info_panel_text,font,info_panel_font_color,info_panel_font_size,x_start,y_start): # draws text for entry info panel
    for i in range(len(info_panel_text)):
        surface.blit(font.render(info_panel_text[i], True, info_panel_font_color),(x_start,y_start + (i * info_panel_font_size)))

#test_gs = pygame.image.load(str(base_dir/ "assets" / "gs.png")).convert_alpha()

def draw_scrolled(entries,scroll): # takes a list of pre loaded images and draws them on locaiton based off of scroll value
    # 220 is base drawing position. off set every img_space. all images moved back by the scroll amount up to one partition.
    scroll_mod = scroll % img_space
    base_x = 220
    for i, img in enumerate(entries):
        if img is None:
            continue
        x = base_x + (i//2)*img_space - scroll_mod
        y = 40 + (i%2)*img_space

        #surface.blit(test_gs, (x-20,y-20))
        surface.blit(img, (x,y))


def load_section_images(section):# returns a list of all active images already loaded, not skipping None vals.
    # entry_path = Database.DB.sections[tab]
    result = []
    for i in range(section.entry_folder_len):
        if section.entry_folder[i] == None:
            result.append(None)
        else:
            # Scales then converts for speed and preformance. Normal convert since entry images should not have alpha.
            result.append(pygame.transform.scale(pygame.image.load(str(section.entry_folder[i].img_path)), (img_size, img_size)).convert())
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None)
    result.append(None) #add a few buffers because it helps avoid index errors. 
    #print(f"loaded images: {result}")    
    return(result)

def set_scroll_images(scroll,section_images_loaded):
    #goal: take the list of entryes and make a smaller list of entryes that covers it based on the scroll value.
    #[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #        [0,0,0,0,0,0,0,0,0,0,0,0] increments by 2
    # scroll max should take care of possible over and under flows. 
    current_index = scroll // (img_space//2)
    if current_index % 2 == 1:
        current_index -= 1
    visible_images = []
    for i in range(12):
        visible_images.append(section_images_loaded[current_index+i])
    return(visible_images)


# GAME LOOP BELOW
# GAME LOOP BELOW
# GAME LOOP BELOW


def game():
    run = True
    tab_count = len([d for d in (base_dir / "database").iterdir() if d.is_dir()])
    tab = 0
    sleep_enabled, sleep_time = user_sleep_time()
    print(f"sleep {sleep_enabled}\nsleep time {sleep_time}")
    #~~~ info panel
    info_panel_active = False
    info_panel_entry = None #Entry type
    info_panel_image = None # loaded image type
    info_panel_text = [] # list of strings
    font_colors = user_font_colors(tab_count)
    font_sizes = user_font_sizes(tab_count)
    bar_color = user_bar_color()
    #~~~ scroll and drag
    scrollOF = 0
    is_dragging = False # used only for calculating drags vs clicks
    drag_start_x = 0    # used only for calculating drags vs clicks
    scroll_start_val = 0 # used only for calculating drags vs clicks
    drag_threshold = 5  # used only for calculating drags vs clicks
    scrollMax = 399 # default in case entries in a tab do not exceed 8ish

    #~~~ tabs
    tab_overlap_px = user_tab_overlap_px() # defines how mani pixles the tab_handle image overlaps with the tab_frame image

    tab_space_between = 10 # defines the empty space between all tabs & top in pixles
    # grab tab heights every time redraing tabs and making hitboxes.
    drawing_order = []
    for j in range(tab_count):
        drawing_order.append(j)
    #defult drawing order is 0,1,2,...
    #drawing order will be used to keep track of the order that tabs appear on screen so that tab can track the databse number
    tab_images = get_tab_images(tab_count)
    tab_hitboxes = get_tab_hitboxes(tab_count,tab_images,drawing_order,tab_overlap_px,tab_space_between) 
    tab_fonts = get_tab_fonts(tab_count,font_sizes)
    tab_backgrounds = get_backgrounds(tab_count)
    tab_loading_screens = get_tab_loading_screens(tab_count)
    sub_draw_x_pos = subs_draws_pos(Database.DB.sections[tab]) # variable exists to simplify finding where group/subsection labels shoudl be drawn.

    subsection_text = [tab_fonts[tab].render(name, True, font_colors[tab]) for name in Database.DB.sections[tab].subsections_names]

    #~~~ preview image during inital loading
    screen.fill((0, 0, 0))
    surface.blit(tab_loading_screens[tab],(190,0))
    pygame.draw.rect(surface, bar_color, (0, 0, 180, 1080))
    draw_tab(tab_count,tab_images,tab_hitboxes,drawing_order)
    screen.blit(surface, (0, 0))
    pygame.display.flip()

    sleep_timer_start = time.perf_counter()

    #~~~~~ inital load images section. program WILL crash if at least 1 subsection is not added from the extracter
    hitboxes = create_or_replace_hitboxes(scrollOF)
    visible_images = [None,None,None,None,None,None,None,None,None,None,None,None]
    scrollMax = (Database.DB.sections[tab].entry_folder_len * img_space//2) - 1600 # (entry count * (width of entry = 400) / (stack height = 2)) - 1600. lenth of 4 more entries. keep it from scrolling to far.
    if scrollMax < 1:
        scrollMax = 1 
    scrollOF = 0 
    section_images_loaded = load_section_images(Database.DB.sections[tab]) #*************
    visible_images = (set_scroll_images(scrollOF,section_images_loaded)) #load once for when tab is clicked
    
    # preload frame update
    # this var is used to tell the game to draw only when it is not None. It sets itself to None after being 'used'.
    # This is done to stop drawing every frame and only drawing when something changes. Significantly helps long runtime.

    draw_next_frame = "inital draw"

    while run:

        # events manger----------------------------------------M
        #------------------------------------------------------M
        #------------------------------------------------------M
        """
        Events manager uses a system where mouse down inside the scrollabel area starts a 'dragging' process, which is not complete until
        the mouse is released. During that time the scroll value is changed so you can drag the scrollable surface left and right.
        If the mouse every moves too far before it is released, it counts as a 'drag' and will not activate any info panel.
        Otherwise it runs the hitbox check for entry images being clicked.
        """
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                sleep_timer_start = time.perf_counter() # reset sleep timer
                mouse_pos = event.pos 
                
                # checking tab clicks first
                if mouse_pos[0] < 170: # tab region
                    if enable_power_button: # test for power button first.
                        if mouse_pos[0]<40 and mouse_pos[1]<40:
                            run = False
                    for i in range(tab_count):
                        if tab_hitboxes[i].collidepoint(mouse_pos):
                            info_panel_active = False # Disables entry info panel i
                            tab = drawing_order[i]

                            scrollMax = (Database.DB.sections[tab].entry_folder_len * img_space//2) - 1600 # (entry count * (width of entry = 400) / (stack height = 2)) - 1600. lenth of 4 more entries. keep it from scrolling to far.
                            if scrollMax < 1:
                                scrollMax = 1 
                            scrollOF = 0 
                            sub_draw_x_pos = subs_draws_pos(Database.DB.sections[tab])

                            surface.blit(tab_backgrounds[tab],(200,0))
                            surface.blit(tab_loading_screens[tab],(190,0))
                            pygame.draw.rect(surface, bar_color, (0, 0, 180, 1080)) #color bar behind tabs

                            old_order = drawing_order.copy()
                            #reorder tabs:
                            moving_value = drawing_order[i]
                            #print(f"was {drawing_order}")
                            #print(f"index clicked = {i}")
                            drawing_order.remove(moving_value)
                            drawing_order.insert(0,moving_value)
                            #print(f"became {drawing_order}")

                            #fix hitboxes to match tab_images
                            tab_hitboxes = get_tab_hitboxes(tab_count,tab_images,drawing_order,tab_overlap_px,tab_space_between)

                            
                            animated_tab_change(tab_images,drawing_order,old_order,tab_overlap_px,tab_space_between,tab_loading_screens[tab],bar_color)
                    

                            draw_tab(tab_count,tab_images,tab_hitboxes,drawing_order)

                            screen.blit(surface, (0, 0))

                            pygame.display.flip()
                            section_images_loaded = load_section_images(Database.DB.sections[tab]) #*************
                            visible_images = (set_scroll_images(scrollOF,section_images_loaded)) #load once for when tab is clicked
                            hitboxes = create_or_replace_hitboxes(scrollOF)
                            clock.tick(2)
                            pygame.event.clear()



                            subsection_text = [tab_fonts[tab].render(name, True, font_colors[tab]) for name in Database.DB.sections[tab].subsections_names]
                            #print(subsection_text)

                            draw_next_frame = "frame after tab change"

                        else:
                            None
                # clicked in the scrollable area
                else:
                    if info_panel_active == False: # info panel check
                        is_dragging = True
                        drag_start_x = mouse_pos[0]
                        scroll_start_val = scrollOF

            # 
            elif event.type == pygame.MOUSEMOTION and is_dragging: # never runs if info panel is active and cant be activivated along side info panel
                mouse_pos = event.pos 
                
                # horizontal distance
                delta_x = mouse_pos[0] - drag_start_x
                
                # update scroll position
                scrollOF = scroll_start_val - delta_x
                if scrollOF < 0:
                    scrollOF = 0
                if scrollOF > scrollMax:
                    scrollOF = scrollMax
                visible_images = (set_scroll_images(scrollOF,section_images_loaded))  #makes a subset of loaded images based on the scroll value.

                draw_next_frame = "scrolling through images"
            # 
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                sleep_timer_start = time.perf_counter() # reset sleep timer
                if info_panel_active:
                    #test for info panel exit button. INFO PANEL HERE INFO PANEL HERE INFO PANEL HERE  $$$$$$$$$$$$$$$$$$$
                    info_panel_active = False
                    draw_next_frame = "info panel exited"


                elif is_dragging:
                    mouse_pos = event.pos 
                    
                    # calculate total horizontal distance moved during the drag
                    total_delta_x = abs(mouse_pos[0] - drag_start_x)
                    
                    # if the mouse barely moved horizontally, it counts as a static click
                    if total_delta_x < drag_threshold:
                        #hitbox check logic here
                        entry_if_clicked = get_entry_for_hitbox_clicked(hitboxes,mouse_pos,Database.DB.sections[tab],scrollOF,section_images_loaded) #returns either index of hitbox clicked or None if no entry clicked

                        if entry_if_clicked != None:
                            info_panel_active = True
                            info_panel_entry = entry_if_clicked
                            info_panel_image = (pygame.transform.scale(pygame.image.load(str(entry_if_clicked.img_path)).convert_alpha(), (700, 700)))
                            info_panel_text = get_info_panel_text(info_panel_entry,font_sizes[tab])
                            draw_next_frame = "info panel opened"

                        else:
                            None

                    else:
                        #print("horizontal drag finished")
                        hitboxes = create_or_replace_hitboxes(scrollOF)
                    
                    is_dragging = False

            #--------------quits-------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False
            if event.type == pygame.QUIT:
                run = False
        #------------------------------------------------------M
        #------------------------------------------------------M
        #------------------------------------------------------M

        
        if draw_next_frame != None: # for preformance saving, the screen is only drawn when the draw_next_frame var is given a summary of the screen change.

            surface.blit(tab_backgrounds[tab],(200,0))
            #--------------------------images
            if info_panel_active == False: # draws scrolling / main screen when info panel not active.
                draw_scrolled(visible_images,scrollOF)
                draw_subsections(subsection_text,scrollOF,sub_draw_x_pos,font_colors[tab])
            else: # draw info panel.
                surface.blit(info_panel_image,(220,40))
                draw_panel_text(info_panel_text,tab_fonts[tab],font_colors[tab],font_sizes[tab],940,40)

            #-------------------------foreground
            pygame.draw.rect(surface, bar_color, (0, 0, 180, 1080)) #color bar behind tabs
            if enable_power_button:
                surface.blit(power_button_image,(0,0))

            draw_tab(tab_count,tab_images,tab_hitboxes,drawing_order)

            screen.blit(surface, (0, 0))

            pygame.display.flip()
            draw_next_frame = None
        #-------------------------------------------------------------------------------------

        
        clock.tick(20)

        #------------------------------ sleeping check and loop.
        if sleep_enabled:
            if (time.perf_counter() - sleep_timer_start) > sleep_time:
                sleeping_loop = True
                screen.fill((0,0,0))
                pygame.display.flip()
                while sleeping_loop:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            sleeping_loop = False
                    clock.tick(2)
                sleep_timer_start = time.perf_counter() # reset sleep timer
                pygame.event.clear()
                draw_next_frame = "after sleep redraw"
                

        #----------------end of loop
    pygame.quit()
    sys.exit()

game()