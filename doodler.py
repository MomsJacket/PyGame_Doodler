import pygame as pg
import random
import os

TITLE = 'Jumper'

WIDTH = 800
HEIGHT = 800
FPS = 60

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
PLATFORM_LIST = [(0, HEIGHT - 40, WIDTH, 40, random.choice(RAND_COLOR_ARRAY)),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4, PLATFORM_WIDTH, PLATFORM_HEIGHT, random.choice(RAND_COLOR_ARRAY)),
                 (400, 200, PLATFORM_WIDTH, PLATFORM_HEIGHT, random.choice(RAND_COLOR_ARRAY)),
                 (PLATFORM_HEIGHT, 300, PLATFORM_WIDTH, PLATFORM_HEIGHT, random.choice(RAND_COLOR_ARRAY)),
                 (600, 50, PLATFORM_WIDTH, PLATFORM_HEIGHT, random.choice(RAND_COLOR_ARRAY))]

PLAYER_ACC = 0.6
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.45


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


vec = pg.math.Vector2
background = load_image("background.png")


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("hero_l.png")

        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.image = load_image("hero_l.png")
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.image = load_image("hero_r.png")

        # Applys Friction
        self.acc.x += self.vel.x * PLAYER_FRICTION

        # Equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0

        if self.pos.x < 0:
            self.pos.x = WIDTH

        # The rectangles new position
        self.rect.midbottom = self.pos

    def jump(self):
        # If the player is on a platform then it is allowed to jump
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            self.vel.y = -20


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image("green_plat.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        # Initialize Pygame and Create Window
        self.running = True
        self.gameOver = False
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

    def new(self):
        # Start a New Game

        # Groups
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        # Player object
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.PLAYER_SCORE = 0

        # Platform Object 
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            if self.gameOver:
                self.show_go_screen()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # Check if the player hits a platform
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0

        # If player reaches the top quarter of the screen the window scrolls up
        if self.player.rect.top < HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top > HEIGHT:
                    self.PLAYER_SCORE += 1
                    plat.kill()

        # Spawn New platforms

        while len(self.platforms) < 6:
            p = Platform(random.randint(10, 700), -(random.randint(20, 100)), PLATFORM_WIDTH, PLATFORM_HEIGHT,
                         random.choice(RAND_COLOR_ARRAY))
            self.platforms.add(p)
            self.all_sprites.add(p)

        if self.player.rect.top > HEIGHT:
            self.playing = False

    def events(self):
        # Game Loop - Events
        for event in pg.event.get():
            # Check for closing window
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        # Game Loop - draw
        # Drawing
        self.screen.fill(BLACK)
        self.screen.blit(background, (450, 0))
        self.screen.blit(background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.display_text(("Очки:" + str(self.PLAYER_SCORE)), 0, 0, 40, BLACK)
        # After everything has been drawn, flip the display
        pg.display.flip()

    def show_go_screen(self):
        # Game Over Screen
        gameOverLoop = False
        while not gameOverLoop:
            self.screen.fill(BLACK)
            self.display_text("Welcome to Jump", WIDTH / 3 + 30, HEIGHT / 4, 30, WHITE)
            self.display_text("A and D to move left and right and SPACE to Jump", WIDTH / 3 - 20, HEIGHT / 3, 15, WHITE)
            self.display_text("Press any button to continue...", WIDTH / 3 + 50, HEIGHT * 2 / 3, 15, WHITE)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()

                if event.type == pg.KEYUP:
                    self.gameOver = False
                    gameOverLoop = True
                    self.new()

    def display_text(self, message, x, y, size, color):
        font = pg.font.SysFont("Comic Sans Ms", size)
        text = font.render(message, False, color)
        self.screen.blit(text, (x, y))


g = Game()
g.show_go_screen()
clock = pg.time.Clock()
while g.running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    clock.tick(FPS)
    g.new()
    g.run()
    g.show_go_screen()
