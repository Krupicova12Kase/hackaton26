import pygame
import asyncio

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

VELOCITY_Y = -10
VELOCITY_X = 5
GRAVITY = 0.2
FRICTION = 0.1
FLOOR_Y = SCREEN_HEIGHT - 10

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

       
async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    


    # DEFAULT SETTINGS
    x = 0
    y = 0
    dt = 0.1
    Y_GRAVITY = 1
    JUMP_HEIGHT = 23
    velocity_y = 0
    velocity_x = 7
    jumping = False
    walking = True 
    facing_right = True
    
    def check_collisions(collist) -> pygame.Rect | None:
        for rect in collist:
            if player.rect.colliderect(rect):
                return rect
        return None
    
    class Player():
        def __init__(self, image_path: str, default_pos: tuple[int, int] = (100, 100)):
            self.img = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (90, 90))
            self.rect = self.img.get_rect()
            self.rect.x, self.rect.y = default_pos
            self.velocity_x = 0
            self.velocity_y = 0
            self.jumping = False
            self.bouncing = False
            self.bounce_timer = 0
            self.direction = "none"
            self.old_rect = None
            self.hitboxlist = rects_list_overworld1
            
        def controller(self):
            keys = pygame.key.get_pressed()

            # Jump
            if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not self.jumping and not self.bouncing:
                self.velocity_y = VELOCITY_Y
                self.jumping = True

            # Sides
            if self.bounce_timer <= 0:
                if keys[pygame.K_a]:
                    self.velocity_x = -VELOCITY_X if not self.bouncing else -VELOCITY_X / 2.5
                    self.direction = "left"
                elif keys[pygame.K_d]:
                    self.velocity_x = VELOCITY_X if not self.bouncing else VELOCITY_X / 2.5
                    self.direction = "right"
                if not keys[pygame.K_a] and not keys[pygame.K_d] and self.velocity_x == 0:
                    self.direction = "none"
            else:
                self.bounce_timer -= 1

            self.move()
            self.draw()



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
            elif self.rect.x + self.rect.width > SCREEN_WIDTH:
                self.rect.x = SCREEN_WIDTH - self.rect.width

            old_rect = self.rect.copy()
            old_vel_x = self.velocity_x
            old_vel_y = self.velocity_y
            self.rect.x += self.velocity_x

            collidedrect = check_collisions(self.hitboxlist)

            # X
            if collidedrect:
                self.bounce_timer = 5
                self.bouncing = True
                # From right
                if old_rect.right <= collidedrect.left:
                    self.rect.right = collidedrect.left
                    self.velocity_x = -abs(old_vel_x)
                    self.velocity_y = -abs(old_vel_y)
                # From left
                elif old_rect.left >= collidedrect.right:
                    self.rect.left = collidedrect.right
                    self.velocity_x = abs(old_vel_x)
                    self.velocity_y = -abs(old_vel_y)

            # Y
            self.velocity_y += GRAVITY
            old_vel_x = self.velocity_x
            old_vel_y = self.velocity_y
            old_rect = self.rect.copy()
            self.rect.y += self.velocity_y

            collidedrect = check_collisions(self.hitboxlist)

            if collidedrect:
                self.bouncing = True
                # From top
                if old_rect.bottom <= collidedrect.top:
                    self.rect.bottom = collidedrect.top
                    self.velocity_y = -abs(old_vel_y)
                    # Pokud chceš, aby ho to vystřelilo i do strany podle směru:
                    self.velocity_x = abs(old_vel_x) if self.direction == "right" else -abs(old_vel_x)
                    
                # From bottom
                elif old_rect.top >= collidedrect.bottom:
                    self.rect.top = collidedrect.bottom
                    self.velocity_y = abs(old_vel_y)

                if old_rect.top <= collidedrect.top:
                    self.velocity_y = -abs(old_vel_y)
                elif old_rect.bottom <= collidedrect.bottom:
                    self.velocity_y = abs(old_vel_y)

            elif self.rect.y + self.rect.height >= FLOOR_Y:
                self.bouncing = False

            if self.rect.y + self.rect.height > FLOOR_Y:
                self.rect.y = FLOOR_Y - self.rect.height
                self.velocity_y = 0
                self.jumping = False

        def draw(self):
            screen.blit(self.img, self.rect)
        

    # GAME VARIABLES 

    game_paused = False

    if game_paused == True:
        if resume_button.draw(screen):
            game_paused = False


    # LOAD BUTTONS

    quit_img = pygame.image.load('button_quit.png').convert_alpha()
    quit_button =  Button(SCREEN_WIDTH // 2, 300, quit_img, 1)
    resume_img = pygame.image.load('button_resume.png').convert_alpha()
    resume_button = Button(SCREEN_WIDTH // 2, 200, resume_img, 1)

    # FONTY

    font = pygame.font.SysFont("arialblack", 40)

    TEXT_COL = (255, 255, 255)

    def draw_text(text, font, text_col, x ,y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    # PORTALS

    portal_img = pygame.image.load('Portal.png')
    portal_img2 = pygame.image.load('Portal2.png')

    portal_img = pygame.transform.scale(portal_img, (110, 80))
    portal_img2 = pygame.transform.scale(portal_img2, (110, 80))

    portal_rect = portal_img.get_rect()
    portal_rect2 = portal_img2.get_rect()
    portal_rect3 = portal_img.get_rect()
    portal_rect4 = portal_img2.get_rect()
    portal_rect5 = portal_img.get_rect()
    portal_rect6 = portal_img2.get_rect()

    portal_rect.x = 1180
    portal_rect.y = 190
    portal_rect2.x = 250
    portal_rect2.y = 190
    portal_rect3.x = 1180
    portal_rect3.y = 190
    portal_rect4.x = 240
    portal_rect4.y = 190
    portal_rect5.x = 1050
    portal_rect5.y = 190
    portal_rect6.x = 250
    portal_rect6.y = 190


    font_title = pygame.font.SysFont(None, 64)
    font_button = pygame.font.SysFont(None, 36)

    # TLACITKA 


    # GAME STATE

    GAME_STATE_MENU = "menu"
    GAME_STATE_PLAYING = "playing"
    current_state = GAME_STATE_MENU
    
    # BACKGROUNDS

    over_img = pygame.image.load('Overworld/background.png')
    over_img2 = pygame.image.load('Overworld/background.png')
    nether_img = pygame.image.load('Nether/background.png')
    nether_img2 = pygame.image.load('Nether/background.png')
    end_img = pygame.image.load('End/background.png')
    end_img2 = pygame.image.load('End/background.png')

    over_img = pygame.transform.scale(over_img, (1280, 720))
    over_img2 = pygame.transform.scale(over_img2, (1280, 720))
    nether_img = pygame.transform.scale(nether_img, (1280, 720))
    nether_img2 = pygame.transform.scale(nether_img2, (1280, 720))
    end_img = pygame.transform.scale(end_img, (1280, 720))
    end_img2 = pygame.transform.scale(end_img2, (1280, 720))
    finalend_img = pygame.transform.scale(end_img, (1280, 720))

    current_bg = over_img

    # END OBJECTS

    obsidian_img = pygame.image.load('End/wall2.png')
    endstone_img = pygame.image.load('End/wall1.png')

    obisidan_img = pygame.transform.scale(obsidian_img, (90, 90))
    endstone_img = pygame.transform.scale(endstone_img, (100, 100))

    obsidian_rect = obsidian_img.get_rect()
    obsidian_rect2 = obsidian_img.get_rect()
    endstone_rect = endstone_img.get_rect()
    endstone_rect2 = endstone_img.get_rect()

    obsidian_rect.x = 150
    obsidian_rect.y = 620
    endstone_rect.x = 450
    endstone_rect.y = 510
    endstone_rect2.x = 750
    endstone_rect2.y = 400
    obsidian_rect2.x = 1050
    obsidian_rect2.y = 290

    # END OBJECT V2 

    obsidian_rect3 = obsidian_img.get_rect()
    obsidian_rect4 = obsidian_img.get_rect()
    endstone_rect3 = endstone_img.get_rect()
    endstone_rect4 = endstone_img.get_rect()

    obsidian_rect3.x = 1150
    obsidian_rect3.y = 620
    endstone_rect3.x = 850
    endstone_rect3.y = 510
    endstone_rect4.x = 550
    endstone_rect4.y = 400
    obsidian_rect4.x = 250
    obsidian_rect4.y = 290

    # NETHER OBJECTS

    soulsand_img = pygame.image.load('Nether/wall1.png')
    netherbrick_img = pygame.image.load('Nether/wall2.png')

    soulsand_img = pygame.transform.scale(soulsand_img, (100, 100))
    netherbrick_img = pygame.transform.scale(netherbrick_img, (100, 100))

    soulsand_rect = soulsand_img.get_rect()
    soulsand_rect2 = soulsand_img.get_rect()
    netherbrick_rect = nether_img.get_rect()
    netherbrick_rect2 = nether_img.get_rect()

    soulsand_rect.x = 300
    soulsand_rect.y = 620
    netherbrick_rect.x = 600
    netherbrick_rect.y = 510
    soulsand_rect2.x = 900
    soulsand_rect2.y = 400
    netherbrick_rect2.x = 1180
    netherbrick_rect2.y =  290

    # NETHER OBJECTS V2

    soulsand_rect3 = soulsand_img.get_rect()
    soulsand_rect4 = soulsand_img.get_rect()
    netherbrick_rect3 = netherbrick_img.get_rect()
    netherbrick_rect4 = netherbrick_img.get_rect()

    soulsand_rect3.x = 1150
    soulsand_rect3.y = 620
    netherbrick_rect3.x = 850
    netherbrick_rect3.y = 510
    soulsand_rect4.x = 550
    soulsand_rect4.y = 400
    netherbrick_rect4.x = 250
    netherbrick_rect4.y =  290

    # OVERWORLD OBJECTS

    grassblock_img = pygame.image.load('Overworld/wall2.png')
    diamond_img = pygame.image.load('Overworld/wall1.png')
    #flag_img = pygame.image.load('pepstein_flag.png')

    grassblock_img = pygame.transform.scale(grassblock_img, (100,100))
    diamond_img = pygame.transform.scale(diamond_img, (100,100))

    grassblock_rect = grassblock_img.get_rect()
    grassblock_rect2 = grassblock_img.get_rect()
    diamond_rect = diamond_img.get_rect()
    diamond_rect2 = diamond_img.get_rect()

    grassblock_rect.x = 400
    grassblock_rect.y = 620
    diamond_rect.x = 700
    diamond_rect.y = 510
    grassblock_rect2.x = 1000
    grassblock_rect2.y = 400
    diamond_rect2.x = 1180
    diamond_rect2.y = 290
    
    # OVERWORLD V2
    grassblock_rect3 = grassblock_img.get_rect()
    grassblock_rect4 = grassblock_img.get_rect()
    diamond_rect3 = diamond_img.get_rect()
    diamond_rect4 = diamond_img.get_rect()

    grassblock_rect3.x = 1150
    grassblock_rect3.y = 620
    diamond_rect3.x = 850
    diamond_rect3.y = 510
    grassblock_rect4.x = 550
    grassblock_rect4.y = 400
    diamond_rect4.x = 250
    diamond_rect4.y = 290

    # PLAYERS 

    ovrplayer_img = pygame.image.load('Overworld/player.png')
    netherplayer_img = pygame.image.load('Nether/player.png')
    endplayer_img = pygame.image.load('End/player.png')

    # current_player = ovrplayer_img
    # current_player = pygame.transform.scale(current_player, (90, 90))

    # PLAYER SETTINGS

    # player_rect = current_player.get_rect()
    # player_rect.x = 20
    # player_rect.y = 680

    # !!!!!!!!!!!!!!!! LIST S OBJEKTY  |||PEPSTEIN|||  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    rects_list_overworld1 = [grassblock_rect, 
                  grassblock_rect2,
                  diamond_rect,
                  diamond_rect2]

    rects_list_overworld2 = [grassblock_rect3, grassblock_rect4, diamond_rect3,
                  diamond_rect4]
                  

    rects_list_nether1 = [soulsand_rect,
                  soulsand_rect2, 
                  netherbrick_rect,
                  netherbrick_rect2]


    rects_list_nether2 = [soulsand_rect3,
                        soulsand_rect4,
                        netherbrick_rect3,
                        netherbrick_rect4]

    rects_list_end1 = [endstone_rect,
                      endstone_rect2,
                      obsidian_rect,
                    obsidian_rect2]

    rects_list_end2 = [
                  endstone_rect3,
                  endstone_rect4,
                  obsidian_rect3,
                  obsidian_rect4]
                  
    player = Player(
        image_path='Overworld/player.png',
        default_pos=(20, 680)
    )

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    game_paused = True
                    print("Paused")
            if event.type == pygame.QUIT:
                running = False

        screen.blit(current_bg, (0, 0))
        # screen.blit(current_player, player_rect)
        # pygame.draw.rect(screen, (255, 0, 0), player_rect, 2 )

        # OBJEKTY NA PARKOUR
        #screen.blit(triangle_img, triangle_rect)

        # KOLIZE S OBJEKTY NA PARKOUR

        #if player_rect.colliderect(triangle_rect) and facing_right == True:
            #player_rect.x -= 150

        #if player_rect.colliderect(triangle_rect) and not facing_right:
            #player_rect.x += 150


        # OBJEKTY

        ground_rect = pygame.Rect(0, 710, 1280 , 15 )
        pygame.draw.rect(screen, ("black"), ground_rect)

        top_rect = pygame.Rect(0, 0 , 1280, 10)
        pygame.draw.rect(screen, ("black"), top_rect)

        leftwall = pygame.Rect(0, 0, 10, 720)
        pygame.draw.rect(screen, ("black"), leftwall)

        rightwall = pygame.Rect(1270, 0, 10, 720)
        pygame.draw.rect(screen, ("black"), rightwall)

        # KOLIZE

        # if player_rect.colliderect(top_rect):
        #     player_rect.y += 100 * dt

        # if player_rect.colliderect(ground_rect):
        #     player_rect.y -= 100 *dt

        # if player_rect.colliderect(leftwall):
        #     player_rect.left = leftwall.right
        #     velocity_x = 7


        # if player_rect.colliderect(rightwall):
        #     player_rect.right = rightwall.left
        #     velocity_x = -7
            
        # # PROMENE 

        # player_rect.x += velocity_x
        # player_rect.y += velocity_y
        # if walking:
        #     player_rect.x += 7    
        #     facing_right = True

        # if not walking:
        #     player_rect.x -= 7
        #     facing_right = False 

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_SPACE]:
        #     jumping = True



        # if  jumping:
        #     velocity_y = 7
        #     velocity_y -= Y_GRAVITY
        #     if player_rect.colliderect(ground_rect):
        #         player_rect.y -= 100 *dt
        #         jumping = False
        #         velocity_y = JUMP_HEIGHT 
        #     # if Y_VELOCITY < -JUMP_HEIGHT:
        #     #     jumping = False
        #     #     Y_VELOCITY = JUMP_HEIGHT 

        # DIFFERNT WORLDS

        if current_bg == over_img:
            screen.blit(grassblock_img, grassblock_rect)
            screen.blit(diamond_img, diamond_rect)
            screen.blit(grassblock_img, grassblock_rect2)
            screen.blit(diamond_img, diamond_rect2)
            screen.blit(portal_img, portal_rect)
        elif current_bg == over_img2:
            screen.blit(grassblock_img, grassblock_rect3)
            screen.blit(diamond_img, diamond_rect3)
            screen.blit(grassblock_img, grassblock_rect4)
            screen.blit(diamond_img, diamond_rect4)
            screen.blit(portal_img2, portal_rect2)
        elif current_bg == nether_img:
            screen.blit(soulsand_img, soulsand_rect)
            screen.blit(netherbrick_img, netherbrick_rect)
            screen.blit(soulsand_img, soulsand_rect2)
            screen.blit(netherbrick_img, netherbrick_rect2)
            screen.blit(portal_img, portal_rect3)
        elif current_bg == nether_img2:
            screen.blit(soulsand_img, soulsand_rect3)
            screen.blit(netherbrick_img, netherbrick_rect3)
            screen.blit(soulsand_img, soulsand_rect4)
            screen.blit(netherbrick_img, netherbrick_rect4)
            screen.blit(portal_img2, portal_rect4)
        elif current_bg == end_img:
            screen.blit(obsidian_img, obsidian_rect)
            screen.blit(endstone_img, endstone_rect)
            screen.blit(endstone_img, endstone_rect2)
            screen.blit(obsidian_img, obsidian_rect2)
            screen.blit(portal_img, portal_rect5)
        elif current_bg == end_img2:
            screen.blit(obsidian_img, obsidian_rect3)
            screen.blit(endstone_img, endstone_rect3)
            screen.blit(endstone_img, endstone_rect4)
            screen.blit(obsidian_img, obsidian_rect4)
            screen.blit(portal_img2, portal_rect6)
        elif current_bg == finalend_img:
            draw_text("Congratulations, you finished the game!!", font, TEXT_COL, 250, SCREEN_HEIGHT // 2)
           

        # OFFICIAL BG AND ASSETS SWITCHES
        if current_bg == over_img:
            if player.rect.colliderect(portal_rect):
                current_bg = over_img2
                player.img = pygame.transform.scale(ovrplayer_img, (90, 90))
                player.hitboxlist = rects_list_overworld2

        if current_bg == over_img2:
            if player.rect.colliderect(portal_rect2):
                player.img = pygame.transform.scale(netherplayer_img, (90, 90))
                current_bg = nether_img
                player.hitboxlist = rects_list_nether1

        if current_bg == nether_img:
            if player.rect.colliderect(portal_rect3):
                current_bg = nether_img2
                player.hitboxlist = rects_list_nether2

        if current_bg == nether_img2:
            if player.rect.colliderect(portal_rect4):
                current_bg = end_img
                player.img = pygame.transform.scale(endplayer_img, (90, 90))
                player.hitboxlist = rects_list_end1


        if current_bg == end_img:
            if player.rect.colliderect(portal_rect5):
                current_bg = end_img2
                player.hitboxlist = rects_list_end2
                
        if current_bg == end_img2:
            if player.rect.colliderect(portal_rect6):
                current_bg = finalend_img
                pass
        

        

        # BG SWICH TEST

        # if keys[pygame.K_i]:
        #     current_bg = nether_img
        #     current_player = netherplayer_img
        # if keys[pygame.K_o]:
        #     current_bg = end_img
        #     current_player = endplayer_img
        # if keys[pygame.K_p]:
        #     current_bg = over_img
        #     current_player = ovrplayer_img
        # if keys[pygame.K_u]:
        #     current_bg = over_img2
        #     current_player = ovrplayer_img
        player.controller()


         # MAIN MENU BULLSHIT

        if game_paused == True:
            draw_text("Welcome to Fortress of Bioms", font, (0, 0, 0), x=300, y=100)
            velocity_x = 0
            if resume_button.draw(screen):
                game_paused = False
                velocity_x += 7
            if quit_button.draw(screen):
                running = False

        clock.tick(60) # Frames per Scond

        pygame.display.flip()
        pygame.display.update()
        await asyncio.sleep(0)
    pygame.quit()
    
asyncio.run(main())