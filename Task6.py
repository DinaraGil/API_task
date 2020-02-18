# -*- coding: utf-8 -*-
import os
import sys
import pygame
import requests
# красная кнопка -- это карта
# зелёная кнопка -- это со спутника
# синяя кнопка -- это смешанное

response = None
pygame.init()
api_server = "http://static-maps.yandex.ru/1.x/"

lon = "37.530887"
lat = "55.703118"
pos_found = (None, None)
scale = "0.01"
l = 'map'

running = True
screen = pygame.display.set_mode((600, 450))
l_color_inactive = (20, 200, 50)
l_color_active = (255, 0, 0)


class InputBox:
    COLOR_INACTIVE = (20, 200, 50)
    COLOR_ACTIVE = (255, 0, 0)
    FONT = pygame.font.Font(None, 32)

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = InputBox.COLOR_INACTIVE
        self.text = text
        self.txt_surface = InputBox.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        global lon, lat, pos_found
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(*event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = InputBox.COLOR_ACTIVE if self.active else InputBox.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
                    params = {
                        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                        "geocode": self.text,
                        "format": "json"
                    }
                    # Выполняем запрос.
                    response = requests.get(geocoder_request, params=params)
                    if response:
                        # Преобразуем ответ в json-объект
                        json_response = response.json()
                        if len(json_response["response"]["GeoObjectCollection"]["featureMember"]) == 0:
                            print(f'По запросу "{self.text}" ничего не найдено')
                            self.text = ''
                            return

                        # Получаем первый топоним из ответа геокодера.
                        # Согласно описанию ответа, он находится по следующему пути:
                        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                        # Полный адрес топонима:
                        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                        # Координаты центра топонима:
                        toponym_coodrinates = toponym["Point"]["pos"]
                        # Печатаем извлечённые из ответа поля:
                        print(self.text, '--', toponym_address, "имеет координаты:", toponym_coodrinates)
                        pos_found = lon, lat = toponym_coodrinates.split()
                    else:
                        print("Ошибка выполнения запроса:")
                        print(geocoder_request)
                        print("Http статус:", response.status_code, "(", response.reason, ")")
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = InputBox.FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


box = InputBox(150, 400, 140, 32)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                lon = str(float(lon) - 2.57 * float(scale))
            if event.key == pygame.K_RIGHT:
                lon = str(float(lon) + 2.57 * float(scale))
            if event.key == pygame.K_UP:
                lat = str(float(lat) + 1.0996 * float(scale))
            if event.key == pygame.K_DOWN:
                lat = str(float(lat) - 1.0996 * float(scale))
            if event.key == pygame.K_PAGEDOWN:
                if (scale - 5) > 0:
                    scale -= 5
            if event.key == pygame.K_PAGEUP:
                if (scale + 5) < 45:
                    scale += 5
        if event.type == pygame.MOUSEBUTTONUP:
            if event.pos[1] >= 400 and event.pos[1] <= 430:
                if event.pos[0] >= 20 and event.pos[0] <= 50:
                    l = 'map'
                if event.pos[0] >= 65 and event.pos[0] <= 95:
                    l = 'sat'
                if event.pos[0] >= 110 and event.pos[0] <= 140:
                    l = 'sat,skl'
        box.handle_event(event)
        box.update()
        params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([scale, scale]),
            "l": l
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
        box.draw(screen)
        if [lon, lat] == pos_found:
            pygame.draw.circle(screen, (255, 0, 0), [300, 205], 10, 7)
            pygame.draw.polygon(screen, (255, 0, 0), [(292, 210), (300, 225), (308, 210)])
        pygame.draw.rect(screen, l_color_active if l == 'map' else l_color_inactive, (20, 400, 30, 30))
        pygame.draw.rect(screen, (208, 232, 183), (22, 402, 26, 26))
        pygame.draw.rect(screen, (253, 250, 242), (28, 402, 14, 26))
        pygame.draw.rect(screen, (255, 220, 159), (31, 402, 7, 26))
        pygame.draw.rect(screen, (255, 240, 180), (32, 402, 5, 26))

        pygame.draw.rect(screen, l_color_active if l == 'sat' else l_color_inactive, (65, 400, 30, 30))
        pygame.draw.rect(screen, (58, 81, 55), (67, 402, 26, 26))
        pygame.draw.rect(screen, (69, 131, 82), (73, 402, 14, 26))
        pygame.draw.rect(screen, (168, 169, 161), (76, 402, 7, 26))
        pygame.draw.rect(screen, (124, 123, 119), (77, 402, 5, 26))

        pygame.draw.rect(screen, l_color_active if l == 'sat,skl' else l_color_inactive, (110, 400, 30, 30))
        pygame.draw.rect(screen, (58, 81, 55), (112, 402, 26, 26))
        pygame.draw.rect(screen, (69, 131, 82), (118, 402, 14, 26))
        pygame.draw.rect(screen, (253, 250, 242), (121, 402, 7, 26))
        pygame.draw.rect(screen, (247, 204, 142), (122, 402, 5, 26))
    pygame.display.flip()
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)