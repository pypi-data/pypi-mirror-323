import numpy as np
import copy
from .algorithm  import Algorithm



class GA(Algorithm):
    def __init__(self, 
                 model,
                 population_size=100, 
                 crossover_rate=0.3, 
                 mutation_rate=0.1, 
                 generations=100, 
                 ):
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.model = model
        self.population = [copy.deepcopy(self.model) for i in range(population_size)]
        self.gene_length = self.model.variables[0].shape[0]
        self.best = self.population[0]
        self.best_value = 0
        
    def initial_population(self):
        for popu in self.population:
            popu.variables[0].init_value()

    def evaluate_fitness(self):
        self.obj_list = []
        self.con_list = []
        for popu in self.population:
            self.obj_list.append([obj(popu) * obj.sense for obj in popu.objectives])
            self.con_list.append([constr(popu) for constr in popu.constraints])
        
    def select(self, population, fitness):
        fitness_ = fitness - np.min(fitness, axis=0)
        fitness_sum = np.sum(fitness_, axis=0)
        probabilities = fitness_ / fitness_sum
        p = [x if not np.isnan(x) else 0 for x in probabilities.ravel()]
        sum_p = np.sum(p)
        p = [x / sum_p for x in p]
        if np.any(np.isnan(p)):
            p = [1 / len(population) for i in p]
            pass
        select = np.random.choice(range(self.population_size), size=2, p=p)
        return population[select[0]], population[select[1]]

    def crossover(self, parent1, parent2):
        X1 = parent1.variables[0].value
        X2 = parent2.variables[0].value
        if np.random.rand() < self.crossover_rate:
            child1_X = np.where(np.random.rand(self.gene_length) < 0.5, X1, X2)
            child2_X = np.where(np.random.rand(self.gene_length) < 0.5, X2, X1)
            child1 = copy.deepcopy(parent1)
            child1.variables[0].set_value(child1_X)
            child2 = copy.deepcopy(parent2)
            child2.variables[0].set_value(child1_X)
            return child1, child2
        else:
            return parent1, parent2

    def mutate(self, individual):
        mutated_genes = individual.variables[0].uniform()
        child_X = np.where(np.random.rand(self.gene_length) < self.mutation_rate, individual.variables[0].value, mutated_genes)
        child = copy.deepcopy(individual)
        child.variables[0].set_value(child_X)
        return child

    def solve(self):
        self.initial_population()
        self.evaluate_fitness()
        fitness = self.obj_list
        for generation in range(self.generations):
            new_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.select(self.population, fitness)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.append(child1)
                new_population.append(child2)
            self.population = new_population
            self.evaluate_fitness()
            fitness = self.obj_list
            best_fitness = np.min(fitness)
            idx = np.argmin(fitness)
            sense = self.model.objectives[0].sense
            if  self.best_value * sense > best_fitness * sense or (not self.best_value ):
                self.best_value = best_fitness
                self.best = self.population[idx]
            print(f"Generation {generation}: Best Fitness = {best_fitness} \t {self.best_value}")
        
        return {"X":[x.value for x in self.best.variables],
            "obj":[obj() for obj in self.best.objectives],
            "con":[constr() for constr in self.best.constraints]}

        
        # return self.best.__dict__
