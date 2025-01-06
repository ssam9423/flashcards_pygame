# Create Flashcard Tester with Pygame - Samantha Song - started 2024.12.16
# Notes:
#   Loads in flashcards from CSV
#   Tests flashcards - Either all flashcards or just daily review
#   Can only test daily review once a day
#   Once flashcards have been tested, scores are updated
#   Supports mouse clicks and hot keys
#   Button hovers included

# Import Packages
import pygame
import pandas as pd
from pygame.locals import *
from datetime import datetime

# Global Variables
fc_csv_name = "flashcards.csv"
fc_set = pd.read_csv(fc_csv_name)
rows = fc_set.shape[0]      # Number of flashcards
columns = fc_set.shape[1]

today = datetime.today()
date_format = '%m/%d/%Y'    # MM/DD/YYYY
today_format = today.strftime(date_format)

fc_front_ind = [0, 2, 4]
fc_back_ind = [1, 3]
show_front = True
to_test = range(rows)

test_ind = 0

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


# Button Class
class Button:
    def __init__(self, name, bg_color, t_color, x_pos, y_pos):
        self.name = name
        self.bg_color = bg_color
        self.t_color = t_color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = pygame.Rect(self.x_pos, self.y_pos, b_width, b_height)

    def draw(self):
        font = pygame.font.SysFont(font_name, font_size_small)
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=fc_radius)
        button_surf = font.render(self.name, 1, self.t_color)
        text_width, text_height = button_surf.get_size()
        x_center = self.x_pos + (b_width - text_width) / 2
        y_center = self.y_pos + (b_height - text_height) / 2
        screen.blit(button_surf, (x_center, y_center))

    def hover_draw(self):
        font = pygame.font.SysFont(font_name, font_size_small)
        if self.bg_color == light_color:
            pygame.draw.rect(screen, self.bg_color, self.rect, 2, border_radius=fc_radius)
            button_surf = font.render(self.name, 1, self.t_color)
        else:
            pygame.draw.rect(screen, self.bg_color, self.rect, 2, border_radius=fc_radius)
            button_surf = font.render(self.name, 1, self.bg_color)
        text_width, text_height = button_surf.get_size()
        x_center = self.x_pos + (b_width - text_width) / 2
        y_center = self.y_pos + (b_height - text_height) / 2
        screen.blit(button_surf, (x_center, y_center))

# Prints the text of a single Flashcard
def blit_text(surface, fc_index):
    font = pygame.font.SysFont(font_name, font_size_large)
    line_num = 0
    # Defaults to back side
    fc_side_ind = fc_back_ind
    line_total = len(fc_back_ind)
    fc_side_ind = fc_front_ind
    line_total = len(fc_front_ind)
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
def previous(fc_index):
    global show_front
    # If previously Correct
    if fc_set.iloc[fc_index, prev_corr]:
        fc_set.iloc[fc_index, corr] -= 1
    else:
        fc_set.iloc[fc_index, incorr] -= 1
    show_front = True

# User Completes all Flashcards
def end_screen(surface):
        line_surf = font.render("Flashcards Completed", 1, text_color)
        line_width, line_height = line_surf.get_size()
        line_x = (s_width - line_width) / 2
        line_y = fc_y_mid - line_height / 2
        surface.blit(line_surf, (line_x, line_y))

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

# Saves data as CSV - Overrides current CSV
def save(updated_fc_set = fc_set):
    updated_fc_set.to_csv(fc_csv_name, index=False)

# initialize pygame
pygame.init()
 
# Define the dimensions of screen object
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Flashcard Test')

# Initialize Flashcard Testing Buttons
corr_b = Button("Correct", comp_1, bg_color, xr_pos, yd_pos)
incorr_b = Button("Incorrect", comp_2, bg_color, xl_pos, yd_pos)
back_b = Button("Go Back", light_color, text_color, xc_pos, yd_pos)

# Initialize Other Buttons
home_b = Button("Go Home", comp_2, bg_color, xl_pos, yd_pos)
conf_b = Button("Confirm", comp_1, bg_color, xr_pos, yd_pos)

# Initialize Start Screen Buttons
test_all_b = Button("Test All", light_color, text_color, xc_pos, y2_pos)
daily_b = Button("Daily", comp_1, bg_color, xc_pos, y3_pos)

# Variable to keep our game loop running
gameOn = True

#Variable to Determine Game State 
#   0 - Start Game Screen
#   1 - Flashcards
#   2 - Add Flashcard?
#   3 - Remove Flashcard?
game_state = 0
daily = True

