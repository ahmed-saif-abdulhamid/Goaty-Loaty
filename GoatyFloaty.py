import pygame
import sys
import random
import os

# ----------- Initialization -----------
pygame.init()
pygame.mixer.init()

# ----------- Game Settings -----------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_SIZE = 50
PLAYER_START_X = 100
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_SIZE - 50
PLAYER_INITIAL_SPEED = 2
PLAYER_MAX_SPEED = 10
GRAVITY = 1
JUMP_VELOCITY = -15

# Obstacle and Coin settings
OBSTACLE_GAP_MIN = 300
OBSTACLE_GAP_MAX = 600
COIN_SIZE = 30
COIN_SPEED = 5
COIN_GAP_MIN = 500
COIN_GAP_MAX = 700

# Paths to assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'assets', 'images')
SOUND_DIR = os.path.join(BASE_DIR, 'assets', 'sounds')

# ----------- Display Setup -----------
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Goaty Loaty")

# ----------- Load Assets -----------
try:
    PLAYER_IMAGE = pygame.image.load(os.path.join(IMAGE_DIR, 'player.png')).convert_alpha()
    PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))

    CACTUS_IMAGE = pygame.image.load(os.path.join(IMAGE_DIR, 'cactus.png')).convert_alpha()
    CACTUS_IMAGE = pygame.transform.scale(CACTUS_IMAGE, (50, 50))

    COIN_IMAGE = pygame.image.load(os.path.join(IMAGE_DIR, 'coin.png')).convert_alpha()
    COIN_IMAGE = pygame.transform.scale(COIN_IMAGE, (COIN_SIZE, COIN_SIZE))

    BACKGROUND_IMAGE = pygame.image.load(os.path.join(IMAGE_DIR, 'background.png')).convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))

    BACKGROUND_MUSIC = os.path.join(SOUND_DIR, 'background.mp3')
    JUMP_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'jump.wav'))
    WASTED_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'wasted.mp3'))
    WIN_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'win.mp3'))
    COIN_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'coin_collect.mp3'))

    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Error loading assets: {e}")
    pygame.quit()
    sys.exit()

# ----------- Classes -----------
class Player:
    def __init__(self):
        self.image = PLAYER_IMAGE
        self.x = PLAYER_START_X
        self.y = PLAYER_START_Y
        self.velocity_y = 0
        self.speed = PLAYER_INITIAL_SPEED
        self.is_jumping = False
        self.on_ground = True
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - PLAYER_SIZE))

    def jump(self, keys):
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.is_jumping = True
            self.on_ground = False
            JUMP_SOUND.play()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        if self.y >= PLAYER_START_Y:
            self.y = PLAYER_START_Y
            self.velocity_y = 0
            self.on_ground = True

    def update(self, keys):
        self.move(keys)
        self.jump(keys)
        self.apply_gravity()
        self.rect.topleft = (self.x, self.y)

    def accelerate(self, elapsed_time):
        """Increase player speed over time."""
        if elapsed_time < 30:  # Accelerate only during the game duration
            self.speed = PLAYER_INITIAL_SPEED + (PLAYER_MAX_SPEED - PLAYER_INITIAL_SPEED) * (elapsed_time / 30)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, x):
        self.image = CACTUS_IMAGE
        self.x = x
        self.y = SCREEN_HEIGHT - 100
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.x -= PLAYER_INITIAL_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Coin:
    def __init__(self, x, y):
        self.image = COIN_IMAGE
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.x -= COIN_SPEED
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


# ----------- Helper Functions -----------
def generate_obstacles_and_coins():
    obstacles = []
    coins = []

    next_obstacle_x = SCREEN_WIDTH + random.randint(OBSTACLE_GAP_MIN, OBSTACLE_GAP_MAX)
    next_coin_x = SCREEN_WIDTH + random.randint(COIN_GAP_MIN, COIN_GAP_MAX)

    for _ in range(3):  # Generate 3 obstacles and coins
        obstacles.append(Obstacle(next_obstacle_x))
        next_obstacle_x += random.randint(OBSTACLE_GAP_MIN, OBSTACLE_GAP_MAX)

        if random.random() < 0.7:  # 70% chance to generate a coin
            coin_y = random.randint(100, SCREEN_HEIGHT - 150)
            coins.append(Coin(next_coin_x, coin_y))
        next_coin_x += random.randint(COIN_GAP_MIN, COIN_GAP_MAX)

    return obstacles, coins


