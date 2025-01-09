# Create Flashcard (FC) Tester with Pygame - Samantha Song - started 2024.12.16
# Notes:
#   Loads in flashcards from CSV
#   Tests flashcards - Either all flashcards or just daily review
#   Can only test daily review once a day
#   Once flashcards have been tested, scores are updated
#   Supports mouse clicks and hot keys
#   Button hovers included

# Additions starting 2025.01.06
#   Keep testing flashcards until all are guessed correctly
#   Keep track of FC indexes which are guessed incorrectly
#   At end of FC testing, have continue option which continues testing

# Major Changes starting 2025.01.06:
#   Moved flashcard testing to its own function to allow for continued testing
#   Additional hot keys for completed flashcard screen

# Major Updates starting 2025.01.07:
#   Textbox Class
#   Additional Button functions
#   Support for Adding Flashcards
#   Support for Removing Flashcards

# Import Packages
import pygame
import pandas as pd
from pygame.locals import *
from datetime import datetime
# Using pygame_textinput from github/nearoo
import pygame_textinput as pyti

# initialize pygame
pygame.init()

# Global Variables
fc_csv_name = "flashcards.csv"
fc_set = pd.read_csv(fc_csv_name)
rows = fc_set.shape[0]      # Number of flashcards
columns = fc_set.shape[1]

today = datetime.today()
date_format = '%m/%d/%Y'    # MM/DD/YYYY
today_format = today.strftime(date_format)
clock = pygame.time.Clock()

fc_front_ind = [0, 2, 4]
fc_back_ind = [1, 3]
show_front = True

gameOn = True

# Screen Variables
s_width = 800
s_height = s_width * 3 / 4

# Button Variables
b_width = s_width / 5
b_height = s_width / 10

spacing = (s_width - 3 * b_width) / 3

xl_pos = spacing                                    # Left Button Position
xr_pos = s_width - spacing - b_width                # Right Button Position
xc_pos = (s_width - b_width) / 2                    # Center Button Position

yd_pos = s_height - spacing / 2 - b_height          # Lower Button Position
yu_pos = spacing                                    # Upper Button Position

y2_pos = (s_height - spacing / 4) / 2 - b_height    # Top 2 Position
y3_pos = (s_height + spacing / 4) / 2               # Top 3 Position
y1_pos = y2_pos - b_height - spacing / 4            # Top 1 Position
y4_pos = y3_pos + b_height + spacing / 4            # Top 4 Position

# Font
pygame.font.init()
font_size_large = 40
font_size_small = 20
font_name = 'yugothicuisemibold'                    # Supports Japanese Characters
font = pygame.font.SysFont(font_name, font_size_large)

# Colors for Light Mode
# https://coolors.co/e8e4da-c4b7a4-606c38-283618-a53f2b
bg_color = (232, 228, 218)      # Light Creme
light_color = (196, 183, 164)   # Dark Creme
text_color = (40, 54, 24)       # Dark Green
comp_1 = (96, 108, 56)          # Green
comp_2 = (165, 63, 43)          # Red

# Flashcard Variables
fc_width = s_width - (2 * spacing)
fc_height = s_height - b_height - spacing * 3 / 2
fc_y_mid = (spacing + fc_height) / 2
fc_x_mid = (s_width) / 2
fc_radius = 4
fc_x_pos = spacing
fc_y_pos = spacing / 2

fc_t_color = text_color
fc_bg_color = light_color

fc_rect = pygame.Rect(fc_x_pos, fc_y_pos, fc_width, fc_height)

# Flashcards - Last 4 columns must always be correct, incorrect, and prev_corr, date
corr = columns - 4
incorr = columns - 3
prev_corr = columns - 2
last_date = columns - 1

# Enable key repeat:
pygame.key.set_repeat(200, 25)

# Textbox Varibles
tb_width = s_width - (2*spacing)
tb_height = b_height
tb_x_pos = (s_width - tb_width)/2
font_height = font.get_height()
tb_spacing = (tb_height - font.get_height()) / 2
tb_font_x_pos = tb_x_pos + tb_spacing
cursor_width = 4
tb_manager = pyti.TextInputManager(validator=lambda input: 
                                   (font.render(input, 1, text_color).get_size()[0] +
                                    cursor_width < (tb_width - 2*tb_spacing)))
stop_type = pyti.TextInputManager(validator=lambda input: False)

