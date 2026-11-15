# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
VELOCITY_Y = -10
VELOCITY_X = 5
GRAVITY = 0.4
FRICTION = 0.3
FLOOR_Y = screen.height - 10

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
rects = []


def check_collisions() -> pygame.Rect | None:
    for rect in rects:
        if player.rect.colliderect(rect):
            return rect
    return None


class Player():
    def __init__(self, x, y):
        self.img = pygame.transform.scale(load_image('pepstein_lopta.png'), (85, 85))
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.bouncing = False
        self.bounce_timer = 0
        self.direction = "none"
        self.old_rect = None

    def controller(self):
        keys = pygame.key.get_pressed()

        # Skok
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not self.jumping:
            self.velocity_y = VELOCITY_Y
            self.jumping = True

        # Pohyb do stran (jen když nevyprší časovač odrazu)
        if self.bounce_timer <= 0:
            if keys[pygame.K_a]:
                self.velocity_x = -VELOCITY_X
                self.direction = "left"
            elif keys[pygame.K_d]:
                self.velocity_x = VELOCITY_X
                self.direction = "right"
        else:
            self.bounce_timer -= 1

        self.move()
        self.draw()
        
        # if not keys[pygame.K_a] and not keys[pygame.K_d] and self.velocity_x == 0:
        #     self.direction = "none"

    def move(self):
        if not self.bouncing:
            if self.direction == "left" and self.velocity_x < 0:
                self.velocity_x += FRICTION
            elif self.direction == "right" and self.velocity_x > 0:
                self.velocity_x -= FRICTION
            else:
                self.velocity_x = 0

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.width > screen.width:
            self.rect.x = screen.width - self.rect.width

        old_rect = self.rect.copy()
        self.rect.x += self.velocity_x
        
        collidedrect = check_collisions()

        # bouncing with collisions
        if collidedrect:
                self.bounce_timer = 15
                self.bouncing = True
                if old_rect.right <= collidedrect.left:      # Narazil zleva
                    self.rect.right = collidedrect.left      # Vytlačit ven z objektu!
                    self.velocity_x = -20
                    self.velocity_y = -10                    # Lehké nadhození při nárazu z boku
                elif old_rect.left >= collidedrect.right:    # Narazil zprava
                    self.rect.left = collidedrect.right      # Vytlačit ven z objektu!
                    self.velocity_x = 20
                    self.velocity_y = -10
                    
         # jumping
        self.velocity_y += GRAVITY
        old_rect = self.rect.copy()
        self.rect.y += self.velocity_y # NA JAKYMKOLIV JINYM RADKU SE TO GLITCHUJE, NEPRESOUVAT!!!
        
        collidedrect = check_collisions()
        
        if collidedrect:
            self.bouncing = True
            if old_rect.bottom <= collidedrect.top:      # Dopadl na překážku shora
                self.rect.bottom = collidedrect.top
                self.velocity_y = -15                    # Vystřelit nahoru
                # Pokud chceš, aby ho to vystřelilo i do strany podle směru:
                self.velocity_x = 15 if self.direction == "right" else -15
            elif old_rect.top >= collidedrect.bottom:    # Narazil hlavou zespodu
                self.rect.top = collidedrect.bottom
                self.velocity_y = 10                     # Odrazit dolů
                
                
            if old_rect.top <= collidedrect.top:
                self.velocity_y = -10
            elif old_rect.bottom <= collidedrect.bottom:
                self.velocity_y = +10
   
        elif self.rect.y + self.rect.height >= FLOOR_Y:
            self.bouncing = False

        if self.rect.y + self.rect.height > FLOOR_Y:
            self.rect.y = FLOOR_Y - self.rect.height
            self.velocity_y = 0
            self.jumping = False
            


    def draw(self):
        screen.blit(self.img, self.rect)


def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print("Nelze načíst:", path, e)
        raise


square_img = load_image('ctverec.png')
square_img = pygame.transform.scale(square_img, (170, 170))
square_rect = square_img.get_rect()

square_rect.x = 500
square_rect.y = 650
rects.append(square_rect)

player = Player(500, 200)
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill("white")
    screen.blit(square_img, square_rect)

    player.controller()
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
