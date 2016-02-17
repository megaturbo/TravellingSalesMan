#!/usr/bin/env python
"""usage: AntogniniAeberli.py [options] [params] [cityfile]

options:
-h, --help      Show this help
-n, --no-gui    Hide the Graphical User Interface during the problem resolution
-v, --verbose	Show verbose informations during the generation of solution on the command line.

params:
-m VALUE, --maxtime=VALUE  Max. execution time of genetic algorithm.
                           Zero for infinite. Default: 0

(c) 2014 by Diego Antognini and Marco Aeberli")
"""

import sys
import getopt
import os
import pygame
from math import hypot
from random import randint, shuffle, sample, choice
from time import clock
from copy import deepcopy


def equal_double(a, b, epsilon=1e-6):
    """
    Returns true if a and b are equal, with epsilon as accepted range.
    False if not.
    """
    return abs(a-b) < epsilon


class Town:
    """
    Class which represents a town in the TSP.
    """

    PRECALCULATE_LIST = []

    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.x = float(x)
        self.y = float(y)

    @staticmethod
    def compute_distance(t1, t2):
        """
        Computes the Euclidean distance between two towns.
        """
        return Town.PRECALCULATE_LIST[t1][t2]

    @staticmethod
    def compute_all_possible_distance(cities):
        for k1 in range(0, len(cities)):
            Town.PRECALCULATE_LIST.append(list())
            for k2 in range(0, len(cities)):
                Town.PRECALCULATE_LIST[k1].append(0)

        for k1 in range(0, len(cities)):
            for k2 in range(k1, len(cities)):
                c1 = cities[k1].id
                c2 = cities[k2].id
                Town.PRECALCULATE_LIST[c1][c2] = Town.PRECALCULATE_LIST[c2][c1] = hypot(cities[k1].x-cities[k2].x, cities[k1].y-cities[k2].y)


class Solution:
    """
    Class which represents a solution in the TSP. Each gene is represented by an unique id, related with the town.
    """
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.distance = 0

    def __repr__(self):
        return str(self.distance) + " : " + " ".join([str(i) for i in self.chromosome])

    def __len__(self):
        return len(self.chromosome)

    def __getitem__(self, item):
        return self.chromosome[item]

    def __setitem__(self, key, value):
        self.chromosome[key] = value

    def index(self, value):
        return self.chromosome.index(value)

    def compute_distance(self):
        """
        Computes for the traveling distance for one soltution.
        """
        self.distance = 0.0
        for s in xrange(0, len(self.chromosome)-1):
            self.distance += Town.compute_distance(self.chromosome[s], self.chromosome[s+1])

        # do not forget to compute the distance between the first and the last city.
        self.distance += Town.compute_distance(self.chromosome[0], self.chromosome[-1])

    def mutate(self):
        """
        Mutation of a solution where the path between two genes are inversed.
        i.e.: [0,1,2,3,4,5,6,7,8,9,10,11]  --> select random 5 and 8
              [0,1,2,3,4,8,7,6,5,9,10,11]
        """
        gene1 = randint(0, len(self.chromosome)-1)
        gene2 = gene1
        while gene2 == gene1:
            gene2 = randint(0, len(self.chromosome)-1)
        if gene1 > gene2:
            gene1, gene2 = gene2, gene1
        while gene1 < gene2:
            self.chromosome[gene1], self.chromosome[gene2] = self.chromosome[gene2], self.chromosome[gene1]
            gene1 += 1
            gene2 -= 1


