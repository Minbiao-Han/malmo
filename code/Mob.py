# Created by Minbiao Han and Roman Sharykin
# AI fall 2018

from __future__ import print_function
from collections import deque
from builtins import range
import MalmoPython
import os
import sys
import time
import json
import sys
import math
import itertools
from itertools import permutations

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools

    print = functools.partial(print, flush=True)


class Node_Elem:

    def __init__(self, parent, x, y, dist):
        self.parent = parent
        self.x = x
        self.y = y
        self.dist = dist


class A_Star:

    def __init__(self, s_x, s_y, e_x, e_y, w, h):
        self.s_x = s_x
        self.s_y = s_y
        self.e_x = e_x
        self.e_y = e_y

        self.width = h
        self.height = w

        self.open = []
        self.close = []
        self.path = []

    def find_path(self):
        p = Node_Elem(None, self.s_x, self.s_y, 0.0)
        while True:
            self.extend_round(p)
            if not self.open:
                return
            idx, p = self.get_best()
            if self.is_target(p):
                self.make_path(p)
                return
            self.close.append(p)
            del self.open[idx]

    def make_path(self, p):
        while p:
            self.path.append((p.x, p.y))
            p = p.parent

    def is_target(self, i):
        return i.x == self.e_x and i.y == self.e_y

    def get_best(self):
        best = None
        bv = 1000000
        bi = -1
        for idx, i in enumerate(self.open):
            value = self.get_dist(i)
            if value < bv:
                best = i
                bv = value
                bi = idx
        return bi, best

    def get_dist(self, i):
        # F = G + H
        return i.dist + math.sqrt(
            (self.e_x - i.x) * (self.e_x - i.x)
            + (self.e_y - i.y) * (self.e_y - i.y)) * 1.2

    def extend_round(self, p):
        xs = (0, -1, 1, 0)
        ys = (-1, 0, 0, 1)
        for x, y in zip(xs, ys):
            new_x, new_y = x + p.x, y + p.y
            if not self.is_valid_coord(new_x, new_y):
                continue
            node = Node_Elem(p, new_x, new_y, p.dist + self.get_cost(
                p.x, p.y, new_x, new_y))
            if self.node_in_close(node):
                continue
            i = self.node_in_open(node)
            if i != -1:
                if self.open[i].dist > node.dist:
                    self.open[i].parent = p
                    self.open[i].dist = node.dist
                continue
            self.open.append(node)

    def get_cost(self, x1, y1, x2, y2):
        if x1 == x2 or y1 == y2:
            return 1.0
        return 1.4

    def node_in_close(self, node):
        for i in self.close:
            if node.x == i.x and node.y == i.y:
                return True
        return False

    def node_in_open(self, node):
        for i, n in enumerate(self.open):
            if node.x == n.x and node.y == n.y:
                return i
        return -1

    def is_valid_coord(self, x, y):
        return level_mat[x][y] != "%"

    def get_searched(self):
        l = []
        for i in self.open:
            l.append((i.x, i.y))
        for i in self.close:
            l.append((i.x, i.y))
        return l


def find_path():
    s_x, s_y = pStart['x'], pStart['z']
    e_x, e_y = pEnd['x'], pEnd['z']
    a_star = A_Star(s_x, s_y, e_x, e_y, len(level_mat[0]), len(level_mat))
    a_star.find_path()
    searched = a_star.get_searched()
    path = a_star.path
    print("A* number of nodes expanded: ", len(searched))
    print("A* path length:", len(path))

    path.reverse()
    return path


def getLayout(name):
    matrix = tryToLoad("layouts/" + name)
    return matrix


def tryToLoad(fullname):
    if (not os.path.exists(fullname)): return None
    f = open(fullname)
    Matrix = [line.strip() for line in f]
    f.close()
    return Matrix


level_mat = getLayout("smallMaze.lay")


def GenBlock(x, y, z, blocktype):
    return '<DrawBlock x="' + str(x) + '" y="' + str(y) + '" z="' + str(z) + '" type="' + blocktype + '"/>'


def GenPlayerStart(x, z):
    return '<Placement x="' + str(x + 0.5) + '" y="56" z="' + str(z + 0.5) + '" yaw="0"/>'


pStart = {'x': 0, 'z': 0}
pEnd = {'x': 0, 'z': 0}
corners = []


