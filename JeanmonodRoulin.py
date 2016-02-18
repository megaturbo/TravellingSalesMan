from unittest.case import _AssertRaisesContext

import pygame
import sys
import math
import numpy
from random import randint
import random

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
        self.links = []

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

        for i in range(len(self.links) - 1):
            pygame.draw.line(self.screen, self.color_blue, self.cities[self.links[i]].pos(),
                             self.cities[self.links[i + 1]].pos(), 1)

        for city in self.cities:
            pygame.draw.circle(self.screen, self.color_blue, (city.x, city.y), self.city_radius)
            text_city_name = self.font_small.render(city.name, True, self.color_white)
            self.screen.blit(text_city_name, (city.x - 15, city.y - 20))

        text = self.font_small.render("Press Enter when you're done.", True, self.color_grey)
        self.screen.blit(text, (0, 490))

        text = self.font_big.render("Number: {}".format(len(self.cities)), True, self.color_white)
        text_rect = text.get_rect()
        self.screen.blit(text, text_rect)
        pygame.display.flip()


class City:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def pos(self):
        return self.x, self.y

    def get_dist(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)


class Chromosome:
    def __init__(self, genes, dists):
        self.genes = genes
        self.eval = evaluate(self, dists)


def evaluate(pop, dists):
    evalu = 0
    for i in range(len(pop.genes) - 1):
        evalu += dists[pop.genes[i]][pop.genes[i + 1]]
    return evalu


def crossover(father, mother):
    newchrom = father[:randint(0, len(father) - 1)]
    newchrom[len(newchrom):] = [j for j in mother if j not in newchrom]
    return newchrom


def evolve(chromosomes, dists):
    popsize = len(chromosomes)
    print(popsize)
    # selection
    newpop = wheelselect(chromosomes, popsize)
    # crossover
    for i in xrange(0, len(newpop), 2):
        father = newpop[i].genes
        mother = newpop[i + 1].genes
        newpop[len(newpop):] = [Chromosome(crossover(father, mother), dists)]
        newpop[len(newpop):] = [Chromosome(crossover(mother, father), dists)]
    print("jeez: {} vs {}".format(len(newpop), len(chromosomes)))
    assert (len(newpop) == len(chromosomes))  # DEBUG
    # mutation
    for i in xrange(len(newpop)):
        if randint(0, 10) < 1:
            cut1 = randint(0, len(newpop[i].genes) - 2)
            cut2 = randint(cut1 + 1, len(newpop[i].genes) - 1)
            # TODO: maybe this? also, randint sucks
            newpop[i] = Chromosome(
                newpop[i].genes[:cut1 - 1] + newpop[i].genes[cut1:cut2 - 1:-1] + newpop[i].genes[cut2:], dists)
    return newpop


def wheelselect(pop, popsize):
    average = 0
    for c in pop:
        average += c.eval
    average /= popsize
    for c in pop:
        c.chance = average / c.eval
    newpop = []
    for i in xrange(popsize / 2):
        # DEBUG dat dice throw
        newpop[len(newpop):] = [pop.pop(randint(0, len(pop) - 1))]
    pop.extend(newpop)
    print('lenths: {} vs {}'.format(len(newpop), len(pop)))
    return newpop


def ga_solve(filename=None, show_gui=True, maxtime=0):
    cities = []
    if filename is None:
        gui = GUI()
        cities = gui.show_user_input()
    else:
        cities = read_cities(filename)
    dists = create_matrix(cities)

    print('Now algorithming with {} cities'.format(len(cities)))

    population = [Chromosome([i for i in range(len(cities))], dists) for j in range(32)]

    for i in population:
        random.shuffle(i.genes)
    # deciding which stop condition to use
    if maxtime <= 0:
        stopcond = 0
    else:
        from datetime import datetime
        stopcond = 1
        starttime = datetime.now()

    stop = False
    while not stop:
        # critically thinking about evolution
        population = evolve(population, dists)
        if gui:
            gui.links = max(population, key=lambda c: c.eval).genes
            gui.refresh()
        # loop stop
        if stopcond == 0:
            stop = False
        else:
            stop = (datetime.now() - starttime).seconds > maxtime


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


# ---------------------------------------------------------------------------- #
#                                                                              #
#                                   UTILS                                      #
#                                                                              #
# ---------------------------------------------------------------------------- #
def create_matrix(cities):
    l = len(cities)
    dists = numpy.zeros((l, l))
    for i in range(0, l):
        for j in range(0, l):
            dists[i][j] = cities[i].get_dist(cities[j])
    return dists


def read_cities(filename):
    with open(filename, 'r+') as file:
        return [read_city(line) for line in file.readlines()]


def read_city(line):
    l = line.split(' ')
    return City(l[0], int(l[1]), int(l[2]))


# ---------------------------------------------------------------------------- #
#                                                                              #
#                               "MAIN" FUNCTION                                #
#                                                                              #
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    filename, show_gui, max_time = handle_argv()

    ga_solve(filename, show_gui, max_time)
