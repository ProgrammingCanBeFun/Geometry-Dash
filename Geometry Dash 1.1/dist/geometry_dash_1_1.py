import pygame
import sys
import json
import tkinter
from tkinter import messagebox

"""Extras"""


def setup_screen():
    # Initialize screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Geometry Dash')
    return screen


def terminate():
    pygame.quit()
    sys.exit()


def get_data(filename='data/level_data.json'):
    with open(filename, 'r') as f:
        return json.load(f)


def show_alert(message: str, title="Alert"):
    root = tkinter.Tk()
    root.withdraw()

    # Message Box
    messagebox.showinfo(title, message)


def reverse(item: int or float or bool):
    if type(item) == bool:
        item = not item
    elif type(item) == int or float:
        item *= 1
    else:
        raise TypeError
    return item


colors = {
    "Yellow": [255, 255, 0],
    "Red": [255, 0, 0],
    "Orange": [255, 165, 0],
    "Light Orange": [255, 201, 14],
    "Green": [0, 255, 0],
    "Blue": [0, 0, 255],
    "White": [255, 255, 255],
    "Black": [0, 0, 0],
    "Gray": [115, 115, 155],
    "Dark Blue": [0, 0, 115],
    "Pink": [255, 192, 203]
}


class Image:
    def __init__(self, screen, image, x, y):
        self.screen = screen
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def position_center(self, centerx=None, centery=None):
        if centerx:
            self.rect.centerx = centerx
        if centery:
            self.rect.centery = centery


class Button(Image):
    def __init__(self, screen, image, x, y):
        super().__init__(screen, image, x, y)
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 1:
            self.clicked = False

        self.screen.blit(self.image, self.rect)

        return action


"""World"""


class World:
    # Tile types:
    # -1: Blank space
    # 0: Player
    # 1-3: Normal Platforms
    # 4: Spike
    # 5: Lava
    # 6: Water
    # 7: End portal
    # 8: Backwards portal
    # 9: Gravity portal
    # These tiles are stored in three separate sprite groups: self.players, self.obstacles, self.platforms
    #   which in turn are stored in a list.
    def __init__(self, screen, tile_size, data: list):
        self.data = data
        if not self._check_data():
            raise IndexError
        self.screen = screen
        self.tile_size = tile_size

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == 0:
                    player = Player(self.screen, x * self.tile_size, y * self.tile_size,
                                    self.tile_size * 0.75, self.tile_size * 0.75, "Dark Blue", "Gray", self)
                    self.player = player

        # Sprite Groups
        self.blocks = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.special_tiles = pygame.sprite.Group()

        block = None
        obstacle = None
        special_tile = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                # Regular block
                if 1 <= tile <= 3:
                    if tile == 1:
                        block = Block(self.screen, x * self.tile_size, y * self.tile_size,
                                      self.tile_size, self.tile_size, "Gray")
                    elif tile == 2:
                        block = Block(self.screen, x * self.tile_size, y * self.tile_size,
                                      self.tile_size, self.tile_size, "White")
                    elif tile == 3:
                        block = Block(self.screen, x * self.tile_size, y * self.tile_size,
                                      self.tile_size, self.tile_size, "Black")
                    self.blocks.add(block)
                # Obstacle and lava
                elif 4 <= tile <= 6:
                    if tile == 4:
                        obstacle = Spike(self.screen, x * self.tile_size, y * self.tile_size,
                                         self.tile_size, self.tile_size, "White")
                    elif tile == 5:
                        obstacle = Lava(self.screen, x * self.tile_size, y * self.tile_size + 4,
                                        self.tile_size, self.tile_size - 4, "Red")
                    elif tile == 6:
                        obstacle = Spike(self.screen, x * self.tile_size, y * self.tile_size,
                                         self.tile_size, self.tile_size, "White", 'd')
                    self.obstacles.add(obstacle)
                # Special circles
                elif 7 <= tile <= 10:
                    if tile == 7:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Green", 'f')
                    elif tile == 8:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Pink", 'd')
                    elif tile == 9:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Dark Blue", 'g')
                    elif tile == 10:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Yellow", 'j')
                    self.special_tiles.add(special_tile)

        self.sprite_groups = [self.player, self.blocks, self.obstacles, self.special_tiles]

    def _check_data(self):
        """Check if data can be processed."""
        length = 0
        start = False
        for y in self.data:
            n_length = len(y)
            if start:
                if n_length == length:
                    length = n_length
                else:
                    return False
            else:
                length = n_length
        return True


