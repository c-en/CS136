import gurobipy as gb
import random
import time
import numpy as np


class AgentLinear:
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
        # add scheduling constraint? how to handle????????????????????

    def demand(self, prices):
        for i, p in enumerate(prices):
            self.prob.chgCoeff(self.budgetConstraint, self.object_vars[self.objects[i]], p)
        self.prob.optimize()
        return np.array([self.object_vars[v].x for v in self.object_vars])

    # do we need stage2 or stage3(!) demand??????

class MarketLinear:
    # objects: array of objects to be allocated
    # agents: agents in the market; MUST BE SORTED (or shuffled) IN ORDER OF INCREASING BUDGET
    # values: linear values of objects for each agent (|agent| by |object| array)
    # capacities: allocation capacity of each agent (|agent| length array)
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
