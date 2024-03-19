#!/home/makcymal/miniconda3/bin/python

from math import sqrt, floor
from typing import Sequence
from time import time
import json
import sys

import numpy as np
from numpy.lib.recfunctions import unstructured_to_structured as unstruc_to_struc


seed = 203089051535183421231184365759039973676
rng = np.random.default_rng(seed)


def reset_rng():
    global rng
    rng = np.random.default_rng(seed)


class Graph:
    def __init__(self, n_nodes: int = 20):
        # generate random node position
        self.n_nodes = n_nodes
        self.nodes = np.array([])
        while len(self.nodes) < self.n_nodes:
            self.nodes = rng.integers(low=0.0, high=100.0, size=(self.n_nodes, 2))
            self.nodes = unstruc_to_struc(
                self.nodes, dtype=np.dtype([("x", int), ("y", int)])
            )
            self.nodes = np.unique(np.sort(self.nodes, order=["x", "y"]))

        self.dist = np.zeros(shape=(self.n_nodes, self.n_nodes))
        for r in range(self.n_nodes):
            for c in range(r):
                self.dist[r][c] = self.dist[c][r]
            for c in range(r + 1, self.n_nodes):
                self.dist[r][c] = sqrt(
                    (self.nodes[r]["x"] - self.nodes[c]["x"]) ** 2
                    + (self.nodes[r]["y"] - self.nodes[c]["y"]) ** 2
                )

    def distance(self, node1: int, node2: int) -> float:
        return self.dist[node1][node2]

    def route_len(self, route: Sequence[int]) -> float:
        rlen = 0
        for i in range(1, self.n_nodes):
            rlen += self.dist[route[i]][route[i - 1]]
        rlen += self.dist[route[-1]][route[0]]
        return rlen


def ants_colony(
    graph: Graph,
    n_gener=50,
    n_ants=4,
    n_elites=0.5,
    alfa=1,
    beta=3,
    pher_delta_cf=3,
    vapor_cf=0.5,
) -> Sequence[int]:

    PHER_INI = 0.5
    PHER_MAX = 1.0

    # pheromones for the first generation, all equals
    pheromone = np.full((graph.n_nodes, graph.n_nodes), PHER_INI)
    # the matrix of values inversed to the distance with certain coefficient
    closeness = np.zeros(shape=(graph.n_nodes, graph.n_nodes))
    for r in range(graph.n_nodes):
        for c in range(r):
            closeness[r][c] = closeness[c][r]
        for c in range(r + 1, graph.n_nodes):
            closeness[r][c] = 1 / graph.distance(r, c)

    # each ant's route and the best (i.e. the shortest) route found so far
    # route end connected to the beginning so it's cycle
    curr_route = list(range(graph.n_nodes))
    best_route = list(range(graph.n_nodes))
    # best route length
    best_len = float("inf")

    # just a list of node indices to pass it to numpy.random.choice
    next_pos_choices = list(range(graph.n_nodes))

    # best_route becomes better through generations
    for gener in range(n_gener):
        # matrix of newly laid pheromones by current generation
        # pheromones are recomputed at the end of the current generation
        pher_delta = np.zeros(shape=(graph.n_nodes, graph.n_nodes))

        # n_ants leaves from each node
        for ant in range(n_ants * graph.n_nodes):
            pos = ant % graph.n_nodes

            # controlling current route
            curr_route[0] = pos
            curr_idx = 1
            curr_len = 0

            # ant marks visited nodes with truthy values
            visited = np.array([False] * graph.n_nodes)

            # iterate through ant steps (their number is n_nodes - 1)
            # the last step is determined by the last and the first nodes in the route
            for step in range(1, graph.n_nodes):
                # mark current node as visited
                visited[pos] = True
                # probablity of moving to each node from the current one
                mv_prob = np.zeros(graph.n_nodes)
                mv_prob_sum = 0

                # iterating through all the nodes
                for dest in range(graph.n_nodes):
                    # ant won't move to the node where it have already been
                    if visited[dest]:
                        mv_prob[dest] = 0
                        continue

                    # probability of moving this node
                    mv_prob[dest] = (pheromone[pos][dest] ** alfa) * (
                        closeness[pos][dest] ** beta
                    )
                    mv_prob_sum += mv_prob[dest]

                # to make probabilities sum up to 1
                mv_prob /= mv_prob_sum

                # choose next node randomly with respect to probabilities
                next_pos = np.random.choice(next_pos_choices, p=mv_prob)

                # updating current route
                curr_route[curr_idx] = next_pos
                curr_idx += 1
                curr_len += graph.distance(pos, next_pos)
                pos = next_pos

            # add the edge from the last to the first node
            curr_len += graph.distance(curr_route[-1], curr_route[0])

            # pheromones signals laid by the current ant
            delta = pher_delta_cf / curr_len
            for step in range(1, graph.n_nodes):
                pher_delta[curr_route[step - 1]][curr_route[step]] += delta
            pher_delta[curr_route[-1]][curr_route[0]] += delta

            # updating best route
            if curr_len < best_len:
                best_route, curr_route = curr_route, best_route
                best_len = curr_len

        # elite ants go only on the best route and lay pheromones there
        elite_delta = floor(n_elites * graph.n_nodes) * pher_delta_cf / best_len
        for step in range(1, graph.n_nodes):
            pher_delta[best_route[step - 1]][best_route[step]] += elite_delta
        pher_delta[best_route[-1]][best_route[0]] += elite_delta

        # updating pheromones signals
        for r in range(graph.n_nodes):
            for c in range(graph.n_nodes):
                pheromone[r][c] = min(
                    vapor_cf * pheromone[r][c] + pher_delta[r][c], PHER_MAX
                )

    return best_route


# number of random test graphs and random param configurations
def hyperparam_optim(n_graphs=3, n_params=3):
    # hyperparameter optimization
    choices = {
        "n_ants": [1, 2, 3, 4],
        "n_elites": [0.3, 0.5, 0.7, 1.0, 1.5, 2.0],
        "alfa": [0.3, 0.5, 0.8, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0],
        "beta": [0.3, 0.5, 0.8, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0],
        "vapor_cf": [0.2, 0.3, 0.5, 0.7, 0.8],
        "pher_delta_cf": [0.5, 0.8, 1.0, 2.0, 3.0, 5.0, 7.0],
    }

    # random test graphs
    graphs = [Graph(rng.integers(5, 25)) for _ in range(n_graphs)]
    # random param configurations
    params = [{k: rng.choice(choices[k]) for k in choices} for _ in range(n_params)]
    # for each graph algo with the given parameters finds shortest route
    # for each graph all the parameters
    total = [0] * n_params

    for graph in graphs:
        for i, param in enumerate(params):
            total[i] += graph.route_len(ants_colony(graph, n_gener=30, **param))

    result = [
        {"param": p, "total": t}
        for p, t in sorted(zip(params, total), key=lambda pair: pair[1])
    ]
    return result


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.float):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


if __name__ == "__main__":
    try:
        n_graphs = int(sys.argv[1])
    except Exception as e:
        n_graphs = 3
    try:
        n_params = int(sys.argv[2])
    except Exception as e:
        n_params = 3

    timeit = {}
    timeit["start"] = time()
    hyperparams = hyperparam_optim(n_graphs, n_params)
    timeit["end"] = time()
    timeit["duration"] = timeit["end"] - timeit["start"]

    json_dump = json.dumps(
        {"timeit": timeit, "hyperparams": hyperparams},
        indent=4,
        cls=NpEncoder,
    )
    
    with open("hyperparams.json", "w") as f:
        print(json_dump, file=f)
