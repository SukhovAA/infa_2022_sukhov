import math
import pygame as pg
from random import randint
import pygame.display

WIDTH, HEIGHT = 500, 500
FONE_COLOR = (155, 155, 155)
FPS = 30
pg.init()
pygame.display.set_caption("_First_ Ball game")

f_score = pg.font.Font(None, 36)
f_good_click = pg.font.Font(None, 24)
screen = pg.display.set_mode((WIDTH, HEIGHT))

class Ball:

    def __init__(self, radius_min=10, radius_max=30, speed_max=3):
        self.x = randint(0, WIDTH)
        self.y = randint(0, HEIGHT)
        self.radius = randint(radius_min, radius_max)
        self.speed_x = randint(-speed_max, speed_max)
        self.speed_y = randint(-speed_max, speed_max)
        self.timeCreate = pg.time.get_ticks()
        colors = [(255, 0, 0), (0, 0, 255)]
        type = randint(0, 1)
        self.type = type
        self.color = colors[type]
        self.speed_max = speed_max

    def check_collision(self, x : int, y : int):
        """
        Проверка вхождения точки в мячик
        """
        return (x - self.x)**2 + (y - self.y)**2 <= self.radius**2

    def update(self, FPS : int):
        """
        Обработка логики шарика
        """
        self.wall_collision()

        self.x += self.speed_x/FPS
        self.y += self.speed_y/FPS

        if self.type == 1:
            k = 1
            if self.speed_x < 0:
                k = -1
            self.speed_x =  k * self.speed_max * (0.5 + 0.5*math.sin((self.timeCreate + pg.time.get_ticks())/500))**2
            if self.speed_y < 0:
                k = -1
            self.speed_y =  k * self.speed_max * (0.5 + 0.5*math.cos((self.timeCreate + pg.time.get_ticks())/500))**2

    def getScore(self):
        """
        Возращает количество очков за мячик
        """
        a = 2
        if self.type == 1:
            a = 1
        if good_click_count >= 5:
            return a*5
        return a*(good_click_count + 1)




    def render(self, surface : pg.Surface):
        """
        Отрисовывает мячик
        """
        pg.draw.circle(surface, self.color, (self.x, self.y), self.radius, 0)
        pg.draw.circle(surface, self.color, (self.x, self.y), self.radius, 1)

    def wall_collision(self):
        """
        Проверка на столкновение со стенами
        """
        if self.x - self.radius < 0:
            self.speed_x = randint(0, self.speed_max)
        elif self.x + self.radius > WIDTH:
            self.speed_x = randint(-self.speed_max, 0)
        elif self.y - self.radius < 0:
            self.speed_y = randint(0, self.speed_max)
        elif self.y + self.radius > HEIGHT:
            self.speed_y = randint(-self.speed_max, 0)

class Word:
    click_words = ["", "Double Kill", "Triple Kill", "Mega Kill", "Rampage"]
    timeLive = 1000

    def __init__(self, countGoodClick : int, time, position):
        self.word = f_good_click.render(self.GetGoodWord(countGoodClick), True, (200, 0, 0))
        self.time = time
        self.position = position

    def GetGoodWord(self, countGoodClick : int):
        """
        Возращает слово, в зависимости от количества попаданий подряд
        """
        l = len(self.click_words)
        if countGoodClick >= l:
            return self.click_words[l-1]
        return self.click_words[countGoodClick]

    def render(self, surface : pg.Surface):
        """
        Отрисовка слова
        """
        surface.blit(self.word, self.position)

    def update(self):
        """
        Обработка логики слова
        """
        kMove = (1 - (pg.time.get_ticks() - self.time)/ self.timeLive) / FPS
        self.position = (self.position[0], self.position[1] - kMove)

    def itBe(self):
        """Проверка истечение срока жизни слова"""
        return pg.time.get_ticks() < self.time + self.timeLive



balls = []
words = []
lastCreate = 0
delayCreate = 0
good_click_count = 0
score = 0

def CreateBall():
    """
    Создание мячика
    """
    balls.append(Ball())

def CreateWord(goodClickCount : int, position):
    """Создание слова"""
    words.append(Word(goodClickCount, pg.time.get_ticks(), position))

def Click(position):
    """Обработка логики нажатия"""
    global score, textScore, good_click_count
    isGoodClick = False
    for ball in balls:
        if ball.check_collision(position[0], position[1]):
            balls.remove(ball)
            score += ball.getScore()
            textScore = f_score.render("Счет: " + str(score), True, (0,0,0))
            CreateWord(good_click_count, position)
            isGoodClick = True
            break

    if isGoodClick:
        good_click_count += 1
    else:
        good_click_count = 0
        score -= 1
        textScore = f_score.render("Счет: " + str(score), True, (0, 0, 0))



def update():
    """Обработка логики игры (Ядро)"""
    global lastCreate, delayCreate, balls, FPS

    for ball in balls:
        ball.update(FPS)

    for word in words:
        if not word.itBe():
            words.remove(word)
            continue
        word.update()

    if pg.time.get_ticks() > (lastCreate + delayCreate):
        lastCreate = pg.time.get_ticks()
        delayCreate = randint(1000, 2000)
        CreateBall()

def render(screen):
    """Отрисовка экрана"""
    global balls
    screen.fill(FONE_COLOR)
    for ball in balls:
        ball.render(screen)

    for word in words:
        word.render(screen)

    screen.blit(textScore, (0,0))

    pg.display.update()

textScore = f_score.render("Счет: " + str(score), True, (0,0,0))
running = True
while running:

    update()
    render(screen)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                Click(event.pos)

pg.quit()
