from pygame import sprite, time


class Tower(sprite.DirtySprite):
    def __init__(self, x, y, image, range_rad, projectile, attack_speed, price, targeting="first"):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.range_rad = range_rad
        self.projectile = projectile  # the projectile class the tower uses (defines the damage and speed)
        self.attack_speed = attack_speed  # in milliseconds
        self.price = price
        self.last_attack = time.get_ticks()  # set initial attack time
        self.targeting = targeting

    def reload(self):
        pass

    def in_range(self, enemy):
        """checks if an enemy is within attack range"""
        return self.rect.centerx - self.range_rad <= enemy.rect.centerx <= self.rect.centerx + self.range_rad and \
            self.rect.centery - self.range_rad <= enemy.rect.centery <= self.rect.centery + self.range_rad

    def attack(self, enemy):
        """attacks the enemy if attack speed cooldown is over"""
        now = time.get_ticks()
        if now - self.last_attack >= self.attack_speed and self.in_range(enemy):
            enemy.health -= self.projectile.damage
            self.last_attack = now  # update last attack time properly

    def sell(self):
        """returns half of the price when selling"""
        return self.price // 2

    def update(self):
        """placeholder update method (useful for animations or cooldown visuals)"""
        pass


class Stack(Tower):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, 50, "stack_projectile", 750, 500, "first")
        self.mag = sprite.LayeredDirty()
        self.mag_size=7
        self.reload(self.mag_size)

    def reload(self, size=7):
        for i in range(size):
            # self.mag.add(self.projectile(self.rect.center_x, self.rect.center_y))
            pass

    def attack(self, enemy):
        super().attack(enemy)
        if len(self.mag) > 0:
            self.mag.remove(self.mag.sprites()[0])
        else:
            time.wait(1500)
            self.reload()

class Queue(Tower):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, 50, "queue_projectile", 1000, 500, "first")
        self.mag = sprite.LayeredDirty()
        self.reload()

    def reload(self, size=7):
        for i in range(size):
            # self.mag.add(self.projectile(self.rect.center_x, self.rect.center_y))
            pass

    def attack(self, enemy):
        super().attack(enemy)
        if len(self.mag) > 0:
            self.mag.remove(self.mag.sprites()[0])
        else:
            time.wait(1500)
            self.reload()