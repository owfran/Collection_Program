# runs with python 3.12.10 interpreter
import pygame 
import sys 
from pathlib import Path
import Database

pygame.init()

base_dir = Path(__file__).resolve().parent
#grabs monitor size info and sets an current aspect ratio for later.
monitor_info = pygame.display.Info()
current_w = monitor_info.current_w
current_h = monitor_info.current_h
print(f"Monitor size: {current_w}x{current_h}")
current_aspect = current_w / current_h


# base game run in 1920 x 1080
screen = pygame.display.set_mode((current_w,current_h),pygame.NOFRAME)
pygame.display.toggle_fullscreen() #needed for raspberry pi
pygame.display.set_caption("Paleo_Database")
aspect = 1920/1080
surface = pygame.Surface((1920,1080)) #IMPORTANT everything should be drawn on the surface so it can be scaled later.

#-----------------Dynamic scaling, uses known aspect 1920/1080, monitor aspect, and current h and w to resize te image to fit any screen.
x_offset = 0
y_offset = 0
if current_aspect > aspect:
    # Window is wider than game aspect ratio (Pillarboxing - bars on sides)
    new_h = current_h
    new_w = int(new_h * aspect)
    x_offset = (current_w - new_w) // 2
    y_offset = 0
else:
    # Window is taller than game aspect ratio (Letterboxing - bars on top/bottom)
    new_w = current_w
    new_h = int(new_w / aspect)
    x_offset = 0
    y_offset = (current_h - new_h) // 2



clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0,)
LIGHTBLUE = (150,200,250)
font = pygame.font.SysFont(None, 48)

tab_base = pygame.image.load(str(base_dir / "assets" / "tab_base.png")).convert_alpha()
left_tab = tab_base.subsurface(pygame.Rect(0, 0, 180, 3240))
right_tab = tab_base.subsurface(pygame.Rect(180, 0, 1920 - 180, 3240))

def tab_y_pos(tab_count,tab_height): # returns a list of usable tab ypos and hitboxes
    # 30p | 170p | center
    # draw acceptable ypos: ony want images to appear between 30 and 1050. tabs are 340 tall. centers between 200 and 880. shift up 170
    # code to find draw positions should be code than can find distributed image centers wibetween 200 and 880. then just shift all ypos up 170
    max_pos = 1060 - (tab_height/2)
    min_pos = 20 + (tab_height/2)
    delta = round((max_pos-min_pos)/tab_count)
    #print(delta)
    list_pos = []
    list_hitboxes = []
    for i in range(tab_count):
        #find evenly distributed position between 20+(tab height/2) and 1060 - (tab height / 2)
        list_pos.append( round(min_pos+(delta*i)+(delta/2))-1620 )
        new_hitbox = pygame.Rect(20,round(min_pos+(delta*i)+(delta/2)-(tab_height/2)),170,tab_height)
        list_hitboxes.append(new_hitbox)
        #pygame.Rect(20, 20, 170, 245)
    return(list_pos,list_hitboxes)

def draw_tab(tabnum,tab_count,tab_ypos):
    for i in range(tab_count):
        surface.blit(left_tab,(0,tab_ypos[i]))
    surface.blit(left_tab,(0,tab_ypos[tabnum]))
    surface.blit(right_tab,(180,-1080))

#----------------------------draw subsections
def subs_draws_pos(section): #should be run at starts and during tab change. returns a list of every tab drawing position (same len as folder names)
    y_pos = []
    ymax = 240 # starting value is 220.
    for i in range(len(section.subsections_each_len)):
        y_pos.append(ymax)
        ymax = ymax + ((section.subsections_each_len[i]*400/2))
    #print(y_pos)
    return(y_pos)

def draw_subsections(section,scroll,sub_draw_x_pos):
    for i in range(len(sub_draw_x_pos)):
        if abs(scroll - sub_draw_x_pos[i])<2600: # 2600 is just a random number above 1920
            surface.blit(font.render(section.subsections_names[i], True, BLACK),(sub_draw_x_pos[i]-scroll,1000))
            pygame.draw.rect(surface,LIGHTBLUE,(sub_draw_x_pos[i]-scroll - 30, 0, 5, 1080))

            
#---------------------------drawing
# x usable space 190 to 1890.  y usable space 20 to 1060
# try pictures 380x380. initial at 220,40.   20 pixel spaceing