# Game loop
while gameOn:
    # for loop through the event queue
    for event in pygame.event.get():
        screen.fill(bg_color)
        # Check to Quit Game      
        if event.type == KEYDOWN:
            # If the Backspace key has been pressed set
            # running to false to exit the main loop
            if event.key == K_BACKSPACE:
                gameOn = False
        # Check for QUIT event
        elif event.type == QUIT:
            gameOn = False

        if game_state == 0: # Start Screen
            # Hot Key Options
            if event.type == KEYDOWN:
                # Pressing 1 - Tests all Flashcards
                if event.key == K_1:
                    to_test = range(rows)
                    daily = False
                    test_ind = 0
                    game_state = 1
                # Pressing 2 - Tests Daily Review
                if event.key == K_2:
                    to_test = daily_review()
                    # Only allows Daily Review if there are FC to test
                    if len(to_test) != 0:
                        daily = True
                        test_ind = 0
                        game_state = 1
            # Mouse Click Options
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if test_all_b.rect.collidepoint(event.pos):
                    to_test = range(rows)
                    daily = False
                    test_ind = 0
                    game_state = 1
                if daily_b.rect.collidepoint(event.pos):
                    to_test = daily_review()
                    daily = True
                    test_ind = 0
                    game_state = 1
            # Shows Buttons
            # Only shows Daily Review if not done yet
            if len(daily_review()) > 0:
                if daily_b.rect.collidepoint(pygame.mouse.get_pos()):
                    daily_b.hover_draw()
                else:
                    daily_b.draw()
            if test_all_b.rect.collidepoint(pygame.mouse.get_pos()):
                test_all_b.hover_draw()
            else:
                test_all_b.draw()

        if game_state == 1: # Testing Flashcards
            # Hot Key Options
            if event.type == KEYDOWN:
                # There are still Flashcards to test
                if test_ind < len(to_test):
                    if event.key == K_SPACE:
                        flip()
                    elif event.key == K_f:
                        incorrect(to_test[test_ind])
                        test_ind += 1
                    elif event.key == K_j:
                        correct(to_test[test_ind])
                        if daily:
                            fc_set.iloc[to_test[test_ind], last_date] = today_format
                        test_ind += 1
                # Complete testing flashcards & save data
                else:
                    if event.key == K_SPACE:
                        game_state = 0
                        save()
                # If there are flashcards to go back to
                if test_ind > 0:
                    if event.key == K_b:
                        test_ind -= 1
                        previous(to_test[test_ind])
            # Mouse Click Options
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # There are still Flashcards to test
                if test_ind < len(to_test):
                    if fc_rect.collidepoint(event.pos):
                        flip()
                    elif incorr_b.rect.collidepoint(event.pos):
                        incorrect(to_test[test_ind])
                        test_ind += 1
                    elif corr_b.rect.collidepoint(event.pos):
                        correct(to_test[test_ind])
                        if daily:
                            fc_set.iloc[to_test[test_ind], last_date] = today_format
                        test_ind += 1
                # Complete testing flashcards & save data
                else:
                    if home_b.rect.collidepoint(event.pos):
                        game_state = 0
                        save()
                # If there are flashcards to go back to
                if test_ind > 0:
                    if back_b.rect.collidepoint(event.pos):
                        test_ind -= 1
                        previous(to_test[test_ind])
            # Displays Flashcard and appropriate buttons
            if fc_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, fc_bg_color, fc_rect, 2, border_radius=fc_radius)
            else:
                pygame.draw.rect(screen, fc_bg_color, fc_rect, border_radius=fc_radius)
            if test_ind < len(to_test):
                blit_text(screen, to_test[test_ind])
                if corr_b.rect.collidepoint(pygame.mouse.get_pos()):
                    corr_b.hover_draw()
                else:
                    corr_b.draw()
                if incorr_b.rect.collidepoint(pygame.mouse.get_pos()):
                    incorr_b.hover_draw()
                else:
                    incorr_b.draw()
            else:
                end_screen(screen)
                if home_b.rect.collidepoint(pygame.mouse.get_pos()):
                    home_b.hover_draw()
                else:
                    home_b.draw()
            if test_ind > 0:
                if back_b.rect.collidepoint(pygame.mouse.get_pos()):
                    back_b.hover_draw()
                else:
                    back_b.draw()

    # Update the display using flip
    pygame.display.flip()
