import matplotlib.pyplot as plt
import numpy as np

def plot_fitness(statistics, ylog=False, view=False, filename="fitness.svg"):
    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    plt.figure()
    plt.plot(generation, avg_fitness, "b-", label="average")
    plt.plot(generation, avg_fitness - stdev_fitness, "g--", label="-1 sd")
    plt.plot(generation, avg_fitness + stdev_fitness, "g--", label="+1 sd")
    plt.plot(generation, best_fitness, "r-", label="best")

    plt.title("Population's Average and Best Fitness")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend(loc="best")
    if ylog:
        plt.yscale('symlog')
    plt.savefig(filename)
    if view:
        plt.show()
    plt.close()