class Player(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, width, height, color: str, inner_color: str, world: World):
        super().__init__()
        self.screen = screen
        self.color = color
        self.image = pygame.Surface((width, height))
        self.image.fill(colors[self.color])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.world = world

        # Initialize inner image
        self.inner_image_color = inner_color
        self.inner_image = pygame.Surface((width - 4, height - 4))
        self.inner_image.fill(colors[self.inner_image_color])
        self.inner_image_rect = self.inner_image.get_rect()

        # Initialize settings
        self.moving_left = False
        self.moving_right = False
        self.in_air = False
        self.jump = False
        self.portal_jump = False
        self.vel_y = 0
        self.speed = 4
        self.jump_height = 11
        self.gravity = 0.75
        self.result = None

    def draw(self):
        self.screen.blit(self.image, self.rect)
        self.screen.blit(self.inner_image, self.inner_image_rect)

    def _position_inner_image(self):
        self.inner_image_rect.width = self.rect.width - 4
        self.inner_image_rect.height = self.rect.height - 4
        self.inner_image_rect.x = self.rect.x + 2
        self.inner_image_rect.y = self.rect.y + 2

    def update(self):
        if not pause:
            global x_scroll
            x_scroll = 0
            dx = self.speed
            dy = 0

            self._check_if_jump()

            self.vel_y += self.gravity
            dy += self.vel_y

            # Check for collision
            x_collision_rect = pygame.Rect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height)
            y_collision_rect = pygame.Rect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height)
            self.in_air = True
            for g, sprites in enumerate(self.world.sprite_groups[1:]):
                for sprite in sprites:
                    if pygame.Rect.colliderect(x_collision_rect, sprite.rect):
                        if g == 2:
                            self.check_special_tile_attributes(sprite)
                        else:
                            self.die()
                    elif pygame.Rect.colliderect(y_collision_rect, sprite.rect):
                        if g == 1:
                            self.die()
                        elif g == 2:
                            self.check_special_tile_attributes(sprite)
                        else:
                            if self._is_gravity_normal():
                                if self.vel_y < 0:
                                    dy = self._block_jump(sprite)
                                elif self.vel_y >= 0:
                                    dy = self._block_fall(sprite)
                            else:
                                if self.vel_y <= 0:
                                    dy = self._block_reverse_fall(sprite)
                                if self.vel_y > 0:
                                    dy = self._block_reverse_jump(sprite)
                    else:
                        if g == 2:
                            sprite.on = True

            self.rect.y += dy
            x_scroll = -dx
            if self.rect.y >= SCREEN_HEIGHT or self.rect.bottom < -200:
                self.die()

            self._position_inner_image()

    def die(self):
        self.result = False

    def win(self):
        self.result = True

    def check_special_tile_attributes(self, sprite):
        if sprite.on is True:
            # Finish level
            if sprite.action == 'f':
                self.win()
            # Change direction
            elif sprite.action == 'd':
                self.speed *= -1
            # Change gravity
            elif sprite.action == 'g':
                self._change_gravity()
            # Jump again
            elif sprite.action == 'j':
                self.portal_jump = True
                self._check_if_jump()
            sprite.on = False

    def _block_fall(self, sprite):
        self.vel_y = 0
        self.in_air = False
        dy = sprite.rect.top - self.rect.bottom
        return dy

    def _block_jump(self, sprite):
        self.vel_y = 0
        dy = sprite.rect.bottom - self.rect.top
        return dy

    def _check_if_jump(self):
        if self.jump is True and (self.in_air is False or self.portal_jump is True):
            self.vel_y = self.jump_height * -1
            self.jump = False
            self.in_air = True
            self.portal_jump = False

    def _change_gravity(self):
        self.gravity *= -1
        self.jump_height *= -1

    def _is_gravity_normal(self):
        answer = None
        if self.gravity > 0:
            answer = True
        elif self.gravity < 0:
            answer = False
        elif answer is None:
            terminate()
        return answer

    def _block_reverse_fall(self, sprite):
        self.vel_y = 0
        self.in_air = False
        dy = sprite.rect.bottom - self.rect.top
        return -dy

    def _block_reverse_jump(self, sprite):
        self.vel_y = 0
        dy = sprite.rect.top - sprite.rect.bottom
        return -dy


class Block(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, width, height, color: str):
        super().__init__()
        self.screen = screen
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += x_scroll

    def draw(self):
        pygame.draw.rect(self.screen, colors[self.color], self.rect)


class Spike(Block):
    def __init__(self, screen, x, y, width, height, color, orientation='u'):
        super().__init__(screen, x, y, width, height, color)
        self.screen = screen
        self.color = color
        self.orientation = orientation
        if self.orientation == 'u':
            self.rect = pygame.Rect(width / 4 + x, height / 2 + y, width / 2, height / 2)
        elif self.orientation == 'd':
            self.rect = pygame.Rect(width / 4 + x, y, width / 2, height / 2)

    def update(self):
        self.rect.x += x_scroll

    def draw(self):
        if self.orientation == 'u':
            pygame.draw.polygon(self.screen, colors[self.color],
                                [self.rect.bottomleft, self.rect.midtop, self.rect.bottomright])
        elif self.orientation == 'd':
            pygame.draw.polygon(self.screen, colors[self.color],
                                [self.rect.topleft, self.rect.midbottom,
                                 self.rect.topright])