class Problem:
    """
    Class which represents the entire problem (without gui) for the TSP.
    """
    NB_POPULATION = 0  # Will be changed during the execution time, by FACTOR*len(cities)
    FACTOR = 1
    SIZE_TOURNAMENT_BATTLE = 10  # Size of the tournament battle with which we keep the best
    MUTATION_RATE = 0.3  # Probability to mutate
    CROSSOVER_FRACTION = 0.8  # Number of generated offsprings
    DELTA_GENERATION = 50  # Convergence criteria. If the best solution hasn't changed since DELTA_GENERATION => STOP

    def __init__(self, cities):
        """
        Initializes a problem, based on the cities passed as argument.
        The cities are expected in format [[name, pos_x, pos_y], ...]
        """
        Problem.NB_POPULATION = len(cities)*Problem.FACTOR
        self.cities_dict = {}
        self.keys = range(0, len(cities))
        self.best_solution = None
        self.population = []

        cities_id = []
        for c in xrange(0, len(cities)):
            town = Town(self.keys[c], cities[c][0], cities[c][1], cities[c][2])
            self.cities_dict[town.id] = town
            cities_id.append(town)
        Town.compute_all_possible_distance(cities_id)

    def create_population(self):
        """
        Creates a population based on the keys passed as argument.
        Returns the population.
        """
        for i in xrange(0, Problem.NB_POPULATION):
            shuffle(self.keys)  # Use Fisher-Yates shuffle, O(n). Better than copying and removing
            self.population.append(Solution(self.keys[:]))

    def initialize(self):
        """
        Preparation for the execution of the algorithm.
        """
        self.best_solution = Solution([])
        self.best_solution.distance = float('inf')
        self.create_population()
        self.compute_all_distances()

    def compute_all_distances(self):
        """
        Computes the distances for all the solutions availlable in the population.
        Determines also the best_solution in the population.
        """
        for p in self.population:
            p.compute_distance()
            if p.distance < self.best_solution.distance and not equal_double(p.distance, self.best_solution.distance):
                self.best_solution = deepcopy(p)

    def generate(self):
        """
        Runs all the steps for the generation of a "good" solution.
        Returns the best solution obtained during the generation.
        """
        new_population = self.selection_process()
        new_population += self.crossover_process(new_population)
        self.mutation_process(new_population)

        self.population = new_population
        self.compute_all_distances()

        # If we don't have enough town to realize a crossover (eg 5)
        if len(self.population) > Problem.NB_POPULATION:
            self.population.sort(key=lambda p:p.distance)
            self.population = self.population[:Problem.NB_POPULATION]
        return self.best_solution

    def selection_process(self):
        """
        Runs the tournament with a specified size (defined as static).
        """
        new_population = []
        # If the number of cities is to small, we return the entire population and we'll cut it later
        if self.SIZE_TOURNAMENT_BATTLE >= len(self.population):
            return self.population
        else:
            for i in xrange(0, int(round((1-Problem.CROSSOVER_FRACTION)*Problem.NB_POPULATION))):
                solutions = sample(self.population, self.SIZE_TOURNAMENT_BATTLE)
                solutions.sort(key=lambda p: p.distance)
                self.population.remove(solutions[0]) # O(n) but if we want, we could do the tricks with swaping with the last element and then pop it. But the population is really small so not necessary
                new_population.append(solutions[0])
        return new_population

    def crossover_process(self, new_population):
        """
        Does the crossover of two random solutions
        """
        future_solution = []
        for i in xrange(0, int(round(Problem.NB_POPULATION*Problem.CROSSOVER_FRACTION)/2)):
            solution1 = choice(new_population)
            solution2 = solution1
            while solution2 == solution1:
                solution2 = choice(new_population)

            future_solution.append(self.crossover(solution1, solution2))
            future_solution.append(self.crossover(solution2, solution1))
        return future_solution

    def crossover(self, ga, gb):
        fa, fb = True, True
        n = len(ga)
        town = choice(ga.chromosome)
        x = ga.index(town)
        y = gb.index(town)
        g = [town]

        while fa or fb:
            x = (x - 1) % n
            y = (y + 1) % n
            if fa:
                if ga[x] not in g:
                    g.insert(0, ga[x])
                else:
                    fa = False
            if fb:
                if gb[y] not in g:
                    g.append(gb[y])
                else:
                    fb = False

        remaining_towns = []
        if len(g) < len(ga):
            while len(g)+len(remaining_towns) != n:
                x = (x - 1) % n
                if ga[x] not in g:
                    remaining_towns.append(ga[x])
            shuffle(remaining_towns)  # Use Fisher-Yates shuffle, O(n). Better than copying and removing
            while len(remaining_towns) > 0:
                g.append(remaining_towns.pop())

        return Solution(g)

    def mutation_process(self, new_population):
        """
        Mutates some of the solutions in the new_population passed as argument.
        """
        for s in sample(new_population, int(round(Problem.MUTATION_RATE*Problem.NB_POPULATION))):
            s.mutate()

