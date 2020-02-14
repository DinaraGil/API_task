# -*- coding: utf-8 -*-
import os
import sys

import pygame
import requests

response = None
pygame.init()
api_server = "http://static-maps.yandex.ru/1.x/"

lon = "37.530887"
lat = "55.703118"
scale = "0.02"
running = True
screen = pygame.display.set_mode((600, 450))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                lon = str(float(lon) - 2.57 * float(scale))
            if event.key == pygame.K_RIGHT:
                lon = str(float(lon) + 2.57 * float(scale))
            if event.key == pygame.K_UP:
                lat = str(float(lat) + 1.0996 * float(scale))
            if event.key == pygame.K_DOWN:
                lat = str(float(lat) - 1.1 * float(scale)) 
        params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([scale, scale]),
            "l": "map"
        }
        response = requests.get(api_server, params=params)
        
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        
        # Запишем полученное изображение в файл.
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)        
        screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)