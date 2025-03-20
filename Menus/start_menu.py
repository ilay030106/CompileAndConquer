import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
import pygame as pg
import sys
import os
import subprocess
import re
import json

# Import tkinter and customtkinter for modal forms.
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import constants as c
from db_connection import initialize_database, get_db_connection, close_database

# Initialize pygame
pg.init()

# Constants
WHITE = c.WHITE
BLACK = c.BLACK
GRAY = c.GRAY
GREEN = c.GREEN
RED = c.RED
FONT = pg.font.Font(None, 36)

button_width = 200
button_height = 50
screen_width = c.SCREEN_WIDTH_Start
screen_height = c.SCREEN_HEIGHT_Start

# Load background image
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, '..', 'assets', 'images', 'Sabrina')
background_image_path = os.path.join(assets_dir, 'Short n Sweet - covers.png')
background_image = pg.image.load(background_image_path)
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
            button_color = GREEN if self.setting else RED
        else:
            button_color = GRAY

        pg.draw.rect(surface, button_color, self.rect, border_radius=10)
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# --- Modal Windows using customtkinter ---

def get_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'config.json')

def save_settings():
    config = {
        'mute_music': c.mute_music,
        'auto_start': c.auto_start,
        'sabrina_mode': c.sabrina_mode,
        'difficulty': c.DIFFICULTY
    }
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f)


def sign_up_window():
    win = ctk.CTk()  # Create a new Tk window for sign up
    win.title("Sign Up")
    win.geometry("400x500")

    # Labels and Entry widgets for each field
    label_title = ctk.CTkLabel(win, text="Sign Up", font=ctk.CTkFont(size=20, weight="bold"))
    label_title.pack(pady=10)

    label_first = ctk.CTkLabel(win, text="First Name:")
    label_first.pack(pady=5)
    entry_first = ctk.CTkEntry(win)
    entry_first.pack(pady=5)

    label_last = ctk.CTkLabel(win, text="Last Name:")
    label_last.pack(pady=5)
    entry_last = ctk.CTkEntry(win)
    entry_last.pack(pady=5)

    label_age = ctk.CTkLabel(win, text="Age:")
    label_age.pack(pady=5)
    entry_age = ctk.CTkEntry(win)
    entry_age.pack(pady=5)

    label_phone = ctk.CTkLabel(win, text="Phone Number (10 digits):")
    label_phone.pack(pady=5)
    entry_phone = ctk.CTkEntry(win)
    entry_phone.pack(pady=5)

    label_email = ctk.CTkLabel(win, text="Email:")
    label_email.pack(pady=5)
    entry_email = ctk.CTkEntry(win)
    entry_email.pack(pady=5)

    label_password = ctk.CTkLabel(win, text="Password:")
    label_password.pack(pady=5)
    entry_password = ctk.CTkEntry(win, show="*")
    entry_password.pack(pady=5)

    def submit_signup():
        first = entry_first.get().strip()
        last = entry_last.get().strip()
        age = entry_age.get().strip()
        phone = entry_phone.get().strip()
        email = entry_email.get().strip()
        password = entry_password.get().strip()

        # Validate first and last names (letters only)
        if not re.fullmatch(r"[A-Za-z]+", first):
            messagebox.showerror("Error", "First name must contain letters only.")
            return
        if not re.fullmatch(r"[A-Za-z]+", last):
            messagebox.showerror("Error", "Last name must contain letters only.")
            return
        # Validate age as a positive integer
        try:
            age_int = int(age)
            if age_int <= 0:
                messagebox.showerror("Error", "Age must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be a positive integer.")
            return
        # Validate phone number (exactly 10 digits)
        if not re.fullmatch(r"\d{10}", phone):
            messagebox.showerror("Error", "Phone number must be exactly 10 digits.")
            return
        # Validate email format
        if not re.fullmatch(r"[\w\.-]+@[\w\.-]+\.\w+", email):
            messagebox.showerror("Error", "Invalid email format.")
            return
        # Validate password (at least one uppercase, one lowercase, minimum 8 characters)
        if not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z]).{8,}", password):
            messagebox.showerror("Error", "Password must have at least one uppercase letter, one lowercase letter, and be at least 8 characters long.")
            return

        # Check if email is already registered
        conn = get_db_connection()
        if conn is None:
            messagebox.showerror("Error", "Database connection error.")
            return
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        if cur.fetchone()[0] > 0:
            messagebox.showerror("Error", "Email is already registered.")
            cur.close()
            conn.close()
            return

        # Insert the new user into the database
        try:
            cur.execute(
                "INSERT INTO users (first_name, last_name, age, phone_number, email, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (first, last, age_int, phone, email, password)
            )
            conn.commit()
            messagebox.showinfo("Success", "Sign up successful!")
            win.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            cur.close()
            conn.close()

    submit_button = ctk.CTkButton(win, text="Submit", command=submit_signup)
    submit_button.pack(pady=20)

    win.mainloop()


