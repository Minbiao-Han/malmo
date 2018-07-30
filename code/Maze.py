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

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools

    print = functools.partial(print, flush=True)

# More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"

missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>Hello world!</Summary>
              </About>

              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                  <DrawingDecorator>
                    <DrawCuboid x1="1" y1="55" z1="-1" x2="-30" y2="59" z2="30" type="diamond_block"/>
                    <DrawCuboid x1="0" y1="56" z1="0" x2="-29" y2="59" z2="29" type="air"/>
                    <DrawCuboid x1="-11" y1="55" z1="11" x2="-18" y2="59" z2="18" type="diamond_block"/>
                    <DrawCuboid x1="-12" y1="56" z1="12" x2="-17" y2="59" z2="17" type="air"/>
                    <DrawCuboid x1="-11" y1="56" z1="14" x2="-12" y2="59" z2="15" type="air"/>
                    <DrawCuboid x1="-7" y1="56" z1="22" x2="-22" y2="59" z2="22" type="diamond_block"/>
                    <DrawCuboid x1="-7" y1="56" z1="7" x2="-22" y2="59" z2="7" type="diamond_block"/>
                    <DrawCuboid x1="-7" y1="56" z1="10" x2="-7" y2="59" z2="19" type="diamond_block"/>
                    <DrawCuboid x1="-7" y1="56" z1="14" x2="-2" y2="59" z2="15" type="diamond_block"/>
                    <DrawCuboid x1="-2" y1="56" z1="2" x2="-2" y2="59" z2="13" type="diamond_block"/>
                    <DrawCuboid x1="-4" y1="56" z1="16" x2="-4" y2="59" z2="27" type="diamond_block"/>
                    <DrawBlock x="-28" y="55" z="2" type="obsidian"/>
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>                <Placement x="-1" y="58" z="1" yaw="90"/>            </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ObservationFromGrid>
                      <Grid name="floor3x3W">
                        <min x="-1" y="1" z="-1"/>
                        <max x="1" y="1" z="1"/>
                      </Grid>
                      <Grid name="floor3x3F">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="-1" z="1"/>
                      </Grid>
                  </ObservationFromGrid>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
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



def turnRight():
    agent_host.sendCommand("turn 1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")


def turnLeft():
    agent_host.sendCommand("turn -1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")


def moveRight():
    agent_host.sendCommand("turn 1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")
    agent_host.sendCommand("move 1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")

def moveLeft():
    agent_host.sendCommand("turn -1")  # Start looking downward slowly
    time.sleep(0.5)  # Wait a second until we are looking in roughly the right direction
    agent_host.sendCommand("turn 0")
    agent_host.sendCommand("move 1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")

def moveStraight():
    agent_host.sendCommand("move 1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")

def moveBack():
    agent_host.sendCommand("move -1")
    time.sleep(0.5)
    agent_host.sendCommand("move 0")

def isWallAhead(world_state):
    blocks = {'N': 0, 'E': 0, 'S': 0, 'W': 0}
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)

        if grid[3]==u'diamond_block':
            blocks['N'] = 1
        if grid[1]==u'diamond_block':
            blocks['E'] = 1
        if grid[5]==u'diamond_block':
            blocks['S'] = 1
        if grid[7]==u'diamond_block':
            blocks['W'] = 1

        return blocks

def isGoalReached(world_state):
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3F', 0)
        if grid[4]==u'obsidian':
            return True
        else:
            return False

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission(my_mission, my_mission_record)
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
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    print(isWallAhead(world_state))
    if(isGoalReached(world_state)):
        break



print()
print("Mission ended")
# Mission has ended.
