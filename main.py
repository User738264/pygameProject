import csv
import math
from random import randint

import pygame

from settings import *

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 50)
my_font_smaller = pygame.font.SysFont('Comic Sans MS', 30)

screen_menu = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
player_sprite_group = pygame.sprite.Group()
enemys_sprite_group = pygame.sprite.Group()
enemys_sprite_group_level_1 = pygame.sprite.Group()
enemys_sprite_group_level_2 = pygame.sprite.Group()
buttons_sprite_group = pygame.sprite.Group()
weapons_select_buttons_sprite_group = pygame.sprite.Group()
level_select_buttons_sprite_group = pygame.sprite.Group()
end_level_button_sprite_group = pygame.sprite.Group()
bullets_sprite_group = pygame.sprite.Group()

star = ''
door = ''
level_completed = False
TILE_TYPES = 20
TILE_SIZE = 50
screen_scroll = 0
vertical_scroll = 0
img_list = []
night_img_list = []

bg = pygame.image.load("sprites/bg/1.jpg")
rect = bg.get_rect()
rect.y -= 370

bg2 = pygame.image.load("sprites/bg/4.png")
bg2 = pygame.transform.scale(bg2, (bg2.get_width() * 1, bg2.get_height() * 1))
rect2 = bg2.get_rect()
rect2.y -= 400

bg3 = pygame.image.load("sprites/bg/3.jpg")
bg3 = pygame.transform.scale(bg3, (bg3.get_width() * 1, bg3.get_height() * 1))
rect3 = bg3.get_rect()

for x in range(TILE_TYPES):
    img = pygame.image.load(f'tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
for x in range(13):
    img = pygame.image.load(f'tile_night/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    night_img_list.append(img)


class Health_bar():
    def __init__(self, x, y, h, mh):
        self.x = x
        self.y = y
        self.health = h
        self.max_health = mh

    def draw(self, health, max_health):
        current_health = health / max_health
        pygame.draw.rect(screen_menu, (255, 0, 0), (self.x, self.y, 200, 30))
        pygame.draw.rect(screen_menu, (0, 255, 0), (self.x, self.y, 200 * current_health, 30))


class Slime_king(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = 3000
        self.max_health = 3000
        self.speed = 10
        self.flip = False
        self.jump = False
        self.in_air = False
        self.vel_y = 0
        scale = 2
        img1 = pygame.image.load(f'sprites/slime_king/1.png')
        img2 = pygame.image.load(f'sprites/slime_king/2.png')
        img3 = pygame.image.load(f'sprites/slime_king/phase2/1.png')
        img4 = pygame.image.load(f'sprites/slime_king/phase2/2.png')
        self.sprites_dict = {
            'idle': [pygame.transform.scale(img1, (img1.get_width() * 2, img1.get_height() * 2)), pygame.transform.scale(img2, (img2.get_width() * 2, img2.get_height() * 2))],
            'jump': [pygame.transform.scale(img1, (img1.get_width() * 2, img1.get_height() * 2))],
            'death_2': [pygame.transform.scale(pygame.image.load(f'sprites/slime_king/death/{i}.png'), (
            pygame.image.load(f'sprites/slime_king/death/{i}.png').get_width() * scale,
            pygame.image.load(f'sprites/slime_king/death/{i}.png').get_height() * scale)) for i in range(1, 6)],
            'idle_2': [pygame.transform.scale(img3, (img1.get_width() * 2, img3.get_height() * 2)),
                     pygame.transform.scale(img4, (img2.get_width() * 2, img4.get_height() * 2))],
            'jump_2': [pygame.transform.scale(img3, (img1.get_width() * 2, img3.get_height() * 2))],
        }

        self.sprite_change = pygame.time.get_ticks()
        self.jump_cooldown = pygame.time.get_ticks()
        self.frame = 0
        self.direction = randint(0, 1)
        self.act = 'idle'
        self.img = self.sprites_dict[self.act][self.frame]
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.moving_left, self.moving_right, self.moving_down = False, False, True
        self.width = self.img.get_width()
        self.height = self.img.get_height() - 1
        self.attack_range = (10, 20)
        self.already_taked_damage = False
        self.dx_bounce = 0
        self.direction_bounce = 1
        self.mask = pygame.mask.from_surface(self.img)
        self.jump_number = 0
        self.bounce_len = 0
        self.phase = ''
        self.shoot_cooldown = pygame.time.get_ticks()
        self.after_death = 0

    def __str__(self):
        return 'slime'

    def move(self, player_x, player_y):
        global bullets
        dx = 0
        dy = 0
        if self.alive:
            if self.jump_number == 3 and self.phase == '':
                self.spawn_attack()
                self.jump_number += 1
                return
            elif self.jump_number == 4 and self.phase == '':
                self.dash_attack()
                self.jump_number = 0
                self.jump_cooldown = pygame.time.get_ticks()
                return
            elif self.phase == '_2' and pygame.time.get_ticks() - self.shoot_cooldown > 1200:
                self.shoot_cooldown = pygame.time.get_ticks()
                bullets.append(
                    Bullet(self.rect.centerx, self.rect.centery, 1, 10, 10, 20, 'sprites/weapon/bullet/2.png',
                           enemy=True))
            elif self.phase == '_2' and self.jump_number % 3 == 0:
                self.jump_number += 1
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, 1, 5, 10, 20, 'sprites/weapon/bullet/2.png',
                                      enemy=True, sx=1))
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, 1, 5, 10, 20, 'sprites/weapon/bullet/2.png',
                                      enemy=True, sx=-1))
            elif self.phase == '_2' and self.jump_number == 9:
                self.jump_number = 0
                self.spawn_attack()
            if self.jump:
                pass
            elif not self.jump:
                if pygame.time.get_ticks() - self.jump_cooldown > 2750:
                    self.jump_cooldown = pygame.time.get_ticks()
                    self.jump = True
                    if player.rect.centerx > self.rect.centerx:
                        self.direction = 1
                    else:
                        self.direction = 0
                    if player.rect.bottom < self.rect.centery:
                        self.jump = False
                        self.vel_y -= 30
                        self.moving_down = False
                    else:
                        self.moving_down = True
                    self.jump_number += 1

            if self.direction == 0:
                self.moving_left = True
            else:
                self.moving_right = True

            if self.moving_left and self.jump:
                dx = -self.speed
                self.act = 'idle'
            if self.moving_right and self.jump:
                dx = self.speed
                self.act = 'idle'
            if self.jump and not self.in_air:
                self.in_air = True
                self.vel_y -= 20

            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False
            for platform in world.platforms_sprite_group:
                if pygame.sprite.collide_mask(self, platform) and not self.moving_down and self.health > 0:
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False
            self.rect.x += dx
            self.rect.y += dy
        else:
            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                        self.moving_down = False
                if tile[1].colliderect(self.rect.x, self.rect.y + 25, self.width, self.height):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False
            self.rect.x += dx
            self.rect.y += dy

    def update_animation(self):
        speed_animation = 150
        if self.alive:
            if pygame.time.get_ticks() - self.sprite_change > speed_animation:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            if self.frame >= len(self.sprites_dict[self.act + self.phase]):
                self.frame = 0
        else:
            if pygame.time.get_ticks() - self.sprite_change > speed_animation and self.frame < len(
                    self.sprites_dict[self.act + self.phase]) - 1:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.sprite_change > speed_animation:
                self.after_death += 1
                self.sprite_change = pygame.time.get_ticks()

    def hit_bounce(self):
        if self.dx_bounce > 0:
            for tile in world.obstacle_list:
                # check collision in the x direction
                if tile[1].colliderect(self.rect.x + (self.dx_bounce + 20) * self.direction_bounce, self.rect.y,
                                       self.width, self.height):
                    self.dx_bounce = 0
                    return
            if self.bounce_len != 50:
                self.rect.x += self.dx_bounce * self.direction_bounce
                self.bounce_len += 1
                return
            else:
                self.dx_bounce = 0
                self.bounce_len = 0

    def draw(self, screen):
        global kill_count
        screen.blit(pygame.transform.flip(self.sprites_dict[self.act + self.phase][self.frame], self.flip, False), self.rect)
        if self.alive:
            current_health = self.health / self.max_health
            pygame.draw.rect(screen, (255, 0, 0), (150, 750, 700, 30))
            pygame.draw.rect(screen, (0, 255, 0), (150, 750, 700 * current_health, 30))
            if self.health <= 0:
                self.alive = False
                self.act = 'death'
                self.rect.y -= 40
                self.height -= 26
                kill_count += 1

    def spawn_attack(self):
        for i in range(randint(1, 3)):
            slime = Slime(self.rect.x + 240 * i, self.rect.y, color='purple')
            enemys_sprite_group.add(slime)

    def dash_attack(self):
        self.dx_bounce = 7

    def update(self, screen):
        global level_completed
        self.move(player.rect.x, player.rect.y)
        self.update_animation()
        self.hit_bounce()
        self.draw(screen)
        if self.health < 1200 and self.phase != '_2':
            self.phase = '_2'
            self.speed = 12
            self.jump_number = 0
        if self.after_death > 10:
            level_completed = True


