# Example file showing a circle moving on screen
import pygame
import tkinter as tk
import tkinter.scrolledtext as st
import socket
import json

UDP_IP = "192.168.3.84"
UDP_PORT = 5005

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Init
sock = socket.socket(socket.AF_INET, # IPv4
                     socket.SOCK_DGRAM) # UDP
sock.bind(("0.0.0.0", 0))   # navaž na libovolný volný port
sock.setblocking(True)

def init_connection():
    print("Starting init")
    init_dict = {
        "init": True
    }
    sock.sendto(json.dumps(init_dict).encode("utf-8"), (UDP_IP, UDP_PORT))
    raw_data, addr = sock.recvfrom(1024)
    data : dict = json.loads(raw_data.decode("utf-8"))
    if not data.get("init_success"):
        raise Exception("Failed to get data")
    print("connection successfull!")
    sock.setblocking(False)

init_connection()

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

def network_update():
    dict_tosend = {
        "playerdata": {
            
        }
    }
    sock.sendto(json.dumps(dict_tosend).encode("utf-8"), (UDP_IP, UDP_PORT))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    network_update()
    
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    pygame.draw.circle(screen, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()