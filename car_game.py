"""
Car Dodge Game - made with Pygame
---------------------------------
Install:  pip install pygame
Run:      python car_game.py

Controls:
    LEFT / A   -> move left
    RIGHT / D  -> move right
    P          -> pause
    SPACE      -> restart after Game Over
    ESC        -> quit
"""

import random
import sys

import pygame

# ---------- STEP 1: Settings ----------
WIDTH, HEIGHT = 480, 700
FPS = 60

ROAD_LEFT = 40
ROAD_WIDTH = 400
LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES

CAR_W, CAR_H = 50, 90

GRAY = (60, 60, 60)
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
RED = (220, 30, 30)
BLUE = (30, 90, 220)
BLACK = (0, 0, 0)

ENEMY_COLORS = [(230, 120, 0), (150, 50, 200), (0, 170, 170), (200, 200, 200)]


# ---------- STEP 2: Draw a car (no images needed) ----------
def draw_car(surface, rect, color):
    pygame.draw.rect(surface, color, rect, border_radius=10)
    # windshield
    wind = pygame.Rect(rect.x + 8, rect.y + 20, rect.w - 16, 22)
    pygame.draw.rect(surface, (170, 220, 255), wind, border_radius=4)
    # wheels
    for wx in (rect.x - 5, rect.right - 3):
        for wy in (rect.y + 10, rect.bottom - 28):
            pygame.draw.rect(surface, BLACK, (wx, wy, 8, 18), border_radius=3)


# ---------- STEP 3: Classes ----------
class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, CAR_W, CAR_H)
        self.rect.centerx = ROAD_LEFT + ROAD_WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 6

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        # keep the car inside the road
        self.rect.left = max(self.rect.left, ROAD_LEFT + 5)
        self.rect.right = min(self.rect.right, ROAD_LEFT + ROAD_WIDTH - 5)

    def draw(self, surface):
        draw_car(surface, self.rect, BLUE)


class Enemy:
    def __init__(self, speed):
        lane = random.randint(0, LANES - 1)
        x = ROAD_LEFT + lane * LANE_WIDTH + (LANE_WIDTH - CAR_W) // 2
        self.rect = pygame.Rect(x, -CAR_H, CAR_W, CAR_H)
        self.speed = speed + random.uniform(-1, 1.5)
        self.color = random.choice(ENEMY_COLORS)

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        draw_car(surface, self.rect, self.color)


# ---------- STEP 4: Road drawing ----------
def draw_road(surface, offset):
    surface.fill(GREEN)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    # road edges
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT, 0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT + ROAD_WIDTH - 4, 0, 4, HEIGHT))
    # moving dashed lane lines
    for i in range(1, LANES):
        x = ROAD_LEFT + i * LANE_WIDTH - 2
        for y in range(-60, HEIGHT, 60):
            pygame.draw.rect(surface, YELLOW, (x, y + offset, 4, 30))


def draw_text(surface, text, font, color, center):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(center=center))


# ---------- STEP 5: Main game ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Car Dodge Game")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("arial", 22, bold=True)
    font_big = pygame.font.SysFont("arial", 48, bold=True)

    high_score = 0

    def reset():
        return Player(), [], 0, 5.0, 0, 0  # player, enemies, score, speed, spawn timer, line offset

    player, enemies, score, base_speed, spawn_timer, line_offset = reset()
    game_over = False
    paused = False

    while True:
        # ----- Events -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                if event.key == pygame.K_SPACE and game_over:
                    player, enemies, score, base_speed, spawn_timer, line_offset = reset()
                    game_over = False

        # ----- Update -----
        if not game_over and not paused:
            player.update(pygame.key.get_pressed())

            line_offset = (line_offset + base_speed) % 60

            # spawn enemy cars (faster as the game gets harder)
            spawn_timer += 1
            spawn_delay = max(25, 60 - int(score // 200))
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                enemies.append(Enemy(base_speed))

            for enemy in enemies:
                enemy.update()

            # remove cars that left the screen and add score
            for enemy in enemies[:]:
                if enemy.rect.top > HEIGHT:
                    enemies.remove(enemy)
                    score += 10

            # collision (slightly smaller hitbox = fairer)
            hitbox = player.rect.inflate(-10, -10)
            for enemy in enemies:
                if hitbox.colliderect(enemy.rect.inflate(-10, -10)):
                    game_over = True
                    high_score = max(high_score, score)

            base_speed = min(5.0 + score / 150, 14)  # speed up slowly, max 14

        # ----- Draw -----
        draw_road(screen, line_offset)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)

        screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font_small.render(f"Best: {max(high_score, score)}", True, WHITE), (10, 40))

        if paused:
            draw_text(screen, "PAUSED", font_big, WHITE, (WIDTH // 2, HEIGHT // 2))
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", font_big, RED, (WIDTH // 2, HEIGHT // 2 - 40))
            draw_text(screen, f"Score: {score}", font_small, WHITE, (WIDTH // 2, HEIGHT // 2 + 10))
            draw_text(screen, "Press SPACE to restart", font_small, YELLOW, (WIDTH // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
