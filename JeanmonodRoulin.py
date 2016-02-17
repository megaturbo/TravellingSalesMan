__author__ = 'Jeanmonod + Roulin'


class City:
    def __init__(self, name, posx, posy):
        self.name = name
        self.posx = posx
        self.posy = posy


def read_city(line):
    l = line.split(' ')
    return City(l[0], int(l[1]), int(l[2]))


def ga_solve(filename=None, gui=True, maxtime=0):
    cities = []
    if filename is None:
        # Show pygame, click to add city
        a = 1
    else:
        with open(filename, 'r+') as file:
            for line in file.readlines():
                cities.append(read_city(line))