# Text Input Class
class Textbox:
    def __init__(self, name, y_pos):
        self.name = name
        self.bg_color = light_color
        self.t_color = text_color
        self.y_pos = y_pos
        self.font_y_pos = self.y_pos + tb_spacing
        self.rect = pygame.Rect(tb_x_pos, self.y_pos, tb_width, tb_height)
        self.textinput = pyti.TextInputVisualizer()
        self.textinput.manager = tb_manager
        self.textinput.cursor_visible = False
        self.textinput.cursor_width = cursor_width
        self.textinput.font_color = text_color
        self.textinput.font_object = font
        self.value = ''
        self.on = False
    
    def draw(self):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=fc_radius)

    def empty_draw(self):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=fc_radius)
        screen.blit(font.render(self.name, 1, bg_color), 
                    (tb_font_x_pos, self.font_y_pos))
        
    def tb_box_show(self):
        if self.textinput.value == '' and self.value == '':
            self.empty_draw()
        else:
            self.draw()

    def tb_text_show(self):
        if self.on:
            screen.blit(self.textinput.surface, (tb_font_x_pos, self.font_y_pos))
        else:
            screen.blit(font.render(self.value, 1, text_color), 
                        (tb_font_x_pos, self.font_y_pos))
            
    def clear(self):
        self.value = ''
        self.textinput.value = ''

    def tb_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if not self.on:
                self.textinput.value = self.value
                self.textinput.manager = tb_manager
                self.textinput.cursor_visible = True
                self.on = True
        # Click outside of Textbox 1
        else:
            if self.on:
                if self.textinput.value != '':
                    self.value = self.textinput.value
                self.textinput.manager = stop_type
                self.textinput.cursor_visible = False
                self.on = False


# Button Class
class Button:
    def __init__(self, name, bg_color, t_color, x_pos, y_pos):
        self.name = name
        self.bg_color = bg_color
        self.t_color = t_color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = pygame.Rect(self.x_pos, self.y_pos, b_width, b_height)
        self.font = pygame.font.SysFont(font_name, font_size_small)

    def draw(self):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=fc_radius)
        button_surf = self.font.render(self.name, 1, self.t_color)
        text_width, text_height = button_surf.get_size()
        x_center = self.x_pos + (b_width - text_width) / 2
        y_center = self.y_pos + (b_height - text_height) / 2
        screen.blit(button_surf, (x_center, y_center))

    def hover_draw(self):
        if self.bg_color == light_color:
            pygame.draw.rect(screen, self.bg_color, self.rect, 2, border_radius=fc_radius)
            button_surf = self.font.render(self.name, 1, self.t_color)
        else:
            pygame.draw.rect(screen, self.bg_color, self.rect, 2, border_radius=fc_radius)
            button_surf = self.font.render(self.name, 1, self.bg_color)
        text_width, text_height = button_surf.get_size()
        x_center = self.x_pos + (b_width - text_width) / 2
        y_center = self.y_pos + (b_height - text_height) / 2
        screen.blit(button_surf, (x_center, y_center))

    def interact(self, mouse_pos=pygame.mouse.get_pos()):
        if self.rect.collidepoint(mouse_pos):
            self.hover_draw()
        else:
            self.draw()


# Prints the text of a single Flashcard
# Assumes text on each side fits in one line
def blit_text(surface, fc_index, fc_set=fc_set):
    global show_front, font
    line_num = 0
    # Defaults to back side
    fc_side_ind = fc_back_ind
    line_total = len(fc_back_ind)
    # If front side needs to be shown
    if show_front:
        fc_side_ind = fc_front_ind
        line_total = len(fc_front_ind)
    for i in fc_side_ind:
        if pd.isna(fc_set.iloc[fc_index, i]):
            line_surf = font.render("", 1, text_color)
        else:
            line_surf = font.render(fc_set.iloc[fc_index, i], 1, text_color)
        line_width, line_height = line_surf.get_size()
        line_x = (s_width - line_width) / 2
        line_y = fc_y_mid - (line_total * line_height) / 2
        line_y += line_num * line_height
        surface.blit(line_surf, (line_x, line_y))
        line_num += 1

# Flips Flashcard
def flip():
    global show_front
    show_front = not show_front

# Flashcard Background
def show_fc():
    if fc_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, fc_bg_color, fc_rect, 2, border_radius=fc_radius)
    else:
        pygame.draw.rect(screen, fc_bg_color, fc_rect, border_radius=fc_radius)

# User gets Flashcard Correct
def correct(fc_index):
    global show_front
    fc_set.iloc[fc_index, corr] += 1
    fc_set.iloc[fc_index, prev_corr] = True
    show_front = True

