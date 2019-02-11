import pygame as pg
import random
import os

TITLE = 'Jumper'

WIDTH = 600
HEIGHT = 780
FPS = 70

RED = (255, 0, 0)
GREEN = (25, 255, 0)
BLUE = (0, 0, 255)

YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RAND_COLOR_ARRAY = [WHITE, YELLOW, MAGENTA, CYAN, RED, BLUE, GREEN]

PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_LIST = [(0, 760), (WIDTH / 2 - 50, 600),
                 (400, 200), (PLATFORM_HEIGHT, 300), (250, 50), (50, 100),
                 (200, 400), (333, 550), (540, 301), (540, 444),
                 (540, 444), (540, 444)]

PLAYER_ACC = 0.6
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.45
vec = pg.math.Vector2

'''
Функция подгрузки изображения из папки data
'''


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pg.image.load(fullname)
    except pg.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


'''
Подгрузка музыки и фона
'''
background = load_image("background.png")
pg.mixer.init()
pg.mixer.music.load("data\\background_music.wav")
pg.mixer.music.play(-1)
sound1 = pg.mixer.Sound('data\\jump.wav')


class Player(pg.sprite.Sprite):
    def __init__(self, game, x=WIDTH / 2, y=HEIGHT / 2, move=True):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("hero_l.png")
        self.move = move
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        '''
        Изменение изображения главного героя в зависимости от стороны поворота
        '''
        if self.move:
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                self.acc.x = -PLAYER_ACC
                self.image = load_image("hero_l.png")
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                self.acc.x = PLAYER_ACC
                self.image = load_image("hero_r.png")

            self.acc.x += self.vel.x * PLAYER_FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0

        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def jump(self):
        '''
        Если игрок на плитформе, он прыгает
        Если звук включен, включается звук прыжка
        '''
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits and self.pos.y < hits[0].rect.top + 2:
            if g.sound:
                sound1.play()
            self.vel.y = -20


class PlayButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("play_button.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class PlayAgainButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("play_again.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class MenuButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("menu.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class OptionButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("option.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("green_plat.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class BackButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("back.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class ScoresButton(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("scores.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class SwitchOffButton(pg.sprite.Sprite):
    def __init__(self, x, y, state):
        pg.sprite.Sprite.__init__(self)
        self.on = load_image("on.png")
        self.off = load_image("off.png")
        if state:
            self.flag = "ON"
            self.image = self.on
        else:
            self.flag = "OFF"
            self.image = self.off
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def change(self):
        if self.flag == "ON":
            self.flag = "OFF"
            self.image = self.off
        else:
            self.flag = "ON"
            self.image = self.on

    def state(self):
        return self.flag


class Game:
    def __init__(self):
        # Создание окна
        self.sound = True
        self.music = True
        self.quit = False
        self.running = True
        self.gameOver = False
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

    def new(self):
        # Новая игра

        # Группы спрайтов
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.platforms_in_game = 12
        self.wall = 75

        # Игрок и счет
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.PLAYER_SCORE = 0

        # Начальные платформы
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def run(self):
        # Основной цикл игры
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            if self.gameOver:
                self.show_end_screen()

    def update(self):
        self.all_sprites.update()
        self.player.jump()
        # Проверка на касание платформы
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0

        # Скролл экрана
        if self.player.rect.top < HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top > HEIGHT:
                    self.PLAYER_SCORE += 1
                    plat.kill()

        # Создание новых платформ
        if self.PLAYER_SCORE - self.wall >= 0 and self.platforms_in_game >= 3:
            self.platforms_in_game -= 1
            self.wall *= 1.5
        while len(self.platforms) < self.platforms_in_game:
            p = Platform(random.randint(10, WIDTH - 50),
                         random.randint(-50, -30))
            if not pg.sprite.spritecollideany(p, self.platforms):
                self.platforms.add(p)
                self.all_sprites.add(p)
        # Проверка на падение (конец игры)
        if self.player.rect.top > HEIGHT:
            self.playing = False
            self.gameOver = True

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
                self.gameOver = True
                self.playing = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.show_go_screen()

    def draw(self):
        # Отрисовка фона
        self.screen.blit(background, (450, 0))
        self.screen.blit(background, (0, 0))
        line = load_image("line_up.png")
        self.screen.blit(line, (0, 0))
        self.all_sprites.draw(self.screen)
        self.display_text(("Score:" + str(self.PLAYER_SCORE)), 0, 0, 30, BLACK)
        pg.display.flip()

    def show_go_screen(self):
        # Окно начала игры
        gameOverLoop = False
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        nlo_x = 400
        nlo_y = 20
        nlo_k = 0.25
        doodle = Player(self, 125, 400, False)
        plat = Platform(100, 750)
        self.platforms.add(plat)
        self.all_sprites.add(plat)
        self.all_sprites.add(doodle)
        while not gameOverLoop and not self.quit:
            self.screen.blit(background, (450, 0))
            self.screen.blit(background, (0, 0))
            name = load_image("name_of_game.png")
            name = pg.transform.rotate(name, 15)
            self.screen.blit(name, (-10, -10))
            play_button = PlayButton(250, 220)
            self.screen.blit(play_button.image, (play_button.rect.x,
                                                 play_button.rect.y))
            option = OptionButton(235, 390)
            self.screen.blit(option.image, (option.rect.x, option.rect.y))
            nlo_body = load_image("nlo_body.png")
            nlo_laser = load_image("nlo_laser.png")
            self.screen.blit(nlo_body, (nlo_x, nlo_y))
            if nlo_y % 0.5 == 0:
                self.screen.blit(nlo_laser, (nlo_x, nlo_y))
            nlo_y -= nlo_k
            if nlo_y < 10 or nlo_y > 20:
                nlo_k *= -1
            scores = ScoresButton(235, 300)
            self.screen.blit(scores.image, (scores.rect.x, scores.rect.y))
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            doodle.jump()
            if doodle.vel.y > 0:
                hits = pg.sprite.spritecollide(doodle, self.platforms, False)
                if hits:
                    doodle.pos.y = hits[0].rect.top + 1
                    doodle.vel.y = 0
            pg.display.flip()
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    gameOverLoop = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if play_button.rect.collidepoint(event.pos):
                        self.gameOver = False
                        gameOverLoop = True
                        self.new()
                        self.run()
                    if option.rect.collidepoint(event.pos):
                        self.options()
                    if scores.rect.collidepoint(event.pos):
                        self.records()

    def show_end_screen(self):
        # Окно конца игры
        end = True
        play_again = PlayAgainButton(200, 450)
        menu = MenuButton(200, 550)
        self.write_record(self.PLAYER_SCORE)
        while end and not self.quit:
            self.screen.blit(background, (450, 0))
            self.screen.blit(background, (0, 0))
            gameover = load_image("game_over.png")
            gameover = pg.transform.rotate(gameover, 15)
            self.screen.blit(gameover, (100, 70))
            self.display_text("Your score: ", 160, 250, 30, BLACK)
            self.display_text(str(self.PLAYER_SCORE), 340, 250, 30, BLACK)

            data = open("data\\records.txt").read().split('\n')
            self.display_text("Best score: " + str(data[0].split()[2]),
                              130, 300, 30, BLACK)
            self.display_text("Your name: Doodler", 140, 350, 30, BLACK)
            self.screen.blit(play_again.image, (play_again.rect.x,
                                                play_again.rect.y))
            self.screen.blit(menu.image, (menu.rect.x, menu.rect.y))
            self.clock.tick(FPS)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True
                    self.show_go_screen()
                    end = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if play_again.rect.collidepoint(event.pos):
                        self.gameOver = False
                        end = False
                        self.new()
                        self.run()
                    if menu.rect.collidepoint(event.pos):
                        self.gameOver = False
                        end = False
                        self.show_go_screen()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.show_go_screen()

    def options(self):
        # Окно настроек
        options = True
        back = BackButton(500, 700)
        switch_music = SwitchOffButton(105, 150, self.music)
        switch_sound = SwitchOffButton(305, 150, self.sound)
        while options:
            self.screen.blit(background, (450, 0))
            self.screen.blit(background, (0, 0))
            self.screen.blit(back.image, (back.rect.x, back.rect.y))
            self.screen.blit(switch_sound.image, (switch_sound.rect.x,
                                                  switch_sound.rect.y))
            self.screen.blit(switch_music.image, (switch_music.rect.x,
                                                  switch_music.rect.y))
            self.display_text("Music", 100, 90, 30, BLACK)
            self.display_text("Sound", 300, 90, 30, BLACK)
            self.clock.tick(FPS)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True
                    options = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if back.rect.collidepoint(event.pos):
                        options = False
                    if switch_music.rect.collidepoint(event.pos):
                        switch_music.change()
                        if switch_music.state() == "ON":
                            pg.mixer.music.play(-1)
                            self.music = True
                        else:
                            pg.mixer.music.stop()
                            self.music = False
                    if switch_sound.rect.collidepoint(event.pos):
                        switch_sound.change()
                        if switch_sound.state() == "ON":
                            self.sound = True
                        else:
                            self.sound = False

    def records(self):
        # Окно рекордов
        records = True
        back = BackButton(500, 700)
        while records:
            text_height = 50
            scores = open("data\\records.txt")
            self.screen.blit(background, (450, 0))
            self.screen.blit(background, (0, 0))
            self.screen.blit(back.image, (back.rect.x, back.rect.y))
            for line in scores:
                self.display_text(line.replace('\n', ''),
                                  50, text_height +
                                  ((int(line.split()[0]) - 1) * 70), 40, BLACK)
            self.clock.tick(FPS)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True
                    records = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if back.rect.collidepoint(event.pos):
                        records = False

    def display_text(self, message, x, y, size, color):
        # Функция написания текста
        font = pg.font.SysFont("Segoe Print", size)
        text = font.render(message, False, color)
        self.screen.blit(text, (x, y))

    def write_record(self, score):
        # Обновление таблицы рекордов
        data = open("data\\records.txt")
        text = data.read().split('\n')
        '''
        Удаление текста из файла путем перемотки на первый символ
        и закрывания файла
        Перезапись таблицы рекордов после сортировки
        '''
        data = open("data\\records.txt", mode="w", encoding="utf-8")
        data.seek(0)
        data.close()
        data = open("data\\records.txt", mode="w", encoding="utf-8")
        scores = []
        for i in text:
            if i:
                scores.append(int(i.split()[2]))
        scores.append(score)
        scores = sorted(scores, reverse=True)
        for i in range(10):
            data.write(str(i + 1) + '  Doodler ' + str(scores[i]) + '\n')
        data.close()


g = Game()
clock = pg.time.Clock()
g.show_go_screen()
