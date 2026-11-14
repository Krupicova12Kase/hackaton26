"""
BOING RUN – auto-runner, kde je všetko skákavé.

Ovládanie:
  SPACE / ŠÍPKA HORE / KLIK  – skok (drž = skáče pri každom dopade)
  ŠÍPKA DOLE / S             – SLAM vo vzduchu (tvrdý dopad = super odraz)
  R                          – reštart
  ESC                        – koniec

Spustenie:  pip install pygame-ce   a potom   python3 main.py
"""
import math
import random
import sys

import pygame

# ---------------------------------------------------------------- nastavenia
W, H = 960, 540
FPS = 60
TILE = 40
GROUND_Y = 440
SPEED = 6.5            # px / frame
GRAVITY = 0.9
JUMP_V = 15.0
SUPER_JUMP_V = 19.0    # skok hneď po slame
PAD_V = 21.0
SLAM_V = 20.0
RESTITUTION = 0.55     # pružnosť pri bežnom dopade
MIN_BOUNCE = 5.0       # aby sa hráč stále jemne odrážal
MAX_BOUNCE = 22.0
PLAYER_SIZE = 34
PLAYER_SCREEN_X = 220
JUMP_WINDOW = 26       # px nad povrchom, kedy ešte uznáme stlačenie skoku

COL_BG_TOP = (28, 10, 60)
COL_BG_BOT = (90, 20, 110)
COL_GROUND = (20, 8, 40)
COL_LINE = (255, 120, 230)
COL_PLAYER = (120, 255, 200)
COL_PLAYER_EYE = (20, 20, 40)
COL_SPIKE = (255, 80, 110)
COL_BLOCK = (70, 50, 160)
COL_BLOCK_EDGE = (160, 140, 255)
COL_PAD = (255, 220, 60)
COL_TEXT = (255, 255, 255)


# ---------------------------------------------------------------- level
def build_level():
    """Vráti zoznam objektov (typ, rect) v herných súradniciach."""
    objs = []

    def spike(tx, n=1, ty=0):
        for i in range(n):
            x = (tx + i) * TILE
            objs.append(("spike", pygame.Rect(x, GROUND_Y - (ty + 1) * TILE, TILE, TILE)))

    def block(tx, w=1, h=1, ty=0):
        objs.append(("block", pygame.Rect(tx * TILE, GROUND_Y - (ty + h) * TILE,
                                          w * TILE, h * TILE)))

    def pad(tx, ty=0):
        objs.append(("pad", pygame.Rect(tx * TILE + 4, GROUND_Y - ty * TILE - 10,
                                        TILE - 8, 10)))

    # rozbeh
    spike(20)
    spike(30)
    spike(40, 2)
    spike(52, 3)
    # schody z blokov
    block(64, 2, 1)
    block(68, 2, 2)
    block(72, 3, 3)
    spike(75, 3)
    # pružiny
    pad(86)
    spike(88, 5)
    pad(100)
    block(103, 4, 4)
    spike(107, 4)
    # rytmus
    for k in range(5):
        spike(116 + k * 6)
    # plošiny so spikmi
    block(150, 3, 1)
    spike(150, 3, ty=1)          # spiky na bloku -> preskoč
    block(158, 5, 2)
    spike(163, 4)
    pad(170)
    block(174, 4, 4)
    pad(177, ty=4)
    spike(178, 6)
    block(187, 6, 2)
    # finále – rýchla séria
    spike(196, 2)
    spike(203, 3)
    pad(211)
    spike(213, 5)
    spike(224)
    spike(229, 2)

    finish_x = 245 * TILE
    return objs, finish_x


# ---------------------------------------------------------------- efekty
class Particle:
    def __init__(self, x, y, color, speed=4.0, life=40, size=5):
        a = random.uniform(0, math.tau)
        s = random.uniform(0.3, 1.0) * speed
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * s, math.sin(a) * s
        self.life = self.max_life = life
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf, cam_x):
        if self.life <= 0:
            return
        r = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surf, self.color, (int(self.x - cam_x), int(self.y)), r)


