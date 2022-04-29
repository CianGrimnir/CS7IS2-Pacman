# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections


class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for state in self.mdp.getStates():
            self.values[state] = 0.0
        for iteration in range(self.iterations):
            values = self.values.copy()
            for state in self.mdp.getStates():
                state_values = util.Counter()
                for action in self.mdp.getPossibleActions(state):
                    state_values[action] = self.computeQValueFromValues(state, action)
                values[state] = state_values[state_values.argMax()]
            self.values = values.copy()

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        total = 0.0
        # print(self.mdp.getTransitionStatesAndProbs(state, action))
        for next_state, problem in self.mdp.getTransitionStatesAndProbs(state, action):
            total += problem * (self.mdp.getReward(state, action, next_state) + (self.discount*self.values[next_state]))
        return total

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        max_value = -float('inf')
        max_action = None
        for action in self.mdp.getPossibleActions(state):
            value = self.computeQValueFromValues(state, action)
            if value > max_value:
                max_value, max_action = value, action
        return max_action

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for state in self.mdp.getStates():
            self.values[state] = 0.0
        for iteration in range(self.iterations):
            state = self.mdp.getStates()[iteration % len(self.mdp.getStates())]
            if self.mdp.isTerminal(state):
                continue
            state_values = util.Counter()
            for action in self.mdp.getPossibleActions(state):
                state_values[action] = self.computeQValueFromValues(state, action)
            self.values[state] = state_values[state_values.argMax()]


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors = {}
        pQueue = util.PriorityQueue()
        for state in self.mdp.getStates():
            predecessors[state] = set()

        for state in self.mdp.getStates():
            state_values = util.Counter()
            for action in self.mdp.getPossibleActions(state):
                for next_state, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if prob > 0:
                        predecessors[next_state].add(state)
                state_values[action] = self.computeQValueFromValues(state, action)
            if not self.mdp.isTerminal(state):
                max_value = state_values[state_values.argMax()]
                diff = abs(self.values[state] - max_value)
                pQueue.update(state, -diff)

        for iteration in range(self.iterations):
            if pQueue.isEmpty():
                return
            state = pQueue.pop()
            if self.mdp.isTerminal(state):
                continue
            state_values = util.Counter()
            for action in self.mdp.getPossibleActions(state):
                state_values[action] = self.computeQValueFromValues(state, action)
            self.values[state] = state_values[state_values.argMax()]
            for predecessor in predecessors[state]:
                pred_state_values = util.Counter()
                for action in self.mdp.getPossibleActions(predecessor):
                    pred_state_values[action] = self.computeQValueFromValues(predecessor, action)
                max_pred_qvalue = pred_state_values[pred_state_values.argMax()]
                diff = abs(self.values[predecessor] - max_pred_qvalue)
                if diff > self.theta:
                    pQueue.update(predecessor, -diff)

