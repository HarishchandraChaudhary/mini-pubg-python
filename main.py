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
pygame.display.set_caption("Mini PUBG 2D - Advanced (Senior UI)")

clock = pygame.time.Clock()

# ===============================
# COLORS
# ===============================

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GREEN = (0, 220, 100)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)
GRAY = (40, 40, 40)
DARK_GREEN = (34, 139, 34)

# ===============================
# FONTS
# ===============================

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 60, bold=True)
small_font = pygame.font.SysFont("Arial", 18)

# ===============================
# CLASSES
# ===============================

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.ammo = 30
        self.max_ammo = 30
        self.reloading = False
        self.reload_time = 0
        self.reload_duration = 2000

    def update(self, keys, mouse_pos):
        # Movement
        speed = self.speed
        if keys[pygame.K_LSHIFT]:
            speed = 8

        if keys[pygame.K_w]:
            self.y -= speed
        if keys[pygame.K_s]:
            self.y += speed
        if keys[pygame.K_a]:
            self.x -= speed
        if keys[pygame.K_d]:
            self.x += speed

        # Boundaries
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def shoot(self, mouse_pos, bullet_list):
        mx, my = mouse_pos
        angle = math.atan2(my - self.y, mx - self.x)

        if self.ammo > 0 and not self.reloading:
            bullet_list.append(
                Bullet(
                    x=self.x,
                    y=self.y,
                    dx=math.cos(angle) * 15,
                    dy=math.sin(angle) * 15,
                )
            )
            self.ammo -= 1

    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_time = pygame.time.get_ticks()

    def finish_reload(self):
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_time >= self.reload_duration:
                self.ammo = self.max_ammo
                self.reloading = False

    def draw(self, screen, mouse_pos):
        mx, my = mouse_pos
        angle = math.atan2(my - self.y, mx - self.x)

        # Shadow
        shadow_offset = 4
        pygame.draw.circle(screen, BLACK, (int(self.x + shadow_offset), int(self.y + shadow_offset)), self.radius)

        # Body
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

        # Gun
        gun_x = self.x + math.cos(angle) * 40
        gun_y = self.y + math.sin(angle) * 40
        pygame.draw.line(screen, BLACK, (self.x, self.y), (gun_x, gun_y), 8)


class Bullet:
    def __init__(self, x, y, dx, dy, radius=5):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

    def is_out_of_bounds(self, w, h):
        return self.x < 0 or self.x > w or self.y < 0 or self.y > h


class Enemy:
    def __init__(self, x, y, difficulty=1.0):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = random.uniform(1.5, 3.0) * difficulty
        self.health = 100 * difficulty
        self.max_health = self.health

    def update(self, player_x, player_y):
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, screen, player_x, player_y):
        # Enemy body
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

        # Health bar above head
        bar_width = 50
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 35

        # Background (red)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 6))
        # Foreground (green)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_ratio), 6))

    def collides(self, other_x, other_y, other_radius):
        dx = other_x - self.x
        dy = other_y - self.y
        dist = math.hypot(dx, dy)
        return dist < self.radius + other_radius


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.life = 20
        self.max_life = 20

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        alpha_ratio = self.life / self.max_life
        color = tuple(int(c * alpha_ratio) for c in YELLOW)
        radius = int(3 * alpha_ratio)
        if radius > 0:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)

    def is_dead(self):
        return self.life <= 0


# ===============================
# GAME MANAGER
# ===============================