def create_or_replace_hitboxes(scroll):
    hitboxes = []
    for i in range(12):
        x_val = (220+((i//2) * 400)-(scroll % 400))
        y_val = 40 + (400 * (i %2 ))
        hitboxes.append(pygame.Rect(x_val, y_val, 380, 380))
    return(hitboxes)

def get_entry_for_hitbox_clicked(hitboxes,mouse_pos,section,scroll,section_images_loaded):
    subset_index = None
    for i in range(12):
        if hitboxes[i].collidepoint(mouse_pos):
            subset_index = i
            clicked_entry_index = section_images_loaded[((scroll // 400)*2) + subset_index] #written this weird way because the section images list is padded with extra tailing None values that wont give index errors and just return None.
            if clicked_entry_index != None:
                clicked_entry = section.entry_folder[((scroll // 400)*2) + subset_index]
                return clicked_entry
            else:
                return None
    return None #if no htibox clicked

def get_info_panel_text(info_panel_entry,info_panel_max_chars_line):
    file_path = info_panel_entry.txt_path
    final_lines = []
    with open(file_path, "r", encoding='utf-8') as file:
        for line in file:
            # Remove trailing newline characters
            current_chunk = line.rstrip("\n")
            # split up the line while it exceeds the character limit
            #if not it just adds to the list of text
            while len(current_chunk) > info_panel_max_chars_line:
                # find the last space within the max character limit
                space_index = current_chunk.rfind(" ", 0, info_panel_max_chars_line)
                # if no space exists before the limit, keep the whole line
                if space_index == -1:
                    break
                final_lines.append(current_chunk[:space_index]) #saves up to index
                current_chunk = current_chunk[space_index + 1 :] # continue on with the rest. +1 to skip the space itself
            # append remaning, or the original line
            final_lines.append(current_chunk)
    return final_lines

def draw_panel_text(info_panel_text,info_panel_font,info_panel_font_color,info_panel_font_size,x_start,y_start):
    #surface.blit(font.render(str(scrollOF), True, BLACK),(600,600))
    for i in range(len(info_panel_text)):
        surface.blit(font.render(info_panel_text[i], True, info_panel_font_color),(x_start,y_start + (i * info_panel_font_size)))


def draw_scrolled(entries,scroll): # takes a list of pre loaded images and draws them on locaiton based off of scroll value
    # 220 is base drawing position. off set every 400. all images moved back by the scroll amount up to one partition (image width plus space between image = 380 + 20 = 400).
    surface.blit(entries[0],((220+0-(scroll % 400)),40)) if entries[0] != None else None
    surface.blit(entries[1],((220+0-(scroll % 400)),440)) if entries[1] != None else None
    surface.blit(entries[2],((220+400-(scroll % 400)),40)) if entries[2] != None else None
    surface.blit(entries[3],((220+400-(scroll % 400)),440)) if entries[3] != None else None
    surface.blit(entries[4],((220+800-(scroll % 400)),40)) if entries[4] != None else None
    surface.blit(entries[5],((220+800-(scroll % 400)),440)) if entries[5] != None else None
    surface.blit(entries[6],((220+1200-(scroll % 400)),40)) if entries[6] != None else None
    surface.blit(entries[7],((220+1200-(scroll % 400)),440)) if entries[7] != None else None
    surface.blit(entries[8],((220+1600-(scroll % 400)),40)) if entries[8] != None else None
    surface.blit(entries[9],((220+1600-(scroll % 400)),440)) if entries[9] != None else None
    surface.blit(entries[10],((220+2000-(scroll % 400)),40)) if entries[10] != None else None
    surface.blit(entries[11],((220+2000-(scroll % 400)),440)) if entries[11] != None else None

def load_section_images(section):# returns a list of all active images already loaded, not skipping None vals.
    # entry_path = Database.DB.sections[tab]
    result = []
    for i in range(section.entry_folder_len):
        if section.entry_folder[i] == None:
            result.append(None)
        else:
            result.append(pygame.transform.scale(pygame.image.load(str(section.entry_folder[i].img_path)).convert_alpha(), (380, 380)))
            #Database.DB.sections[0].entry_folder[0].img_path
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
    result.append(None) #add a few buffers because i didnt solve index error properly
    #print(f"loaded images: {result}")    
    return(result)

def set_scroll_images(scroll,section_images_loaded):
    #goal: take the list of entries and make a smaller list of entries that covers it based on the scroll value.
    #[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #        [0,0,0,0,0,0,0,0,0,0,0,0] increments by 2
    # scroll max shoudl take care of possible over and under flows. 
    current_index = scroll // (200)
    if current_index % 2 == 1:
        current_index -= 1
    visible_images = []
    for i in range(12):
        visible_images.append(section_images_loaded[current_index+i])
    return(visible_images)



def game():
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    run = True
    #~~~ info panel
    info_panel_active = False
    info_panel_entry = None #Entry type
    info_panel_image = None # loaded image type
    #info panel background_image
    info_panel_text = [] # list of strings
    info_panel_max_chars_line = 50
    info_panel_font_size = 60
    info_panel_font = pygame.font.SysFont(None, info_panel_font_size)
    info_panel_font_color = BLACK
    
    #~~~ scroll and drag
    scrollOF = 0
    is_dragging = False
    drag_start_x = 0
    scroll_start_val = 0
    drag_threshold = 5
    scrollMax = 399

    #~~~ tabs
    tab = 0
    tab_height = 160 # height of tab part that sticks out in pixels
    tab_count = len([d for d in (base_dir / "database").iterdir() if d.is_dir()])
    tab_ypos,tab_hitboxes = tab_y_pos(tab_count,tab_height) # list of tab y positions and returns list of tab hitboxes


    sub_draw_x_pos = subs_draws_pos(Database.DB.sections[tab])
    #~~~~~~inital load images section. program WILL crash if at least 1 subsection is not added from the extracter
    hitboxes = create_or_replace_hitboxes(scrollOF)
    visible_images = [None,None,None,None,None,None,None,None,None,None,None,None]
    scrollMax = (Database.DB.sections[tab].entry_folder_len * 200) - 1600 # (entry count * (width of entry = 400) / (stack height = 2)) - 1600. lenth of 4 more entries. keep it from scrolling to far.
    if scrollMax < 1:
        scrollMax = 1 
    scrollOF = 0 
    section_images_loaded = load_section_images(Database.DB.sections[tab]) #*************
    visible_images = (set_scroll_images(scrollOF,section_images_loaded)) #load once for when tab is clicked
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    while run:

        # events manger----------------------------------------M
        #------------------------------------------------------M
        #------------------------------------------------------M
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                mouse_pos = event.pos 
                if current_aspect > aspect: #pillarbox 
                    mouse_pos = (int((mouse_pos[0]-x_offset)*(1920/(current_h*aspect))),int((mouse_pos[1])*(1080/current_h))) 
                else: # letterbox 
                    mouse_pos = (int((mouse_pos[0])*(1920/current_w)),int((mouse_pos[1]-y_offset)*(1080/(current_w/aspect)))) 
                
                # checking tab clicks first #-------------------tabs
                if mouse_pos[0] < 170: 
                    for i in range(tab_count):
                        if tab_hitboxes[i].collidepoint(mouse_pos):
                            info_panel_active = False
                            tab = i
                            scrollMax = (Database.DB.sections[tab].entry_folder_len * 200) - 1600 # (entry count * (width of entry = 400) / (stack height = 2)) - 1600. lenth of 4 more entries. keep it from scrolling to far.
                            if scrollMax < 1:
                                scrollMax = 1 
                            scrollOF = 0 
                            sub_draw_x_pos = subs_draws_pos(Database.DB.sections[tab])

                            screen.fill((0, 0, 0))
                            surface.fill((255,255,255))
                            loading_screen = pygame.image.load(str(base_dir / "assets" / "loading_screen.png")).convert_alpha()
                            surface.blit(loading_screen,(0,0))
                            pygame.draw.rect(surface, (50,50,50), (0, 0, 180, 1080)) #color bar behind tabs
                            draw_tab(tab,tab_count,tab_ypos)
                            scaled_surface = pygame.transform.smoothscale(surface, (new_w, new_h))
                            screen.blit(scaled_surface, (x_offset, y_offset))
                            pygame.display.flip()
                            section_images_loaded = load_section_images(Database.DB.sections[tab]) #*************
                            visible_images = (set_scroll_images(scrollOF,section_images_loaded)) #load once for when tab is clicked
                            hitboxes = create_or_replace_hitboxes(scrollOF)
                            clock.tick(2)
                            pygame.event.clear()
                    else:
                        None
                
                # clicked in the scrollable area
                else:
                    if info_panel_active == False: # ^info panel check^
                        is_dragging = True
                        drag_start_x = mouse_pos[0]
                        scroll_start_val = scrollOF

            # 
            elif event.type == pygame.MOUSEMOTION and is_dragging: # never runs if info panel is active and cant be activivated along side info panel
                mouse_pos = event.pos 
                if current_aspect > aspect: 
                    scaled_x = int((mouse_pos[0]-x_offset)*(1920/(current_h*aspect)))
                else: 
                    scaled_x = int((mouse_pos[0])*(1920/current_w))
                
                # horizontal distance
                delta_x = scaled_x - drag_start_x
                
                # update scroll position
                scrollOF = scroll_start_val - delta_x
                if scrollOF < 0:
                    scrollOF = 0
                if scrollOF > scrollMax:
                    scrollOF = scrollMax
                visible_images = (set_scroll_images(scrollOF,section_images_loaded))  #makes a subset of loaded images based on the scroll value.
                                #*************
            # 
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if info_panel_active:
                    #test for info panel exit button. INFO PANEL HERE INFO PANEL HERE INFO PANEL HERE  $$$$$$$$$$$$$$$$$$$
                    info_panel_active = False


                elif is_dragging:
                    mouse_pos = event.pos 
                    if current_aspect > aspect: 
                        mouse_pos = (int((mouse_pos[0]-x_offset)*(1920/(current_h*aspect))),int((mouse_pos[1])*(1080/current_h))) 
                    else: 
                        mouse_pos = (int((mouse_pos[0])*(1920/current_w)),int((mouse_pos[1]-y_offset)*(1080/(current_w/aspect))))
                    
                    # halculate total horizontal distance moved during the drag
                    total_delta_x = abs(mouse_pos[0] - drag_start_x)
                    
                    # if the mouse barely moved horizontally, it counts as a static click
                    if total_delta_x < drag_threshold:
                        #hitbox check logic here
                        #print("click detected")
                        entry_if_clicked = get_entry_for_hitbox_clicked(hitboxes,mouse_pos,Database.DB.sections[tab],scrollOF,section_images_loaded) #returns either index of hitbox clicked or None if no entry clicked
                        # shift error either in section_images_loaded or git entry funciton
                        #probably a discontinuity between section_images_loaded and section.tab
                        #print(entry_if_clicked)
                        if entry_if_clicked != None:
                            info_panel_active = True
                            info_panel_entry = entry_if_clicked
                            info_panel_image = (pygame.transform.scale(pygame.image.load(str(entry_if_clicked.img_path)).convert_alpha(), (700, 700)))
                            info_panel_text = get_info_panel_text(info_panel_entry,info_panel_max_chars_line)


                        else:
                            None
                        #here comapre hitbox clicked index to entry index to bring up info panel if not None
                        #if entry_if_clicked test for None. if not None then load info panel.


                    else:
                        #print("horizontal drag finished")
                        hitboxes = create_or_replace_hitboxes(scrollOF)
                        #print(hitboxes)
                    
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



        screen.fill((0, 0, 0)) #first thing to draw to give black bars 

        surface.fill((255,255,255)) # first layer in game surface is background
        #--------------------------images
        # x usable space 190 to 1890.  y usable space 20 to 1060
        # try pictures 380x380. initial at 220,40.   20 pixel spaceing?
        if info_panel_active == False:
            draw_scrolled(visible_images,scrollOF)     #*************
            draw_subsections(Database.DB.sections[tab],scrollOF,sub_draw_x_pos)
            #surface.blit(font.render(str(scrollOF), True, BLACK),(600,600)) # debug for scroll
        else:
            #draw info panel data here INFO PANEL HERE INFO PANEL HERE INFO PANEL HERE INFO PANEL HERE  $$$$$$$$$$$$
            surface.blit(info_panel_image,(220,40)) #image size is 700x700 @ ((220+700+20),40)
            draw_panel_text(info_panel_text,info_panel_font,info_panel_font_color,info_panel_font_size,940,40)
            #draw text function (text,font,color,pos)


        #-------------------------foreground

        #images displayed as screen.blit(imagename,(x,y))  images displayed with their coords beign in the top left and 0,0 on screen beign top left
        # pygame.draw.rect (surface, color, (x, y, width, height))
        pygame.draw.rect(surface, (50,50,50), (0, 0, 180, 1080)) #color bar behind tabs
        
        draw_tab(tab,tab_count,tab_ypos)

        # Scale the internal virtual surface to the calculated size
        scaled_surface = pygame.transform.smoothscale(surface, (new_w, new_h))
        
        # Blit (draw) the scaled surface onto the real screen at the centered offsets
        screen.blit(scaled_surface, (x_offset, y_offset))
        #-------------------------------------------------------------------------------------

        pygame.display.flip()
        clock.tick(30)
        #----------------end of loop
    pygame.quit()
    sys.exit()

game()