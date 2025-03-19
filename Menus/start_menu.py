import pygame as pg
import sys
import os
import constants as c
import subprocess

# Initialize pygame
pg.init()

# Constants
WHITE = c.WHITE
BLACK = c.BLACK
GRAY = c.GRAY
GREEN = c.GREEN
RED = c.RED
FONT = pg.font.Font(None, 36)

# Load background image
background_image = pg.image.load(
    r"C:\Programming\ProgrammingOrt\Python\CompileAndConquer\assets\images\Sabrina\Short n Sweet - covers.png")
background_image = pg.transform.scale(background_image, (c.SCREEN_WIDTH_Start, c.SCREEN_HEIGHT_Start))

# Create screen
screen = pg.display.set_mode((c.SCREEN_WIDTH_Start, c.SCREEN_HEIGHT_Start))
pg.display.set_caption("Tower Defence - Start Menu")


# Button class
class Button:
    def __init__(self, text, x, y, width, height, action, setting=None):
        self.text = text
        self.rect = pg.Rect(x, y, width, height)
        self.action = action
        self.setting = setting  # If setting is None, this button won't change color

    def draw(self, surface):
        # Set button color based on whether it has a setting
        if self.setting is not None:
            # Button with a setting (changes color based on setting)
            if self.setting:
                button_color = GREEN  # On (True)
            else:
                button_color = RED  # Off (False)
        else:
            # Button without a setting (defaults to gray)
            button_color = GRAY

        pg.draw.rect(surface, button_color, self.rect, border_radius=10)
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Actions
def start_game():
    print("Starting game...")

    pg.quit()  # Close the start menu before launching the game

    # Change working directory to the correct location before running main.py
    game_dir = r"C:\Programming\ProgrammingOrt\Python\CompileAndConquer"
    os.chdir(game_dir)  # Change directory to where main.py is located

    # Run main.py from the correct directory
    subprocess.run(["python", "main.py"], shell=True)

    sys.exit()


def choose_difficulty():
    print("Choosing difficulty...")
    difficulty_menu()


def open_settings():
    print("Opening settings...")
    # Implement settings screen logic


def exit_game():
    pg.quit()
    sys.exit()


def open_settings():
    settings_menu()


def exit_game():
    pg.quit()
    sys.exit()


def settings_menu():
    settings_running = c.settings_running

    mute_music = c.mute_music
    auto_start = c.auto_start
    sabrina_mode = c.sabrina_mode

    mute_button = Button("Mute Music", 300, 200, 200, 50, lambda: toggle_setting("mute"))
    auto_start_button = Button("Auto-Start", 300, 270, 200, 50, lambda: toggle_setting("auto_start"))
    sabrina_mode_button = Button("Sabrina-Mode", 300, 340, 200, 50, lambda: toggle_setting("sabrina"))
    back_button = Button("Back", 300, 410, 200, 50, lambda: close_settings())

    buttons = [mute_button, auto_start_button, sabrina_mode_button, back_button]

    def toggle_setting(setting):
        nonlocal mute_music, auto_start, sabrina_mode
        if setting == "mute":
            mute_music = not mute_music
            c.MUTE_MUSIC = mute_music  # Update the constant in constants.py
            print(f"Mute Music: {mute_music}")
        elif setting == "auto_start":
            auto_start = not auto_start
            c.auto_start = auto_start
            print(f"Auto-Start: {auto_start}")
        elif setting == "sabrina":
            sabrina_mode = not sabrina_mode
            c.sabrina_mode = sabrina_mode
            print(f"Sabrina Mode: {sabrina_mode}")

    def close_settings():
        nonlocal settings_running
        settings_running = False

    while settings_running:
        screen.fill(WHITE)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                settings_running = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        button.action()

        # Update buttons to reflect changes in settings
        mute_button.setting = mute_music
        auto_start_button.setting = auto_start
        sabrina_mode_button.setting = sabrina_mode

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        pg.display.flip()


def difficulty_menu():
    # Start difficulty screen
    difficulty_running = True

    # Current selected difficulty
    easy_selected = c.DIFFICULTY == 'Easy'
    medium_selected = c.DIFFICULTY == 'Medium'
    hard_selected = c.DIFFICULTY == 'Hard'

    # Buttons for each difficulty
    easy_button = Button("Easy", 300, 200, 200, 50, lambda: select_difficulty('Easy'), easy_selected)
    medium_button = Button("Medium", 300, 270, 200, 50, lambda: select_difficulty('Medium'), medium_selected)
    hard_button = Button("Hard", 300, 340, 200, 50, lambda: select_difficulty('Hard'), hard_selected)
    back_button = Button("Back", 300, 410, 200, 50, lambda: close_difficulty())

    buttons = [easy_button, medium_button, hard_button, back_button]

    def select_difficulty(difficulty):
        nonlocal easy_selected, medium_selected, hard_selected
        c.DIFFICULTY = difficulty
        easy_selected = difficulty == 'Easy'
        medium_selected = difficulty == 'Medium'
        hard_selected = difficulty == 'Hard'
        print(f"Difficulty set to: {difficulty}")

    def close_difficulty():
        nonlocal difficulty_running
        difficulty_running = False

    while difficulty_running:
        screen.fill(WHITE)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                difficulty_running = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        button.action()

        # Update button states
        easy_button.setting = easy_selected
        medium_button.setting = medium_selected
        hard_button.setting = hard_selected

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        pg.display.flip()



# Create buttons
buttons = [
    Button("Start Game", 300, 150, 200, 50, start_game),
    Button("Choose Difficulty", 300, 220, 200, 50, choose_difficulty),
    Button("Settings", 300, 290, 200, 50, open_settings),
    Button("Log In", 300, 360, 200, 50, lambda: print("Log In Clicked")),
    Button("Sign Up", 300, 430, 200, 50, lambda: print("Sign Up Clicked")),
    Button("Exit", 300, 500, 200, 50, exit_game)
]

# Main loop
running = True
while running:
    screen.blit(background_image, (0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button.is_clicked(event.pos):
                    button.action()

    for button in buttons:
        button.draw(screen)

    pg.display.flip()

pg.quit()