class TS_GUI:
    """
    Class attached with Problem to represent the TSP.
    """
    screen_x = 500
    screen_y = 600
    offset_y = 50
    offset_y_between_text = 20
    offset_x_y_city_name = 10

    city_color = [10, 10, 200]
    city_start_color = [255, 0, 0]
    city_end_color = [0, 255, 0]
    city_radius = 3
    cities_name = 'v'

    infobox_color = [128, 128, 128]
    font_color = [255, 255, 255]

    def __init__(self, gui=True):
        if gui:
            pygame.init()
            self.window = pygame.display.set_mode((TS_GUI.screen_x, TS_GUI.screen_y))
            pygame.display.set_caption('Travelling Salesman Problem - Antognini Aeberli')
            self.screen = pygame.display.get_surface()
            self.font = pygame.font.Font(None, 18)
            self.font_city_name = pygame.font.Font(None, 12)
            pygame.display.flip()
            self.cities_dict = {}

    def draw_one_city(self, name, x, y, color, color_font):
        """
        Draws one city to the pygame gui screen.
        """
        pygame.draw.circle(self.screen, color, (int(x), int(y)), TS_GUI.city_radius)
        text = self.font_city_name.render(name, True, color_font)
        self.screen.blit(text, (x-TS_GUI.offset_x_y_city_name, y-TS_GUI.offset_x_y_city_name))

    def draw_path(self, solution, nb_generation):
        """
        Draws the path (between cities) of a solution and the appropriate informations to the pygame gui screen.
        """
        self.screen.fill(0)
        cities_to_draw = []
        for c in xrange(0, len(solution)):
            color, color_font = TS_GUI.city_color, TS_GUI.font_color
            if c == 0:
                color, color_font = TS_GUI.city_start_color, TS_GUI.city_start_color
            elif c == len(solution)-1:
                color, color_font = TS_GUI.city_end_color, TS_GUI.city_end_color

            town = self.cities_dict[solution[c]]
            self.draw_one_city(town.name, town.x, town.y, color, color_font)
            cities_to_draw.append((int(town.x), int(town.y)))

        pygame.draw.lines(self.screen, self.city_color, True, cities_to_draw)  # True close the polygon between the first and last point

        self.draw_infobox()

        text = self.font.render("Generation %i, Length %s" % (nb_generation, solution.distance), True, TS_GUI.font_color)
        self.screen.blit(text, (0, TS_GUI.screen_y - TS_GUI.offset_y + TS_GUI.offset_y_between_text))

        text = self.font.render("%i cities" % len(self.cities_dict), True, TS_GUI.font_color)
        self.screen.blit(text, (0, TS_GUI.screen_y - TS_GUI.offset_y))

        pygame.display.flip()

    def draw_infobox(self):
        """
        Draws the base style of the infobox at the bottom of the gui.
        """
        pygame.draw.rect(self.screen, TS_GUI.infobox_color, (0, TS_GUI.screen_y-TS_GUI.offset_y, TS_GUI.screen_x, TS_GUI.offset_y))

    def read_cities(self):
        """
        Proposes a gui for entering cities on a 500x500 sized map and returns the entered cities.
        Returns a list with [NAME, POS_X, POS_X] where the names are auto generated.
        """
        self.draw_infobox()
        text = self.font.render("Click with the mouse to create a city. Press Enter to continue.", True, TS_GUI.font_color)
        self.screen.blit(text, (0, TS_GUI.screen_y - TS_GUI.offset_y + TS_GUI.offset_y_between_text))
        pygame.display.flip()

        running = True
        cities = []
        i = 0
        while running:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if y <= TS_GUI.screen_y-TS_GUI.offset_y:
                    cities.append([TS_GUI.cities_name + str(i), x, y])
                    self.draw_one_city(TS_GUI.cities_name + str(i), x, y, TS_GUI.city_color, TS_GUI.font_color)
                    pygame.display.flip()
                    i += 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False
            elif event.type == pygame.QUIT:
                exit(-1)
        return cities

    def wait_to_quit(self, i, best_solution):
        """
        Proposes a gui showing the best_solution to the user and waits for its confirmation to quit.
        """
        self.draw_infobox()
        text = self.font.render(str(len(self.cities_dict)) + " cities, Best : #" + str(i) + " generation, Distance : " + str(best_solution.distance), True, TS_GUI.font_color)
        self.screen.blit(text, (0, TS_GUI.screen_y - TS_GUI.offset_y))
        text = self.font.render("Press Enter to quit !", True, TS_GUI.font_color)
        self.screen.blit(text, (0, TS_GUI.screen_y - TS_GUI.offset_y + TS_GUI.offset_y_between_text))
        pygame.display.flip()

        # wait until the user closes the window or presses the return key.
        running = True
        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False

    def display(self, problem, max_time=0):
        """
        Executes the problem resolving and visualizes the results on the pygame gui.
        """
        old_best_solution = problem.best_solution
        printVerbose("Generation 0 : " + str(old_best_solution))
        self.draw_path(old_best_solution, 0)

        running = True
        i = 1
        t0 = 0
        ith_best = 0

        if max_time > 0:
            t0 = clock()

        while running:
            best_solution = problem.generate()
            if not equal_double(old_best_solution.distance, best_solution.distance):
                old_best_solution = best_solution
                self.draw_path(old_best_solution, i)
                printVerbose("Generation " + str(i) + " : " + str(best_solution))
                ith_best = i
            i += 1

            event = pygame.event.poll()

            # Verify if the user has request to quit the gui, or the maximum time has passed, or if the problem has converged.
            if event.type == pygame.QUIT or i-ith_best > Problem.DELTA_GENERATION and max_time <= 0 or (max_time > 0 and int(clock()-t0) > max_time):
                # Quit the loop if so.
                running = False

        self.wait_to_quit(ith_best, old_best_solution)

        # prepare the solution and return it
        return self.return_solution(problem.best_solution)

    def display_text_only(self, problem, max_time=0):
        """
        Executes the problem resolving and displays the results on the command line.
        """
        old_best_solution = problem.best_solution
        printVerbose("Generation 0 : " + str(old_best_solution))

        t0 = 0
        i = 1
        ith_best = 0

        if max_time > 0:
            t0 = clock()

        # Until no convergence appears or the maximum processing time reached, generate new solutions and keep the best.
        while i-ith_best <= Problem.DELTA_GENERATION and max_time <= 0 or (max_time > 0 and int(clock()-t0) < max_time):
            best_solution = problem.generate()
            if not equal_double(old_best_solution.distance, best_solution.distance):
                old_best_solution = best_solution
                printVerbose("Generation " + str(i) + " : " + str(best_solution))
                ith_best = i
            i += 1


        # prepare the best solution for returning.
        return self.return_solution(problem.best_solution)

    def return_solution(self, solution):
        """
        Creates the by the laboratory requested solution format and returns it..
        Returns the solution in format  (distance, list(cities))
        """
        cities = []
        for c in xrange(0, len(solution)):
            cities.append(self.cities_dict[solution[c]].name)
        return solution.distance, cities

    def quit(self):
        """
        Closes and exits pygame.
        """
        pygame.quit()