class GameManager:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.score = 0
        self.wave = 1
        self.difficulty = 1.0
        self.spawn_timer = 0
        self.spawn_delay = 1000  # ms
        self.running = True
        self.game_over = False

    def spawn_enemy(self):
        side = random.randint(0, 3)
        radius = 20

        if side == 0:
            x = random.randint(0, WIDTH)
            y = -radius - 10
        elif side == 1:
            x = WIDTH + radius + 10
            y = random.randint(0, HEIGHT)
        elif side == 2:
            x = random.randint(0, WIDTH)
            y = HEIGHT + radius + 10
        else:
            x = -radius - 10
            y = random.randint(0, HEIGHT)

        self.enemies.append(Enemy(x, y, difficulty=self.difficulty))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.restart()
                else:
                    self.player.shoot(pygame.mouse.get_pos(), self.bullets)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.player.start_reload()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        dt = clock.tick(60)
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer -= self.spawn_delay
            self.spawn_enemy()

        self.player.update(keys, mouse_pos)
        self.player.finish_reload()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds(WIDTH, HEIGHT):
                self.bullets.remove(bullet)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y)

            # Player collision
            if enemy.collides(self.player.x, self.player.y, self.player.radius):
                self.player.health -= 0.2

            # Bullet collision
            for bullet in self.bullets[:]:
                if enemy.collides(bullet.x, bullet.y, bullet.radius):
                    enemy.health -= 50
                    self.create_particles(enemy.x, enemy.y)

                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10
                    break

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.is_dead():
                self.particles.remove(p)

        if self.player.health <= 0:
            self.game_over = True

    def create_particles(self, x, y):
        for _ in range(10):
            self.particles.append(Particle(x, y))

    def draw_background(self):
        screen.fill(DARK_GREEN)

        # Grid over green
        grid_color = (40, 160, 40)
        spacing = 60
        for x in range(0, WIDTH, spacing):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

    def draw_hud(self):
        # Health bar
        bar_x, bar_y = 20, 20
        bar_width = 300
        bar_height = 30

        # Background
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        # Health
        health_width = int(bar_width * (self.player.health / self.player.max_health))
        pygame.draw.rect(
            screen,
            GREEN,
            (bar_x, bar_y, health_width, bar_height),
            border_radius=8
        )
        # Text
        draw_text(
            f"Health: {int(self.player.health)}",
            font,
            WHITE,
            bar_x + 14,
            bar_y + 7,
        )

        # Ammo bar
        ammo_bar_x, ammo_bar_y = 20, 60
        ammo_bar_width = 300
        ammo_bar_height = 20

        pygame.draw.rect(screen, GRAY, (ammo_bar_x, ammo_bar_y, ammo_bar_width, ammo_bar_height), border_radius=6)
        # Ammo current
        ammo_width = int(ammo_bar_width * (self.player.ammo / self.player.max_ammo))
        color = GREEN if not self.player.reloading else YELLOW
        pygame.draw.rect(
            screen,
            color,
            (ammo_bar_x, ammo_bar_y, ammo_width, ammo_bar_height),
            border_radius=6
        )
        # Text
        ammo_text = f"Ammo: {self.player.ammo}/{self.player.max_ammo}"
        if self.player.reloading:
            ammo_text += " - Reloading..."
        draw_text(ammo_text, small_font, WHITE, ammo_bar_x + 8, ammo_bar_y + 4)

        # Score
        score_text = f"Score: {self.score}"
        draw_text(score_text, font, WHITE, WIDTH - 230, 30)

        # Wave
        wave_text = f"Wave: {self.wave}"
        draw_text(wave_text, small_font, WHITE, WIDTH - 230, 70)

        # Minimap
        mini_x, mini_y = WIDTH - 220, HEIGHT - 220
        mini_w, mini_h = 200, 200

        pygame.draw.rect(screen, BLACK, (mini_x, mini_y, mini_w, mini_h), border_radius=8)
        pygame.draw.rect(screen, DARK_GREEN, (mini_x + 2, mini_y + 2, mini_w - 4, mini_h - 4), border_radius=6)

        # Player dot on minimap
        mini_px = mini_x + 100 + int((self.player.x - WIDTH // 2) * 0.2)
        mini_py = mini_y + 100 + int((self.player.y - HEIGHT // 2) * 0.2)
        pygame.draw.circle(screen, BLUE, (mini_px, mini_py), 5)

        # Enemies on minimap
        for enemy in self.enemies:
            ex = mini_x + 100 + int((enemy.x - WIDTH // 2) * 0.2)
            ey = mini_y + 100 + int((enemy.y - HEIGHT // 2) * 0.2)
            pygame.draw.circle(screen, RED, (ex, ey), 3)

        # Crosshair
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, WHITE, (mx, my), 15, 2)

        # Lines
        line_len = 20
        pygame.draw.line(screen, WHITE, (mx - line_len, my), (mx + line_len, my), 2)
        pygame.draw.line(screen, WHITE, (mx, my - line_len), (mx, my + line_len), 2)

    def draw_game_over(self):
        screen.fill((20, 10, 20))

        draw_text("GAME OVER", big_font, RED, WIDTH // 2 - 230, HEIGHT // 2 - 80)
        draw_text(f"Final Score: {self.score}", font, WHITE, WIDTH // 2 - 120, HEIGHT // 2 - 10)
        draw_text("Wave Reached: " + str(self.wave), font, WHITE, WIDTH // 2 - 140, HEIGHT // 2 + 40)

        draw_text("Click to restart or press ESC to quit", small_font, WHITE, WIDTH // 2 - 180, HEIGHT // 2 + 100)

    def restart(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.bullets.clear()
        self.enemies.clear()
        self.particles.clear()
        self.score = 0
        self.wave = 1
        self.difficulty = 1.0
        self.spawn_delay = 1000
        self.game_over = False

    def run(self):
        while self.running:
            self.handle_events()
            if not self.game_over:
                self.draw_background()
                self.player.draw(screen, pygame.mouse.get_pos())
                for bullet in self.bullets:
                    bullet.draw(screen)
                for enemy in self.enemies:
                    enemy.draw(screen, self.player.x, self.player.y)
                for p in self.particles:
                    p.draw(screen)
                self.draw_hud()
            else:
                self.draw_game_over()
            pygame.display.update()

        pygame.quit()
        sys.exit()


def draw_text(text, font_obj, color, x, y):
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    manager = GameManager()
    manager.run()