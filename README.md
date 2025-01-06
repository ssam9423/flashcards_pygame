# Flashcard Tester - Pygame Version

## Description
This project is an extension of the Flashcard Tester - Simple Version. 

This is a simple flashcard tester which takes flashcards from a CSV file, and allows the user to mark each flashcard as either correct or incorrect and records how many times a flashcard is marked correct/incorrect.
In the event that the user incorrectly marks a card correct or incorrect, the user can go back to the previous card.
The amount of times the user gets a flashcard correct or incorrect is also adjusted when the user chooses to go back to the previous card.
Once all flashcards have been tested, the user has a chance to return to the last card, in case they made a mistake on the last card. 
After all flashcards are tested or the user quits prematurely, the CSV file is over written with the updated scores.
In additon, this version also has the Daily Review - Creates a subset of flashcards which the user tends to struggle with according to the following:
- User gets flashcard correct less than 50% of the time and it has been at least 2 days since it has been in the daily review.
- User gets flashcard correct between 50% - 75% of the time and it has been at least 2 days since it has been in the daily review.
- User gets flashcard correct between 75% - 90% of the time and it has been at least 3 days since it has been in the daily review.
- User gets flashcard correct more than 90% of the time and it has been at least 5 days since it has been in the daily review.

## CSV File Requirements - Flashcards
This code requires the python program to be in the same directory as the CSV file which contains the flashcards the user wants to test.
The CSV file requires at least 5 columns:
- side1 - side of the flashcard
- side2 - side of the flashcard
- side3 ... side# - sides of flashcard (optional)
- corr - # of times tester has gotten the answer correct
- incorr - # of times the tester has gotten the answer incorrect
- prev_corr - boolean - did tester get the answer correct last time?
- last_date - the last date of when the flashcard was tested in the daily review. (In the format MM/DD/YY.)
  
>[!IMPORTANT]
>Last 3 columns must always be correct, incorrect, prev_corr, and last_date. (In that order.)

>[!NOTE]
>By default, the program assumes that there are column names. Thus, the first row will not be tested.

## Adapting the Code
In the code, update the file name to the desired CSV file name ```fc_csv_name = '<filename>.csv'```.

If there are more than 2 sides to the flashcards, the sides that show up on the front and back of the flashcards can be adjusted by changing the lists ```fc_front``` and ```fc_back```.
The list of integers are the indexes for the columns in the CSV file.

```
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
```

> [!IMPORTANT]
> Unlike the prior simple verison, the flashcard CSV file name is a variable, so only the variable ```fc_csv_name``` needs to be updated.

## Buttons and Hot Keys
While the user can use their mouse to click on the buttons and flashcards to select options and flip flashcards, the program also supports the following hot keys:
- On the Home Page:
  - 1 - Test All flashcards
  - 2 - Daily Review
- When testing flashcards:
  - f - Incorrect
  - j - Correct
  - b - Back
  - space bar - Flip Flashcard

## Printing Text
One main difference between the previous versions and this pygame version is that printing text on new lines is not as straightforward.
The ```blit_text()``` function takes in the surface to print text onto and the index of the flashcard to be shown.
It then determines which side of the flashcard needs to be shown via the global boolean variable ```show_front```.
Then for each line (which represents a "side" of the flashcard), the text is printed and centered on the x-axis on the flashcard. 
The y-position of each line of text is also calculated so that the text on the flashcard is centered on the y-axis on the flashcard.
In the event that a "side" of the flashcard does not exist, nothing is printed.

```
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
```

## Button Class
As there were many buttons in this project, a Button Class was created.
The button class has many variables and a consistent button size.
By default, the button will present itself using the defined ```draw()``` function.
In the case that the user hovers their mouse over a button, the button will present itself using the defined ```hover_draw()``` function. 
This function changes the button so that the button is outlined rather than filled, and the text on the button is the same color as the outline. 
However, for ease of reading, if the button background color is close to the background color, the text on the button will remain the same as it is in the ```draw()``` function.

```
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
```