# User gets Flashcard Incorrect
def incorrect(fc_index):
    global show_front
    fc_set.iloc[fc_index, incorr] += 1
    fc_set.iloc[fc_index, prev_corr] = False
    show_front = True

# User goes back to Previous Flashcard
def previous(fc_index, test_more):
    global show_front
    show_front = True
    # If previously correct
    if fc_set.iloc[fc_index, prev_corr]:
        fc_set.iloc[fc_index, corr] -= 1
        return test_more
    else:
        fc_set.iloc[fc_index, incorr] -= 1
        test_more.pop()
        return test_more

# End Screen - Flashcard Background with static text
def end_screen(text="Flashcards Completed"):
    line_surf = font.render(text, 1, text_color)
    line_width, line_height = line_surf.get_size()
    line_x = (s_width - line_width) / 2
    line_y = fc_y_mid - line_height / 2
    screen.blit(line_surf, (line_x, line_y))

# Prints Text at Top of Screen
def top_text(text):
    top_text_surf = font.render(text, 1, text_color)
    screen.blit(top_text_surf, ((s_width - top_text_surf.get_size()[0]) / 2, 
                                y1_pos))

# Daily Review - returns list of indexes to test
def daily_review():
    daily_set = []
    for index in range(rows):
        fc = fc_set.iloc[index]
        # Number of times a FC has been tested
        num_tested = fc.iloc[corr] + fc.iloc[incorr]
        # FC has never been tested, add to daily_set list
        if num_tested == 0:
            daily_set.append(index)
        # Dependent on % correct and time since last 
        else:
            # Percentage that a FC has been guessed correctly
            perc_corr = fc.iloc[corr] / num_tested
            # Days since last time FC was tested
            last_date_str = fc.iloc[last_date]
            last_date_obj = datetime.strptime(last_date_str, date_format)
            days_since = (today - last_date_obj).days
            if perc_corr >= 0.90 and days_since >= 5:
                daily_set.append(index)
            elif perc_corr >= 0.75 and days_since >= 3:
                daily_set.append(index)
            elif perc_corr >= 0.50 and days_since >= 2:
                daily_set.append(index)
            elif perc_corr <= 0.50 and days_since >= 1:
                daily_set.append(index)
    # Returns list of indexes to test from full list
    return daily_set

# Test Flashcards - given list of indexes to test
def test_all(to_test = range(rows), daily=False):
    global gameOn, screen
    test_ind = 0
    test_more = []
    if len(to_test) == 0:
        screen.fill(bg_color)
        return 0
    while gameOn:
        # for loop through the event queue
        for event in pygame.event.get():
            screen.fill(bg_color)
            # Check to Quit Game      
            if event.type == QUIT:
                gameOn = False

            # Hot Key Options
            if event.type == KEYDOWN:
                # There are still Flashcards to test
                if test_ind < len(to_test):
                    if event.key == K_SPACE:
                        flip()
                    elif event.key == K_f:
                        incorrect(to_test[test_ind])
                        test_more.append(to_test[test_ind])
                        test_ind += 1
                    elif event.key == K_j:
                        correct(to_test[test_ind])
                        if daily:
                            fc_set.iloc[to_test[test_ind], last_date] = today_format
                        test_ind += 1
                # There are no more Flashcards to test
                else:
                    if event.key == K_f:
                        save()
                        screen.fill(bg_color)
                        return 1
                    elif event.key == K_j:
                        save()
                        return test_all(to_test=test_more, daily=daily)
                # If there are flashcards to go back to
                if test_ind > 0:
                    if event.key == K_b:
                        test_ind -= 1
                        test_more = previous(to_test[test_ind], test_more)
            # Mouse Click Options
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # There are still Flashcards to test
                if test_ind < len(to_test):
                    if fc_rect.collidepoint(event.pos):
                        flip()
                    elif incorr_b.rect.collidepoint(event.pos):
                        incorrect(to_test[test_ind])
                        test_more.append(to_test[test_ind])
                        test_ind += 1
                    elif corr_b.rect.collidepoint(event.pos):
                        correct(to_test[test_ind])
                        if daily:
                            fc_set.iloc[to_test[test_ind], last_date] = today_format
                        test_ind += 1
                # Complete testing flashcards & save data
                else:
                    if home_b.rect.collidepoint(event.pos):
                        save()
                        screen.fill(bg_color)
                        return 1
                    if cont_b.rect.collidepoint(event.pos) and len(test_more) != 0:
                        save()
                        return test_all(to_test=test_more, daily=daily)
                # If there are flashcards to go back to
                if test_ind > 0:
                    if back_b.rect.collidepoint(event.pos):
                        test_ind -= 1
                        test_more = previous(to_test[test_ind], test_more)
            # Displays Flashcard and appropriate buttons
            show_fc()
            if test_ind < len(to_test):
                blit_text(screen, to_test[test_ind])
                corr_b.interact(pygame.mouse.get_pos())
                incorr_b.interact(pygame.mouse.get_pos())
            else:
                end_screen()
                home_b.interact(pygame.mouse.get_pos())
                if len(test_more) != 0:
                    cont_b.interact(pygame.mouse.get_pos())
            if test_ind > 0:
                back_b.interact(pygame.mouse.get_pos())
            # Update the display using flip
            pygame.display.flip()
    return 1

