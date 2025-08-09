import pgzrun
from pgzero.actor import Actor
from pygame import Rect
import random
import math

WIDTH = 800
HEIGHT = 600
TITLE = "Escape from Scrabby - Roguelike Skeleton"

TILE_SIZE = 48
HERO_SPEED = 160
ENEMY_SPEED = 90

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
STATE_DYING = "dying"
death_timer = 0
death_duration = 2.0

music_on = True

try:
    music.play("background")
except Exception:
    pass


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


class AnimatedActor:
    def __init__(self, animations, pos):
        """
        animations: dict com chaves de estado e valores listas com nomes das imagens (sem extensão)
        pos: posição inicial (tupla)
        """
        self.animations = animations
        self.state = 'idle'
        self.frame_index = 0
        self.frame_time = 0
        self.frame_duration = 0.15  # tempo entre frames em segundos
        self.pos = pos
        self.actor = Actor(self.animations[self.state][self.frame_index], pos)

    def update(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.actor.image = self.animations[self.state][self.frame_index]
        self.actor.pos = self.pos

    def change_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.frame_time = 0
            self.actor.image = self.animations[self.state][self.frame_index]

    def draw(self):
        self.actor.draw()


class Hero:
    def __init__(self, pos):
        self.animations = {
            'idle': [f'hero_idle_{i}' for i in range(8)],
            'walk': [f'hero_walk_{i}' for i in range(6)],
            'dead': [f'hero_dead_{i}' for i in range(4)],
        }
        self.state = 'idle'
        self.frame_index = 0
        self.frame_time = 0
        self.frame_duration = 0.15  # tempo entre frames
        self.pos = list(pos)
        self.speed = 120
        self.is_dead = False
        self.actor = Actor(self.animations[self.state][self.frame_index], self.pos)

    def update(self, dt, sprinting=False):
        if self.is_dead:
            self.change_state('dead')
            self.animate(dt)
            return

        dx, dy = 0, 0
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
            speed = self.speed * (2 if sprinting else 1)
            norm = math.hypot(dx, dy)
            dx /= norm
            dy /= norm
            self.pos[0] += dx * speed * dt
            self.pos[1] += dy * speed * dt
            self.change_state('walk')
        else:
            self.change_state('idle')

        self.animate(dt)
        self.actor.pos = tuple(self.pos)

    def change_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.frame_time = 0
            self.actor.image = self.animations[self.state][self.frame_index]

    def animate(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.actor.image = self.animations[self.state][self.frame_index]

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, pos, territory):
        self.animations = {
            'walk': [f'enemy_walk_{i}' for i in range(6)],
        }
        self.state = 'walk'
        self.frame_index = 0
        self.frame_time = 0
        self.frame_duration = 0.15
        self.pos = list(pos)
        self.speed = 100
        self.is_dead = False
        self.actor = Actor(self.animations[self.state][self.frame_index], self.pos)
        self.territory = territory  # pygame.Rect definindo onde o inimigo pode se mover

    def update(self, dt, hero_pos):
        if self.is_dead:
            return

        dx = hero_pos[0] - self.pos[0]
        dy = hero_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist > 5:  # só persegue se estiver a mais de 5 pixels
            dx /= dist
            dy /= dist

            new_x = self.pos[0] + dx * self.speed * dt
            new_y = self.pos[1] + dy * self.speed * dt

            # limita movimento ao território
            if self.territory.left <= new_x <= self.territory.right:
                self.pos[0] = new_x
            if self.territory.top <= new_y <= self.territory.bottom:
                self.pos[1] = new_y

        self.animate(dt)
        self.actor.pos = tuple(self.pos)

    def animate(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.actor.image = self.animations[self.state][self.frame_index]

    def draw(self):
        self.actor.draw()


game_state = STATE_MENU
hero = Hero((WIDTH // 2, HEIGHT // 2))
entire_map = Rect(0, 0, WIDTH, HEIGHT)
enemies = [
    Enemy((200, 200), entire_map),
    Enemy((600, 400), entire_map),
]

buttons = []

def start_game():
    global game_state, hero, enemies
    game_state = STATE_PLAYING
    hero.pos = [WIDTH // 2, HEIGHT // 2]  # atualiza a posição do herói
    hero.is_dead = False 
    hero.change_state('idle')
    entire_map = Rect(0, 0, WIDTH, HEIGHT)
    enemies = [
        Enemy((200, 200), entire_map),
        Enemy((600, 400), entire_map),
    ]


def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        try:
            music.unpause()
        except Exception:
            try:
                music.play("background")
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
    global game_state, death_timer
    if game_state == STATE_PLAYING:
        hero.update(dt)
        for enemy in enemies:
            enemy.update(dt, tuple(hero.pos))
            dx = hero.pos[0] - enemy.actor.pos[0]
            dy = hero.pos[1] - enemy.actor.pos[1]
            dist = math.hypot(dx, dy)
            if dist < 10:
                if game_state != STATE_DYING:
                    sounds.hit.play()
                    game_state = STATE_DYING
                    hero.is_dead = True
                    death_timer = 0
    
    elif game_state == STATE_DYING:
        hero.update(dt)
        death_timer += dt
        if death_timer >= death_duration:
            game_state = STATE_GAMEOVER
                

def draw():
    screen.clear()
    if game_state == STATE_MENU:
        draw_menu()
    elif game_state == STATE_PLAYING or game_state == STATE_DYING:
        draw_game()
    elif game_state == STATE_GAMEOVER:
        draw_gameover()

def draw_menu():
    img = images.menu_background
    img_width = img.get_width()
    img_height = img.get_height()

    x = (WIDTH - img_width) // 2
    y = (HEIGHT - img_height) // 2

    screen.blit("menu_background", (x, y))  
    screen.draw.text("ESCAPE FROM CRABBY",
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

pgzrun.go()
