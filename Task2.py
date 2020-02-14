# -*- coding: utf-8 -*-
import os
import sys

import pygame
import requests


#delta 0 - 90


def get_response(scale):
    response = None

    api_server = "http://static-maps.yandex.ru/1.x/"
    lon = "37.530887"
    lat = "55.703118"
    scale = scale

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

    return response


def drawing():
    pygame.init()
    screen = pygame.display.set_mode((600, 450))

    scale = 10

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    if (scale - 5) > 0:
                        scale -= 5

                if event.key == pygame.K_PAGEUP:
                    if (scale + 5) < 45:
                        scale += 5

            map_file = "map.png"
            response = get_response(str(scale))

            with open(map_file, "wb") as file:
                file.write(response.content)

            screen.blit(pygame.image.load(map_file), (0, 0))

        pygame.display.flip()

    os.remove(map_file)


drawing()