# ---------------------------------------------------------------- hráč
class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 0.0
        self.y = GROUND_Y - PLAYER_SIZE
        self.vy = 0.0
        self.slamming = False
        self.squash = 0.0      # >0 sploštený, <0 natiahnutý
        self.angle = 0.0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)


# ---------------------------------------------------------------- hra
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("BOING RUN")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arialrounded,arial", 26, bold=True)
        self.big = pygame.font.SysFont("arialrounded,arial", 64, bold=True)
        self.bg = self.make_bg()
        self.objs, self.finish_x = build_level()
        self.player = Player()
        self.particles = []
        self.attempt = 1
        self.best = 0.0
        self.dead_timer = 0
        self.won = False
        self.started = False
        self.shake = 0.0
        self.pulse = 0.0

    def make_bg(self):
        bg = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            c = [int(COL_BG_TOP[i] + (COL_BG_BOT[i] - COL_BG_TOP[i]) * t) for i in range(3)]
            pygame.draw.line(bg, c, (0, y), (W, y))
        return bg

    # ------------------------------------------------------------ logika
    def restart(self):
        self.player.reset()
        self.particles.clear()
        self.dead_timer = 0
        self.won = False

    def jump_held(self):
        keys = pygame.key.get_pressed()
        return (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
                or pygame.mouse.get_pressed()[0])

    def support_y(self, p):
        """Najvyšší povrch pod hráčom (zem alebo vrch bloku)."""
        best = GROUND_Y
        bottom = p.y + PLAYER_SIZE
        for kind, r in self.objs:
            if kind != "block":
                continue
            if r.right > p.x and r.left < p.x + PLAYER_SIZE and r.top >= bottom - 8:
                best = min(best, r.top)
        return best

    def try_jump(self):
        p = self.player
        if not p.alive or self.won:
            return
        if p.y + PLAYER_SIZE >= self.support_y(p) - JUMP_WINDOW and p.vy > -JUMP_V * 0.5:
            self.do_jump(SUPER_JUMP_V if p.slamming else JUMP_V)

    def do_jump(self, v):
        p = self.player
        p.vy = -v
        p.slamming = False
        p.squash = -0.35
        for _ in range(8):
            self.particles.append(Particle(p.x + PLAYER_SIZE / 2, p.y + PLAYER_SIZE,
                                           COL_PLAYER, 3, 25, 4))

    def slam(self):
        p = self.player
        if p.alive and not self.won and p.y + PLAYER_SIZE < self.support_y(p) - 20:
            p.vy = SLAM_V
            p.slamming = True

    def land(self, surface_y):
        p = self.player
        impact = abs(p.vy)
        p.y = surface_y - PLAYER_SIZE
        if self.jump_held():
            self.do_jump(SUPER_JUMP_V if p.slamming else JUMP_V)
        else:
            rest = 0.95 if p.slamming else RESTITUTION
            p.vy = -min(MAX_BOUNCE, max(MIN_BOUNCE, impact * rest))
            p.slamming = False
            p.squash = min(0.5, impact / 30)
        if impact > 10:
            self.shake = min(10, impact / 2)
            self.pulse = 1.0
            for _ in range(int(impact)):
                self.particles.append(Particle(p.x + PLAYER_SIZE / 2, surface_y,
                                               COL_LINE, 4, 30, 4))

    def die(self):
        p = self.player
        p.alive = False
        self.dead_timer = 50
        self.shake = 14
        cx, cy = p.x + PLAYER_SIZE / 2, p.y + PLAYER_SIZE / 2
        for _ in range(60):
            self.particles.append(Particle(cx, cy, random.choice(
                [COL_PLAYER, COL_LINE, (255, 255, 255)]), 9, 50, 7))

    def update(self):
        self.pulse = max(0.0, self.pulse - 0.05)
        self.shake *= 0.85
        for pt in self.particles:
            pt.update()
        self.particles = [pt for pt in self.particles if pt.life > 0]

        p = self.player
        if not p.alive:
            self.dead_timer -= 1
            if self.dead_timer <= 0:
                self.attempt += 1
                self.restart()
            return
        if self.won or not self.started:
            return

        # horizontálny pohyb + kontrola bočných kolízií
        p.x += SPEED
        p.angle = (p.angle - 7) % 360 if p.vy != 0 else p.angle
        for kind, r in self.objs:
            if kind == "block" and p.rect.colliderect(r):
                if p.y + PLAYER_SIZE - 10 > r.top:   # narazil zboku
                    self.die()
                    return

        # vertikálny pohyb
        prev_bottom = p.y + PLAYER_SIZE
        prev_top = p.y
        p.vy += GRAVITY
        p.y += p.vy
        p.squash *= 0.8

        if p.y + PLAYER_SIZE >= GROUND_Y:
            self.land(GROUND_Y)

        for kind, r in self.objs:
            pr = p.rect
            if not pr.colliderect(r):
                continue
            if kind == "block":
                if prev_bottom <= r.top + 1 and p.vy >= 0:
                    self.land(r.top)
                elif prev_top >= r.bottom - 1 and p.vy < 0:
                    p.y = r.bottom
                    p.vy = 2.0                       # buchnutie hlavou
                else:
                    self.die()
                    return
            elif kind == "spike":
                hit = r.inflate(-TILE * 0.55, -TILE * 0.35)
                hit.bottom = r.bottom
                if pr.inflate(-6, -6).colliderect(hit):
                    self.die()
                    return
            elif kind == "pad" and p.vy >= 0:
                p.y = r.top - PLAYER_SIZE
                p.vy = -PAD_V
                p.slamming = False
                p.squash = -0.45
                self.pulse = 1.0
                for _ in range(20):
                    self.particles.append(Particle(r.centerx, r.top, COL_PAD, 5, 30, 5))

        # stopa
        if random.random() < 0.6:
            self.particles.append(Particle(p.x, p.y + PLAYER_SIZE / 2,
                                           COL_PLAYER, 0.8, 18, 3))

        prog = min(1.0, p.x / self.finish_x)
        self.best = max(self.best, prog)
        if p.x >= self.finish_x:
            self.won = True
            for _ in range(120):
                self.particles.append(Particle(p.x, p.y, random.choice(
                    [COL_PAD, COL_LINE, COL_PLAYER]), 10, 70, 6))

    # ------------------------------------------------------------ kreslenie
    def draw_player(self, cam_x):
        p = self.player
        if not p.alive:
            return
        s = PLAYER_SIZE
        sq = p.squash
        w, h = s * (1 + sq), s * (1 - sq)
        surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        body = pygame.Rect(0, 0, w, h)
        body.center = (s, s)
        pygame.draw.rect(surf, COL_PLAYER, body, border_radius=10)
        pygame.draw.rect(surf, (255, 255, 255), body, 3, border_radius=10)
        ex = body.centerx + w * 0.15
        pygame.draw.circle(surf, COL_PLAYER_EYE, (int(ex), int(body.centery - h * 0.12)), 5)
        pygame.draw.circle(surf, COL_PLAYER_EYE, (int(ex + w * 0.22), int(body.centery - h * 0.12)), 5)
        if p.slamming:
            pygame.draw.line(surf, COL_PLAYER_EYE, (ex - 6, body.centery + 6),
                             (ex + w * 0.3, body.centery + 6), 3)
        else:
            pygame.draw.arc(surf, COL_PLAYER_EYE, (ex - 6, body.centery - 2, w * 0.4, 12),
                            math.pi, math.tau, 3)
        tilt = max(-25, min(25, -p.vy * 1.5))
        surf = pygame.transform.rotate(surf, tilt)
        cx = p.x + s / 2 - cam_x
        cy = p.y + s - h / 2
        self.screen.blit(surf, surf.get_rect(center=(int(cx), int(cy))))

    def draw(self):
        sc = self.screen
        cam_x = self.player.x - PLAYER_SCREEN_X
        ox = random.uniform(-self.shake, self.shake)
        oy = random.uniform(-self.shake, self.shake)
        cam_x += ox

        sc.blit(self.bg, (0, 0))
        # paralaxové stĺpy v pozadí
        for i in range(14):
            bx = (i * 120 - cam_x * 0.3) % (W + 120) - 60
            bh = 120 + (i * 53) % 160 + self.pulse * 30
            pygame.draw.rect(sc, (60, 25, 110), (bx, GROUND_Y - bh + oy, 70, bh))

        # zem
        pygame.draw.rect(sc, COL_GROUND, (0, GROUND_Y + oy, W, H - GROUND_Y))
        line_col = [min(255, int(c + self.pulse * 80)) for c in COL_LINE]
        pygame.draw.line(sc, line_col, (0, GROUND_Y + oy), (W, GROUND_Y + oy), 4)
        for i in range(0, W + TILE, TILE):
            gx = i - cam_x % TILE
            pygame.draw.line(sc, (45, 20, 80), (gx, GROUND_Y + oy + 4), (gx - 30, H), 2)

        # objekty
        for kind, r in self.objs:
            x = r.x - cam_x
            if x > W or x + r.w < -10:
                continue
            rr = pygame.Rect(x, r.y + oy, r.w, r.h)
            if kind == "spike":
                pts = [(rr.left + 3, rr.bottom), (rr.centerx, rr.top + 4), (rr.right - 3, rr.bottom)]
                pygame.draw.polygon(sc, COL_SPIKE, pts)
                pygame.draw.polygon(sc, (255, 200, 210), pts, 2)
            elif kind == "block":
                pygame.draw.rect(sc, COL_BLOCK, rr, border_radius=6)
                pygame.draw.rect(sc, COL_BLOCK_EDGE, rr, 3, border_radius=6)
            elif kind == "pad":
                pygame.draw.ellipse(sc, COL_PAD, rr.inflate(0, 6))

        # cieľ
        fx = self.finish_x - cam_x
        if fx < W + 50:
            for j in range(0, GROUND_Y, 20):
                c = (255, 255, 255) if (j // 20) % 2 == 0 else (30, 30, 30)
                pygame.draw.rect(sc, c, (fx, j + oy, 16, 20))

        for pt in self.particles:
            pt.draw(sc, cam_x)
        self.draw_player(cam_x)
        self.draw_ui()
        pygame.display.flip()

    def text(self, s, font, y, color=COL_TEXT):
        img = font.render(s, True, color)
        self.screen.blit(img, img.get_rect(center=(W // 2, y)))

    def draw_ui(self):
        sc = self.screen
        prog = min(1.0, max(0.0, self.player.x / self.finish_x))
        pygame.draw.rect(sc, (0, 0, 0), (W // 2 - 200, 16, 400, 14), border_radius=7)
        pygame.draw.rect(sc, COL_PLAYER, (W // 2 - 200, 16, 400 * prog, 14), border_radius=7)
        sc.blit(self.font.render(f"{int(prog * 100)}%", True, COL_TEXT), (W // 2 + 210, 8))
        sc.blit(self.font.render(f"Pokus {self.attempt}", True, COL_TEXT), (16, 8))
        sc.blit(self.font.render(f"Best {int(self.best * 100)}%", True, COL_TEXT), (W - 150, 8))

        if not self.started:
            self.text("BOING RUN", self.big, 170, COL_PAD)
            self.text("SPACE / klik = skok    DOLE = SLAM (super odraz)", self.font, 250)
            self.text("Stlač SPACE pre štart", self.font, 300, COL_LINE)
        elif self.won:
            self.text("LEVEL HOTOVÝ!", self.big, 200, COL_PAD)
            self.text(f"Pokusov: {self.attempt}   —   R = znova", self.font, 270)

    # ------------------------------------------------------------ loop
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if e.key == pygame.K_r:
                        self.attempt += 1
                        self.restart()
                    elif e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        if not self.started:
                            self.started = True
                        self.try_jump()
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        self.slam()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.started = True
                    self.try_jump()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