def win_screen(score, coins_collected):
    font = pygame.font.SysFont('arial', 50)
    small_font = pygame.font.SysFont('arial', 30)
    pygame.mixer.music.stop()  # Stop background music
    WIN_SOUND.play()

    while True:
        SCREEN.fill(BLACK)
        display_text("You Won!", font, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        display_text(f"Score: {score}", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        display_text(f"Coins Collected: {coins_collected}", small_font, GOLD, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_text("Press Enter to Play Again", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


def game_over_screen(score, coins_collected):
    font = pygame.font.SysFont('arial', 50)
    small_font = pygame.font.SysFont('arial', 30)
    pygame.mixer.music.stop()  # Stop background music
    WASTED_SOUND.play()

    while True:
        SCREEN.fill(BLACK)
        display_text("Wasted", font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        display_text(f"Score: {score}", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        display_text(f"Coins Collected: {coins_collected}", small_font, GOLD, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_text("Press Enter to Try Again", small_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


def display_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    SCREEN.blit(text_surface, text_rect)


# ----------- Game Loop -----------

def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 30)

    player = Player()
    score = 0
    coins_collected = 0

    obstacles, coins = generate_obstacles_and_coins()

    bg_x = 0
    start_time = pygame.time.get_ticks()  # Track start time

    running = True
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000

        # Player mechanics
        player.accelerate(elapsed_time)
        player.update(keys)

        # Obstacle mechanics
        for obstacle in obstacles[:]:
            obstacle.update()
            if obstacle.x < -50:
                obstacles.remove(obstacle)

        # Coin mechanics
        for coin in coins[:]:
            coin.update()
            if coin.x < -COIN_SIZE:
                coins.remove(coin)

        # Regenerate obstacles and coins
        if len(obstacles) < 2:
            new_obstacles, new_coins = generate_obstacles_and_coins()
            obstacles.extend(new_obstacles)
            coins.extend(new_coins)

        # Collision detection
        for obstacle in obstacles:
            if player.rect.colliderect(obstacle.rect):
                game_over_screen(score, coins_collected)
                return

        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins_collected += 1
                score += 10
                coins.remove(coin)

        # Check win condition
        if elapsed_time >= 30:
            win_screen(score, coins_collected)
            return

        # Background movement
        bg_x -= int(player.speed)
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0

        # Draw elements
        SCREEN.blit(BACKGROUND_IMAGE, (bg_x, 0))
        SCREEN.blit(BACKGROUND_IMAGE, (bg_x + SCREEN_WIDTH, 0))
        player.draw(SCREEN)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
        for coin in coins:
            coin.draw(SCREEN)

        # Display score, coins, and time
        text_score = font.render(f"Score: {score}", True, WHITE)
        text_coins = font.render(f"Coins: {coins_collected}", True, GOLD)
        text_time = font.render(f"Time: {max(0, int(30 - elapsed_time))}s", True, WHITE)
        SCREEN.blit(text_score, (SCREEN_WIDTH - 150, 10))
        SCREEN.blit(text_coins, (20, 10))
        SCREEN.blit(text_time, (SCREEN_WIDTH // 2 - 50, 10))

        pygame.display.flip()

    pygame.quit()


# ----------- Main Menu -----------

def main_menu():
    font = pygame.font.SysFont('arial', 50)
    small_font = pygame.font.SysFont('arial', 30)

    while True:
        SCREEN.fill(BLACK)
        text_title = font.render("Goaty Loaty", True, WHITE)
        text_start = small_font.render("Press Enter to Start", True, WHITE)

        SCREEN.blit(text_title, (SCREEN_WIDTH // 2 - text_title.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        SCREEN.blit(text_start, (SCREEN_WIDTH // 2 - text_start.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


# ----------- Run the Game -----------

if __name__ == "__main__":
    while True:
        main_menu()
        main()