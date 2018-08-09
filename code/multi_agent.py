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


def getLayout(name):
    matrix = tryToLoad("layouts/" + name)
    return matrix


def tryToLoad(fullname):
    if (not os.path.exists(fullname)): return None
    f = open(fullname)
    Matrix = [line.strip() for line in f]
    f.close()
    return Matrix


level_mat = getLayout("multiAgent.lay")


def GenBlock(x, y, z, blocktype):
    return '<DrawBlock x="' + str(x) + '" y="' + str(y) + '" z="' + str(z) + '" type="' + blocktype + '"/>'


def GenPlayerStart(x, z):
    return '<Placement x="' + str(x + 0.5) + '" y="56" z="' + str(z + 0.5) + '" yaw="0"/>'


pStart = {'x': 0, 'z': 0}
# pEnd = {'x': 0, 'z': 0}
apple = set()

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
                genstring += '<DrawItem x="' + str(i) + '" y="55" z="' + str(j) + '" type="apple"/>'
                apple.add((i, j))
                # pEnd['x'] = i
                # pEnd['z'] = j

            # elif level_mat[i][j] == "E":
            #     genstring += '<DrawEntity x="'+ str(i+0.5)+'" y="56" z="'+ str(j+0.5) +'" type="Zombie"/>'
                # corners.append((i, j))

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
                    <StartTime>22000</StartTime>
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
                  <AgentQuitFromTouchingBlockType>
                     <Block type="diamond_block" />
                  </AgentQuitFromTouchingBlockType>
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


def evaluationFunction(c):
    if c == '%': return -100
    if c == '.': return 1
    if c == ' ': return -1


def decideNextAction(maze, loc):
    xs = (0, -1, 1, 0)
    ys = (-1, 0, 0, 1)
    dx = 0
    dy = 0
    r = -2
    for x, y in zip(xs, ys):
        new_x, new_y = x + loc[0], y + loc[1]
        if evaluationFunction(maze[new_x][new_y]) > r:
            dx = x
            dy = y
    if maze[loc[0] + dx][loc[1] + dy] == '.':
        apple.remove((loc[0] + x, loc[1] + y))
    return dx, dy


my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()
my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001)) #10000 in use - try 10001

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        #agent_host.startMission( my_mission, my_mission_record )
        agent_host.startMission( my_mission, my_client_pool, my_mission_record, 0, "experimentID" )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
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
        print("Error:",error.text)

print()
print("Mission running ", end=' ')


while len(apple) > 0:
    x = pStart['x']
    y = pStart['z']
    nx, ny = decideNextAction(level_mat, (x, y))
    if (nx == 0 and ny == +1): moveStraight()
    if (nx == 0 and ny == -1): moveBack()
    if (nx == -1 and ny == 0): moveRight()
    if (nx == +1 and ny == 0): moveLeft()
    x = x + nx
    y = y + ny
    if level_mat[x][y] == '.':
        level_mat[x][y] == ' '

# Loop until mission ends:
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    if world_state.number_of_rewards_since_last_state != 0:
        reward += world_state.rewards[-1].getValue()
        print(reward)
    for error in world_state.errors:
        print("Error:",error.text)
    if len(apple) == 0:
        break

print()
print("Mission ended")
# Mission has ended.
