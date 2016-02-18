import pygame
import sys

from pygame.constants import QUIT, K_RETURN, KEYDOWN, MOUSEBUTTONDOWN

class GUI:
    base_name = "city"
    screen_x = 500
    screen_y = 500
    city_radius = 3
    color_blue = [10, 200, 10]
    color_grey = [200, 200, 200]
    color_white = [255, 255, 255]

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((GUI.screen_x, GUI.screen_y))
        pygame.display.set_caption('Travelling Salesman - Jeanmonod / Roulin')
        self.screen = pygame.display.get_surface()
        self.font_big = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 15)
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
                    self.cities.append(City(GUI.base_name + str(len(self.cities)), pos[0], pos[1]))
                    self.refresh()
        return self.cities

    def refresh(self):
        self.screen.fill(0)
        for city in self.cities:
            pygame.draw.circle(self.screen, self.color_blue, (city.posx, city.posy), self.city_radius)
            text_city_name = self.font_small.render(city.name, True, self.color_white)
            self.screen.blit(text_city_name, (city.posx - 15, city.posy - 20))

        text = self.font_small.render("Press Enter when you're done.", True, self.color_grey)
        self.screen.blit(text, (0, 490))

        text = self.font_big.render("Number: {}".format(len(self.cities)), True, self.color_white)
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
            cities = [read_city(line) for line in file.readlines()]

    print(cities)


def handle_argv():
    """
    usage: JeanmonodRoulin.py [options] [parameters

    options:
    -n, --no-gui                Disable graphical user interface.

    parameters:
    -m VALUE, --maxtime=VALUE   Maximum execution time.
    -f VALUE, --filename=VALUE  File containing city coords.

    Jeanmonod Roulin"""

    import getopt
    opts = []
    try:
        opts = getopt.getopt(
            sys.argv[1:],
            "nm:f:",
            ["no-gui", "maxtime=", "filename="])[0]
    except getopt.GetoptError:
        print(handle_argv.__doc__)
        sys.exit(2)

    show_gui = True
    max_time = 0
    filename = None

    for opt, arg in opts:
        if opt in ("-n", "--no-gui"):
            show_gui = False
        elif opt in ("-m", "--maxtime"):
            max_time = int(arg)
        elif opt in ("-f", "--filename"):
            filename = str(arg)

    return filename, show_gui, max_time


if __name__ == '__main__':
    """
    Main
    """
    filename, show_gui, max_time = handle_argv()

    ga_solve(filename, show_gui, max_time)
