import customtkinter as ct
import pygame as pg
import json
import sys
import os
import subprocess
from enemy.enemy import Enemy
from world import World
from towers.turret import Turret
from towers.turret_upgrades_data import TURRET_DATA
from button import Button
import constants as c
from Menus.Settings_menu import SettingsMenu
import matplotlib.pyplot as plt
import numpy as np  # for the heat map
import argparse

pg.init()

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        c.mute_music = config.get('mute_music', c.mute_music)
        c.auto_start = config.get('auto_start', c.auto_start)
        c.sabrina_mode = config.get('sabrina_mode', c.sabrina_mode)
        c.DIFFICULTY = config.get('difficulty', c.DIFFICULTY)
except FileNotFoundError:
        c.mute_music = False
        c.auto_start = False
        c.sabrina_mode = False

parser = argparse.ArgumentParser()
parser.add_argument("--mute_music", type=str, default="false")
parser.add_argument("--auto_start", type=str, default="false")
parser.add_argument("--sabrina_mode", type=str, default="false")
args = parser.parse_args()

# Convert string values to booleans
c.mute_music = args.mute_music.lower() == "true"
c.auto_start = args.auto_start.lower() == "true"
c.sabrina_mode = args.sabrina_mode.lower() == "true"

print(c.sabrina_mode, c.auto_start, c.mute_music)

# -------------------------------
total_money_earned = c.MONEY  # starting money
tower_kills = {"Type1": 0, "Type2": 0, "Type3": 0}

money_history = []
enemy_kills_history = []
data_update_interval = 1000  # in milliseconds
last_data_update = pg.time.get_ticks()

# Create clock and game window
clock = pg.time.Clock()
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

# --- Settings Button: Scaled smaller and repositioned ---
settings_button_image = pg.image.load('assets/images/Settings/Settings.jpg').convert_alpha()
settings_button_image = pg.transform.scale(settings_button_image, (40, 40))  # Scale to 40x40
# Place it on the side panel near other buttons (for example, top left of side panel)
settings_button = Button(c.SCREEN_WIDTH + 10, 10, settings_button_image, True)

# CHANGE THIS PIC LATER !!!
# Sell Button (to remove a turret and refund money)
sell_button_image = pg.image.load('assets/images/Settings/Settings.jpg').convert_alpha()
sell_button_image = pg.transform.scale(sell_button_image, (40, 40))
sell_button = Button(c.SCREEN_WIDTH + 5, 230, sell_button_image, True)

# Analytics Button (to display Matplotlib analytics)
analytics_button_image = pg.image.load('assets/images/Settings/Settings.jpg').convert_alpha()
analytics_button_image = pg.transform.scale(analytics_button_image, (40, 40))
analytics_button = Button(c.SCREEN_WIDTH + c.SIDE_PANEL - 50, 10, analytics_button_image, True)

# Game variables
game_over = False
game_outcome = 0  # -1 for loss, 1 for win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None
cursor_range = None
fast_forward = False
insufficient_message = None
paused = False  # Indicates if the game is paused
auto_start = c.auto_start

# Load images
map_image = pg.image.load('levels/level.png').convert_alpha()
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
enemy_images = {
    "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
pause_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()  # Placeholder image

heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()

# Load sounds and level data
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)
with open('levels/level.tmj') as file:
    world_data = json.load(file)
text_font = pg.font.Font(None, 24)
large_font = pg.font.Font(None, 36)

# Music setup
if c.mute_music:
    if c.sabrina_mode:
        pg.mixer.music.load('assets/audio/Sabrina_Music/sabrina carpenter edit audios cause you wrote a pop hit  (timestamps).mp3')  # Your Sabrina song
    else:
        pg.mixer.music.load('assets/audio/Sabrina_Music/sabrina carpenter edit audios cause you wrote a pop hit  (timestamps).mp3')  # Default music

    pg.mixer.music.play(-1)  # Loop indefinitely
    pg.mixer.music.set_volume(0.0 if c.mute_music else 0.5)
else:
    shot_fx.set_volume(0)


# Analytics Function using Matplotlib
def show_analytics():
    # Use the historical data for the graphs:
    if not money_history or not enemy_kills_history:
        print("Not enough data to display analytics yet.")
        return

    # Create a figure with three subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Game Analytics", fontsize=16)

    # Graph: Money earned vs. Enemies killed over time
    axs[0].plot(enemy_kills_history, money_history, marker="o")
    axs[0].set_title("Money Earned vs. Enemies Killed")
    axs[0].set_xlabel("Enemies Killed")
    axs[0].set_ylabel("Money Earned")

    # Heat Map: Characters (dummy data) vs. Area
    # Replace this dummy data with your own if available.
    data = np.random.randint(0, 20, (10, 10))
    cax = axs[1].imshow(data, cmap='hot', interpolation='nearest')
    axs[1].set_title("Heat Map of Characters")
    fig.colorbar(cax, ax=axs[1])

    # Pie Chart: Kills per tower type
    labels = list(tower_kills.keys())
    sizes = list(tower_kills.values())
    if sum(sizes) == 0:
        sizes = [1 for _ in labels]  # Avoid division by zero
    axs[2].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    axs[2].set_title("Kills per Tower Type")

    plt.tight_layout()
    plt.show()