# Remove Flashcard
def remove():
    global gameOn
    remove_tb.on = True
    while gameOn:
        events = pygame.event.get()
        screen.fill(bg_color)
        # User Inputs
        remove_tb.textinput.update(events)
        for event in events:
            screen.fill(bg_color)
            # Check to Quit Game      
            if event.type == QUIT:
                gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if cont_b.rect.collidepoint(event.pos):
                    return search(remove_tb.textinput.value)
                if home_b.rect.collidepoint(event.pos):
                    remove_tb.clear()
                    return 2
                remove_tb.tb_click(event.pos)
            # Hot Key Options
            if event.type == KEYDOWN and event.key == K_RETURN:
                return search(remove_tb.textinput.value)
        # Shows Relavent Textboxes
        remove_tb.tb_box_show()
        # Shows Relavent Buttons
        cont_b.interact(pygame.mouse.get_pos())
        home_b.interact(pygame.mouse.get_pos())
        # Blit its surface onto the screen
        remove_tb.tb_text_show()
        # Shows Text Above Textbox
        top_text("Input side1 of Flashcard to Remove")
        pygame.display.update()
        clock.tick(30)
    return 0


# Search for flashcard to Remove
# Takes in string and searches flashcards for side1
#   Assumes all side1 are unique
def search(search_for):
    global gameOn, fc_set, rows
    found_ind = rows
    # Flashcards are searched to find a match for user_input on side1
    for ind in range(rows):
        if fc_set.iloc[ind, 0].lower() == search_for.lower():
            found_ind = ind
    while gameOn:
        screen.fill(bg_color)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if cont_b.rect.collidepoint(event.pos):
                    fc_set = fc_set.drop(ind)
                    rows = fc_set.shape[0]
                    end_screen(text="The Flashcard has been Removed")
                    save()
                if home_b.rect.collidepoint(event.pos):
                    return 1
                if back_b.rect.collidepoint(event.pos):
                    return remove()
                if fc_rect.collidepoint(event.pos):
                    flip()
            # Hot Key Options
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    flip()
                if event.key == K_RETURN:
                    fc_set = fc_set.drop(ind)
                    rows = fc_set.shape[0]
                    end_screen(text="The Flashcard has been Removed")
                    save()
            # Displays Flashcard and appropriate buttons
            show_fc()
            # If Flashcard is Found
            if found_ind < rows:
                blit_text(screen, found_ind)
                conf_b.interact(pygame.mouse.get_pos())
            # If Flashcard does not exist
            else:
                end_screen(text="The Flashcard does not Exist")
            back_b.interact(pygame.mouse.get_pos())
            home_b.interact(pygame.mouse.get_pos())
            # Update the display using flip
            pygame.display.flip()
    return 0

