import pgzrun
from pgzero.actor import Actor
from pygame import Rect
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Dungeon Escape - Roguelike Skeleton"

TILE_SIZE = 48
HERO_SPEED = 160
ENEMY_SPEED = 90

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"

music_on = True

try:
    music.play("background")
    music.pause()
except Exception:
    music_on = False


class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = Rect(x, y, width, height)
        self.callback = callback

    def draw(self):
        screen.draw.filled_rect(self.rect, "darkslategray")
        screen.draw.rect(self.rect, "white")
        screen.draw.textbox(
            self.text,
            self.rect,
            color="white",
            align=("center", "center"),
        )

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()


class Hero:
    def __init__(self, pos):
        self.x, self.y = pos
        self.speed = HERO_SPEED
        # Só uma imagem por estado
        self.images = {
            "idle": "hero_idle",
            "walk": "hero_walk"
        }
        self.state = "idle"
        self.actor = Actor(self.images[self.state], (self.x, self.y))

    def update(self, dt):
        dx = 0
        dy = 0
        if keyboard.left:
            dx -= 1
        if keyboard.right:
            dx += 1
        if keyboard.up:
            dy -= 1
        if keyboard.down:
            dy += 1

        moving = (dx != 0) or (dy != 0)

        if moving:
            self.state = "walk"
            norm = math.hypot(dx, dy)
            if norm != 0:
                dx /= norm
                dy /= norm
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
        else:
            self.state = "idle"

        self.x = max(16, min(WIDTH - 16, self.x))
        self.y = max(16, min(HEIGHT - 16, self.y))

        # Atualiza a imagem do ator para o estado atual (sem animação)
        self.actor.image = self.images[self.state]
        self.actor.pos = (self.x, self.y)

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, pos, patrol_rect):
        self.x, self.y = pos
        self.speed = ENEMY_SPEED
        self.patrol_rect = patrol_rect
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle)
        self.vy = math.sin(angle)
        self.images = {
            "idle": "enemy_idle",
            "walk": "enemy_walk"
        }
        self.state = "walk"
        self.actor = Actor(self.images[self.state], (self.x, self.y))
        self.change_timer = random.uniform(1.0, 3.0)

    def update(self, dt, hero_pos):
        dx = hero_pos[0] - self.x
        dy = hero_pos[1] - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            dx /= dist
            dy /= dist

            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt

        self.actor.image = self.images[self.state]
        self.actor.pos = (self.x, self.y)


    def draw(self):
        self.actor.draw()

    def collides_with_actor(self, actor):
        return self.actor.colliderect(actor.actor)


game_state = STATE_MENU
hero = Hero((WIDTH // 2, HEIGHT // 2))
enemies = [
    Enemy((200, 200), Rect(150, 150, 200, 200)),
    Enemy((600, 400), Rect(520, 320, 160, 160)),
]

buttons = []

def start_game():
    global game_state, hero, enemies
    game_state = STATE_PLAYING
    hero.x, hero.y = WIDTH // 2, HEIGHT // 2
    if music_on:
        try:
            music.unpause()
        except Exception:
            pass

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        try:
            music.unpause()
        except Exception:
            pass
    else:
        try:
            music.pause()
        except Exception:
            pass

def exit_game():
    global game_state
    game_state = STATE_GAMEOVER

button_width = 220
button_height = 54
buttons.append(Button("Start Game", WIDTH // 2 - button_width // 2, 180, button_width, button_height, start_game))
buttons.append(Button("Music On/Off", WIDTH // 2 - button_width // 2, 260, button_width, button_height, toggle_music))
buttons.append(Button("Exit", WIDTH // 2 - button_width // 2, 340, button_width, button_height, exit_game))

def update(dt):
    global game_state
    if game_state == STATE_PLAYING:
        hero.update(dt)
        for enemy in enemies:
            enemy.update(dt, (hero.x, hero.y))
            if enemy.collides_with_actor(hero):
                sounds.hit.play()
                game_state = STATE_GAMEOVER

def draw():
    screen.clear()
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_PLAYING:
        draw_game()
    elif game_state == STATE_GAMEOVER:
        draw_gameover()

def draw_menu():
    screen.fill((30, 30, 40))
    screen.draw.text("DUNGEON ESCAPE",
                     center=(WIDTH // 2, 100),
                     fontsize=56,
                     color="white")
    for btn in buttons:
        btn.draw()

def draw_game():
    for x in range(0, WIDTH, TILE_SIZE):
        screen.draw.line((x, 0), (x, HEIGHT), (50, 50, 60))
    for y in range(0, HEIGHT, TILE_SIZE):
        screen.draw.line((0, y), (WIDTH, y), (50, 50, 60))

    hero.draw()
    for enemy in enemies:
        enemy.draw()

def draw_gameover():
    screen.fill((0, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=72, color="red")
    screen.draw.text("Press Space to return to Menu", center=(WIDTH // 2, HEIGHT // 2 + 40), fontsize=28, color="white")

def on_mouse_down(pos):
    if game_state == STATE_MENU:
        for btn in buttons:
            btn.check_click(pos)

def on_key_down(key):
    global game_state
    if game_state == STATE_GAMEOVER and key == keys.SPACE:
        game_state = STATE_MENU
        try:
            music.stop()
        except Exception:
            pass

pgzrun.go()