def log_in_window():
    win = ctk.CTk()
    win.title("Log In")
    win.geometry("350x250")

    label_title = ctk.CTkLabel(win, text="Log In", font=ctk.CTkFont(size=20, weight="bold"))
    label_title.pack(pady=10)

    label_email = ctk.CTkLabel(win, text="Email:")
    label_email.pack(pady=5)
    entry_email = ctk.CTkEntry(win)
    entry_email.pack(pady=5)

    label_password = ctk.CTkLabel(win, text="Password:")
    label_password.pack(pady=5)
    entry_password = ctk.CTkEntry(win, show="*")
    entry_password.pack(pady=5)

    def submit_login():
        email = entry_email.get().strip()
        password = entry_password.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        conn = get_db_connection()
        if conn is None:
            messagebox.showerror("Error", "Database connection error.")
            return
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            messagebox.showinfo("Success", "Log in successful!")
            win.destroy()
        else:
            messagebox.showerror("Error", "Incorrect email or password.")

    submit_button = ctk.CTkButton(win, text="Log In", command=submit_login)
    submit_button.pack(pady=20)

    win.mainloop()


def display_users_window():
    win = ctk.CTk()
    win.title("Registered Users")
    win.geometry("700x400")

    # Connect to database and fetch all users (excluding password)
    conn = get_db_connection()
    if conn is None:
        messagebox.showerror("Error", "Database connection error.")
        return
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, age, phone_number, email FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Create a frame to hold the treeview
    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a Treeview widget (using ttk)
    tree = ttk.Treeview(frame, columns=("ID", "First Name", "Last Name", "Age", "Phone", "Email"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("First Name", text="First Name")
    tree.heading("Last Name", text="Last Name")
    tree.heading("Age", text="Age")
    tree.heading("Phone", text="Phone")
    tree.heading("Email", text="Email")

    # Insert data into the treeview
    for row in rows:
        tree.insert("", "end", values=row)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    win.mainloop()


# --- Actions for Pygame Menu ---

def start_game():
    print("Starting game...")
    pg.quit()  # Close the start menu before launching the game

    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_dir = os.path.join(script_dir, '..')
    os.chdir(game_dir)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Contents of the directory: {os.listdir(game_dir)}")
    python_executable = sys.executable

    args = [
        python_executable,
        "main.py",
        "--mute_music", str(c.mute_music).lower(),
        "--auto_start", str(c.auto_start).lower(),
        "--sabrina_mode", str(c.sabrina_mode).lower(),
    ]

    result = subprocess.run(args, shell=False)
    if result.returncode != 0:
        print(f"Failed to start main.py. Return code: {result.returncode}")
    else:
        print("main.py started successfully")
    sys.exit()

def choose_difficulty():
    print("Choosing difficulty...")
    difficulty_menu()

def open_settings():
    settings_menu()

def exit_game():
    close_database()  # Close all idle database connections
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
            c.mute_music = mute_music
            print(f"Mute Music: {mute_music}")
        elif setting == "auto_start":
            auto_start = not auto_start
            c.auto_start = auto_start
            print(f"Auto-Start: {auto_start}")
        elif setting == "sabrina":
            sabrina_mode = not sabrina_mode
            c.sabrina_mode = sabrina_mode
            print(f"Sabrina Mode: {sabrina_mode}")
        save_settings()  # Save after each toggle

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

        mute_button.setting = mute_music
        auto_start_button.setting = auto_start
        sabrina_mode_button.setting = sabrina_mode

        for button in buttons:
            button.draw(screen)

        pg.display.flip()

def difficulty_menu():
    difficulty_running = True
    easy_selected = c.DIFFICULTY == 'Easy'
    medium_selected = c.DIFFICULTY == 'Medium'
    hard_selected = c.DIFFICULTY == 'Hard'

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
        save_settings()  # Save after changing difficulty

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

        easy_button.setting = easy_selected
        medium_button.setting = medium_selected
        hard_button.setting = hard_selected

        for button in buttons:
            button.draw(screen)

        pg.display.flip()


# Calculate the starting Y position so that the buttons are centered vertically
start_y = (screen_height - (7 * (button_height + 20))) // 2  # Adjust for spacing

buttons = [
    Button("Start Game", (screen_width - button_width) // 2, start_y, button_width, button_height, start_game),
    Button("Choose Difficulty", (screen_width - button_width) // 2, start_y + (button_height + 20), button_width, button_height, choose_difficulty),
    Button("Settings", (screen_width - button_width) // 2, start_y + 2 * (button_height + 20), button_width, button_height, open_settings),
    Button("Log In", (screen_width - button_width) // 2, start_y + 3 * (button_height + 20), button_width, button_height, log_in_window),
    Button("Sign Up", (screen_width - button_width) // 2, start_y + 4 * (button_height + 20), button_width, button_height, sign_up_window),
    Button("Display Users", (screen_width - button_width) // 2, start_y + 5 * (button_height + 20), button_width, button_height, display_users_window),
    Button("Exit", (screen_width - button_width) // 2, start_y + 6 * (button_height + 20), button_width, button_height, exit_game)
]

# --- Pygame Main Loop ---
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

exit_game()