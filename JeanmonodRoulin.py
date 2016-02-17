import pygame
import sys

from pygame.constants import QUIT, K_RETURN, KEYDOWN, MOUSEBUTTONDOWN

__author__ = 'Jeanmonod + Roulin'


class GUI:
    screen_x = 500
    screen_y = 500
    city_color = [10, 10, 200]  # blue
    city_radius = 3
    font_color = [255, 255, 255]  # white

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((GUI.screen_x, GUI.screen_y))
        pygame.display.set_caption('Travelling Salesman - Jeanmonod / Roulin')
        self.screen = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.font_city_name = pygame.font.Font(None, 15)
        self.cities = []

    def show_user_input(self):
        self.refresh()
        collecting = True

        while collecting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == K_RETURN:
                    collecting = False
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.cities.append(City("c" + str(len(self.cities)), pos[0], pos[1]))
                    self.refresh()

    def refresh(self):
        self.screen.fill(0)
        for city in self.cities:
            pygame.draw.circle(self.screen, self.city_color, (city.posx, city.posy), self.city_radius)
            text_city_name = self.font_city_name.render(city.name, True, self.font_color)
            self.screen.blit(text_city_name, (city.posx - 15, city.posy - 10))
        text = self.font.render("Number: {}".format(len(self.cities)), True, self.font_color)
        text_rect = text.get_rect()
        self.screen.blit(text, text_rect)
        pygame.display.flip()


class City:
    def __init__(self, name, posx, posy):
        self.name = name
        self.posx = posx
        self.posy = posy


def read_city(line):
    l = line.split(' ')
    return City(l[0], int(l[1]), int(l[2]))


def ga_solve(filename=None, show_gui=True, maxtime=0):
    cities = []
    if filename is None:
        gui = GUI()
        cities = gui.show_user_input()
    else:
        with open(filename, 'r+') as file:
            for line in file.readlines():
                cities.append(read_city(line))


if __name__ == '__main__':
    ga_solve(None, True, 60)
