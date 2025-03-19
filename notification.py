import pygame as pg
import math

class Notification:
    def __init__(self, text, font, color, duration=1.5, size=(300, 80)):
        self.text = text
        self.font = font
        self.color = color
        self.duration = duration * 1000  # Convert to milliseconds
        self.size = size

        # Animation properties
        self.alpha = 0  # Start fully transparent
        self.y_offset = 0  # For floating effect
        self.active = False
        self.start_time = 0
        self.particles = []

        # Create text surface
        self.font_size = 32
        self.bold_font = pg.font.Font(None, self.font_size)
        self.bold_font.set_bold(True)
        self.text_surf = self.bold_font.render(text.upper(), True, color)
        self.text_rect = self.text_surf.get_rect()

        # Create background surface
        self.bg_surf = pg.Surface(size, pg.SRCALPHA)

        # Optional warning icon (uncomment to use)
        # self.warning_icon = pg.image.load('assets/images/gui/warning.png').convert_alpha()
        # self.warning_icon = pg.transform.scale(self.warning_icon, (32, 32))

        # Sound effect (optional, uncomment to use)
        # self.sound = pg.mixer.Sound('assets/audio/notification.wav')
        # self.sound.set_volume(0.3)

    def show(self):
        self.active = True
        self.start_time = pg.time.get_ticks()
        self.alpha = 0
        self.y_offset = 0
        self.particles = []

        # Play sound (uncomment to use)
        # self.sound.play()

        # Create particles
        for _ in range(15):
            particle = {
                'x': self.size[0] // 2,
                'y': self.size[1] // 2,
                'dx': (math.random() - 0.5) * 3,
                'dy': (math.random() - 0.5) * 3,
                'size': math.random() * 5 + 2,
                'alpha': 255,
                'color': self.color
            }
            self.particles.append(particle)

    def update(self):
        if not self.active:
            return

        current_time = pg.time.get_ticks()
        elapsed = current_time - self.start_time

        # Animation phases: fade in (20%), hold (60%), fade out (20%)
        fade_in_time = self.duration * 0.2
        hold_time = self.duration * 0.6
        fade_out_time = self.duration * 0.2

        if elapsed < fade_in_time:
            # Fade in phase
            progress = elapsed / fade_in_time
            self.alpha = 255 * progress
            self.y_offset = -10 * (1 - progress)
        elif elapsed < fade_in_time + hold_time:
            # Hold phase
            self.alpha = 255
            self.y_offset = 0
        elif elapsed < self.duration:
            # Fade out phase
            progress = (elapsed - fade_in_time - hold_time) / fade_out_time
            self.alpha = 255 * (1 - progress)
            self.y_offset = -10 * progress
        else:
            # Animation complete
            self.active = False

        # Update particles
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['size'] -= 0.1
            particle['alpha'] -= 5

            if particle['size'] <= 0 or particle['alpha'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen, x, y):
        if not self.active:
            return

        # Center position
        center_x = x - self.size[0] // 2
        center_y = y - self.size[1] // 2 + self.y_offset

        # Create a new background surface with current alpha
        bg_surf = pg.Surface(self.size, pg.SRCALPHA)

        # Draw background with rounded corners and border
        border_radius = 12
        border_color = (200, 30, 30, int(self.alpha))
        bg_color = (40, 0, 0, int(self.alpha * 0.8))

        # Main background
        pg.draw.rect(bg_surf, bg_color, (0, 0, self.size[0], self.size[1]),
                     border_radius=border_radius)

        # Border (slightly smaller to keep border inside)
        pg.draw.rect(bg_surf, border_color, (0, 0, self.size[0], self.size[1]),
                     width=2, border_radius=border_radius)

        # Draw particles
        for particle in self.particles:
            pg.draw.circle(bg_surf,
                           (particle['color'][0], particle['color'][1], particle['color'][2], int(particle['alpha'])),
                           (int(particle['x']), int(particle['y'])),
                           int(particle['size']))

        # Create a text surface with current alpha
        text_surf = self.bold_font.render(self.text.upper(), True, self.color)

        # Apply a text shadow for better visibility
        shadow_surf = self.bold_font.render(self.text.upper(), True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.size[0] // 2 + 2, self.size[1] // 2 + 2))

        # Set the alpha for text
        text_surf.set_alpha(int(self.alpha))
        shadow_surf.set_alpha(int(self.alpha * 0.7))

        # Position text in the center of background
        text_rect = text_surf.get_rect(center=(self.size[0] // 2, self.size[1] // 2))

        # Optional: Draw warning icon
        # icon_rect = self.warning_icon.get_rect(midright=(text_rect.left - 10, text_rect.centery))
        # self.warning_icon.set_alpha(int(self.alpha))
        # bg_surf.blit(self.warning_icon, icon_rect)

        # Draw shadow and text
        bg_surf.blit(shadow_surf, shadow_rect)
        bg_surf.blit(text_surf, text_rect)

        # Draw the notification on screen
        screen.blit(bg_surf, (center_x, center_y))

        # Screen shake effect (uncomment to use)
        # if self.alpha > 200:
        #     shake_offset = (random.randint(-3, 3), random.randint(-3, 3))
        #     return shake_offset
        # return (0, 0)