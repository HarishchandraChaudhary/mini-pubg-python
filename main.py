import pygame
import random
import math
import sys

pygame.init()
pygame.mixer.init()

# ===============================
# SCREEN SETTINGS
# ===============================
WIDTH = 1400
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini PUBG 2D - Advanced")

clock = pygame.time.Clock()

# ===============================
# COLORS
# ===============================
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 255, 100)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)
GRAY = (40, 40, 40)

# ===============================
# FONTS
# ===============================
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 50)

# ===============================
# PLAYER
# ===============================
player = {
    "x": WIDTH // 2,
    "y": HEIGHT // 2,
    "radius": 25,
    "speed": 5,
    "health": 100,
    "ammo": 30,
    "max_ammo": 30,
    "reloading": False,
    "reload_time": 0
}

# ===============================
# BULLETS
# ===============================
bullets = []

# ===============================
# PARTICLES
# ===============================
particles = []

# ===============================
# ENEMIES
# ===============================
enemies = []

# ===============================
# SCORE
# ===============================
score = 0

# ===============================
# ENEMY SPAWN TIMER
# ===============================
SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 1000)

# ===============================
# FUNCTIONS
# ===============================

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def spawn_enemy():
    side = random.randint(0, 3)

    if side == 0:
        x = random.randint(0, WIDTH)
        y = -50

    elif side == 1:
        x = WIDTH + 50
        y = random.randint(0, HEIGHT)

    elif side == 2:
        x = random.randint(0, WIDTH)
        y = HEIGHT + 50

    else:
        x = -50
        y = random.randint(0, HEIGHT)

    enemy = {
        "x": x,
        "y": y,
        "radius": 20,
        "speed": random.uniform(1.5, 3),
        "health": 100
    }

    enemies.append(enemy)

def create_particles(x, y):
    for _ in range(10):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-3, 3),
            "dy": random.uniform(-3, 3),
            "life": 20
        })

# ===============================
# MAIN LOOP
# ===============================

running = True