class Lava(Block):
    pass


class Portal(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, width, height, color: str, action: str):
        super().__init__()
        self.action = action
        self.screen = screen
        self.rect = pygame.Rect(width / 4 + x, height / 4 + y, width / 2, height / 2)
        self.color = color

        self.on = True

    def update(self):
        self.rect.x += x_scroll

    def draw(self):
        pygame.draw.circle(self.screen, colors[self.color], self.rect.center, self.rect.width / 2)


"""Intro"""


def run_intro():
    screen = setup_screen()

    global main_menu
    main_menu = True

    def intro_terminate(redo=False):
        global main_menu
        main_menu = False
        pygame.quit()
        return redo

    screen_rect = screen.get_rect()

    title_img = pygame.image.load('data/img/title.png')
    title = Image(screen, title_img, 0, 0)
    title.position_center(centerx=screen_rect.centerx)
    title.rect.y = 20

    start_btn_img = pygame.image.load('data/img/start_btn.png')
    start_btn = Button(screen, start_btn_img, 0, 0)
    start_btn.position_center(screen_rect.centerx, screen_rect.centery)

    instructions_btn_img = pygame.image.load('data/img/instructions_btn.png')
    instructions_btn = Button(screen, instructions_btn_img, 0, 0)
    instructions_btn.position_center(screen_rect.centerx)
    instructions_btn.rect.top = start_btn.rect.bottom + 20

    instructions = """
Welcome to Geometry Dash. 
Press the space bar to jump.
Avoid the spikes and the lava.
Don't crash into the sides of blocks.
Green Circles complete the level.
Blue Circles change your gravity.
Pink Circles change your direction.
Jump while touching a Yellow Circle to jump again.
Get to the last level for the gravity challenge.
                        """

    while main_menu:
        screen.fill(colors["Blue"])

        title.draw()
        if instructions_btn.draw():
            show_alert(instructions, "How To Play")
            return intro_terminate(True)
        if start_btn.draw():
            return intro_terminate()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro_terminate()

        if main_menu:
            pygame.display.update()


"""End"""


def run_end(screen):
    screen_rect = screen.get_rect()

    play_again_btn_image = pygame.image.load('data/img/play_again_btn.png')
    play_again_btn = Button(screen, play_again_btn_image, 0, 0)
    play_again_btn.position_center(centerx=screen_rect.centerx)
    play_again_btn.rect.bottom = screen_rect.centery - 20

    credits_image = pygame.image.load('data/img/credits.png')
    credits = Image(screen, credits_image, 0, 0)
    credits.position_center(centerx=screen_rect.centerx)
    credits.rect.top = screen_rect.centery + 20

    while True:

        credits.draw()
        if play_again_btn.draw():
            game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        pygame.display.update()


"""Game"""


def set_level(screen, level: int, data: list):
    level_data = data[level - 1]
    world = World(screen, TILE_SIZE, level_data)
    while world.player.result is None:
        run(screen, world.sprite_groups, world.player)
    return world.player.result


def run(screen, sprite_groups, player):
    """Run the game."""

    def update_sprites():
        for sprite_group in sprite_groups:
            try:
                for sprite in sprite_group:
                    sprite.draw()
            except TypeError:
                # sprite_group is player, so call player's draw method
                sprite_group.draw()
            sprite_group.update()

    clock.tick(FPS)

    screen.fill(colors["Blue"])

    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                terminate()
            if event.key == pygame.K_SPACE:
                player.jump = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player.jump = False

    # Update sprites
    update_sprites()

    # Update screen
    if not pause:
        pygame.display.update()


def game():
    global level
    level = START_LEVEL
    screen = setup_screen()
    try:
        while True:
            if set_level(screen, level, data):
                level += 1
    except IndexError:
        run_end(screen)


if __name__ == '__main__':
    # Set screen width
    SCREEN_WIDTH = 600
    # Set other settings
    TILE_SIZE = 50

    # Set game settings
    x_scroll = 0
    pause = False
    stop = False
    START_LEVEL = 1  # Leave at 1 except for testing
    level = START_LEVEL

    # Initialize clock
    clock = pygame.time.Clock()
    FPS = 60

    data = get_data()
    SCREEN_HEIGHT = 600
    max_height = 0
    for level_data in data:
        height = len(level_data)
        if height > max_height:
            max_height = height
    if max_height * TILE_SIZE > SCREEN_HEIGHT:
        SCREEN_HEIGHT = max_height * TILE_SIZE

    # Intro
    redo = True
    while redo:
        redo = run_intro()
    # Game
    game()
