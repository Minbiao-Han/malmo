from __future__ import print_function
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #2: Run simple mission using raw XML

from builtins import range
import MalmoPython
import os
import sys
import time
import json
import sys

MAX_STEP = 100000

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


level_mat = getLayout("smallMaze.lay")

def GenBlock(x, y, z, blocktype):
    return '<DrawBlock x="' + str(x) + '" y="' + str(y) + '" z="' + str(z) + '" type="' + blocktype + '"/>'

def GenPlayerStart(x, z):
    return '<Placement x="' + str(x + 0.4) + '" y="56" z="' + str(z + 0.4) + '" yaw="0"/>'

pStart = {'x': 0, 'z': 0}
pGoal = {'x': 0, 'z': 0}

def mazeCreator():
    genstring = ""
    for i in range(len(level_mat)):
        for j in range(len(level_mat[0])):
            if level_mat[i][j] == "%":
                genstring += GenBlock(i, 56, j, "diamond_block") + "\n"
            elif level_mat[i][j] == "P":
                pStart['x'] = i
                pStart['z'] = j
            elif level_mat[i][j] == ".":
                pGoal['x'] = i
                pGoal['z'] = j
                genstring += GenBlock(i, 55, j, "glowstone") + "\n"
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
                        <StartTime>12000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                    </Time>
                    <Weather>clear</Weather>
                </ServerInitialConditions>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                  <DrawingDecorator>
                    ''' + mazeCreator() + '''
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="60000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart> '''   + GenPlayerStart(pStart['x'], pStart['z']) +  ''' </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
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
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <AgentQuitFromTouchingBlockType>
                      <Block type="glowstone" />
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

# loc = ['N', 'E', 'S', 'W']
# u = 3
# facing_curr = 'W'

def turnRight():
    agent_host.sendCommand("turn 1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")
    # u += 1
    # facing_curr = loc[u%4]


def turnLeft():
    agent_host.sendCommand("turn -1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")
    # u -= 1
    # facing_curr = loc[u]

def moveRight():
    agent_host.sendCommand("strafe 1")
    time.sleep(0.5)
    agent_host.sendCommand("strafe 0")
    # u += 1
    # facing_curr = loc[u%4]
    global x
    global z
    global table
    x = x + 1
    table[x][z] = 1
    print('moved right:', x, z)

def moveLeft():
    agent_host.sendCommand("strafe -1")
    time.sleep(0.5)
    agent_host.sendCommand("strafe 0")
    # u -= 1
    # facing_curr = loc[u%4]
    global x
    global z
    global table
    x = x - 1
    table[x][z] = 1
    print('moved left', x, z)

def moveStraight():
    agent_host.sendCommand("move 1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")
    global x
    global z
    global table
    z = z + 1
    table[x][z] = 1
    print('moved straight', x, z)

def moveBack():
    agent_host.sendCommand("move -1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")
    global x
    global z
    global table
    z = z - 1
    table[x][z] = 1

def isWallAhead(world_state):
    blocks = {'N': 0, 'E': 0, 'S': 0, 'W': 0}
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)
        if grid[3]==u'diamond_block':
            blocks['E'] = 1
        if grid[1]==u'diamond_block':
            blocks['S'] = 1
        if grid[5]==u'diamond_block':
            blocks['W'] = 1
        if grid[7]==u'diamond_block':
            blocks['N'] = 1
        return blocks


def isGoalReached(world_state):
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3F', 0)
        if grid[4] == u'glowstone':
            return True
        else:
            return False

def actOK(world_state, actions, step):
    #print('observations of world_state.number_of_observations_since_last_state', world_state.number_of_observations_since_last_state)
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        #entities = observations[ENV_ENTITIES]
        #print(entities)
        grid = observations.get(u'floor3x3W', 0)
        #print('grid:', grid[3], grid[1], grid[5], grid[7])
        if actions[step] > 4:
            return False
        if grid[1]==u'diamond_block':
            if actions[step] == 3:
                return False
        if grid[3]==u'diamond_block':
            if actions[step] == 2:
                return False
        if grid[5]==u'diamond_block':
            if actions[step] == 4:
                return False
        if grid[7]==u'diamond_block':
            if actions[step] == 1:
                return False
        nextx = x
        nextz = z
        if actions[step] == 1: nextz = z + 1
        if actions[step] == 2: nextx = x + 1
        if actions[step] == 3: nextz = x - 1
        if actions[step] == 4: nextx = x - 1
        if table[nextx][nextz] == 1: return False
        # if abs(actions[step] - actions[step - 1]) == 2:
        #     return False
    # if actions[step] == 1: z = z + 1
    # if actions[step] == 2: x = x + 1
    # if actions[step] == 3: z = z - 1
    # if actions[step] == 4: x = x - 1
    # table[x][z] = 1
    return True

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()
my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001)) #10000 in use - try 10001

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        #agent_host.startMission(my_mission, my_mission_record)
        agent_host.startMission( my_mission, my_client_pool, my_mission_record, 0, "experimentID2" )
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

# for i in range(4):
#     turnRight()
#
# for i in range(4):
#     moveStraight()
#
# moveLeft()
# moveStraight()
# moveLeft()
# moveLeft()
# for i in range(3):
#     moveBack()
# moveLeft()
# for i in range(8):
#     moveStraight()


# Loop until mission ends:

x = pStart['x']
z = pStart['z']
goal_x = pGoal['x']
goal_z = pGoal['z']
table = [[0 for i in range(len(level_mat[0])+1)] for j in range(len(level_mat)+1)]
actions = [0 for i in range(MAX_STEP)]
table[x][z] = 1
step = 0
# world_state = agent_host.getWorldState()
# while not isGoalReached(world_state):
#     True

while True:
    world_state = agent_host.getWorldState()
    step = step + 1
    data = isWallAhead(world_state)
    stepComplete = 0
    actions[step] = 0
    while(stepComplete != 1):
        print('step: ', step)
        actions[step] = actions[step] + 1
        print('actions is being tried', actions[step])
        print(data)
        print('x and z', x, z)
        if(actions[step] <= 4):
            if (actOK(world_state, actions, step)):
                if actions[step] == 1: moveStraight()
                if actions[step] == 2: moveRight()
                if actions[step] == 3: moveBack()
                if actions[step] == 4: moveLeft()
                stepComplete = 1
        else:
            if(actions[step] > 4):
                table[x][z] = 0
                if actions[step - 1] == 1: moveBack()
                if actions[step - 1] == 2: moveLeft()
                if actions[step - 1] == 3: moveStraight()
                if actions[step - 1] == 4: moveRight()
                actions[step] = 0
                step = step - 1
                if step < 0: stepComplete = 1
    if(step < 0):
        break

while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.5)
    world_state = agent_host.getWorldState()

print()
print("Mission ended")
# Mission has ended.