def mazeCreator():
    genstring = ""
    for i in range(len(level_mat)):
        for j in range(len(level_mat[0])):

            if level_mat[i][j] == "%":
                genstring += GenBlock(i, 54, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 55, j, "diamond_block") + "\n"
                genstring += GenBlock(i, 56, j, "diamond_block") + "\n"

            elif level_mat[i][j] == "P":
                pStart['x'] = i
                pStart['z'] = j

            elif level_mat[i][j] == ".":
                genstring += '<DrawItem x="' + str(i) + '" y="56" z="' + str(j) + '" type="apple"/>'
                pEnd['x'] = i
                pEnd['z'] = j

            elif level_mat[i][j] == "E":
                genstring += '<DrawEntity x="'+ str(i+0.5)+'" y="56" z="'+ str(j+0.5) +'" type="Zombie"/>'
                #corners.append((i, j))

    return genstring


# More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"

missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <About>
                <Summary>Hello world!</Summary>
              </About>
              <ServerSection>
                <ServerInitialConditions>
                  <Time>
                    <StartTime>21000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                  </Time>
                </ServerInitialConditions>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                  <DrawingDecorator>
                    ''' + mazeCreator() + '''
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="45000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart> ''' + GenPlayerStart(pStart['x'], pStart['z']) + ''' </AgentStart>
                <AgentHandlers>
                  <DiscreteMovementCommands/>
                  <ObservationFromFullStats/>
                  <RewardForCollectingItem>
                        <Item type="apple" reward="1"/>
                  </RewardForCollectingItem>
                  <ObservationFromGrid>
                      <Grid name="floor3x3W">
                        <min x="-1" y="0" z="-1"/>
                        <max x="1" y="0" z="1"/>
                      </Grid>
                      <Grid name="floor3x3F">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="-1" z="1"/>
                      </Grid>
                  </ObservationFromGrid>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print('ERROR:', e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)


def moveRight():
    agent_host.sendCommand("strafe 1")
    time.sleep(0.2)

    print("moving right")


def moveLeft():
    agent_host.sendCommand("strafe -1")
    time.sleep(0.2)
    print("moving left")


def moveStraight():
    agent_host.sendCommand("move 1")
    time.sleep(0.2)
    print("moving straight")


def moveBack():
    agent_host.sendCommand("move -1")
    time.sleep(0.2)
    print("moving backwards")


def isWallAhead(world_state):
    blocks = {'N': 0, 'E': 0, 'S': 0, 'W': 0}
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)

        if grid[3] == u'diamond_block':
            blocks['N'] = 1
        if grid[1] == u'diamond_block':
            blocks['E'] = 1
        if grid[5] == u'diamond_block':
            blocks['S'] = 1
        if grid[7] == u'diamond_block':
            blocks['W'] = 1

        return grid


def isGoalReached(world_state):
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3F', 0)
        if grid[4] == u'glowstone':
            return True
        else:
            return False

def BFS(maze, start, end):
    queue = [start]
    visited = set()

    while len(queue) != 0:
        if queue[0] == start:
            path = [queue.pop(0)]  # Required due to a quirk with tuples in Python
        else:
            path = queue.pop(0)
        front = path[-1]
        if front == end:
            print("BFS number of nodes expanded: ", len(visited))
            print("BFS path length:", len(path))
            return path
        elif front not in visited:
            for adjacentSpace in getAdjacentSpaces(maze, front, visited):
                newPath = list(path)
                newPath.append(adjacentSpace)
                queue.append(newPath)
            visited.add(front)

    return None


def DFS(maze, start, end):
    queue = deque([start])
    visited = set()

    while len(queue) != 0:
        if queue[0] == start:
            path = [queue.pop()]  # Required due to a quirk with tuples in Python
        else:
            path = queue.pop()
        front = path[-1]
        if front == end:
            print("DFS number of nodes expanded: ", len(visited))
            print("DFS path length:", len(path))
            return path
        elif front not in visited:
            for adjacentSpace in getAdjacentSpaces(maze, front, visited):
                newPath = list(path)
                newPath.append(adjacentSpace)
                queue.append(newPath)
            visited.add(front)
    return None


