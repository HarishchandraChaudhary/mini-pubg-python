import pygame
import random
import math
import sys

pygame.init()

# Screen
WIDTH = 1200
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini PUBG 2D")

clock = pygame.time.Clock()

# Colors
GREEN = (16, 185, 129)
BLUE = (59, 130, 246)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont("Arial", 30)

# Player
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_size = 20
player_speed = 5
player_health = 100

# Bullets
bullets = []

# Enemies
enemies = []

# Score
score = 0

# Enemy Spawn Event
SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 1200)

running = True

while running:
    clock.tick(60)

    # Background
    screen.fill(GREEN)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot Bullet
        if event.type == pygame.MOUSEBUTTONDOWN:
            angle = math.atan2(mouse_y - player_y, mouse_x - player_x)

            bullet = {
                "x": player_x,
                "y": player_y,
                "dx": math.cos(angle) * 10,
                "dy": math.sin(angle) * 10,
                "size": 5
            }

            bullets.append(bullet)

        # Spawn Enemy
        if event.type == SPAWN_ENEMY:
            side = random.randint(0, 3)

            if side == 0:
                x = random.randint(0, WIDTH)
                y = -30

            elif side == 1:
                x = WIDTH + 30
                y = random.randint(0, HEIGHT)

            elif side == 2:
                x = random.randint(0, WIDTH)
                y = HEIGHT + 30

            else:
                x = -30
                y = random.randint(0, HEIGHT)

            enemy = {
                "x": x,
                "y": y,
                "size": 20,
                "speed": random.uniform(1, 2)
            }

            enemies.append(enemy)

    # Movement
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed

    if keys[pygame.K_s]:
        player_y += player_speed

    if keys[pygame.K_a]:
        player_x -= player_speed

    if keys[pygame.K_d]:
        player_x += player_speed

    # Keep Player Inside Screen
    player_x = max(0, min(WIDTH, player_x))
    player_y = max(0, min(HEIGHT, player_y))

    # Draw Player
    pygame.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_size)

    # Gun Direction
    angle = math.atan2(mouse_y - player_y, mouse_x - player_x)

    gun_x = player_x + math.cos(angle) * 30
    gun_y = player_y + math.sin(angle) * 30

    pygame.draw.line(
        screen,
        WHITE,
        (player_x, player_y),
        (gun_x, gun_y),
        6
    )

    # Update Bullets
    for bullet in bullets[:]:
        bullet["x"] += bullet["dx"]
        bullet["y"] += bullet["dy"]

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(bullet["x"]), int(bullet["y"])),
            bullet["size"]
        )

        if (
            bullet["x"] < 0 or
            bullet["x"] > WIDTH or
            bullet["y"] < 0 or
            bullet["y"] > HEIGHT
        ):
            bullets.remove(bullet)

    # Update Enemies
    for enemy in enemies[:]:
        angle = math.atan2(player_y - enemy["y"], player_x - enemy["x"])

        enemy["x"] += math.cos(angle) * enemy["speed"]
        enemy["y"] += math.sin(angle) * enemy["speed"]

        pygame.draw.circle(
            screen,
            RED,
            (int(enemy["x"]), int(enemy["y"])),
            enemy["size"]
        )

        # Collision with Player
        dist_to_player = math.hypot(
            player_x - enemy["x"],
            player_y - enemy["y"]
        )

        if dist_to_player < player_size + enemy["size"]:
            player_health -= 0.2

        # Bullet Collision
        for bullet in bullets[:]:
            dist = math.hypot(
                bullet["x"] - enemy["x"],
                bullet["y"] - enemy["y"]
            )

            if dist < bullet["size"] + enemy["size"]:
                if enemy in enemies:
                    enemies.remove(enemy)

                if bullet in bullets:
                    bullets.remove(bullet)

                score += 10
                break

    # HUD
    health_text = font.render(
        f"Health: {int(player_health)}",
        True,
        WHITE
    )

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(health_text, (20, 20))
    screen.blit(score_text, (20, 60))

    # Game Over
    if player_health <= 0:
        game_over = font.render(
            f"GAME OVER - Score: {score}",
            True,
            WHITE
        )

        screen.blit(game_over, (WIDTH // 2 - 180, HEIGHT // 2))

        pygame.display.update()
        pygame.time.delay(3000)

        running = False

    pygame.display.update()

pygame.quit()
sys.exit()