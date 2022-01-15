#!/bin/python

import sys
import pygame
import os
import random


def resource_path(relative_path):
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


FPS = 30
W, H = 800, 600  # Ширина и высота окна
FIRE_DELAY = 500
HILLS_DELAY = 2800
FUEL_DELAY = 10000  # как часто падают бочки с топливом
LIVES_DELAY = 50000

SCREEN_TITLE = "PyXenon v0.1 dev"

# цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# инициализация холста
pygame.init()
pygame.display.set_caption(SCREEN_TITLE)
window = pygame.display.set_mode((W, H))

# загрузка графики
game_bg = pygame.image.load(resource_path("images/background.jpg")).convert_alpha()
intro_bg = pygame.image.load(resource_path("images/intro.png")).convert()
menu_bg = pygame.image.load(resource_path("images/menu.png")).convert()
level_fail_bg = pygame.image.load(resource_path("images/red_border.png")).convert_alpha()
game_over_bg = pygame.image.load(resource_path("images/game_over.png")).convert()
level_completed_bg = pygame.image.load(resource_path("images/level_completed.png")).convert_alpha()
game_icon = pygame.image.load(resource_path("images/pyxenon.ico")).convert_alpha()

# загрузка звуков
music = pygame.mixer.Sound(resource_path("sounds/loop.ogg"))
music.set_volume(0.3)
player_crash_sound = pygame.mixer.Sound(resource_path("sounds/player_crash.ogg"))
multikill_sound = pygame.mixer.Sound(resource_path("sounds/multikill.ogg"))
multikill_sound.set_volume(0.3)
doublekill = pygame.mixer.Sound(resource_path("sounds/doublekill.ogg"))
doublekill.set_volume(0.3)
monsterkill = pygame.mixer.Sound(resource_path("sounds/monsterkill.ogg"))
monsterkill.set_volume(0.3)
enemy_crash_sound = pygame.mixer.Sound(resource_path("sounds/crash.ogg"))
enemy_crash_sound.set_volume(0.3)
fire_sound = pygame.mixer.Sound(resource_path("sounds/fire.ogg"))
fuel_beep_sound = pygame.mixer.Sound(resource_path("sounds/fuel_beep.ogg"))
fuel_beep_sound.set_volume(0.1)
got_fuel_sound = pygame.mixer.Sound(resource_path("sounds/got_fuel.ogg"))
got_bonus_sound = pygame.mixer.Sound(resource_path("sounds/got_bonus.ogg"))

# установка первоначальных значений
pygame.display.set_icon(game_icon)
clock = pygame.time.Clock()


class Game:
    """
    В этом классе содержится информация о состоянии игрового процесса
    а также о текушем уровне
    INTRO, PLAYING, GAME_OVER, LEVEL_FAIL, MENU, LEVEL_COMPLETED
    """
    def __init__(self):
        self.state = "INTRO"
        self.fragged_enemies = 0


class Level:
    """
    В этом классе содержится информация о текущем уровне
    """
    def __init__(self):
        self.level = 0
        self.number_of_enemies = 4  # первоначальное кол-во противника
        self.number_of_canons = 2  # первоначальное кол-во пушек
        self.hills_speed = 1  # скорость анимации скал
        self.canons_speed = 1  # скорость анимации пушек
        self.canons_shoot_speed = 3  # скорость выстрела
        self.canons_delay = 6000  # как часто появляется пушка
        self.canons_shoot_delay = 7000 # как часто стреляет пушка
        self.fuel_delay = 5000  # как быстро заканчивается топливо
        self.enemy_delay = 1500  # как часто появляется противник
        self.time = pygame.time.get_ticks()  # фиксация текущего времени

    def check_if_level_completed(self):
        if cur_game.fragged_enemies > self.level * 10 - 1:
            self.number_of_enemies += 1
            self.number_of_canons += 1
            self.canons_shoot_speed += 1
            self.canons_shoot_delay -= 20
            if self.fuel_delay > 100:  # увеличивание скорости расхода топлива
                self.fuel_delay -= 50  # при условии, что не упадет менее чем на 50
            if self.enemy_delay > 200:  # увеличивание скорости появления противника
                self.enemy_delay -= 100  # при условии, что не упадет менее чем на 50
            cur_level.time = pygame.time.get_ticks()  # фиксирование времени
            level_completed()


