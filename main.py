import pygame
import time
import platform
import asyncio
import sys 

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    ## SOUNDS
    pygame.mixer.init()
    
    last_jump_sound = 0
    SOUND_DELAY = 500
    
    jump_sound = pygame.mixer.Sound('jump.waw')
    overworld_theme = pygame.mixer.music.load('end_theme_drama.ogg')

    jump_sound.set_volume(0.5)          # hlasitost 0.0 az 1.0
    '''
    # hudba v pozadi
    pygame.mixer.music.load('pisnicka hra.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)         # -1 = hra dokola
    '''
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

    # FONTY

    font_title = pygame.font.SysFont(None, 64)
    font_button = pygame.font.SysFont(None, 36)

    # TLACITKA 
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 250, 200, 50)
    play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 50 )

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
    netherbrick_rect3 = nether_img.get_rect()
    netherbrick_rect4 = nether_img.get_rect()

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
    #flag_img = pygame.transform.scale(flag_img, (220,300))

    grassblock_rect = grassblock_img.get_rect()
    grassblock_rect2 = grassblock_img.get_rect()
    diamond_rect = diamond_img.get_rect()
    diamond_rect2 = diamond_img.get_rect()
    #flag_rect = flag_img.get_rect()

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
    #flag_rect = flag_img.get_rect()

    grassblock_rect.x = 1150
    grassblock_rect.y = 620
    diamond_rect.x = 850
    diamond_rect.y = 510
    grassblock_rect2.x = 550
    grassblock_rect2.y = 400
    diamond_rect2.x = 250
    diamond_rect2.y = 290

    # PLAYERS 

    ovrplayer_img = pygame.image.load('Overworld/player.png')
    netherplayer_img = pygame.image.load('Nether/player.png')
    endplayer_img = pygame.image.load('End/player.png')

    current_player = ovrplayer_img
    current_player = pygame.transform.scale(current_player, (85, 85))

    # PLAYER SETTINGS

    player_rect = current_player.get_rect()
    player_rect.x = 20
    player_rect.y = 700

    # !!!!!!!!!!!!!!!! LIST S OBJEKTY  |||PEPSTEIN|||  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    rects_list = [grassblock_rect, 
                  grassblock_rect2,
                  grassblock_rect3,
                  grassblock_rect4,
                  diamond_rect,
                  diamond_rect2,
                  diamond_rect3,
                  diamond_rect4,
                  soulsand_rect,
                  soulsand_rect2,
                  soulsand_rect3,
                  soulsand_rect4,
                  netherbrick_rect,
                  netherbrick_rect2,
                  netherbrick_rect3,
                  netherbrick_rect4,
                  ]


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.blit(current_bg, (0, 0))
        screen.blit(current_player, player_rect)
        pygame.draw.rect(screen, (255, 0, 0), player_rect, 2 )

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

        if player_rect.colliderect(top_rect):
            player_rect.y += 100 * dt

        if player_rect.colliderect(ground_rect):
            player_rect.y -= 100 *dt

        if player_rect.colliderect(leftwall):
            player_rect.left = leftwall.right
            velocity_x = 7


        if player_rect.colliderect(rightwall):
            player_rect.right = rightwall.left
            velocity_x = -7
            
        # PROMENE 

        player_rect.x += velocity_x
        player_rect.y += velocity_y
        # if walking:
        #     player_rect.x += 7    
        #     facing_right = True

        # if not walking:
        #     player_rect.x -= 7
        #     facing_right = False 

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            jumping = True
            jump_sound.play()
            now = pygame.time.get_ticks()
            
            if now - last_jump_sound > SOUND_DELAY:
                jump_sound.play()
                last_jump_sound = now

        if  jumping:
            velocity_y = 7
            velocity_y -= Y_GRAVITY
            if player_rect.colliderect(ground_rect):
                player_rect.y -= 100 *dt
                jumping = False
                velocity_y = JUMP_HEIGHT 
            # if Y_VELOCITY < -JUMP_HEIGHT:
            #     jumping = False
            #     Y_VELOCITY = JUMP_HEIGHT 

        # DIFFERNT WORLDS

        if current_bg == over_img:
            overworld_theme.play()
            screen.blit(grassblock_img, grassblock_rect)
            screen.blit(diamond_img, diamond_rect)
            screen.blit(grassblock_img, grassblock_rect2)
            screen.blit(diamond_img, diamond_rect2)
        elif current_bg == over_img2:
            pass
        elif current_bg == nether_img:
            screen.blit(soulsand_img, soulsand_rect)
            screen.blit(netherbrick_img, netherbrick_rect)
            screen.blit(soulsand_img, soulsand_rect2)
            screen.blit(netherbrick_img, netherbrick_rect2)
        elif current_bg == nether_img2:
            pass
        elif current_bg == end_img:
            screen.blit(obsidian_img, obsidian_rect)
            screen.blit(endstone_img, endstone_rect)
            screen.blit(endstone_img, endstone_rect2)
            screen.blit(obsidian_img, obsidian_rect2)
        elif current_bg == end_img2:
            pass    
           



        # BG SWICH TEST

        if keys[pygame.K_i]:
            current_bg = nether_img
            current_player = netherplayer_img
        if keys[pygame.K_o]:
            current_bg = end_img
            current_player = endplayer_img
        if keys[pygame.K_p]:
            current_bg = over_img
            current_player = ovrplayer_img


        clock.tick(60) # Frames per Scond

        pygame.display.flip()
        pygame.display.update
    pygame.quit()
    
main()