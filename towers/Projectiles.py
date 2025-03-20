import pygame
from pygame import sprite
import math
import random

class Projectile(sprite.DirtySprite):
    def __init__(self, image, dmg, travel_speed, target, special_ability=None, special_value=None):
        """
        special_ability options:
        - "splash" : special_value -> splash radius
        - "chaining_attacks" : special_value -> number of chains
        - "split_attack" : special_value -> number of splits
        - "arc_projectile" : special_value -> arc height
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.dmg = dmg
        self.travel_speed = travel_speed
        self.target = target
        self.pos_x = self.rect.x
        self.pos_y = self.rect.y
        self.special_ability = special_ability
        self.special_value = special_value  # holds radius, chain count, etc.

    def update(self):
        # move towards target
        if self.target:
            dx = self.target.rect.centerx - self.pos_x
            dy = self.target.rect.centery - self.pos_y
            distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)  # prevent division by zero
            self.pos_x += self.travel_speed * dx / distance
            self.pos_y += self.travel_speed * dy / distance
            self.rect.center = (self.pos_x, self.pos_y)

    def check_collision(self, enemy_group):
        hits = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hits:
            enemy.take_damage(self.dmg)
            self.apply_special(enemy, enemy_group)
            self.kill()  # remove projectile after hit

    def apply_special(self, enemy, enemy_group):
        if self.special_ability == "splash":
            self.apply_splash(enemy_group)
        elif self.special_ability == "chaining_attacks":
            self.apply_chaining(enemy, enemy_group)
        elif self.special_ability == "split_attack":
            self.apply_split(enemy_group)
        elif self.special_ability == "arc_projectile":
            self.apply_arc()

    def apply_splash(self, enemy_group):
        for enemy in enemy_group:
            dist = math.hypot(self.rect.centerx - enemy.rect.centerx,
                              self.rect.centery - enemy.rect.centery)
            if dist <= self.special_value:
                enemy.take_damage(self.dmg // 2)  # splash deals half damage

    def apply_chaining(self, hit_enemy, enemy_group):
        chained = 0
        for enemy in enemy_group:
            if enemy != hit_enemy:
                dist = math.hypot(hit_enemy.rect.centerx - enemy.rect.centerx,
                                  hit_enemy.rect.centery - enemy.rect.centery)
                if dist <= 100:  # chaining range
                    enemy.take_damage(self.dmg // 2)
                    chained += 1
                    if chained >= self.special_value:
                        break

    def apply_split(self, enemy_group):
        # spawns new projectiles in different directions
        for _ in range(self.special_value):
            angle = random.uniform(0, 2 * math.pi)
            new_proj = Projectile(self.image, self.dmg // 2, self.travel_speed,
                                  None, special_ability=None)
            new_proj.pos_x = self.pos_x
            new_proj.pos_y = self.pos_y
            new_proj.rect.center = (self.pos_x, self.pos_y)
            new_proj.target = DummyTarget(self.pos_x + math.cos(angle) * 100,
                                          self.pos_y + math.sin(angle) * 100)
            enemy_group.add(new_proj)

    def apply_arc(self):
        # basic arc effect: adjust y-coordinate for a bounce
        self.pos_y -= math.sin(pygame.time.get_ticks() / 100) * self.special_value


class QueueProjectile(Projectile):
    def __init__(self, img, dmg, travel_speed, target, special_ability=None, special_value=None):
        super().__init__(img, dmg, travel_speed, target, special_ability, special_value)


class Queue_Projectile(Projectile):
    def __init__(self,img,travel_speed,target):
        super().__init__(img,10,travel_speed,target)#place holder values

class DummyTarget:
    """ Helper class for split projectiles to fly in specific directions """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 1, 1)

