import matplotlib.pyplot as plt
import numpy as np

def plot_fitness(statistics, ylog=False, view=False, filename="fitness.svg"):
    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