class Slime(pygame.sprite.Sprite):
    def __init__(self, x, y, color='blue'):
        pygame.sprite.Sprite.__init__(self)
        h_scale = 0
        if color == 'blue':
            pass
        elif color == 'purple':
            h_scale = 20
        self.color = color
        self.alive = True
        self.health = 80 + h_scale
        self.max_health = 80 + h_scale
        self.speed = 8 + h_scale // 10
        self.flip = False
        self.jump = False
        self.in_air = False
        self.vel_y = 0
        scale = 1 + h_scale // 50
        self.sprites_dict = {
            'idle': [pygame.image.load(f'sprites/slime_{self.color}/1.png'), pygame.image.load(f'sprites/slime_{self.color}/2.png')],
            'jump': [pygame.image.load(f'sprites/slime_{self.color}/1.png')],
            'death': [pygame.transform.scale(pygame.image.load(f'sprites/slime_{self.color}/death/{i}.png'), (
            pygame.image.load(f'sprites/slime_{self.color}/death/{i}.png').get_width() * scale,
            pygame.image.load(f'sprites/slime_{self.color}/death/{i}.png').get_height() * scale)) for i in range(1, 6)]}

        self.sprite_change = pygame.time.get_ticks()
        self.jump_cooldown = pygame.time.get_ticks()
        self.frame = 0
        self.direction = randint(0, 1)
        self.act = 'idle'
        self.img = self.sprites_dict[self.act][self.frame]
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.moving_left, self.moving_right = False, False
        self.width = self.img.get_width()
        self.height = self.img.get_height() - 1
        self.attack_range = (10, 20)
        self.already_taked_damage = False
        self.dx_bounce = 0
        self.direction_bounce = 1
        self.mask = pygame.mask.from_surface(self.img)
        self.bounce_len = 0
        self.kill_sprite = 0

    def __str__(self):
        return 'slime'

    def move(self, player_x, player_y):
        dx = 0
        dy = 0
        if self.alive:
            if self.jump:
                pass
            elif not self.jump:
                if pygame.time.get_ticks() - self.jump_cooldown > 3000:
                    self.jump_cooldown = pygame.time.get_ticks()
                    self.jump = True
                    self.direction = randint(0, 1)
            '''if abs(player_x - self.rect.x) > 100:
                print(1)
                direction = randint(0, 1)'''

            if self.direction == 0:
                self.moving_left = True
            else:
                self.moving_right = True

            if self.moving_left and self.jump:
                dx = -self.speed
                self.act = 'idle'
            if self.moving_right and self.jump:
                dx = self.speed
                self.act = 'idle'
            if self.jump and not self.in_air:
                self.in_air = True
                self.vel_y -= 16

            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                if tile[1].colliderect(self.rect.x, self.rect.y + dy * 2, self.width, self.height):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False
            for platform in world.platforms_sprite_group:
                if pygame.sprite.collide_mask(self, platform):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False

            self.rect.x += dx
            self.rect.y += dy
        else:
            self.vel_y += 1
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = tile[1].bottom - self.rect.top
                if tile[1].colliderect(self.rect.x, self.rect.y + 25, self.width, self.height):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
                        self.jump = False
                        self.moving_left = False
                        self.moving_right = False
            self.rect.x += dx
            self.rect.y += dy

    def update_animation(self):
        speed_animation = 100
        if self.alive:
            if pygame.time.get_ticks() - self.sprite_change > speed_animation:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            if self.frame >= len(self.sprites_dict[self.act]):
                self.frame = 0
        else:
            if pygame.time.get_ticks() - self.sprite_change > speed_animation and self.frame < len(
                    self.sprites_dict[self.act]) - 1:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()

    def hit_bounce(self):
        if self.dx_bounce > 0:
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + ((self.dx_bounce + 2) * self.direction_bounce), self.rect.y,
                                       self.width, self.height):
                    self.dx_bounce = 0

            if self.bounce_len != 50:
                self.rect.x += self.dx_bounce * self.direction_bounce
                self.bounce_len += 1
                return
            else:
                self.dx_bounce = 0
                self.bounce_len = 0

    def draw(self, screen):
        global kill_count
        if self.alive:
            current_health = self.health / self.max_health
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - 2, self.rect.y + 100, 100, 15))
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x - 2, self.rect.y + 100, 100 * current_health, 15))
            if self.health <= 0:
                self.alive = False
                self.act = 'death'
                self.height *= 0.7
                self.width *= 2
                kill_count += 1
                self.kill_sprite = pygame.time.get_ticks()

        screen.blit(pygame.transform.flip(self.sprites_dict[self.act][self.frame], self.flip, False), self.rect)

    def update(self, screen):
        self.move(player.rect.x, player.rect.y)
        self.update_animation()
        self.hit_bounce()
        self.draw(screen)
        if pygame.time.get_ticks() - self.kill_sprite > 25000 and self.health <= 0:
            enemys_sprite_group.remove(self)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, health, max_health, vel_change=0):
        pygame.sprite.Sprite.__init__(self)
        self.vel_change = vel_change
        self.health = health
        self.max_health = max_health
        self.direction = 1
        self.flip = False
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.moving_down = False
        self.sprites_dict = {}
        self.sprites_list = []
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 0
        for i in range(1, 6):
            img = pygame.image.load(f'sprites/player/run/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.sprites_list.append(img)
        self.sprites_dict['run'] = self.sprites_list
        self.sprites_list = []
        for i in range(1, 4):
            img = pygame.image.load(f'sprites/player/idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.sprites_list.append(img)
        self.sprites_dict['idle'] = self.sprites_list
        self.sprites_dict['air'] = [pygame.transform.scale(pygame.image.load(f'sprites/player/idle/{i}.png'), (
            pygame.image.load(f'sprites/player/idle/{i}.png').get_width() * scale,
            pygame.image.load(f'sprites/player/idle/{i}.png').get_height() * scale))]
        self.act = 'idle'
        self.img = self.sprites_list[self.frame]
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.speed = speed
        self.width = self.img.get_width() - 6
        self.height = self.img.get_height()
        self.add(player_sprite_group)
        self.invulnerability = False
        self.invulnerability_frames = pygame.time.get_ticks()
        self.damage_taken = pygame.time.get_ticks()
        self.sprites_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'sprites/player/run/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            if i % 2 == 1:
                set_color(img, pygame.Color(230, 40, 40))
            self.sprites_list.append(img)
        self.sprites_dict['run_d'] = self.sprites_list
        self.sprites_list = []
        for i in range(1, 4):
            img = pygame.image.load(f'sprites/player/idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            if i % 2 == 1:
                set_color(img, pygame.Color(230, 40, 40))
            self.sprites_list.append(img)
        self.sprites_dict['idle_d'] = self.sprites_list
        self.sprites_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'sprites/player/death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale * 1.5, img.get_height() * scale * 1.5))
            self.sprites_list.append(img)
        self.sprites_dict['death'] = self.sprites_list
        self.mask = pygame.mask.from_surface(self.img)
        self.dash = 0
        self.after_death = 0
        self.start_ticks = pygame.time.get_ticks()
        self.dx_bounce = 0
        self.direction_bounce = 1

    def move(self, moving_left, moving_right, world):
        global star_collected, level_completed
        dx = 0
        dy = 0
        if self.dash > 3:
            self.dash *= 0.9
            dx += self.speed * 2.5 * self.direction
            self.act = 'run'
        elif 1 < self.dash < 3:
            self.dash *= 0.9
            dx += self.speed * 2 * self.direction
            self.act = 'run'
        elif self.dash < 1:
            self.dash = 0
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
                self.act = 'run'
            elif moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1
                self.act = 'run'
            elif self.health > 0:
                self.stop_moving()
        if self.jump and not self.in_air and self.health > 0:
            self.vel_y -= 20 + self.vel_change
            self.jump = False
            self.in_air = True

        if self.health <= 0:
            dx = 0
            dy = 0
            self.act = 'death'
        self.vel_y += 0.7
        if self.vel_y > 15:
            self.vel_y = 15
        dy += self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
            if tile[1].colliderect(self.rect.x, self.rect.y + dy + 2, self.width, self.height):
                if self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = 0
                    self.moving_down = False
        for platform in world.platforms_sprite_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy + 2, self.width, self.height) and not self.moving_down:
                if pygame.sprite.collide_mask(self, platform):
                    if self.vel_y >= 0:
                        self.vel_y = 0
                        self.in_air = False
                        dy = 0
        for tile in world.death:
            if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.after_death = 6
            if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.after_death = 6
            if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                self.after_death = 6

        if pygame.sprite.collide_mask(self, star):
            star_collected = True
        if pygame.sprite.collide_mask(self, door):
            level_completed = True
        self.rect.x += dx
        self.rect.y += dy
        screen_scroll, vertical_scroll = self.update_scroll(dx, dy)
        return screen_scroll, vertical_scroll, dx, dy

    def stop_moving(self):
        self.frame = 0
        self.act = 'idle'

    def update_scroll(self, dx, dy):
        screen_scroll = 0
        vertical_scroll = 0
        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        if self.rect.bottom > 500:
            self.rect.y -= dy
            vertical_scroll = -dy

        if self.rect.top < 300:
            self.rect.y -= dy
            vertical_scroll -= dy

        if self.rect.y > 550:
            self.rect.y = SCREEN_HEIGHT / 2

        return screen_scroll, int(vertical_scroll)

    def update_animation(self):
        speed_animation = 300

        if self.invulnerability and self.act[-2:] != '_d' and self.act != 'death':
            self.act += '_d'
            if self.act == 'air_d':
                self.act = 'idle_d'
        elif self.act[-2:] == '_d' and not self.invulnerability:
            self.act = self.act[:-2]
        if self.health <= 0:
            self.act = 'death'
            self.in_air = False
            speed_animation = 200
        self.img = self.sprites_dict[self.act][self.frame]
        if self.act == 'idle':
            speed_animation = 200
        elif self.act == 'run':
            speed_animation = 100
        if self.in_air:
            self.act = 'air'

        if pygame.time.get_ticks() - self.sprite_change > speed_animation:
            self.frame += 1
            self.sprite_change = pygame.time.get_ticks()
            if (self.act == 'run' or self.act == 'run_d') and self.frame == 1 or self.frame == 4:
                pygame.mixer.Sound(f'sound/step{randint(1, 4)}.mp3').play()

        if self.frame >= len(self.sprites_dict[self.act]) and self.act != 'death':
            self.frame = 0
        elif self.act == 'death' and self.frame == len(self.sprites_dict[self.act]):
            self.frame = len(self.sprites_dict[self.act]) - 1
            self.after_death += 1

    def health_regeneration(self):
        if pygame.time.get_ticks() - self.damage_taken > 7000 and self.max_health > self.health > 0:
            if self.health < self.max_health * 0.3:
                self.health += 0.35
            elif self.health < self.max_health * 0.5:
                self.health += 0.25
            elif self.health < self.max_health * 0.8:
                self.health += 0.15
            else:
                self.health += 0.075

    def take_damage(self, world):
        screen_scroll = 0
        vertical_scroll = 0
        dy = 0
        if self.health < 0:
            return 0, 0
        if self.invulnerability:
            if pygame.time.get_ticks() - self.invulnerability_frames > 2000:
                self.invulnerability = False
                self.invulnerability_frames = pygame.time.get_ticks()
        for i in enemys_sprite_group:
            if pygame.sprite.collide_mask(self, i) and i.alive:
                self.in_air = True
                if not self.invulnerability:
                    pygame.mixer.Sound(f'sound/getting_hit{randint(1, 2)}.mp3').play()
                    self.invulnerability = True
                    self.damage_taken = pygame.time.get_ticks()
                    self.dash = 0
                    if str(i) == 'slime':
                        self.health -= randint(10, 20)
                        if self.health < 0:
                            self.rect.y -= 16
                        self.dx_bounce = 5
                        self.bounce_len = 40
                        self.vel_y -= 5
                        if i.rect.centerx > self.rect.centerx:
                            self.direction_bounce = -1
                        else:
                            self.direction_bounce = 1
        return screen_scroll, vertical_scroll

    def hit_bounce(self):
        if self.dx_bounce > 0:
            for tile in world.obstacle_list:
                if tile[1].colliderect(self.rect.x + ((self.dx_bounce + 2) * self.direction_bounce), self.rect.y,
                                       self.width, self.height):
                    self.dx_bounce = 0

            if self.bounce_len != 50:
                self.rect.x += self.dx_bounce * self.direction_bounce
                self.bounce_len += 1
                screen_scroll = self.update_scroll(self.dx_bounce * self.direction_bounce, 0)
                return screen_scroll[0]
            else:
                self.dx_bounce = 0
                self.bounce_len = 0
        return 0

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)


class Wooden_sword(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.flip = False
        self.angle = 340
        self.scale = scale
        img = pygame.image.load(f'sprites/weapon/wooden_sword/1.png')
        self.img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))

        self.img = pygame.transform.rotate(self.img, 340)
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 0
        self.sprite_list = []
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 1
        self.ATTACK = False
        for i in range(2, 7):
            img = pygame.image.load(f'sprites/weapon/wooden_sword/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            self.sprite_list.append(img)
        self.damage = (20, 30)

    def move(self, x, y):
        self.rect.x = x + 15
        self.rect.y = y + 50

    def attack_animation(self, i_frames):
        if self.ATTACK:
            if i_frames:
                self.frame = 0
                self.ATTACK = False
                return
            if self.frame == 1:
                pygame.mixer.Sound(f'sound/w_d{randint(1, 3)}.mp3').play()
            speed_animation = 75
            self.img = self.sprite_list[self.frame]
            self.rect.y -= 90
            self.rect.x -= 10
            if pygame.time.get_ticks() - self.sprite_change > speed_animation and not i_frames:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            if self.frame >= len(self.sprite_list):
                self.frame = 1
                self.ATTACK = False
                for i in enemys_sprite_group:
                    if i.already_taked_damage:
                        i.already_taked_damage = False

            if self.flip:
                self.rect.x -= 150
            screen_menu.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
            if self.flip:
                self.rect.x += 150
            self.rect.x += 10
            self.rect.y += 90

    def dealing_damage(self, i_frames):
        if self.flip:
            self.rect.x -= 150
        for i in enemys_sprite_group:
            if self.rect.colliderect(i.rect) and self.ATTACK and not i.already_taked_damage and not i_frames:
                i.health -= randint(self.damage[0], self.damage[1])
                i.already_taked_damage = True
                i.dx_bounce = 5
                i.bounce_len = 40
                i.vel_y = -5
                if self.flip:
                    i.direction_bounce = -1
                else:
                    i.direction_bounce = 1
                pygame.mixer.Sound(f'sound/slime_hit{randint(1, 2)}.mp3').play()
        if self.flip:
            self.rect.x += 150

    def draw(self, screen):
        if not self.ATTACK:
            img = pygame.image.load(f'sprites/weapon/wooden_sword/1.png')
            self.img = pygame.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            self.img = pygame.transform.rotate(self.img, self.angle)
            if self.flip:
                self.rect.x -= 45
            screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
            if self.flip:
                self.rect.x += 45


class Magic_sword(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.flip = False
        self.angle = 340
        self.scale = scale
        img = pygame.image.load(f'sprites/weapon/magic_sword/1.png')
        self.img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
        self.img = pygame.transform.rotate(self.img, 340)
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 0
        self.sprite_list = []
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 1
        self.ATTACK = False
        for i in range(2, 6):
            img = pygame.image.load(f'sprites/weapon/magic_sword/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * scale * 1.5, img.get_height() * scale * 1.5))
            self.sprite_list.append(img)
        self.damage = (50, 70)
        self.projectile_cooldown = pygame.time.get_ticks()

    def move(self, x, y):
        self.rect.x = x + 15
        self.rect.y = y + 50

    def attack_animation(self, i_frames):
        if self.ATTACK:
            if i_frames:
                self.frame = 0
                self.ATTACK = False
                return
            if self.frame == 1:
                pygame.mixer.Sound(f'sound/s_w{randint(1, 3)}.mp3').play()
            speed_animation = 120
            self.img = self.sprite_list[self.frame]
            self.rect.y -= 90
            self.rect.x -= 10
            if pygame.time.get_ticks() - self.sprite_change > speed_animation and not i_frames:
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.projectile_cooldown > 500:
                if self.frame == 4 and ((pygame.mouse.get_pos()[0] > self.rect.x and not self.flip) or (pygame.mouse.get_pos()[0] < self.rect.x and self.flip)):
                    if self.flip:
                        bullets.append(Bullet(self.rect.right - self.rect.width * 1.6, self.rect.bottom, 1, 12, 20, 30, 'sprites/weapon/magic_sword/projectile.png'))
                    else:
                        bullets.append(Bullet(self.rect.right, self.rect.bottom, 1, 12, 20, 30,
                                              'sprites/weapon/magic_sword/projectile.png'))
                    self.projectile_cooldown = pygame.time.get_ticks()
            if self.frame >= len(self.sprite_list):
                self.frame = 1
                self.ATTACK = False
                for i in enemys_sprite_group:
                    if i.already_taked_damage:
                        i.already_taked_damage = False

            if self.flip:
                self.rect.x -= self.rect.width
            screen_menu.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
            if self.flip:
                self.rect.x += self.rect.width
            self.rect.x += 10
            self.rect.y += 90

    def dealing_damage(self, i_frames):
        if self.flip:
            self.rect.x -= self.rect.width * 0.8
        for i in enemys_sprite_group:
            if self.rect.colliderect(i.rect) and self.ATTACK and not i.already_taked_damage and not i_frames:
                i.health -= randint(self.damage[0], self.damage[1])
                i.already_taked_damage = True
                i.dx_bounce = 5
                i.bounce_len = 40
                i.vel_y = -5
                pygame.mixer.Sound(f'sound/slime_hit{randint(1, 2)}.mp3').play()
                if self.flip:
                    i.direction_bounce = -1
                else:
                    i.direction_bounce = 1
        if self.flip:
            self.rect.x += self.rect.width * 0.8

    def draw(self, screen):
        if not self.ATTACK:
            img = pygame.image.load(f'sprites/weapon/magic_sword/1.png')
            self.img = pygame.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            self.img = pygame.transform.rotate(self.img, self.angle)
            if self.flip:
                self.rect.x -= self.rect.width * 0.7
            screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
            if self.flip:
                self.rect.x += self.rect.width * 0.7


class Early_gun(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.flip = False
        self.v_flip = False
        self.angle = 340
        self.scale = scale
        img = pygame.image.load(f'sprites/weapon/early_pistol/1.png')
        self.img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
        self.img = pygame.transform.rotate(self.img, 340)
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.frame = 0
        self.sprite_list = []
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 2
        self.ATTACK = False
        for i in range(2, 7):
            img = pygame.image.load(f'sprites/weapon/wooden_sword/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
            self.sprite_list.append(img)
        self.current_player_pos = 0
        self.shot_cooldown = pygame.time.get_ticks()

    def move(self, x, y):
        self.rect.x = x + 15
        self.rect.y = y + 40

    def attack_animation(self, i_frames):
        if pygame.time.get_ticks() - self.shot_cooldown > 600 and not i_frames:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
            self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            if mouse_x < SCREEN_WIDTH / 2:
                self.v_flip = True
                self.angle = 360 - self.angle
            else:
                self.v_flip = False
            bullets.append(Bullet(self.rect.centerx, self.rect.centery, 0.2, 25, 10, 30, 'sprites/weapon/bullet/1.png'))
            self.shot_cooldown = pygame.time.get_ticks()
        else:
            self.ATTACK = False

    def draw(self, screen):
        if not self.ATTACK:
            img = pygame.image.load(f'sprites/weapon/early_pistol/1.png')
            self.img = pygame.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            self.img = pygame.transform.rotate(self.img, 340)
            screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
        else:
            img = pygame.image.load(f'sprites/weapon/early_pistol/{self.frame}.png')
            self.img = pygame.transform.scale(img,
                                              (img.get_width() * self.scale * 2, img.get_height() * self.scale * 2))
            self.img = pygame.transform.rotate(self.img, int(self.angle))

            self.rect = self.img.get_rect(center=self.rect.center)
            screen.blit(pygame.transform.flip(self.img, False, self.v_flip), self.rect)
            if pygame.time.get_ticks() - self.sprite_change > 100:
                if self.frame == 3:
                    pygame.mixer.Sound(f'sound/gunshot{randint(1, 3)}.mp3').play()
                self.frame += 1
                self.sprite_change = pygame.time.get_ticks()
            if self.frame == 4:
                self.frame = 2
                self.ATTACK = False
                self.sprite_change = pygame.time.get_ticks()


class Steam_gun(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.flip = False
        self.v_flip = False
        self.angle = 340
        self.scale = scale
        img = pygame.image.load(f'sprites/weapon/steam_gun/1.png')
        self.img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
        self.img = pygame.transform.rotate(self.img, 340)
        self.rect = self.img.get_rect()
        self.rect.center = x, y
        self.frame = 0
        self.sprite_change = pygame.time.get_ticks()
        self.frame = 2
        self.ATTACK = False
        self.current_player_pos = 0
        self.shot_cooldown = pygame.time.get_ticks()
        self.mouse_pressed = False

    def move(self, x, y):
        self.rect.x = x + 5
        self.rect.y = y + 40

    def attack_animation(self, i_frames):
        if pygame.time.get_ticks() - self.shot_cooldown > 250 and not i_frames:
            pygame.mixer.Sound(f'sound/gunshot{randint(1, 3)}.mp3').play()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
            self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            if mouse_x < SCREEN_WIDTH / 2:
                self.v_flip = True
                self.angle = 360 - self.angle
            else:
                self.v_flip = False
            bullets.append(Bullet(self.rect.centerx, self.rect.centery, 0.2, 25, 15, 20, 'sprites/weapon/bullet/1.png'))
            self.shot_cooldown = pygame.time.get_ticks()

    def draw(self, screen):
        if not self.ATTACK:
            img = pygame.image.load(f'sprites/weapon/steam_gun/1.png')
            self.img = pygame.transform.scale(img, (img.get_width() * self.scale, img.get_height() * self.scale))
            self.img = pygame.transform.rotate(self.img, 340)
            screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
        else:
            img = pygame.image.load(f'sprites/weapon/steam_gun/1.png')
            self.img = pygame.transform.scale(img,
                                              (img.get_width() * self.scale, img.get_height() * self.scale))
            self.img = pygame.transform.rotate(self.img, int(self.angle))

            self.rect = self.img.get_rect(center=self.rect.center)
            screen.blit(pygame.transform.flip(self.img, False, self.v_flip), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, min_damage, max_damage, path, enemy=False, sx=0):
        pygame.sprite.Sprite.__init__(self)
        self.enemy = enemy
        self.pos = (x, y)
        if self.enemy:
            mx, my = player.rect.x, player.rect.y
        else:
            mx, my = pygame.mouse.get_pos()
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = [0, -1]
        else:
            self.dir = [self.dir[0] / length, self.dir[1] / length]
        if sx != 0:
            self.dir = [sx, 0]
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))
        self.bullet = pygame.image.load(path)
        self.bullet = pygame.transform.scale(self.bullet, (self.bullet.get_width() * scale, self.bullet.get_height() * scale))
        self.bullet = pygame.transform.rotate(self.bullet, angle)
        self.speed = speed
        self.add(bullets_sprite_group)
        self.rect = self.bullet.get_rect(center=self.pos)
        self.width = self.bullet.get_width()
        self.height = self.bullet.get_height()
        self.damage = (min_damage, max_damage)
        self.bullet_timer = pygame.time.get_ticks()

    def check_collision(self, dx, dy):
        global bullets
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                bullets.remove(self)
                return
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                bullets.remove(self)
                return
            if tile[1].colliderect(self.rect.x, self.rect.y + dy * 2, self.width, self.height):
                bullets.remove(self)
                return
        for i in enemys_sprite_group:
            if self.rect.colliderect(i.rect) and i.alive and not self.enemy:
                i.health -= randint(self.damage[0], self.damage[1])
                i.dx_bounce = 5
                i.bounce_len = 40
                i.vel_y = -5
                bullets.remove(self)
                if self.rect.x > i.rect.x:
                    i.direction_bounce = -1
                else:
                    i.direction_bounce = 1
                pygame.mixer.Sound(f'sound/slime_hit{randint(1, 2)}.mp3').play()
                return
        if self.rect.colliderect(player.rect) and player.alive and self.enemy:
            player.health -= randint(self.damage[0], self.damage[1])
            #player.dx_bounce = 5
            #player.bounce_len = 40
            #player.vel_y = -5
            bullets.remove(self)
        if pygame.time.get_ticks() - self.bullet_timer > 10000:
            bullets.remove(self)

    def update(self, scroll, vscroll):
        self.check_collision(self.dir[0] * self.speed, self.dir[1] * self.speed)
        self.pos = (self.pos[0] + self.dir[0] * self.speed + scroll,
                    self.pos[1] + self.dir[1] * self.speed + vscroll)

    def draw(self, screen):
        self.rect = self.bullet.get_rect(center=self.pos)
        screen.blit(self.bullet, self.rect)


class Game_obj(pygame.sprite.Sprite):
    def __init__(self, tile_data, star=False, door=False):
        pygame.sprite.Sprite.__init__(self)
        if star:
            self.img = pygame.image.load('tile/12.png')
        elif door:
            self.img = pygame.image.load('sprites/door/1.png')
        else:
            self.img = tile_data[0]
        self.rect = tile_data[1]
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        screen_menu.blit(self.img, self.rect)


class World():
    def __init__(self, night=False):
        self.obstacle_list = []
        self.decoration = []
        self.platforms_sprite_group = pygame.sprite.Group()
        self.death = []
        self.night = night

    def process_data(self, data):
        self.level_length = len(data[0])
        if not self.night:
            for y, row in enumerate(data):
                for x, tile in enumerate(row):
                    if tile >= 0:
                        img = img_list[tile]
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE - 5 * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)
                        if 0 <= tile <= 8 and tile != 4:
                            self.obstacle_list.append(tile_data)
                        elif tile == 4:
                            self.decoration.append(tile_data)
                        elif 9 <= tile <= 11:
                            p = Game_obj(tile_data)
                            self.platforms_sprite_group.add(p)
                        elif tile == 13:
                            self.death.append(tile_data)
                        elif tile == 16:
                            Slime(img_rect.x, img_rect.y)
        else:
            for y, row in enumerate(data):
                for x, tile in enumerate(row):
                    if tile >= 0:
                        img = night_img_list[tile]
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)
                        if 0 <= tile <= 8 and tile != 4:
                            self.obstacle_list.append(tile_data)
                        elif tile == 4:
                            self.decoration.append(tile_data)
                        elif 9 <= tile <= 11:
                            p = Game_obj(tile_data)
                            self.platforms_sprite_group.add(p)
                        elif tile == 16:
                            Slime(img_rect.x, img_rect.y)

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            tile[1][1] += vertical_scroll
            screen_menu.blit(tile[0], tile[1])
        for tile in self.decoration:
            tile[1][0] += screen_scroll
            tile[1][1] += vertical_scroll
            screen_menu.blit(tile[0], tile[1])
        for tile in self.platforms_sprite_group:
            tile.rect.x += screen_scroll
            tile.rect.y += vertical_scroll
            screen_menu.blit(tile.img, tile.rect)
        for tile in self.death:
            tile[1][0] += screen_scroll
            tile[1][1] += vertical_scroll
            screen_menu.blit(tile[0], tile[1])
        for enemy in enemys_sprite_group:
            enemy.rect.x += screen_scroll
            enemy.rect.y += vertical_scroll
        star.rect.x += screen_scroll
        star.rect.y += vertical_scroll
        door.rect.x += screen_scroll
        door.rect.y += vertical_scroll


class Button(pygame.sprite.Sprite):
    def __init__(self, img_path, scale, x, y, level=None):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        self.img_path = img_path
        self.level = level
        self.button_click = False
        self.button = pygame.image.load(f"{self.img_path}/1.png")
        self.button = pygame.transform.scale(self.button, (self.button.get_width() * self.scale, self.button.get_height() * self.scale))
        self.rect = self.button.get_rect()
        self.add(buttons_sprite_group)
        self.rect.x, self.rect.y = x, y
        self.frame = 1
        self.sprite_change = pygame.time.get_ticks()
        self.ticks = 0
        self.weapon_select = False
        self.level_select = False

    def __str__(self):
        return self.level

    def mouse_on_button(self):
        self.button = pygame.image.load(f"{self.img_path}/2.png")
        self.button = pygame.transform.scale(self.button, (self.button.get_width() * self.scale, self.button.get_height() * self.scale))
        self.frame = 2

    def mouse_not_on_button(self):
        self.button = pygame.image.load(f"{self.img_path}/1.png")
        self.button = pygame.transform.scale(self.button, (self.button.get_width() * self.scale, self.button.get_height() * self.scale))
        self.frame = 1

    def mouse_click_on_button(self):
        if self.button_click and not self.weapon_select:
            if pygame.time.get_ticks() - self.sprite_change > 75:
                self.sprite_change = pygame.time.get_ticks()
                if self.frame == 2:
                    self.button = pygame.image.load(f"{self.img_path}/3.png")
                    self.button = pygame.transform.scale(self.button, (self.button.get_width() * self.scale,
                                                                       self.button.get_height() * self.scale))
                    self.frame = 3
                else:
                    self.mouse_on_button()
                self.ticks += 1

    def mouse_select_weapon(self):
        if self.weapon_select:
            self.button = pygame.image.load(f"{self.img_path}/3.png")

    def mouse_select_level(self):
        if self.level_select:
            self.button = pygame.image.load(f"{self.img_path}/2.png")
            self.button = pygame.transform.scale(self.button, (self.button.get_width() * self.scale, self.button.get_height() * self.scale))
        elif not self.weapon_select and self.level is not None and self.level not in ('sword', 'gun'):
            self.button = pygame.image.load(f"{self.img_path}/1.png")
            self.button = pygame.transform.scale(self.button, (
            self.button.get_width() * self.scale, self.button.get_height() * self.scale))

    def draw(self):
        self.mouse_select_weapon()
        self.mouse_click_on_button()
        self.mouse_select_level()
        screen_menu.blit(self.button, self.rect)


class Menu(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.bg = pygame.image.load("bg.jpg")
        self.rect = self.bg.get_rect()

    def draw_background_menu(self):
        self.rect.x -= 1
        if self.rect.x == -900:
            self.bg = pygame.image.load("bg.jpg")
            self.rect = self.bg.get_rect()
            self.rect.x = 500
        screen_menu.blit(self.bg, self.rect)
        pygame.draw.polygon(screen_menu, (60, 60, 60),
                            ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT), (SCREEN_WIDTH * 0.5, 0)))


class Level_select(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.bg = pygame.image.load("sprites/bg/2.png")
        self.bg = pygame.transform.scale(self.bg, (self.bg.get_width() * 0.15, self.bg.get_height() * 0.15))
        self.rect = self.bg.get_rect()
        self.width = self.bg.get_width()
        self.height = self.bg.get_height()

    def draw_background_menu(self):
        for y in range(2):
            for x in range(2):
                screen_menu.blit(self.bg, self.rect)
                self.rect.x += self.width
            self.rect.x -= 2 * self.width
            self.rect.y += self.height
        self.rect.y -= 2 * self.height


def draw_background():
    width = bg.get_width()
    rect.x += screen_scroll * 0.5
    rect.y += vertical_scroll * 0.2
    for x in range(5):
        screen_menu.blit(bg, rect)
        rect.x += width
    rect.x -= 5 * width


def draw_background_2():
    width = bg2.get_width()
    rect2.x += screen_scroll * 0.1
    rect2.y += vertical_scroll * 0.05
    for _ in range(5):
        screen_menu.blit(bg2, rect2)
        rect2.x += width
    rect2.x -= 5 * width


def draw_background_3():
    width = bg3.get_width()
    rect3.x -= width
    rect3.x += screen_scroll * 0.1
    rect3.y += vertical_scroll * 0.05
    for _ in range(5):
        screen_menu.blit(bg3, rect3)
        rect3.x += width
    rect3.x -= 4 * width


def load_data_level_1():
    global screen_scroll, vertical_scroll, player, enemys_sprite_group, world, rect, star, door, level_completed, star_collected
    player = Player(500, 350, 1, 9, 100, 100)
    world = World()
    world.process_data(world_data)
    enemys_sprite_group.empty()
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE - 5 * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                tile_data = (img, img_rect)
                if tile == 12:
                    star = Game_obj(tile_data, star=True)
                elif tile == 14:
                    door = Game_obj(tile_data, door=True)
                if tile == 16:
                    slime = Slime(img_rect.x, img_rect.y)
                    enemys_sprite_group.add(slime)
    rect.x = 0
    rect.y = -370
    level_completed, star_collected = False, False


def load_data_level_2():
    global screen_scroll, vertical_scroll, player, enemys_sprite_group, world, star, door, level_completed, star_collected
    player = Player(500, 350, 1, 12, 200, 200, 4)
    world = World(True)
    world.process_data(world_data2)
    enemys_sprite_group.empty()
    for y, row in enumerate(world_data2):
        for x, tile in enumerate(row):
            if tile >= 0:
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE - 5 * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                tile_data = (img, img_rect)
                if tile == 12:
                    star = Game_obj(tile_data)
                if tile == 16:
                    slime = Slime(img_rect.x, img_rect.y)
                    enemys_sprite_group.add(slime)
    slime_king = Slime_king(1000, 300)
    enemys_sprite_group.add(slime_king)
    img = img_list[14]
    img_rect = img.get_rect()
    img_rect.x = 2000
    img_rect.y = 2000
    tile_data = (img, img_rect)
    door = Game_obj(tile_data, door=True)
    level_completed, star_collected = False, False


def load_data_level_3():
    global screen_scroll, vertical_scroll, player, enemys_sprite_group, world, rect, star, door, level_completed, star_collected
    player = Player(500, 350, 1, 9, 100, 100)
    world = World()
    world.process_data(world_data3)
    enemys_sprite_group.empty()
    for y, row in enumerate(world_data3):
        for x, tile in enumerate(row):
            if tile >= 0:
                img = img_list[tile]
                img_rect = img.get_rect()
                img_rect.x = x * TILE_SIZE - 5 * TILE_SIZE
                img_rect.y = y * TILE_SIZE
                tile_data = (img, img_rect)
                if tile == 12:
                    star = Game_obj(tile_data, star=True)
                elif tile == 14:
                    door = Game_obj(tile_data, door=True)
                elif tile == 16:
                    slime = Slime(img_rect.x, img_rect.y, color='purple')
                    enemys_sprite_group.add(slime)
    rect.x = 0
    rect.y = -370
    level_completed, star_collected = False, False
    vertical_scroll -= 2000


def set_color(img, color):
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            color.a = img.get_at((x, y)).a
            img.set_at((x, y), color)


ROWS, COLS = 20, 300

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
with open(f'level1_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world_data2 = []
for row in range(30):
    r = [-1] * 60
    world_data2.append(r)
with open(f'level2_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data2[x][y] = int(tile)
world_data3 = []
for row in range(120):
    r = [-1] * 120
    world_data3.append(r)
with open(f'level3_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data3[x][y] = int(tile)
world = World()
world.process_data(world_data)
world = World(True)
world.process_data(world_data2)
x, y = 500, 350

player = Player(x, y, 1, 9, 100, 100)
weapon = Early_gun(x + 35, y + 30, 0.5)
health_bar = Health_bar(50, 40, player.health, player.max_health)
moving_left = False
moving_right = False
moving_down = False

running = True

screen = 'menu'
selected_level = 'first_level'
selected_weapon = 'sword'


def deactivate_weapon_select(b):
    for i in weapons_select_buttons_sprite_group:
        if i != b:
            i.weapon_select = False


def deactivate_level_select(b):
    for i in level_select_buttons_sprite_group:
        if i != b:
            i.level_select = False


menu = Menu()
level_select_menu = Level_select()
start_button = Button('sprites/buttons/start_button', 2, 150, 200)
exit_button = Button('sprites/buttons/exit_button', 2, 300, 600)
back_to_menu_button = Button('sprites/buttons/back_button', 1, 60, 650)
start_level_button = Button('sprites/buttons/start_button', 2, 430, 600)
sword_select_button = Button('sprites/buttons/sword_weapon_select', 1, 400 - 46, 50, 'sword')
sword_select_button.add(weapons_select_buttons_sprite_group)
gun_select_button = Button('sprites/buttons/gun_weapon_select', 1, 600 - 46, 50, 'gun')
gun_select_button.add(weapons_select_buttons_sprite_group)
first_level_button = Button('sprites/buttons/first_leveLselect', 2, 60, 250, 'first_level')
first_level_button.add(level_select_buttons_sprite_group)
second_level_button = Button('sprites/buttons/second_level_select', 2, 260, 250, 'second_level')
second_level_button.add(level_select_buttons_sprite_group)
third_level_button = Button('sprites/buttons/third_level_select', 2, 460, 250, 'third_level')
third_level_button.add(level_select_buttons_sprite_group)
back_to_level_select_button = Button('sprites/buttons/back_button', 1, 60, 650)
weapons_for_levels = {'first_levelsword': Wooden_sword(x + 35, y + 30, 1),
                      'first_levelgun': Early_gun(x + 35, y + 30, 0.5),
                      'second_levelsword': Magic_sword(x + 35, y + 30, 1.5),
                      'second_levelgun': Steam_gun(x + 35, y + 30, 1),
                      'third_levelsword': Magic_sword(x + 35, y + 30, 1.5),
                      'third_levelgun': Steam_gun(x + 35, y + 30, 1)}

bullets = []
game_over = ''
timer = 0
kill_count = 0
kill_message = ''
star_collected = False
star_message = ''


def menu_screen(clock, FPS):
    global running, screen
    clock.tick(FPS)
    menu.draw_background_menu()
    start_button.draw()
    exit_button.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.rect.collidepoint(event.pos):
                pygame.mixer.Sound(f'sound/button_pressed.mp3').play()
                if not start_button.button_click:
                    start_button.button_click = True
            if exit_button.rect.collidepoint(event.pos):
                running = False
        if event.type == pygame.MOUSEMOTION:
            if not start_button.button_click:
                if start_button.rect.collidepoint(event.pos):
                    start_button.mouse_on_button()
                else:
                    start_button.mouse_not_on_button()
            if not exit_button.button_click:
                if exit_button.rect.collidepoint(event.pos):
                    exit_button.mouse_on_button()
                else:
                    exit_button.mouse_not_on_button()
    for i in buttons_sprite_group:
        if i.ticks > 8:
            screen = 'level_select'
            i.ticks = 0
            i.button_click = False


def level_select(clock, FPS):
    global running, screen, selected_level, selected_weapon, weapon, screen_scroll, vertical_scroll
    clock.tick(FPS)
    level_select_menu.draw_background_menu()
    start_level_button.draw()
    back_to_menu_button.draw()
    for i in weapons_select_buttons_sprite_group:
        i.draw()
    for i in level_select_buttons_sprite_group:
        i.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in weapons_select_buttons_sprite_group:
                if i.rect.collidepoint(event.pos):
                    pygame.mixer.Sound(f'sound/button_pressed.mp3').play()
                    i.weapon_select = True
                    selected_weapon = str(i)
                    deactivate_weapon_select(i)
            for i in level_select_buttons_sprite_group:
                if i.rect.collidepoint(event.pos):
                    pygame.mixer.Sound(f'sound/button_pressed.mp3').play()
                    i.level_select = True
                    selected_level = str(i)
                    deactivate_level_select(i)
            if start_level_button.rect.collidepoint(event.pos):
                if not start_level_button.button_click:
                    pygame.mixer.Sound(f'sound/button_pressed.mp3').play()
                    start_level_button.button_click = True
            if back_to_menu_button.rect.collidepoint(event.pos):
                if not back_to_menu_button.button_click:
                    pygame.mixer.Sound(f'sound/button_pressed.mp3').play()
                    back_to_menu_button.button_click = True
        if event.type == pygame.MOUSEMOTION:
            for i in weapons_select_buttons_sprite_group:
                if not i.weapon_select:
                    if i.rect.collidepoint(event.pos):
                        i.mouse_on_button()
                    else:
                        i.mouse_not_on_button()
            if not start_level_button.button_click:
                if start_level_button.rect.collidepoint(event.pos):
                    start_level_button.mouse_on_button()
                else:
                    start_level_button.mouse_not_on_button()
            if not back_to_menu_button.button_click:
                if back_to_menu_button.rect.collidepoint(event.pos):
                    back_to_menu_button.mouse_on_button()
                else:
                    back_to_menu_button.mouse_not_on_button()
    if start_level_button.ticks > 6:
        weapon = weapons_for_levels[selected_level + selected_weapon]
        screen = selected_level
        screen_scroll = 0
        vertical_scroll = 0
        if screen == 'first_level':
            load_data_level_1()
        elif screen == 'second_level':
            load_data_level_2()
        elif screen == 'third_level':
            load_data_level_3()
        start_level_button.ticks = 0
        start_level_button.button_click = False
    if back_to_menu_button.ticks > 4:
        screen = 'menu'
        back_to_menu_button.ticks = 0
        back_to_menu_button.button_click = False


def end_level(clock, FPS):
    global running, screen, selected_level, selected_weapon, weapon, screen_scroll, vertical_scroll
    clock.tick(FPS)
    level_select_menu.draw_background_menu()
    back_to_level_select_button.draw()
    screen_menu.blit(game_over, (350, 100))
    screen_menu.blit(timer, (200, 250))
    screen_menu.blit(kill_message, (200, 350))
    screen_menu.blit(star_message, (200, 450))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_to_level_select_button.rect.collidepoint(event.pos):
                if not back_to_level_select_button.button_click:
                    back_to_level_select_button.button_click = True
        if event.type == pygame.MOUSEMOTION:
            if not back_to_level_select_button.button_click:
                if back_to_level_select_button.rect.collidepoint(event.pos):
                    back_to_level_select_button.mouse_on_button()
                else:
                    back_to_level_select_button.mouse_not_on_button()
    if back_to_level_select_button.ticks > 6:
        screen = 'level_select'
        back_to_level_select_button.button_click = False
        back_to_level_select_button.ticks = 0


def check_level_progress():
    global screen, game_over, timer, kill_message, kill_count, star_message
    if player.after_death > 5:
        screen = 'level_end'
        game_over = my_font.render('Игра окончена!', False, (255, 255, 255))
        timer = my_font.render(f'Времени затраченно: {(pygame.time.get_ticks() - player.start_ticks) // 1000} секунд', False, (255, 255, 255))
        kill_message = my_font.render(f'Врагов убито: {kill_count}', False, (255, 255, 255))
        kill_count = 0
        if star_collected:
            star_message = my_font.render(f'Звезда собрана', False, (255, 255, 255))
        else:
            star_message = my_font.render(f'Звезда не собрана', False, (255, 255, 255))
    if level_completed:
        screen = 'level_end'
        game_over = my_font.render('Уровень пройден!', False, (255, 255, 255))
        timer = my_font.render(f'Времени затраченно: {(pygame.time.get_ticks() - player.start_ticks) // 1000} секунд', False, (255, 255, 255))
        kill_message = my_font.render(f'Врагов убито: {kill_count}', False, (255, 255, 255))
        kill_count = 0
        if star_collected:
            star_message = my_font.render(f'Звезда собрана', False, (255, 255, 255))
        else:
            star_message = my_font.render(f'Звезда не собрана', False, (255, 255, 255))


def level1(clock, FPS):
    global screen_scroll, vertical_scroll, moving_left, moving_right, running, screen_menu, screen
    draw_background()
    world.draw()
    clock.tick(FPS)
    if not star_collected:
        star.draw()
    door.draw()
    player.update_animation()
    player.draw(screen_menu)
    if player.health > 0:
        weapon.draw(screen_menu)
    screen_scroll, vertical_scroll, dx, dy = player.move(moving_left, moving_right, world)
    screen_scroll += player.hit_bounce()
    weapon.move(player.rect.x, player.rect.y)
    if selected_weapon == 'sword':
        weapon.attack_animation(player.invulnerability)
        weapon.dealing_damage(player.invulnerability)
    player.health_regeneration()
    scroll = player.take_damage(world)
    screen_scroll += scroll[0]
    vertical_scroll += scroll[1]

    for i in enemys_sprite_group:
        i.update(screen_menu)

    health_bar.draw(player.health, player.max_health)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            weapon.ATTACK = True
            if selected_weapon == 'gun':
                weapon.attack_animation(player.invulnerability)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and player.health > 0:
                moving_left = True
                moving_right = False
                weapon.flip = True
            if event.key == pygame.K_d and player.health > 0:
                moving_right = True
                moving_left = False
                weapon.flip = False
            if event.key == pygame.K_w and not player.in_air:
                player.jump = True
            if event.key == pygame.K_ESCAPE and screen != 'menu':
                screen_scroll = 0
                vertical_scroll = 0
                screen_menu = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                screen = 'level_select'

        if event.type == pygame.KEYUP and player.health > 0:
            if event.key == pygame.K_a:
                moving_left = False
                player.stop_moving()
            if event.key == pygame.K_d:
                moving_right = False
                player.stop_moving()

    for bullet in bullets[:]:
        bullet.update(screen_scroll, vertical_scroll)
    for bullet in bullets:
        bullet.draw(screen_menu)
    check_level_progress()


def level2(clock, FPS):
    global screen_scroll, vertical_scroll, moving_left, moving_right, moving_down, running, screen, screen_menu
    draw_background_2()
    world.draw()
    clock.tick(FPS)
    if not star_collected:
        star.draw()
    player.update_animation()
    player.draw(screen_menu)
    weapon.draw(screen_menu)
    screen_scroll, vertical_scroll, dx, dy = player.move(moving_left, moving_right, world)
    weapon.move(player.rect.x, player.rect.y)
    if selected_weapon == 'sword':
        weapon.attack_animation(player.invulnerability)
        weapon.dealing_damage(player.invulnerability)
    player.health_regeneration()
    scroll = player.take_damage(world)
    screen_scroll += scroll[0]
    vertical_scroll += scroll[1]

    for i in enemys_sprite_group:
        i.update(screen_menu)

    health_bar.draw(player.health, player.max_health)

    if selected_weapon == 'gun':
        if weapon.mouse_pressed:
            weapon.attack_animation(player.invulnerability)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and player.health > 0:
            if event.button == 1:
                weapon.ATTACK = True
                if selected_weapon == 'gun':
                    weapon.mouse_pressed = True

            elif event.button == 3:
                player.dash = 10

        if event.type == pygame.MOUSEBUTTONUP and player.health > 0:
            if event.button == 1:
                if selected_weapon == 'gun':
                    weapon.mouse_pressed = False
                    weapon.ATTACK = False

        if event.type == pygame.KEYDOWN and player.health > 0:
            if event.key == pygame.K_a:
                moving_left = True
                moving_right = False
                weapon.flip = True
            if event.key == pygame.K_d and player.health > 0 and player.health > 0:
                moving_right = True
                moving_left = False
                weapon.flip = False
            if event.key == pygame.K_w and not player.in_air and player.health > 0:
                player.jump = True
            if event.key == pygame.K_s and player.health > 0:
                player.moving_down = True
            if event.key == pygame.K_ESCAPE and screen != 'menu':
                screen_menu = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                screen = 'level_select'

        if event.type == pygame.KEYUP and player.health > 0:
            if event.key == pygame.K_a:
                moving_left = False
                player.stop_moving()
            if event.key == pygame.K_d:
                moving_right = False
                player.stop_moving()

    for bullet in bullets[:]:
        bullet.update(screen_scroll, vertical_scroll)
    for bullet in bullets:
        bullet.draw(screen_menu)
    check_level_progress()


def level3(clock, FPS):
    global screen_scroll, vertical_scroll, moving_left, moving_right, moving_down, running, screen, screen_menu
    draw_background_3()
    world.draw()
    clock.tick(FPS)
    if not star_collected:
        star.draw()
    door.draw()
    player.update_animation()
    player.draw(screen_menu)
    weapon.draw(screen_menu)
    screen_scroll, vertical_scroll, dx, dy = player.move(moving_left, moving_right, world)
    weapon.move(player.rect.x, player.rect.y)
    if selected_weapon == 'sword':
        weapon.attack_animation(player.invulnerability)
        weapon.dealing_damage(player.invulnerability)
    player.health_regeneration()
    scroll = player.take_damage(world)
    screen_scroll += scroll[0]
    vertical_scroll += scroll[1]

    for i in enemys_sprite_group:
        i.update(screen_menu)

    health_bar.draw(player.health, player.max_health)

    if selected_weapon == 'gun':
        if weapon.mouse_pressed:
            weapon.attack_animation(player.invulnerability)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and player.health > 0:
            if event.button == 1:
                weapon.ATTACK = True
                if selected_weapon == 'gun':
                    weapon.mouse_pressed = True

            elif event.button == 3:
                player.dash = 10

        if event.type == pygame.MOUSEBUTTONUP and player.health > 0:
            if event.button == 1:
                if selected_weapon == 'gun':
                    weapon.mouse_pressed = False
                    weapon.ATTACK = False

        if event.type == pygame.KEYDOWN and player.health > 0:
            if event.key == pygame.K_a:
                moving_left = True
                moving_right = False
                weapon.flip = True
            if event.key == pygame.K_d and player.health > 0 and player.health > 0:
                moving_right = True
                moving_left = False
                weapon.flip = False
            if event.key == pygame.K_w and not player.in_air and player.health > 0:
                player.jump = True
            if event.key == pygame.K_s and player.health > 0:
                player.moving_down = True
            if event.key == pygame.K_ESCAPE and screen != 'menu':
                screen_menu = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                screen = 'level_select'

        if event.type == pygame.KEYUP and player.health > 0:
            if event.key == pygame.K_a:
                moving_left = False
                player.stop_moving()
            if event.key == pygame.K_d:
                moving_right = False
                player.stop_moving()

    for bullet in bullets[:]:
        bullet.update(screen_scroll, vertical_scroll)
    for bullet in bullets:
        bullet.draw(screen_menu)
    check_level_progress()


def main():
    global screen_scroll, vertical_scroll, running, screen
    clock = pygame.time.Clock()
    FPS = 60

    while running:
        if screen == 'menu':
            menu_screen(clock, FPS)
        elif screen == 'level_select':
            level_select(clock, FPS)
        elif screen == 'level_end':
            end_level(clock, FPS)
        elif screen == 'first_level':
            level1(clock, FPS)
        elif screen == 'second_level':
            level2(clock, FPS)
        elif screen == 'third_level':
            level3(clock, FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()


if __name__ == '__main__':
    main()