def getAdjacentSpaces(maze, space, visited):
    spaces = list()
    spaces.append((space[0] - 1, space[1]))  # Up
    spaces.append((space[0] + 1, space[1]))  # Down
    spaces.append((space[0], space[1] - 1))  # Left
    spaces.append((space[0], space[1] + 1))  # Right

    final = list()
    for i in spaces:
        if maze[i[0]][i[1]] != '%' and i not in visited:
            final.append(i)
    return final

def getAllCornerPaths(maze, start, corners):
    paths = {}
    for i in corners:
        paths[(start, i)] = BFS(maze, start, i)

    perm = list(itertools.permutations(corners, 2))

    for i in perm:
        stuff = (i[0], i[1])
        paths[(i[0], i[1])] = BFS(maze, i[0], i[1])
        print(i[0], paths[stuff][0])
        print(i[1], paths[stuff][-1])

    return paths


def CornerSearch(maze, start, perm, searched):
    all_paths = []
    seq_path = []
    total_BFS = 0

    for i in range(len(perm)):
        sequence = perm[i]

        for i in range(len(sequence)):
            if i == 0:
                seq_path = searched[(start, sequence[i])]
                #print(seq_path[0], start)
                #print(start, sequence[i])
            # elif i == len(sequence) -1:
            #     #print(sequence[i - 1])
            #     temp = searched[(sequence[i - 1], sequence[i])]
            #     #temp.pop(0)
            #     seq_path += temp

            else:
                # temp1 = searched[(sequence[i - 1], sequence[i])]
                # if temp1 == BFS(maze, sequence[i - 1], sequence[i]):
                #     print("not same same")
                # else: print("different")
                #temp1.pop(0)
                seq_path += searched[(sequence[i - 1], sequence[i])]


        all_paths.append(seq_path)
        seq_path = []
        print("length of all paths", len(all_paths))

    #print("Total nodes expanded: ", total_BFS)
    shortest = []
    for i in all_paths:

        if len(shortest) == 0:
            shortest = i
        elif len(shortest) > len(i):
            shortest = i

    return shortest


my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()
my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001)) #10000 in use - try 10001

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        # agent_host.startMission(my_mission, my_mission_record)
        agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "experimentID2")
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:", e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)

print()
print("Mission running ", end=' ')

print(pStart)

#path = [(3, 11), (3, 12), (3, 13), (4, 13), (5, 13), (5, 12), (6, 12), (7, 12), (7, 11), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (8, 6), (8,5), (8,4), (8,3), (8,2), (8,1)]
#pathD = DFS(level_mat, (pStart['x'], pStart['z']), (pEnd['x'], pEnd['z']))
#pathB = BFS(level_mat, (pStart['x'], pStart['z']), (pEnd['x'], pEnd['z']))
#pathA = find_path()

# perm = list(itertools.permutations(corners))
# searched = getAllCornerPaths(level_mat, (pStart['x'], pStart['z']), corners)

#pathC = CornerSearch(level_mat, (pStart['x'], pStart['z']), perm, searched)


# if pathB == pathD:
#     print("the paths are the exact same lol")
#
# else:
#     print("paths are different")

# path = searched
# print(path)
# # print(pStart)
# while len(path) != 1:
#     point = path.pop(0)
#     x_cur = point[0]
#     y_cur = point[1]
#     next = path[0]
#
#     if (x_cur == next[0] and y_cur == (next[1] - 1)):
#         moveStraight()
#
#     elif (x_cur == next[0] and y_cur == (next[1] + 1)):
#         moveBack()
#
#     elif (x_cur == (next[0] - 1) and y_cur == next[1]):
#         moveLeft()
#
#     elif (x_cur == (next[0] + 1) and y_cur == next[1]):
#         moveRight()
#
#     elif (x_cur == next[0] and y_cur == next[1]):
#         pass
#
#     else:
#         print("current: " + str(point))
#         print("next: " + str(next))
#         print("The path you entered is not continuous. Please fix your path input and try again.")
#         break
reward = 0
while world_state.is_mission_running:

    world_state = agent_host.getWorldState()
    if world_state.number_of_rewards_since_last_state > 0:
        reward += world_state.rewards[-1].getValue()
        print(reward)

    if reward == 4:
        break

    print(".", end="")
    time.sleep(0.1)

print()
print("Mission ended")
# Mission has ended.