# Add Flashcard
def add(side=0, new_fc=[]):
    global gameOn, fc_set
    add_tb.on = True
    add_tb.textinput.manager = tb_manager
    while gameOn:
        screen.fill(bg_color)
        events = pygame.event.get()
        # User Inputs
        add_tb.textinput.update(events)

        for event in events:
            if event.type == QUIT:
                    gameOn = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Return to Home Screen
                if home_b.rect.collidepoint(event.pos):
                    add_tb.clear()
                    add_tb.on = False
                    return 1
                # All Sides have been Input - Show flashcard for confirmation
                if side >= columns - 4:
                    # User Confirms & Adds Flashcard
                    if conf_b.rect.collidepoint(event.pos):
                        add_tb.clear()
                        new_fc.extend([0, 0, False, today.strftime(date_format)])
                        fc_set.iloc[len(fc_set)] = new_fc
                        end_screen(text="The Flashcard has been Added")
                        save()
                        return 1
                    # Flip to see other side of Flashcard
                    if fc_rect.collidepoint(event.pos):
                        flip()
                # There are still Sides to Input
                else:
                    # User Confirms Side
                    if conf_b.rect.collidepoint(event.pos):
                        new_fc.extend([add_tb.textinput.value])
                        add_tb.clear()
                        side += 1
                        return add(side, new_fc)
                    add_tb.tb_click(event.pos)
                # If not on first side
                if side > 0:
                    # Goes back one side
                    if back_b.rect.collidepoint(event.pos):
                        side -= 1
                        new_fc.pop()
                        return add(side, new_fc)
            # Hot Key Options
            if event.type == KEYDOWN:
                if (event.key == K_SPACE) and (side >= columns - 4):
                    flip()
                if event.key == K_RETURN:
                    # User Confirms to Add new Flashcard
                    if side >= columns - 4:
                        add_tb.clear()
                        new_fc.extend([0, 0, False, today.strftime(date_format)])
                        fc_set.iloc[len(fc_set)] = new_fc
                        end_screen(text="The Flashcard has been Added")
                        save()
                        return 1
                    # User Confirms Side
                    else:
                        new_fc.extend([add_tb.textinput.value])
                        add_tb.clear()
                        side += 1
                        return add(side, new_fc)
        # Shows Appropriate Buttons
        if side > 0:
            back_b.interact(pygame.mouse.get_pos())
        home_b.interact(pygame.mouse.get_pos())
        conf_b.interact(pygame.mouse.get_pos())

        # Flashcard if all Sides Input
        if side >= columns - 4:
            show_fc()
            blit_text(screen, 0, fc_set=pd.DataFrame(new_fc).T)
        # Tells User which side to Input
        else:
            top_text("This is Side" + str(side + 1))
            add_tb.tb_box_show()
            add_tb.tb_text_show()
        
        pygame.display.update()
        clock.tick(30)
        

# Saves data as CSV - Overrides current CSV
def save(updated_fc_set = fc_set):
    updated_fc_set.to_csv(fc_csv_name, index=False)

 
# Define the dimensions of screen object
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Flashcard Test')

# Initialize Flashcard Testing Buttons
corr_b = Button("Correct", comp_1, bg_color, xr_pos, yd_pos)
incorr_b = Button("Incorrect", comp_2, bg_color, xl_pos, yd_pos)
back_b = Button("Go Back", light_color, text_color, xc_pos, yd_pos)

# Initialize End Screen Buttons
home_b = Button("Go Home", comp_2, bg_color, xl_pos, yd_pos)
cont_b = Button("Continue", comp_1, bg_color, xr_pos, yd_pos)
conf_b = Button("Confirm", comp_1, bg_color, xr_pos, yd_pos)

# Initialize Start/Home Screen Buttons
test_all_b = Button("Test All", light_color, text_color, xc_pos, y1_pos)
daily_b = Button("Daily", comp_1, bg_color, xc_pos, y4_pos)
add_b = Button("Add", light_color, text_color, xc_pos, y2_pos)
remove_b = Button("Remove", light_color, text_color, xc_pos, y3_pos)

# Remove Textboxes
remove_tb = Textbox("Remove", fc_y_mid)
add_tb = Textbox("Add", fc_y_mid)

# Game loop - Start Screen
while gameOn:
    # for loop through the event queue
    for event in pygame.event.get():
        screen.fill(bg_color)
        # Check to Quit Game      
        if event.type == QUIT:
            gameOn = False

        # Hot Key Options
        if event.type == KEYDOWN:
            # Pressing 1 - Tests all Flashcards
            if event.key == K_1:
                test_all()
            # Pressing 2 - Add Flashcard
            if event.key == K_2:
                add()
            # Pressing 3 - Remove Flashcard
            if event.key == K_3:
                remove()
            # Pressing 4 - Tests Daily Review
            if event.key == K_4:
                test_all(to_test=daily_review(), daily=True)
        # Mouse Click Options
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if test_all_b.rect.collidepoint(event.pos):
                test_all()
            if daily_b.rect.collidepoint(event.pos):
                test_all(to_test=daily_review(), daily=True)
            if add_b.rect.collidepoint(event.pos):
                add_tb.textinput.value = ''
                add()
            if remove_b.rect.collidepoint(event.pos):
                remove_tb.textinput.value = ''
                remove()

        # Shows Buttons
        # Only shows Daily Review if not done yet
        if len(daily_review()) > 0:
            daily_b.interact(pygame.mouse.get_pos())
        test_all_b.interact(pygame.mouse.get_pos())
        add_b.interact(pygame.mouse.get_pos())
        remove_b.interact(pygame.mouse.get_pos())

    # Update the display using flip
    pygame.display.flip()
