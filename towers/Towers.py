from pygame import sprite, time
from Projectiles import *
class Tower(sprite.DirtySprite):
    def __init__(self, x, y, image, range_rad, projectile, attack_speed, price, targeting="first"):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.range_rad = range_rad
        self.projectile = projectile
        self.attack_speed = attack_speed
        self.price = price
        self.last_attack = time.get_ticks()
        self.targeting = targeting

    def in_range(self, enemy):
        return self.rect.centerx - self.range_rad <= enemy.rect.centerx <= self.rect.centerx + self.range_rad and \
               self.rect.centery - self.range_rad <= enemy.rect.centery <= self.rect.centery + self.range_rad

    def attack(self, enemy):
        now = time.get_ticks()
        if now - self.last_attack >= self.attack_speed and self.in_range(enemy):
            enemy.health -= self.projectile.damage
            self.last_attack = now

    def sell(self):
        return self.price // 2

    def update(self):
        pass

class Stack(Tower):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, 50, "stack_projectile", 750, 500)
        self.mag = sprite.LayeredDirty()
        self.mag_size = 7
        self.reload()
        self.reload_time = 1500

    def reload(self):
        for _ in range(self.mag_size):
            #need to add projectiles to mag
            #need to create projectiles class
            pass

    def attack(self, enemy):
        super().attack(enemy)
        if len(self.mag) > 0:
            self.mag.remove(self.mag.sprites()[0])
        else:
            time.wait(self.reload_time)
            self.reload()


class Queue(Tower):
    def __init__(self, x, y, image):
        # Create base projectile for the queue tower
        base_projectile = Queue_Projectile("base_QueueProjImg", 10, None)  # Placeholder image and damage
        super().__init__(x, y, image, 50, base_projectile, 1000, 500)
        self.mag = sprite.LayeredDirty()  # Magazine to hold projectiles
        self.mag_size = 10  # Size of the magazine
        self.reload_time = 1200
        self.reload()

    def reload(self):
        self.mag.empty()  # Clear the magazine before reloading
        for _ in range(self.mag_size):
            # Create new Queue_Projectile instances for the magazine
            new_proj = Queue_Projectile("queue_proj_img", 10, None)  # Placeholder image and damage
            self.mag.add(new_proj)

    def attack(self, enemy):
        now = time.get_ticks()
        if now - self.last_attack >= self.attack_speed and self.in_range(enemy):
            if len(self.mag) > 0:
                # Fire projectile from the magazine
                projectile = self.mag.sprites()[0]
                projectile.target = enemy  # Assign the enemy as the target
                projectile.pos_x = self.rect.centerx
                projectile.pos_y = self.rect.centery
                projectile.rect.center = (self.rect.centerx, self.rect.centery)

                # Add projectile to game world (you'll need to add it to a sprite group in the main loop)
                self.mag.remove(projectile)  # Remove from magazine after firing

                self.last_attack = now
            else:
                # If magazine is empty, reload
                time.wait(self.reload_time)
                self.reload()
