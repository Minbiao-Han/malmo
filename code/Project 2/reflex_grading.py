from __future__ import print_function
from __future__ import division

from builtins import range
from past.utils import old_div
import MalmoPython
import json
import logging
import math
import os
import random
import sys
import time
import re
import uuid
from collections import namedtuple
from operator import add
from random import *
import numpy as np

def evalfuncReflex(pos, enemy_pos, food):
    # Inputs: pos - tuple, enemy_pos - tuple, food - array
    # Output: your evaluation score

    if pos == enemy_pos:
        return(-100000)
    else:
        if (pos[0] - 0.5, pos[1] - 0.5) in food:
            foodtmp = food.copy()
            foodtmp.remove((pos[0] - 0.5, pos[1] - 0.5))
            enemydist = manhattan_distance(pos, enemy_pos)
            escore = -12 / enemydist
            if foodtmp:
                closestfood = min([manhattan_distance(pos, i) for i in foodtmp])

            else:
                closestfood = 0
            return (-2 * closestfood) + escore - (100 * len(foodtmp))
        else:
            enemydist = manhattan_distance(pos, enemy_pos)
            escore = -12/enemydist

            if food:
                closestfood = min([manhattan_distance(pos, i) for i in food])

            else:
                closestfood = 0
            return (-2 * closestfood) +escore - (100 * len(food))


def chooseAction(pos, wstate, food, enemy_pos):
     #print('wstate', wstate)
     illegalgrid = illegalMoves(wstate)
     dirscores = []
     scores = []
     if "left" not in illegalgrid:
         score = evalfuncReflex((pos[0]+1, pos[1]), enemy_pos, food)
         scores.append(score)
         dirscores.append(('left', evalfuncReflex((pos[0]+1, pos[1]), enemy_pos, food)))
     if "forward" not in illegalgrid:
         #print(pos[0], pos[1]+1)
         score = evalfuncReflex((pos[0], pos[1] + 1), enemy_pos, food)
         scores.append(score)
         dirscores.append(('forward', evalfuncReflex((pos[0], pos[1]+1), enemy_pos, food)))
     if "right" not in illegalgrid:
         #print(pos[0] - 1, pos[1])
         score = evalfuncReflex((pos[0]-1, pos[1]), enemy_pos, food)
         scores.append(score)
         dirscores.append(('right', evalfuncReflex((pos[0]-1, pos[1]), enemy_pos, food)))
     if "back" not in illegalgrid:
         #print(pos[0], pos[1]-1)
         score = evalfuncReflex((pos[0], pos[1]-1), enemy_pos, food)
         scores.append(score)
         dirscores.append(('back', score))

     togo = max(scores)
     togolst = []
     for i in dirscores:
         if i[1] == togo:
             togolst.append(i)

     lengo = len(togolst) - 1

     rand = randint(0, lengo)
     togo = togolst[rand]
     return togo

def reflexAgentMove(agent, pos, wstate, food, enemy_pos):

    togo = chooseAction(pos, wstate, food, enemy_pos)

    if togo[0] == "right":
        moveRight(agent)
    elif togo[0] == "left":
        moveLeft(agent)
    elif togo[0] == "forward":
        moveStraight(agent)
    elif togo[0] == "back":
        moveBack(agent)

### Helper methods for you to use ###

# Simple movement functions
# Hint: if you want your execution to run faster you can decrease time.sleep
def moveRight(ah):
    ah.sendCommand("strafe 1")
    time.sleep(0.1)


def moveLeft(ah):
    ah.sendCommand("strafe -1")
    time.sleep(0.1)


def moveStraight(ah):
    ah.sendCommand("move 1")
    time.sleep(0.1)


def moveBack(ah):
    ah.sendCommand("move -1")
    time.sleep(0.1)

# Used to find which movements will result in the player walking into a wall
### Input: current world state
### Output: An array directional strings
def illegalMoves(world_state):
    blocks = []
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)
        if grid[3] == u'diamond_block':
            blocks.append("right")
        if grid[1] == u'diamond_block':
            blocks.append("back")
        if grid[5] == u'diamond_block':
            blocks.append("left")
        if grid[7] == u'diamond_block':
            blocks.append("forward")

        return blocks

# Used to find the Manhattan distance between two tuples
def manhattan_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(ex - sx) + abs(ey - sy)

# Do not modify!
###
###
# This functions moves the enemy agent randomly #
def enemyAgentMoveRand(agent, ws):
    time.sleep(0.1)
    illegalgrid = illegalMoves(ws)
    legalLST = ["right", "left", "forward", "back"]
    for x in illegalgrid:
        if x in legalLST:
            legalLST.remove(x)
    y = randint(0,len(legalLST)-1)
    togo = legalLST[y]
    if togo == "right":
        moveRight(agent)

    elif togo == "left":
        moveLeft(agent)

    elif togo == "forward":
        moveStraight(agent)

    elif togo == "back":
        moveBack(agent)
