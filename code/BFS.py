from __future__ import print_function

from builtins import range
import MalmoPython
import os
import sys
import time
import json
import sys


def get_matrix(layout):
    if not os.path.exists(layout):
        return None
    f = open(layout)
    matrix = [line.strip() for line in f]
    f.close()
    return matrix


def generate_map():
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == "%":
                map[i][j] = 1
            elif matrix[i][j] == "P":
                pStart['x'] = i
                pStart['z'] = j
            elif matrix[i][j] == ".":
                pGoal['x'] = i
                pGoal['z'] = j


matrix = get_matrix("layouts/smallMaze.lay")
map = [[0 for i in range(len(matrix[0]))] for j in range(len(matrix))]
pStart = {'x': 0, 'z': 0}
pGoal = {'x': 0, 'z': 0}


if __name__ == "__main__":
    generate_map()
    print(map)
    print(pStart)
    print(pGoal)