class CanonBullet(pygame.sprite.Sprite):
    def __init__(self, side, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.side = side
        self.image = pygame.image.load(resource_path("images/canons/%s_canon_bullet.png" % self.side)).convert_alpha()
        self.rect = self.image.get_rect()

        if self.side == "left":
            self.rect.x = x
        else:
            self.rect.x = x - self.rect.width

        self.rect.y = y - self.rect.height / 2
        canon_bullet_sprites.add(self)

    def update(self):
        self.rect.y += cur_level.canons_speed

        if self.side == "left":
            self.rect.x += cur_level.canons_shoot_speed
        else:
            self.rect.x -= cur_level.canons_shoot_speed

        # удалять обьекты за пределами экрана
        if self.rect.x > W or self.rect.x < 0 or self.rect.y > H:
            canon_bullet_sprites.remove(self)


class Canon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        _img_side = random.getrandbits(1)
        if _img_side:
            self.side = "left"
        else:
            self.side = "right"

        self.image = pygame.image.load(resource_path("images/canons/%s.png" % self.side)).convert_alpha()

        self.rect = self.image.get_rect()
        self.last_time = pygame.time.get_ticks()
        self.last_shoot_time = pygame.time.get_ticks()

        if self.side == "left":
            self.rect.x = 1
        else:
            self.rect.x = W - self.rect.width

        self.rect.y = 0 - self.rect.height
        canon_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += cur_level.canons_speed

        if pygame.time.get_ticks() - self.last_shoot_time > cur_level.canons_shoot_delay:
            self.last_shoot_time = pygame.time.get_ticks()
            if self.side == "left":
                canon_bullet_sprites.add(
                    CanonBullet(self.side, self.rect.x + self.rect.width, self.rect.y + self.rect.height / 2))
            else:
                canon_bullet_sprites.add(
                    CanonBullet(self.side, self.rect.x, self.rect.y + self.rect.height / 2))

        # удалять обьекты за пределами экрана
        if self.rect.y > H:
            canon_sprites.remove(self)


class Hill(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        _img_side = random.getrandbits(1)
        if _img_side:
            _side = "l_"
        else:
            _side = "r_"

        _image_number = random.randrange(1, 5)
        self.image = pygame.image.load(resource_path("images/hills/%s%s.png" % (_side, _image_number))).convert_alpha()

        self.rect = self.image.get_rect()
        self.last_time = pygame.time.get_ticks()

        if _side == "l_":
            self.rect.x = 1
        else:
            self.rect.x = W - self.rect.width

        self.rect.y = 0 - self.rect.height
        hill_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += cur_level.hills_speed

        # удалять обьекты вылетевшие за пределы экрана
        if self.rect.y > H:
            hill_sprites.remove(self)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Explosion, self).__init__()
        self.images = []
        self.images.append(pygame.image.load(resource_path("images/boom_1.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_2.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_3.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_3.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_2.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_2.png")).convert_alpha())
        self.images.append(pygame.image.load(resource_path("images/boom_last.png")).convert_alpha())

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
            explosion_sprites.remove(self)
        self.image = self.images[self.index]


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img_number = random.randrange(1, 7)
        self.speed = random.randrange(1, cur_level.level + 2)
        self.image = pygame.image.load(resource_path("images/enemy/%s.png" % self.img_number)).convert_alpha()
        self.rect = self.image.get_rect()
        self.last_time = pygame.time.get_ticks()
        self.rect.x = random.randrange(1, W - self.rect.width)
        self.rect.y = 0 - self.rect.height
        self.directionUpdates = 0

    def update(self):
        _direction = random.getrandbits(1)
        self.directionUpdates = 0
        self.rect.y += self.speed

        # ии полета противника
        if _direction:
            self.rect.x += 1
            if self.rect.x > W - self.rect.width - 160:
                self.rect.x -= 2
        else:
            self.rect.x -= 1
            if self.rect.x < 160:
                self.rect.x += 2
        self.directionUpdates += 1

        if self.rect.x < player.rect.x:
            self.rect.x += 1
        else:
            self.rect.x -= 1

        # удалять обьекты вылетевшие за пределы экрана
        if self.rect.y > H:
            enemy_sprites.remove(self)


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(resource_path("images/bullet.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.y = player.rect.y
        self.last_time = pygame.time.get_ticks()
        # вычисление центра координат откуда появляются пульки
        self.rect.x = player.rect.x + player.rect.width / 2 - self.rect.width / 2 + 1
        bullet_sprites.add(self)

    def update(self):
        self.rect.y -= 10
        _number_of_enemies_before = len(enemy_sprites.sprites())  # проверка сколько противников до попадения
        # проверка попала ли пуля в противника, и если да
        if pygame.sprite.spritecollide(self, enemy_sprites, True):  # удалить противника с поля
            pygame.mixer.Sound.play(enemy_crash_sound)  # проиграть звук взрыва
            explosion_sprites.add(Explosion(self.rect.x - 20, self.rect.y - 40))  # отобразить взрыв
            bullet_sprites.remove(self)  # а так же удалить пулю, попавшую в противника
            _number_of_enemies_fragged = _number_of_enemies_before - len(enemy_sprites.sprites())
            cur_game.fragged_enemies += _number_of_enemies_fragged  # подсчет уничтоженных врагов
            text_score.score += 10 * _number_of_enemies_fragged  # увеличить счет игрока
            play_frag_sound(_number_of_enemies_fragged)

        # проверить не попала ли пуля в топливо и если да,
        if pygame.sprite.spritecollide(self, fuel_sprites, True):  # удалить бочку
            pygame.mixer.Sound.play(player_crash_sound)  # проиграть звук взрыва
            explosion_sprites.add(Explosion(self.rect.x - 20, self.rect.y - 40))  # отобразить взрыв противника
            for enemy in enemy_sprites:
                # вычислить центр спрайта противника на данный момент
                enemy_cx = enemy.rect.x + enemy.image.get_width() / 2
                enemy_cy = enemy.rect.y + enemy.image.get_width() / 2
                if (self.rect.x - 150 < enemy_cx < self.rect.x + 150 and
                        self.rect.y - 150 < enemy_cy < self.rect.y + 150):
                    explosion_sprites.add(Explosion(enemy_cx, enemy_cy))  # отобразить взрыв противника
                    enemy_sprites.remove(enemy)  # удалить противника
            bullet_sprites.remove(self)  # а так же удалить пулю, попавшую в топливо
            # подсчет уничтоженных врагов
            _number_of_enemies_fragged = _number_of_enemies_before - len(enemy_sprites.sprites())
            cur_game.fragged_enemies += _number_of_enemies_fragged
            text_score.score += 10 * _number_of_enemies_fragged  # увеличить счет игрока
            play_frag_sound(_number_of_enemies_fragged)

        if self.rect.y < 0:
            bullet_sprites.remove(self)


class Fuel(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.last_time = pygame.time.get_ticks()
        self.image = pygame.image.load(resource_path("images/fuel.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (35, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(250, W - 250)
        self.rect.y = -30
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += 1

        # удалять обьекты вылетевшие за пределы экрана
        if self.rect.y > H:
            fuel_sprites.remove(self)


class Info(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 70
        self.y = 30
        self.score = 0
        self.font = pygame.font.Font(resource_path("fonts/game_font.ttf"), 20)
        self.last_beep_time = pygame.time.get_ticks()

    def update(self):
        _score_img = self.font.render(str(self.score).zfill(5), True, WHITE)
        window.blit(_score_img, (self.x, self.y))

        _level_img = self.font.render("level: " + str(cur_level.level), True, WHITE)
        window.blit(_level_img, (self.x, self.y + 25))

        _targets_remain = cur_level.level * 10 - cur_game.fragged_enemies
        if _targets_remain < 1:
            _targets_remain = 0

        _targets_to_destroy = self.font.render("targets to destroy: " + str(_targets_remain), True, WHITE)
        window.blit(_targets_to_destroy, (self.x, H - 35))

        if player.fuel >= 60:
            _color = WHITE
        elif player.fuel < 30:
            _color = RED
            if pygame.time.get_ticks() - self.last_beep_time > 650:
                beep()
                self.last_beep_time = pygame.time.get_ticks()
        else:
            _color = YELLOW
            if pygame.time.get_ticks() - self.last_beep_time > 950:
                beep()
                self.last_beep_time = pygame.time.get_ticks()

        if player.fuel <= 0:
            _fuel = 0
            if pygame.time.get_ticks() - self.last_beep_time > 250:
                beep()
                self.last_beep_time = pygame.time.get_ticks()
        else:
            _fuel = player.fuel

        _fuel_img = self.font.render("fuel: " + str(_fuel) + "%", True, _color)
        window.blit(_fuel_img, (self.x, self.y + 50))


class ShowText(pygame.sprite.Sprite):
    def __init__(self, text, font_color, font_size, y_shift):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.y_shift = y_shift
        self.color = font_color
        self.size = font_size
        self.font = pygame.font.Font(resource_path("fonts/game_font.ttf"), self.size)
        self.img = self.font.render(self.text, True, self.color)
        self.rect = self.img.get_rect()
        self.center = self.rect.width / 2

    def show(self):
        window.blit(self.img, (W / 2 - self.center, H / 2 - self.y_shift))


# noinspection PyTypeChecker
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(resource_path("images/rocket.png")).convert_alpha()  # only for collision detection
        self.rocket_img_fire = pygame.image.load(resource_path("images/rocket_fire.png")).convert_alpha()
        self.rocket_img_normal = pygame.image.load(resource_path("images/rocket.png")).convert_alpha()
        self.rocket_img_left = pygame.image.load(resource_path("images/rocket_l.png")).convert_alpha()
        self.rocket_img_right = pygame.image.load(resource_path("images/rocket_r.png")).convert_alpha()
        self.lives_image = pygame.transform.scale(self.rocket_img_normal, (18, 30))
        self.speedAccelerating = 2
        self.speedStopping = 1
        self.speedX = 0
        self.speedY = 0
        self.lives = 3
        self.rect = self.rocket_img_normal.get_rect()
        self.rect.x = W / 2
        self.rect.y = H - 170
        self.fuel = 100
        self.last_fuel_time = pygame.time.get_ticks()

    def reset(self):
        self.speedX = 0
        self.speedY = 0
        self.rect.x = W / 2
        self.rect.y = H - 170

    def update(self):
        keystate = pygame.key.get_pressed()

        # отображаем взрыв ракеты, если она вышла за пределы поля или врезалась в саклы
        if self.rect.x < 0 or \
                self.rect.x > W - 40 or \
                self.rect.y < 0 or \
                self.rect.y > H - 60 or \
                pygame.sprite.spritecollide(self, hill_sprites, False, pygame.sprite.collide_mask) or \
                pygame.sprite.spritecollide(self, canon_bullet_sprites, False) or \
                pygame.sprite.spritecollide(self, enemy_sprites, False):
            explosion_sprites.add(Explosion(self.rect.x, self.rect.y))
            pygame.mixer.Sound.play(player_crash_sound)
            cur_level.time = pygame.time.get_ticks()  # фиксирование времени
            level_fail()
        else:
            # задаем отображение спрайта в зависимости от движения
            if keystate[pygame.K_UP] and keystate[pygame.K_LEFT]:
                if self.fuel > 0:
                    window.blit(self.rocket_img_fire, (self.rect.x, self.rect.y))
                window.blit(self.rocket_img_left, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_UP] and keystate[pygame.K_RIGHT]:
                if self.fuel > 0:
                    window.blit(self.rocket_img_fire, (self.rect.x, self.rect.y))
                window.blit(self.rocket_img_right, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_UP]:
                if self.fuel > 0:
                    window.blit(self.rocket_img_fire, (self.rect.x, self.rect.y))
                window.blit(self.rocket_img_normal, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_DOWN]:
                window.blit(self.rocket_img_normal, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_DOWN] and keystate[pygame.K_RIGHT]:
                window.blit(self.rocket_img_normal, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_DOWN] and keystate[pygame.K_LEFT]:
                window.blit(self.rocket_img_normal, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_LEFT]:
                window.blit(self.rocket_img_left, (self.rect.x, self.rect.y))
            elif keystate[pygame.K_RIGHT]:
                window.blit(self.rocket_img_right, (self.rect.x, self.rect.y))
            else:
                window.blit(self.rocket_img_normal, (self.rect.x, self.rect.y))

            # задаем динамику полета
            if keystate[pygame.K_UP]:
                if self.fuel > 0:
                    self.speedY -= self.speedAccelerating
                    self.fuel -= 1

            if keystate[pygame.K_DOWN]:
                self.speedY += self.speedStopping

            if keystate[pygame.K_LEFT]:
                self.speedX -= self.speedAccelerating
            else:
                if self.speedX < 0:
                    self.speedX += self.speedStopping

            if keystate[pygame.K_RIGHT]:
                self.speedX += self.speedAccelerating
            else:
                if self.speedX > 0:
                    self.speedX -= self.speedStopping

            # если кончилось топливо - ракета начинает падение
            if self.fuel <= 0:
                self.speedY = 2

            # задаем новые координаты ракеты
            self.rect.x += self.speedX
            self.rect.y += self.speedY

            # коректируем координаты в случае, если они выходят за рамки полей
            if self.rect.x < 0:
                self.rect.x = -1
            if self.rect.x + 40 > W:
                self.rect.x = W - 40 + 1
            if self.rect.y < 0:
                self.rect.y = -1
            if self.rect.y + 60 > H:
                self.rect.y = H - 60 + 1

            if keystate[pygame.K_SPACE]:
                if pygame.time.get_ticks() - Bullet.last_time > FIRE_DELAY:
                    Bullet.last_time = pygame.time.get_ticks()
                    bullet_sprites.add(Bullet())
                    pygame.mixer.Sound.play(fire_sound)

        for i in range(0, self.lives - 1):
            window.blit(self.lives_image, (text_score.x + 90 + i * 19, 30))

        # проверка не поймал ли топливо
        if pygame.sprite.spritecollide(self, fuel_sprites, True, pygame.sprite.collide_mask):
            pygame.mixer.Sound.play(got_fuel_sound)
            if player.fuel < 50:
                player.fuel += 50
            else:
                player.fuel = 100

        # проверка не поймал ли бонус в виде жизни
        if pygame.sprite.spritecollide(self, live_sprites, True, pygame.sprite.collide_mask):
            pygame.mixer.Sound.play(got_bonus_sound)
            player.lives += 1


class Live(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.last_time = pygame.time.get_ticks()
        self.image = game_icon
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200, W - 200)
        self.rect.y = -30
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += 5

        # удалять обьекты вылетевшие за пределы экрана
        if self.rect.y > H:
            live_sprites.remove(self)


class Star(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = random.randrange(5, W - 5)
        self.y = 1
        self.img_number = random.randrange(1, 10)
        self.star_img = pygame.image.load(resource_path("images/stars/%s.png" % self.img_number)).convert_alpha()

    def update(self):
        self.y += self.img_number
        window.blit(self.star_img, (self.x, self.y))


def play_frag_sound(num_of_fragged_enemies):
    if num_of_fragged_enemies == 2:
        pygame.mixer.Sound.play(doublekill)
        text_score.score += 30
    elif num_of_fragged_enemies == 3:
        pygame.mixer.Sound.play(multikill_sound)
        text_score.score += 50
    elif num_of_fragged_enemies > 3:
        pygame.mixer.Sound.play(monsterkill)
        text_score.score += 100


def beep():
    if cur_game.state == "PLAYING":
        pygame.mixer.Sound.play(fuel_beep_sound)


def intro():
    window.blit(intro_bg, (0, 0))
    text_press_space.show()


def start_new_level():
    cur_level.level += 1
    cur_game.fragged_enemies = 0
    player.fuel = 100
    player.reset()
    remove_objects()
    Bullet.last_time = pygame.time.get_ticks()
    cur_game.state = "PLAYING"


def level_completed():
    # позволить закончить анимацию взрыва
    window.blit(game_bg, (0, 0))
    explosion_sprites.update()
    explosion_sprites.draw(window)
    pygame.mixer.Sound.stop(music)

    # отображения конца уровня
    window.blit(level_completed_bg, (0, 0))
    if pygame.time.get_ticks() - cur_level.time > 1000:
        text_press_space.show()
    text_score.update()
    cur_game.state = "LEVEL_COMPLETED"


def start_new_game():
    text_score.score = 0
    Live.last_time = pygame.time.get_ticks()
    Fuel.last_time = pygame.time.get_ticks()
    cur_level.number_of_enemies = 4
    cur_level.canons_shoot_speed = 3
    player.lives = 3
    hill_sprites.empty()
    cur_level.level = 0
    start_new_level()


def game_over():
    # позволить закончить анимацию взрыва
    window.blit(game_bg, (0, 0))
    explosion_sprites.update()
    explosion_sprites.draw(window)
    window.blit(game_over_bg, (0, 0))
    if pygame.time.get_ticks() - cur_level.time > 1000:
        text_press_space.show()
    text_score.update()
    cur_game.state = "GAME_OVER"
    pygame.mixer.Sound.stop(music)


def restart_level():
    player.lives -= 1
    player.fuel = 100
    if player.lives < 1:
        game_over()
    else:
        cur_game.state = "PLAYING"
        Bullet.last_time = pygame.time.get_ticks()


def remove_objects():
    for obj in enemy_sprites:
        enemy_sprites.remove(obj)

    for obj in bullet_sprites:
        bullet_sprites.remove(obj)

    for obj in canon_sprites:
        canon_sprites.remove(obj)

    for obj in live_sprites:
        live_sprites.remove(obj)

    for obj in canon_bullet_sprites:
        canon_bullet_sprites.remove(obj)


def level_fail():
    # позволить закончить анимацию взрыва
    window.blit(game_bg, (0, 0))
    explosion_sprites.update()
    explosion_sprites.draw(window)
    pygame.mixer.Sound.stop(music)

    for obj in fuel_sprites:
        fuel_sprites.remove(obj)

    remove_objects()

    Live.last_time = pygame.time.get_ticks()

    if player.lives == 1:
        cur_game.state = "GAME_OVER"
    else:
        window.blit(level_fail_bg, (0, 0))
        text_fail.show()
        if pygame.time.get_ticks() - cur_level.time > 1000:
            text_press_space.show()
        player.reset()
        cur_game.state = "LEVEL_FAIL"


def game():
    window.blit(game_bg, (0, 0))

    # отрисовка звезд
    if len(stars) < 50:
        stars.append(Star())
    for star in stars:
        star.update()
        if star.y > H:
            stars.pop(stars.index(star))  # убираем улетевшее за пределы экрана из массива

    # отрисовка пулек
    bullet_sprites.update()
    bullet_sprites.draw(window)

    # отрисовка противника
    if len(enemy_sprites) < cur_level.number_of_enemies:
        try:
            if pygame.time.get_ticks() - Enemy.last_time > cur_level.enemy_delay:
                Enemy.last_time = pygame.time.get_ticks()
                enemy_sprites.add(Enemy())
        except AttributeError:
            Enemy.last_time = pygame.time.get_ticks()
    enemy_sprites.update()
    enemy_sprites.draw(window)

    # отрисовка скал
    try:
        if pygame.time.get_ticks() - Hill.last_time > HILLS_DELAY:
            Hill.last_time = pygame.time.get_ticks()
            hill_sprites.add(Hill())
    except AttributeError:
        Hill.last_time = pygame.time.get_ticks()
    hill_sprites.update()
    hill_sprites.draw(window)

    player.update()
    text_score.update()

    # отрисовка пушек
    if len(canon_sprites) < cur_level.number_of_canons:
        try:
            if pygame.time.get_ticks() - Canon.last_time > cur_level.canons_delay:
                Canon.last_time = pygame.time.get_ticks()
                canon_sprites.add(Canon())
        except AttributeError:
            Canon.last_time = pygame.time.get_ticks()
    canon_sprites.update()
    canon_sprites.draw(window)

    canon_bullet_sprites.update()
    canon_bullet_sprites.draw(window)

    # уровень топлива
    if pygame.time.get_ticks() - player.last_fuel_time > cur_level.fuel_delay:
        player.fuel -= 10
        player.last_fuel_time = pygame.time.get_ticks()

    # топливные бочки
    if player.fuel < 110:
        try:
            if pygame.time.get_ticks() - Fuel.last_time > FUEL_DELAY:
                Fuel.last_time = pygame.time.get_ticks()
                fuel_sprites.add(Fuel())
        except AttributeError:
            Fuel.last_time = pygame.time.get_ticks()

    fuel_sprites.update()
    fuel_sprites.draw(window)

    # бонус - жизнь
    if player.lives < 2:
        try:
            if pygame.time.get_ticks() - Live.last_time > LIVES_DELAY:
                Live.last_time = pygame.time.get_ticks()
                live_sprites.add(Live())
        except AttributeError:
            Live.last_time = pygame.time.get_ticks()
    elif text_score.score == 1000:
        text_score.score += 100
        live_sprites.add(Live())

    live_sprites.update()
    live_sprites.draw(window)

    # отрисовка анимации взрыва
    explosion_sprites.update()
    explosion_sprites.draw(window)

    cur_level.check_if_level_completed()


def game_menu():
    cur_game.state = "MENU"
    window.blit(menu_bg, (0, 0))
    pygame.mixer.Sound.stop(music)


# инициализация обьектов и групп
cur_game = Game()
cur_level = Level()
player = Player()
stars = []
bullet_sprites = pygame.sprite.Group()
canon_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
hill_sprites = pygame.sprite.Group()
fuel_sprites = pygame.sprite.Group()
live_sprites = pygame.sprite.Group()
explosion_sprites = pygame.sprite.Group()
canon_bullet_sprites = pygame.sprite.Group()

# инициалицация надписей
text_fail = ShowText("-=Crashed=-", RED, 35, 0)
text_press_space = ShowText("Press space to continue...", WHITE, 25, -130)
text_score = Info()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if cur_game.state == "INTRO" and event.key == pygame.K_SPACE:
                if pygame.time.get_ticks() - cur_level.time > 1000:
                    start_new_game()
                    pygame.mixer.Sound.play(music, -1)
            elif cur_game.state == "PLAYING" and event.key == pygame.K_ESCAPE:
                game_menu()
            elif cur_game.state == "MENU" and event.key == pygame.K_ESCAPE:
                cur_game.state = "PLAYING"
                pygame.mixer.Sound.play(music, -1)
            elif cur_game.state == "LEVEL_FAIL" and event.key == pygame.K_SPACE:
                if pygame.time.get_ticks() - cur_level.time > 1000:
                    restart_level()
                    pygame.mixer.Sound.play(music, -1)
            elif cur_game.state == "LEVEL_COMPLETED" and event.key == pygame.K_SPACE:
                if pygame.time.get_ticks() - cur_level.time > 1000:
                    start_new_level()
                    pygame.mixer.Sound.play(music, -1)
            elif cur_game.state == "GAME_OVER" and event.key == pygame.K_SPACE:
                if pygame.time.get_ticks() - cur_level.time > 1000:
                    start_new_game()
                    pygame.mixer.Sound.play(music, -1)

    if cur_game.state == "INTRO":
        intro()

    if cur_game.state == "GAME_OVER":
        game_over()

    if cur_game.state == "LEVEL_FAIL":
        level_fail()

    if cur_game.state == "LEVEL_COMPLETED":
        level_completed()

    if cur_game.state == "PLAYING":
        game()

    if cur_game.state == "MENU":
        game_menu()

    pygame.display.update()
    clock.tick(FPS)