def usage():
    """
    Prints the module how to usage instructions to the console"
    """
    print(__doc__)


def get_argv_params():
    """
    Recuperates the arguments from the command line
    """
    opts = []
    try:
        opts = getopt.getopt(
            sys.argv[1:],
            "hnm:v",
            ["help", "no-gui", "maxtime=", "verbose"])[0]
    except getopt.GetoptError:
        usage()
        print("Wrong options or params.")
        exit(2)

    gui = True
    verbose = False
    max_time = 0

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-n", "--no-gui"):
            gui = False
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-m", "--maxtime"):
            max_time = int(arg)

    filename = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[-1]):
        filename = sys.argv[-1]

    return gui, max_time, filename, verbose


def ga_solve(filename=None, gui=True, max_time=0):
    cities = []
    g = None
    if filename is None:
        g = TS_GUI()
        cities = g.read_cities()

        # quit the gui here, when no gui to show the progress is necessary in future.
        if not gui:
            pygame.quit()
    else:
        with open(filename, 'r+') as f:
            for l in f.readlines():
                cities.append(l.split())

    problem = Problem(cities)
    problem.initialize()
    if g is None:
        g = TS_GUI(gui)
    g.cities_dict = problem.cities_dict

    if gui:
        return g.display(problem, max_time)
    else:
        return g.display_text_only(problem, max_time)

def printVerbose(output):
    if printVerbose.VERBOSE:
        print(output)

printVerbose.VERBOSE = False

if __name__ == "__main__":
    (GUI, MAX_TIME, FILENAME, VERBOSE) = get_argv_params()
    print("arguments( gui: %s maxtime: %s filename: %s verbose: %s )" % (GUI, MAX_TIME, FILENAME, VERBOSE))
    printVerbose.VERBOSE = VERBOSE

    results = ga_solve(FILENAME, GUI, MAX_TIME)
    print("distance: %s" % results[0])
    print("cities:   %s" % results[1])