while running:

    dt = clock.tick(60)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ===============================
    # EVENTS
    # ===============================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Spawn enemies
        if event.type == SPAWN_ENEMY:
            spawn_enemy()

        # Shoot
        if event.type == pygame.MOUSEBUTTONDOWN:

            if player["ammo"] > 0 and not player["reloading"]:

                angle = math.atan2(
                    mouse_y - player["y"],
                    mouse_x - player["x"]
                )

                bullets.append({
                    "x": player["x"],
                    "y": player["y"],
                    "dx": math.cos(angle) * 15,
                    "dy": math.sin(angle) * 15,
                    "radius": 5
                })

                player["ammo"] -= 1

        # Reload
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player["reloading"] = True
                player["reload_time"] = pygame.time.get_ticks()

    # ===============================
    # BACKGROUND
    # ===============================

    screen.fill((34, 139, 34))

    # Grid effect
    for x in range(0, WIDTH, 60):
        pygame.draw.line(screen, (40, 150, 40), (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (40, 150, 40), (0, y), (WIDTH, y))

    # ===============================
    # PLAYER MOVEMENT
    # ===============================

    keys = pygame.key.get_pressed()

    speed = player["speed"]

    # Sprint
    if keys[pygame.K_LSHIFT]:
        speed = 8

    if keys[pygame.K_w]:
        player["y"] -= speed

    if keys[pygame.K_s]:
        player["y"] += speed

    if keys[pygame.K_a]:
        player["x"] -= speed

    if keys[pygame.K_d]:
        player["x"] += speed

    # Boundaries
    player["x"] = max(0, min(WIDTH, player["x"]))
    player["y"] = max(0, min(HEIGHT, player["y"]))

    # ===============================
    # PLAYER DRAW
    # ===============================

    angle = math.atan2(
        mouse_y - player["y"],
        mouse_x - player["x"]
    )

    # Shadow
    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (int(player["x"] + 4), int(player["y"] + 4)),
        player["radius"]
    )

    # Body
    pygame.draw.circle(
        screen,
        BLUE,
        (int(player["x"]), int(player["y"])),
        player["radius"]
    )

    # Gun
    gun_x = player["x"] + math.cos(angle) * 40
    gun_y = player["y"] + math.sin(angle) * 40

    pygame.draw.line(
        screen,
        BLACK,
        (player["x"], player["y"]),
        (gun_x, gun_y),
        8
    )

    # ===============================
    # BULLETS
    # ===============================

    for bullet in bullets[:]:

        bullet["x"] += bullet["dx"]
        bullet["y"] += bullet["dy"]

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(bullet["x"]), int(bullet["y"])),
            bullet["radius"]
        )

        if (
            bullet["x"] < 0 or
            bullet["x"] > WIDTH or
            bullet["y"] < 0 or
            bullet["y"] > HEIGHT
        ):
            bullets.remove(bullet)

    # ===============================
    # ENEMIES
    # ===============================

    for enemy in enemies[:]:

        angle = math.atan2(
            player["y"] - enemy["y"],
            player["x"] - enemy["x"]
        )

        enemy["x"] += math.cos(angle) * enemy["speed"]
        enemy["y"] += math.sin(angle) * enemy["speed"]

        # Enemy draw
        pygame.draw.circle(
            screen,
            RED,
            (int(enemy["x"]), int(enemy["y"])),
            enemy["radius"]
        )

        # Enemy health bar
        pygame.draw.rect(
            screen,
            RED,
            (
                enemy["x"] - 20,
                enemy["y"] - 35,
                40,
                5
            )
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                enemy["x"] - 20,
                enemy["y"] - 35,
                enemy["health"] * 0.4,
                5
            )
        )

        # Collision with player
        dist = math.hypot(
            player["x"] - enemy["x"],
            player["y"] - enemy["y"]
        )

        if dist < player["radius"] + enemy["radius"]:
            player["health"] -= 0.2

        # Bullet collision
        for bullet in bullets[:]:

            dist = math.hypot(
                bullet["x"] - enemy["x"],
                bullet["y"] - enemy["y"]
            )

            if dist < enemy["radius"] + bullet["radius"]:

                enemy["health"] -= 50

                create_particles(enemy["x"], enemy["y"])

                if bullet in bullets:
                    bullets.remove(bullet)

                if enemy["health"] <= 0:
                    enemies.remove(enemy)
                    score += 10

                break

    # ===============================
    # PARTICLES
    # ===============================

    for particle in particles[:]:

        particle["x"] += particle["dx"]
        particle["y"] += particle["dy"]

        particle["life"] -= 1

        pygame.draw.circle(
            screen,
            YELLOW,
            (int(particle["x"]), int(particle["y"])),
            3
        )

        if particle["life"] <= 0:
            particles.remove(particle)

    # ===============================
    # RELOAD SYSTEM
    # ===============================

    if player["reloading"]:

        now = pygame.time.get_ticks()

        if now - player["reload_time"] > 2000:
            player["ammo"] = player["max_ammo"]
            player["reloading"] = False

    # ===============================
    # UI
    # ===============================

    # Health Bar
    pygame.draw.rect(screen, GRAY, (20, 20, 300, 30))
    pygame.draw.rect(
        screen,
        GREEN,
        (20, 20, player["health"] * 3, 30)
    )

    draw_text(
        f"Health: {int(player['health'])}",
        font,
        WHITE,
        25,
        22
    )

    # Ammo
    draw_text(
        f"Ammo: {player['ammo']}/{player['max_ammo']}",
        font,
        WHITE,
        20,
        70
    )

    # Reloading
    if player["reloading"]:
        draw_text(
            "Reloading...",
            font,
            YELLOW,
            20,
            110
        )

    # Score
    draw_text(
        f"Score: {score}",
        font,
        WHITE,
        WIDTH - 200,
        20
    )

    # Minimap
    pygame.draw.rect(
        screen,
        BLACK,
        (WIDTH - 220, HEIGHT - 220, 200, 200)
    )

    pygame.draw.circle(
        screen,
        BLUE,
        (WIDTH - 120, HEIGHT - 120),
        5
    )

    # Crosshair
    pygame.draw.circle(
        screen,
        WHITE,
        (mouse_x, mouse_y),
        15,
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mouse_x - 20, mouse_y),
        (mouse_x + 20, mouse_y),
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mouse_x, mouse_y - 20),
        (mouse_x, mouse_y + 20),
        2
    )

    # ===============================
    # GAME OVER
    # ===============================

    if player["health"] <= 0:

        draw_text(
            "GAME OVER",
            big_font,
            RED,
            WIDTH // 2 - 180,
            HEIGHT // 2 - 50
        )

        draw_text(
            f"Final Score: {score}",
            font,
            WHITE,
            WIDTH // 2 - 90,
            HEIGHT // 2 + 20
        )

        pygame.display.update()
        pygame.time.delay(4000)

        running = False

    pygame.display.update()

pygame.quit()
sys.exit()