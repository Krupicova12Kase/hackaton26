"""
Univerzálna kostra pygame hry.

Spustenie:
    pip install -r requirements.txt
    python3 main.py

Štruktúra:
    Game   – okno, hlavná slučka, prepínanie scén
    Scene  – základná trieda; každá obrazovka (menu, hra, ...) je jedna scéna
             s metódami handle_event / update / draw
"""
import os
import sys

import pygame

# ---------------------------------------------------------------- nastavenia
TITLE = "Hackathon 26"
WIDTH, HEIGHT = 960, 540
FPS = 60
BG_COLOR = (25, 25, 35)
TEXT_COLOR = (240, 240, 240)

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def asset(name):
    """Cesta k súboru v priečinku assets/."""
    return os.path.join(ASSETS, name)


# ---------------------------------------------------------------- scény
class Scene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class MenuScene(Scene):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.game.change_scene(PlayScene(self.game))

    def draw(self, screen):
        self.game.draw_text(TITLE, 64, WIDTH // 2, HEIGHT // 2 - 40)
        self.game.draw_text("SPACE = štart   ESC = koniec", 28, WIDTH // 2, HEIGHT // 2 + 30)


class PlayScene(Scene):
    """Ukážková scéna: štvorec ovládaný šípkami / WASD. Nahraď vlastnou hrou."""

    SPEED = 300  # px / s

    def __init__(self, game):
        super().__init__(game)
        self.player = pygame.Rect(0, 0, 40, 40)
        self.player.center = (WIDTH // 2, HEIGHT // 2)
        self.pos = pygame.Vector2(self.player.topleft)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        if move.length_squared():
            move = move.normalize()
        self.pos += move * self.SPEED * dt
        self.pos.x = max(0, min(WIDTH - self.player.w, self.pos.x))
        self.pos.y = max(0, min(HEIGHT - self.player.h, self.pos.y))
        self.player.topleft = (round(self.pos.x), round(self.pos.y))

    def draw(self, screen):
        pygame.draw.rect(screen, (90, 200, 255), self.player, border_radius=6)
        self.game.draw_text("Šípky / WASD = pohyb   ESC = menu", 22, WIDTH // 2, 24)


# ---------------------------------------------------------------- hra
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.running = True
        self.scene = MenuScene(self)

    def change_scene(self, scene):
        self.scene = scene

    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("arial", size, bold=True)
        return self.fonts[size]

    def draw_text(self, text, size, x, y, color=TEXT_COLOR):
        img = self.font(size).render(text, True, color)
        self.screen.blit(img, img.get_rect(center=(x, y)))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                      and isinstance(self.scene, MenuScene)):
                    self.running = False
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)
            self.screen.fill(BG_COLOR)
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