# Function to render text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Function to display the side panel data
def display_data():
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
    screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)


# Create turret at a valid mouse position
def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    if world.tile_map[mouse_tile_num] == 7:
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        if space_is_free:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            world.money -= c.BUY_COST
            # Update total money earned if you treat spending as an "investment"
            global total_money_earned
            total_money_earned -= c.BUY_COST


def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


def clear_selection():
    for turret in turret_group:
        turret.selected = False


def trigger_insufficient_funds_message(duration=1000):
    global insufficient_message
    pos_x = c.SCREEN_WIDTH // 2 - 150
    pos_y = c.SCREEN_HEIGHT // 2 - 20
    insufficient_message = {
        "text": "Insufficient Funds",
        "color": "red",
        "end_time": pg.time.get_ticks() + duration,
        "pos": (pos_x, pos_y)
    }


# Grayscale blur effect for paused state (requires NumPy)
def apply_grayscale_blur(surface):
    grayscale_surface = pg.Surface(surface.get_size())
    grayscale_surface.blit(surface, (0, 0))
    grayscale_array = pg.surfarray.pixels3d(grayscale_surface)
    grayscale_array[:, :, :] = grayscale_array.mean(axis=2, keepdims=True)
    del grayscale_array
    grayscale_surface = pg.transform.smoothscale(grayscale_surface,
                                                 (surface.get_width() // 10, surface.get_height() // 10))
    grayscale_surface = pg.transform.smoothscale(grayscale_surface, surface.get_size())
    return grayscale_surface


# Callback functions for the SettingsMenu
def unpause_game():
    global paused
    paused = False


def restart_game():
    global game_over, level_started, placing_turrets, selected_turret, last_enemy_spawn, world, enemy_group, turret_group, fast_forward, paused
    # Reset paused state to ensure no overlay persists
    paused = False
    game_over = False
    level_started = False
    placing_turrets = False
    selected_turret = None
    fast_forward = False
    last_enemy_spawn = pg.time.get_ticks()
    world = World(world_data, map_image)
    world.process_data()
    world.process_enemies()
    enemy_group.empty()
    turret_group.empty()


import os
import sys
import subprocess
import pygame as pg


def exit_to_main_menu():
    global run
    run = False
    print("returning to main menu game...")
    pg.quit()  # close the start menu before launching the game

    # find the project root dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..','PycharmProjects','CompileAndConquer'))  # Adjusted to locate CompileAndConquer

    # ensure correct case sensitivity for Windows/Linux
    menus_dir = os.path.join(project_root, 'Menus')
    if not os.path.isdir(menus_dir):
        print(f"Error: Menus directory not found at {menus_dir}")
        sys.exit(1)

    main_menu_script = os.path.join(menus_dir, 'start_menu.py')

    if not os.path.isfile(main_menu_script):
        print(f"Error: start_menu.py not found at {main_menu_script}")
        sys.exit(1)

    os.chdir(project_root)
    print(f"current working directory: {os.getcwd()}")
    print(f"contents of the directory: {os.listdir(project_root)}")
    python_executable = sys.executable

    args = [
        python_executable,
        main_menu_script,
        "--mute_music", str(getattr(c, 'mute_music', False)).lower(),
        "--auto_start", str(getattr(c, 'auto_start', False)).lower(),
        "--sabrina_mode", str(getattr(c, 'sabrina_mode', False)).lower(),
    ]

    try:
        result = subprocess.run(args, shell=False, check=True)
        print("start_menu.py started successfully")
    except subprocess.CalledProcessError as e:
        print(f"failed to start start_menu.py return code: {e.returncode}")

    sys.exit()


def toggle_auto_start():
    global auto_start
    auto_start = not auto_start


# Function to open the modal settings menu and pause the game
def open_settings_menu():
    global paused
    paused = True
    # Draw grayscale overlay before opening settings
    grayscale_surface = apply_grayscale_blur(screen)
    screen.blit(grayscale_surface, (0, 0))
    draw_text("PAUSED", large_font, "red", c.SCREEN_WIDTH // 2 - 100, c.SCREEN_HEIGHT // 2 - 50)
    pg.display.flip()
    settings_menu = SettingsMenu(unpause_game, restart_game, exit_to_main_menu, toggle_auto_start)
    settings_menu.show()


# Create world and process it
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

# Create sprite groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# Create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, True)
pause_button = Button(c.SCREEN_WIDTH + 50, 350, pause_image, True)

# Main game loop
run = True
while run:
    clock.tick(c.FPS)

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        # Keybinds for opening settings menu (ESC or P) only when not already paused
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_ESCAPE, pg.K_p) and not paused:
                open_settings_menu()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                    else:
                        trigger_insufficient_funds_message()
                else:
                    selected_turret = select_turret(mouse_pos)

    #########################
    # UPDATING SECTION
    #########################
    if not game_over and not paused:
        if world.health <= 0:
            game_over = True
            game_outcome = -1
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1

        # Update turrets first so damage is applied immediately.
        turret_group.update(enemy_group, world)
        # Then update enemies to check for death.
        enemy_group.update(world)

        if selected_turret:
            selected_turret.selected = True

        if pg.mixer.music.get_volume() > 0 and c.mute_music:
            pg.mixer.music.set_volume(0.0)
        elif pg.mixer.music.get_volume() == 0 and not c.mute_music:
            pg.mixer.music.set_volume(0.5)

    # Update data history every 'data_update_interval' milliseconds
    current_time = pg.time.get_ticks()
    if current_time - last_data_update >= data_update_interval:
        money_history.append(total_money_earned)  # or world.money if you prefer current money
        enemy_kills_history.append(world.killed_enemies)
        last_data_update = current_time

    #########################
    # DRAWING SECTION
    #########################
    world.draw(screen)
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)
    display_data()

    # Always draw the settings button (it now appears in the side panel)
    if settings_button.draw(screen):
        open_settings_menu()

    # Draw the Analytics button and check for click
    if analytics_button.draw(screen):
        show_analytics()

    if not game_over:
        if not level_started and c.auto_start:
            if begin_button.draw(screen):
                level_started = True
        else:
            world.game_speed = 2 if fast_forward else 1
            if fast_forward_button.draw(screen):
                fast_forward = not fast_forward
            if fast_forward:
                draw_text("2x", text_font, "grey100", c.SCREEN_WIDTH + 120, 305)
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        if world.check_level_complete():
            world.money += c.LEVEL_COMPLETE_REWARD
            total_money_earned += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = c.auto_start  # Auto-start next level if enabled
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()
            fast_forward = False

        draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
        if turret_button.draw(screen):
            placing_turrets = True
            range_value = TURRET_DATA[0].get("range")
            cursor_range = pg.Surface((range_value * 2, range_value * 2))
            cursor_range.fill((0, 0, 0))
            cursor_range.set_colorkey((0, 0, 0))
            pg.draw.circle(cursor_range, "grey100", (range_value, range_value), range_value)
            cursor_range.set_alpha(100)

        if placing_turrets:
            cursor_pos = pg.mouse.get_pos()
            cursor_rect = cursor_turret.get_rect(center=cursor_pos)
            valid = False
            if 0 <= cursor_pos[0] <= c.SCREEN_WIDTH and 0 <= cursor_pos[1] <= c.SCREEN_HEIGHT:
                mouse_tile_x = cursor_pos[0] // c.TILE_SIZE
                mouse_tile_y = cursor_pos[1] // c.TILE_SIZE
                if 0 <= mouse_tile_x < c.COLS and 0 <= mouse_tile_y < c.ROWS:
                    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
                    if world.tile_map[mouse_tile_num] == 7:
                        space_free = True
                        for turret in turret_group:
                            if (turret.tile_x, turret.tile_y) == (mouse_tile_x, mouse_tile_y):
                                space_free = False
                                break
                        valid = space_free
            range_color = "grey100" if valid else "red"
            range_value = TURRET_DATA[0].get("range")
            range_surface = pg.Surface((range_value * 2, range_value * 2), pg.SRCALPHA)
            pg.draw.circle(range_surface, range_color, (range_value, range_value), range_value)
            range_surface.set_alpha(100)
            if cursor_pos[0] <= c.SCREEN_WIDTH:
                screen.blit(range_surface, range_surface.get_rect(center=cursor_pos))
                screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
                placing_turrets = False

        if selected_turret:
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST
                    else:
                        trigger_insufficient_funds_message()
            # Sell Button: remove the turret and refund money (e.g., 80% of BUY_COST)
            if sell_button.draw(screen):
                refund_amount = c.BUY_COST * 0.8
                world.money += refund_amount
                total_money_earned += refund_amount  # update money earned if desired
                # Optionally update tower_kills (if the turret had any kills)
                turret_type = "Type" + str(selected_turret.upgrade_level)
                tower_kills[turret_type] += selected_turret.kills
                turret_group.remove(selected_turret)
                selected_turret = None
    else:
        pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        if restart_button.draw(screen):
            restart_game()

    # If the game is paused, draw the grayscale overlay and red "PAUSED" text
    if paused:
        grayscale_surface = apply_grayscale_blur(screen)
        screen.blit(grayscale_surface, (0, 0))
        draw_text("PAUSED", large_font, "red", c.SCREEN_WIDTH // 2 - 100, c.SCREEN_HEIGHT // 2 - 50)

    # Display insufficient funds message if active
    current_time = pg.time.get_ticks()
    if insufficient_message is not None:
        if current_time < insufficient_message["end_time"]:
            draw_text(
                insufficient_message["text"],
                large_font,
                insufficient_message["color"],
                insufficient_message["pos"][0],
                insufficient_message["pos"][1]
            )
        else:
            insufficient_message = None

    pg.display.flip()

pg.quit()
