import pygame as pg
import json
from enemy.enemy import Enemy
from world import World
from towers.turret import Turret
from button import Button
import constants as c
import customtkinter as ct
from settings_menu import SettingsMenu





#initialise pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

# Game variables
game_over = False
game_outcome = 0  # -1 is loss & 1 is a win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None
paused = False
auto_start = False

#load images
#map
map_image = pg.image.load('levels/level.png').convert_alpha()
#turret spritesheets
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)
#individual turret image for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
#enemies
enemy_images = {
    "weak": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}
#buttons
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
#gui
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()

#load sounds
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

#load json data for level
with open('levels/level.tmj') as file:
    world_data = json.load(file)

# load fonts for displaying text on the screen (using default font)
text_font = pg.font.Font(None, 24)  # Use None for the default font, no bold argument
large_font = pg.font.Font(None, 36)


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def display_data():
    #draw panel
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
    #display data
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
    screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    #calculate the sequential number of the tile
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    #check if that tile is grass
    if world.tile_map[mouse_tile_num] == 7:
        #check that there isn't already a turret there
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        #if it is a free space then create turret
        if space_is_free == True:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            #deduct cost of turret
            world.money -= c.BUY_COST


def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


def clear_selection():
    for turret in turret_group:
        turret.selected = False

def unpause_game():
    global paused
    paused = False

def restart_game():
    global game_over, level_started, placing_turrets, selected_turret, last_enemy_spawn, world, enemy_group, turret_group
    game_over = False
    level_started = False
    placing_turrets = False
    selected_turret = None
    last_enemy_spawn = pg.time.get_ticks()
    world = World(world_data, map_image)
    world.process_data()
    world.process_enemies()
    enemy_group.empty()
    turret_group.empty()

def exit_to_main_menu():
    global run
    run = False

def toggle_auto_start():
    global auto_start
    auto_start = not auto_start

def apply_grayscale_blur(surface):
    # Convert the screen to grayscale
    grayscale_surface = pg.Surface(surface.get_size())
    grayscale_surface.blit(surface, (0, 0))
    grayscale_array = pg.surfarray.pixels3d(grayscale_surface)
    grayscale_array[:, :, :] = grayscale_array.mean(axis=2, keepdims=True)
    del grayscale_array

    # Apply a blur effect
    grayscale_surface = pg.transform.smoothscale(grayscale_surface, (surface.get_width() // 10, surface.get_height() // 10))
    grayscale_surface = pg.transform.smoothscale(grayscale_surface, surface.get_size())

    return grayscale_surface

#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)
pause_button = Button(c.SCREEN_WIDTH + 50, 350, fast_forward_image, False)

# Add a variable to track the paused state
paused = False



pg.mixer.init()

# Game loop
run = True
while run:

    clock.tick(c.FPS)

    #########################
    # UPDATING SECTION
    #########################


    if not paused and not game_over:
        # Check if player has lost
        if world.health <= 0:
            game_over = True
            game_outcome = -1  # loss
        # Check if player has won
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  # win

        # Update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        # Highlight selected turret
        if selected_turret:
            selected_turret.selected = True

    #########################
    # DRAWING SECTION
    #########################

    # Draw level
    world.draw(screen)

    # Draw groups
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()


    if not game_over:
        # Check if the level has been started or not
        if not level_started:
            if begin_button.draw(screen):
                level_started = True
        else:
            # Draw the pause button
            if pause_button.draw(screen):
                paused = not paused
                if paused:
                    # Create the settings menu
                    settings_menu = SettingsMenu(unpause_game, restart_game, exit_to_main_menu, toggle_auto_start)
                    settings_menu.show()

            if not paused:
                # Fast forward option
                world.game_speed = 1
                if fast_forward_button.draw(screen):
                    world.game_speed = 2
                # Spawn enemies
                if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                    if world.spawned_enemies < len(world.enemy_list):
                        enemy_type = world.enemy_list[world.spawned_enemies]
                        enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                        enemy_group.add(enemy)
                        world.spawned_enemies += 1
                        last_enemy_spawn = pg.time.get_ticks()

                # Check if the wave is finished
                if world.check_level_complete():
                    world.money += c.LEVEL_COMPLETE_REWARD
                    world.level += 1
                    level_started = False
                    last_enemy_spawn = pg.time.get_ticks()
                    world.reset_level()
                    world.process_enemies()

                # Draw buttons
                # Button for placing turrets
                # For the "turret button" show cost of turret and draw the button
                draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
                if turret_button.draw(screen):
                    placing_turrets = True
                # If placing turrets then show the cancel button as well
                if placing_turrets:
                    # Show cursor turret
                    cursor_rect = cursor_turret.get_rect()
                    cursor_pos = pg.mouse.get_pos()
                    cursor_rect.center = cursor_pos
                    if cursor_pos[0] <= c.SCREEN_WIDTH:
                        screen.blit(cursor_turret, cursor_rect)
                    if cancel_button.draw(screen):
                        placing_turrets = False
                # If a turret is selected then show the upgrade button
                if selected_turret:
                    # If a turret can be upgraded then show the upgrade button
                    if selected_turret.upgrade_level < c.TURRET_LEVELS:
                        # Show cost of upgrade and draw the button
                        draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                        if upgrade_button.draw(screen):
                            if world.money >= c.UPGRADE_COST:
                                selected_turret.upgrade()
                                world.money -= c.UPGRADE_COST

            else:
                # Convert the screen to grayscale
                grayscale_surface = apply_grayscale_blur(screen)

                # Draw the grayscale and blurred screen
                screen.blit(grayscale_surface, (0, 0))

                # Draw "PAUSED" text
                draw_text("PAUSED", large_font, "red", c.SCREEN_WIDTH // 2 - 100, c.SCREEN_HEIGHT // 2 - 50)

    else:
        pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius=30)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        # Restart level
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            # Empty groups
            enemy_group.empty()
            turret_group.empty()

    # Event handler
    for event in pg.event.get():
        # Quit program
        if event.type == pg.QUIT:
            run = False
        # Mouse click
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            # Check if mouse is on the game area
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                # Clear selected turrets
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    # Check if there is enough money for a turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

    # Update display
    pg.display.flip()

pg.quit()