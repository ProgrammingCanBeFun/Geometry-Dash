import pygame
import argparse
import extras as e


# Tile types:
# -1: Blank space
# 0: Player
# 1-3: Normal Platforms
# 4: Spike
# 5: Lava
# 6: Water
# 7: End portal
# 8:
# These tiles are stored in three separate sprite groups: self.players, self.obstacles, self.platforms
#   which in turn are stored in a list.


class World:
    def __init__(self, screen, tile_size, data: list):
        self.data = data
        if not self._check_data():
            print("Data is corrupt.")
            e.terminate()
        self.screen = screen
        self.tile_size = tile_size

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == 0:
                    player = Player(self.screen, x * self.tile_size, y * self.tile_size,
                                    self.tile_size * 0.75, self.tile_size * 0.75, "Light Blue", "Gray", self)
                    self.player = player
                    # Check if player is off the screen
                    if self.player.rect.x > SCREEN_WIDTH:
                        new_player_x = SCREEN_WIDTH - 150
                        new_scroll = self.player.rect.x - new_player_x
                        self.player.rect.x = new_player_x
                        global x_scroll
                        x_scroll = new_scroll

        # Sprite Groups
        self.blocks = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.special_tiles = pygame.sprite.Group()

        block = None
        obstacle = None
        special_tile = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
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
                elif 7 <= tile <= 9:
                    if tile == 7:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Green", 'f')
                    elif tile == 8:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Pink", 'd')
                    elif tile == 9:
                        special_tile = Portal(self.screen, x * tile_size, y * tile_size,
                                              self.tile_size, self.tile_size, "Light Blue", 'g')
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
        self.image.fill(e.colors[self.color])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.world = world

        # Initialize inner image
        self.inner_image_color = inner_color
        self.inner_image = pygame.Surface((width - 4, height - 4))
        self.inner_image.fill(e.colors[self.inner_image_color])
        self.inner_image_rect = self.inner_image.get_rect()

        # Initialize settings
        self.moving_left = False
        self.moving_right = False
        self.in_air = False
        self.jump = False
        self.vel_y = 0
        self.speed = 4
        self.jump_height = 11
        self.gravity = 0.75
        self.game_over = False
        self.level = level

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

            self._check_if_jump(message=True)

            self.vel_y += self.gravity
            print(f'Vel_Y: {self.vel_y}')
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
                            if self._is_gravity_normal(True):
                                if self.vel_y < 0:
                                    dy = self._block_jump(sprite)
                                elif self.vel_y >= 0:
                                    dy = self._block_fall(sprite)
                            else:
                                if self.vel_y <= 0:
                                    dy = self._block_reverse_fall(sprite)
                                if self.vel_y > 0:
                                    dy = self._block_reverse_jump(sprite)

            self.rect.y += dy
            x_scroll = -dx
            if self.rect.y >= SCREEN_HEIGHT:
                self.die()

            self._position_inner_image()

    def die(self, test=False, message=False):
        if message:
            print("Game Over")
        if test:
            global pause
            pause = True
        else:
            global level
            set_level(level, data)

    def level_up(self):
        try:
            print("Level Up")
            global level
            level += 1
            set_level(level, data)
        except IndexError:
            self.win()

    def check_special_tile_attributes(self, sprite, message=False):
        if sprite.on is True:
            if message:
                print(sprite.action)
            # Finish level
            if sprite.action == 'f':
                self.level_up()
            # Change direction
            elif sprite.action == 'd':
                self.speed *= -1
            # Change gravity
            elif sprite.action == 'g':
                self._change_gravity()
            sprite.on = False

    def win(self):
        print("You won!")
        e.terminate()

    def _block_fall(self, sprite):
        self.vel_y = 0
        self.in_air = False
        dy = sprite.rect.top - self.rect.bottom
        return dy

    def _block_jump(self, sprite):
        self.vel_y = 0
        dy = sprite.rect.bottom - self.rect.top
        return dy

    def _check_if_jump(self, message=False):
        if message:
            print(self.jump, self.in_air)
        if self.jump is True and self.in_air is False:
            self.vel_y = self.jump_height * -1
            self.jump = False
            self.in_air = True
            if message:
                print("Jump")

    def _change_gravity(self):
        self.gravity *= -1
        self.jump_height *= -1

    def _is_gravity_normal(self, message=False):
        answer = None
        if self.gravity > 0:
            answer = True
        elif self.gravity < 0:
            answer = False
        if answer is None:
            print("GeometryDashError: no gravity")
            e.terminate()
        if message:
            print(answer)
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
        pygame.draw.rect(self.screen, e.colors[self.color], self.rect)


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
            pygame.draw.polygon(self.screen, e.colors[self.color],
                                [self.rect.bottomleft, self.rect.midtop, self.rect.bottomright])
        elif self.orientation == 'd':
            pygame.draw.polygon(self.screen, e.colors[self.color],
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
        pygame.draw.circle(self.screen, e.colors[self.color], self.rect.center, self.rect.width / 2)


def set_level(level: int, data: list):
    print(level)
    level_data = data[level - 1]
    world = World(screen, TILE_SIZE, level_data)
    while world.player.game_over is False:
        run(world.sprite_groups, world.player)


def game_start():
    e.show_alert(
        '''
        Welcome to Geometry Dash. The goal of the game is to complete all the levels.
        You are constantly moving in the right direction. If you crash into a block, you will die. 
        Avoid landing on spikes, lava and water.
        Get to the Green Portal. The Green Portal Teleports you to the next level.
        Pink portals reverse the direction you travel in. 
        Light Blue Portals reverse your gravity.
        '''
    )


def run(sprite_groups, player):
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

    screen.fill(e.colors["Blue"])

    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            e.terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                e.terminate()
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Runs Geometry Dash.")
    parser.add_argument('--screen-width', dest='SCREEN_WIDTH', required=False)
    args = parser.parse_args()

    # Set screen width
    SCREEN_WIDTH = 600
    if args.SCREEN_WIDTH and int(args.SCREEN_WIDTH) > 600:
        SCREEN_WIDTH = int(args.SCREEN_WIDTH)
    # Set screen color
    BG_COLOR = e.colors["Green"]
    # Set other settings
    TILE_SIZE = 50

    # Set game settings
    x_scroll = 0
    pause = False
    stop = False
    level = 6

    # Initialize clock
    clock = pygame.time.Clock()
    FPS = 60

    data = e.get_data()
    max_height = 0
    for level_data in data:
        height = len(level_data)
        if height > max_height:
            max_height = height
    SCREEN_HEIGHT = max_height * TILE_SIZE

    # Initialize screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Geometry Dash')

    set_level(level, data)
