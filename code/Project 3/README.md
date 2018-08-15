Project 3 Reinforcement Learning:

Note that the value iteration agent we have seen in class does not actually learn from experience. Rather, it ponders its MDP model to arrive at a complete policy before ever interacting with a real environment. When it does interact with the environment, it simply follows the precomputed policy (e.g. it becomes a reflex agent). This distinction may be subtle in a simulated environment, but it's very important in the real world, where the real MDP is not available.

In this project you will implement a Q-learning agent, which does very little on construction, but instead learns by trial and error from interactions with the environment through its update(reward, state, action, nextState) method. A stub of a Q-learner is specified in QLearning.py. In this assignment, the purpose of the agent is to learn how to navigate a given landscape and get to the redstone ore block to receive a large reward of 100 points. If the agent falls in the water, it will incur a negative reward of -100 points. The agent will also lose a point for each action it takes. Please see the qlearning.xml file for more details on how rewards are assigned.     

For this assignment you will need to complete the following methods:

updateQTable() 
updateQTableFromTerminatingState()
act()
run()  

Complete your Q-learning agent by implementing epsilon-greedy action selection in act(), meaning the agent chooses random actions an epsilon fraction of the time, and follows its current best Q-values otherwise. Note that choosing a random action may result in choosing the best action - that is, you should not choose a random sub-optimal action, but rather any random legal action.

Hint 1: When implementing the run() method, consider what happens when the action being taken by the agent is it’s first action vs all the subsequent actions. 

Hint 2: Use the q value formula we saw in class to update the Q-Table in the updateQTable() method.  

Grading: We will run your code on a number of different terrains to ensure that your code can learn the optimal policy of each given map. You will be awarded 4 points for a correct implementation of each method, for a total of 12 points. However, keep in mind that your agent must actually do something, so if you successfully complete the updateQTable() and updateQTableFromTerminatingState() but add no code to the remaining methods, your Q-Table will never get updated, your agent will stand in place and your implementation will receive a score of 0.
