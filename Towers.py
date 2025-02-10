from pygame import sprite, time

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
        super().__init__(x, y, image, 50, "queue_projectile", 1000, 500)
        self.mag = sprite.LayeredDirty()
        self.mag_size = 10
        self.reload()
        self.reload_time = 1200

    def reload(self):
        for _ in range(self.mag_size):
            pass

    def attack(self, enemy):
        super().attack(enemy)
        if len(self.mag) > 0:
            self.mag.remove(self.mag.sprites()[0])
        else:
            time.wait(self.reload_time)
            self.reload()