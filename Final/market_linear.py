import gurobipy as gb
import random
import time
import numpy as np

# generates a given agent's demand MIP
class AgentLinear:
    # objects: array of objects to be allocated
    # value: linear values of objects for this agent (length |object| array)
    # capacity: allocation capacity of this agent (integer)
    # budget: budget for this agent (float)
    def __init__(self, objects, value, complements, capacity, budget):
        self.objects = objects
        # initialize MIP
        self.prob = gb.Model("agent")
        self.prob.setParam("OutputFlag", 0)
        # add variables
        self.object_vars = self.prob.addVars(self.objects, vtype = gb.GRB.BINARY, name='object')
        complement_vars = []
        complement_coeffs = {}
        for objs, u in np.ndenumerate(complements):
            if not u==0:
                complement_vars.append(objs)
                complement_coeffs[objs] = u
        self.complement_vars = self.prob.addVars(complement_vars, vtype = gb.GRB.BINARY, name = 'complement')
        # budget constraint
        self.budget = budget
        self.budgetConstraint = self.prob.addConstr(sum(0.0 * self.object_vars[a] for a in self.object_vars), sense=gb.GRB.LESS_EQUAL, rhs=float(budget), name='budget')
        # capacity constraints
        self.prob.addConstr(sum(1.0 * self.object_vars[x] for x in objects), sense=gb.GRB.LESS_EQUAL, rhs=float(capacity),name='capacity')
        # complement constraints
        for objs in complement_vars:
            self.prob.addConstr(2.0*self.complement_vars[objs] - 1.0*self.object_vars[self.objects[objs[0]]] - 1.0*self.object_vars[self.objects[objs[1]]], sense=gb.GRB.EQUAL, rhs=0.0,name='complement'+str(objs))
        # add objective
        self.prob.setObjective(self.object_vars.prod({objects[i]:v for i,v in enumerate(value)}) + self.complement_vars.prod(complement_coeffs), gb.GRB.MAXIMIZE)

    # get this agent's demand when faced with a given price vector
    def demand(self, prices):
        # set MIP bugdet constraint to reflect to given prices
        for i, p in enumerate(prices):
            self.prob.chgCoeff(self.budgetConstraint, self.object_vars[self.objects[i]], p)
        self.prob.optimize()
        return np.array([self.object_vars[v].x for v in self.object_vars])

# generates a set of agent demand MIPs for a given market
class MarketLinear:
    # objects: array of objects to be allocated
    # agents: agents in the market; MUST BE SORTED (or shuffled) IN ORDER OF INCREASING BUDGET
    # values: linear values of objects for each agent (|agent| by |object| array)
    # complements: matrix of values for each agent for having 2 objects simultaneously (|agent| by |object| by |object|)
    # capacities: allocation capacity of each agent (|agent| length array)
    # note: budgets are distributed linearly, with first agent lowest - order agents as desired before initializing
    def __init__(self, objects, agents, values, complements, capacities):
        self.agent_names = agents
        self.agent_models = []
        self.objects = objects
        budgets = np.linspace(start = 100., stop = 107., num = len(agents))
        for i in range(len(agents)):
            self.agent_models.append(AgentLinear(objects, values[i], complements[i], capacities[i], budgets[i]))

    # given price vector, get total demand
    def demand(self, prices):
        total_demand = np.zeros_like(prices)
        for a in self.agent_models:
            total_demand = np.add(total_demand, a.demand(prices))
        return total_demand

    # given price vector, get allocation
    def allocation(self, prices):
        return np.array([a.demand(prices) for a in self.agent_models])

    # return list of agent models
    def agents(self):
        return self.agent_models

def test():
    objects = ['A','B','C']
    value = [1,1,4]
    complements = [[0,3,0],[0,0,0],[0,0,0]]
    capacity = 2
    budget = 100
    agent = AgentLinear(objects, value, complements, capacity, budget)
    print agent.demand([50,50,50])

if __name__ == '__main__':
    test()