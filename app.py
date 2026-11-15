# Example file showing a circle moving on screen
import os

import pygame
import time
import platform
import asyncio

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

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
    JUMP_HEIGHT = 20
    Y_VELOCITY = JUMP_HEIGHT
    jumping = False
    walking = True 

    # PLAYER SETTINGS

    player_img = pygame.image.load('pepstein_lopta.png')
    player_img = pygame.transform.scale(player_img, (85, 85))
    player_rect = player_img.get_rect()
    player_rect.x = 20
    player_rect.y = 700

    # OBJECTS SETTINGS

    triangle_img = pygame.image.load('trojuhelnik.png')
    square_img = pygame.image.load('ctverec.png')
    rectangle_img = pygame.image.load('obdelnik.png')

    triangle_img = pygame.transform.scale(triangle_img, (120, 120))
    square_img = pygame.transform.scale(square_img, (170, 170))
    rectangle_img = pygame.transform.scale(rectangle_img, (80, 190))

    triangle_rect = triangle_img.get_rect()
    square_rect = square_img.get_rect()
    rectangle_rect = rectangle_img.get_rect()

    triangle_rect.x = 350 
    triangle_rect.y = 600

    square_rect.x = 800
    square_rect.y = 560

    rectangle_rect.x = 1100
    rectangle_rect.y = 540

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        screen.blit(player_img, player_rect)
        pygame.draw.rect(screen, (255, 0, 0), player_rect, 2 )

        # OBJEKTY NA PARKOUR
        screen.blit(triangle_img, triangle_rect)
        screen.blit(square_img, square_rect)
        screen.blit(rectangle_img, rectangle_rect)

        # KOLIZE S OBJEKTY NA PARKOUR

        if player_rect.colliderect(triangle_rect):
            player_rect.x -= 150

        if player_rect.colliderect()

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
            walking = True


        if player_rect.colliderect(rightwall):
            player_rect.right = rightwall.left
            walking = False
        # PROMENE 

        if walking:
            player_rect.x += 7    

        if not walking:
            player_rect.x -= 7

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            jumping = True

        if  jumping:
            player_rect.y -= Y_VELOCITY
            Y_VELOCITY -= Y_GRAVITY
            if Y_VELOCITY < -JUMP_HEIGHT:
                jumping = False
                Y_VELOCITY = JUMP_HEIGHT 


        # ANIMATIONS

        

        clock.tick(60) # Frames per Scond

        pygame.display.flip()
        pygame.display.update

try:
    asyncio.get_running_loop()        # v pygbagu už smyčka běží
    asyncio.ensure_future(main())
except RuntimeError:                  # na desktopu žádná smyčka neběží
    asyncio.run(main())