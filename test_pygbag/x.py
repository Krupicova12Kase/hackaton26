import asyncio
import pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    while True:
        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (200, 80, 80), (150, 100, 100, 100))
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())