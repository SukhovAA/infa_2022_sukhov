import math
from random import randint

import pygame as pg


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600
lastTime = 0

class Ball:
    def __init__(self, screen: pg.Surface, x0=40, y0=450):
        """ Конструктор мячей для стрельбы

        x0 - начальное положение мяча по горизонтали
        y0 - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x0
        self.y = y0
        self.r = 10
        self.vx = 0
        self.vy = 0
        a = randint(0, 5)
        self.color = GAME_COLORS[a]
        self.live = 30
        self.time_create = pg.time.get_ticks()

    def move(self):
        """Перемещение мяча на расстояние v*dt а за 1 кадр прорисовки,
        с учётом ускорения свободного падения g и столкновений со стенами
        """
        if self.x + self.r > WIDTH or self.x - self.r < 0:
            self.vx *= -1
        if self.y + self.r > HEIGHT or self.y - self.r < 0:
            self.vy *= -1

        self.vy -= 15 * dt

        self.x += self.vx
        self.y -= self.vy

    def hittest(self, obj):
        """
        Функция для проверки сталкиваний мячей
        """
        return (self.x - obj.x)**2 + (self.y - obj.y)**2 <= (self.r + obj.r)**2

    def draw(self):
        """
        Рисуем мячи
        """
        pg.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.gun_power = 10
        self.gun_on = 0
        self.angle = 1
        self.color = GREY

    def fire_start(self, event):
        self.gun_on = 1

    def fire_end(self, event):
        """Выстрел мячом, скорость мяча зависит от того, как долго удерживалась кнопка мыши
        (Есть шкала заряда пушки)
        """
        global balls
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.angle = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.gun_power * math.cos(self.angle)
        new_ball.vy = - self.gun_power * math.sin(self.angle)
        balls.append(new_ball)
        self.gun_on = 0
        self.gun_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.angle = math.atan((event.pos[1]-450) / (event.pos[0]-40))
        if self.gun_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)
        pg.draw.line(self.screen, BLACK, (40, 450), (40 + cos * 50, 450 + sin * 50), 15)
        pg.draw.circle(self.screen, BLACK, (30, 463), 20)
        pg.draw.rect(self.screen, BLACK, (5, 410, 70, 10), 2)
        pg.draw.rect(self.screen, RED, (5, 410, 0.7*self.gun_power, 10))

    def power_up(self):
        if self.gun_on:
            if self.gun_power < 100:
                self.gun_power += 1
            self.color = RED
        else:
            self.color = GREY


class Target:

    def __init__(self, screen: pg.Surface):
        self.points = 0
        self.screen = screen
        self.new_target()

    def new_target(self):
        """ Создание новой цели. """
        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(2, 50)
        self.vy = randint(-5, 5)
        self.color = RED
        self.live = 1

    def move(self):
        if self.y > HEIGHT - self.r or self.y + self.r < 0:
            self.vy *= -1

        self.y += self.vy


    def draw(self):
        pg.draw.circle(self.screen, self.color, (self.x, self.y), self.r)

    def hit(self):
        """Попадание шарика в цель."""
        self.live = 0



pg.init()
f_score = pg.font.Font(None, 36)
screen = pg.display.set_mode((WIDTH, HEIGHT))
balls = []
targets = []
targets.append(Target(screen))
targets.append(Target(screen))
score = 0
textScore = f_score.render("Счет: " + str(score), True, (0,0,0))

clock = pg.time.Clock()
gun = Gun(screen)
finished = False

while not finished:
    dt = (pg.time.get_ticks() - lastTime)/1000
    lastTime = pg.time.get_ticks()
    screen.fill(WHITE)

    gun.draw()
    screen.blit(textScore, (0,0))
    for target in targets:
        target.draw()
    for b in balls:
        b.draw()
    pg.display.update()

    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            gun.fire_start(event)
        elif event.type == pg.MOUSEBUTTONUP:
            gun.fire_end(event)
        elif event.type == pg.MOUSEMOTION:
            gun.targetting(event)

    for b in balls:
        b.move()
        for target in targets:
            if b.hittest(target):
                target.hit()
                balls.remove(b)
                break

    for target in targets:
        if target.live == 0:
            targets.remove(target)
            targets.append(Target(screen))
            score += 1
            textScore = f_score.render("Счет: " + str(score), True, (0,0,0))
        target.move()
    gun.power_up()

pg.quit()