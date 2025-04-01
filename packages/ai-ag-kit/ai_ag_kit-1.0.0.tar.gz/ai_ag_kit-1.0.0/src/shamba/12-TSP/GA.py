"""GA for Travelling Salesman Problem"""

"""
Method: 
- Population creation
- Encoding
- Selection based on weighted probability, parents with good fitness score
- Crossover
- Mutation

No elitism
"""

import numpy as np
import click
import random

from itertools import permutations
from tqdm import tqdm, trange
from pprint import pp

def generate_population(num_cities: int, pop_size: int) -> list :
    """Method to generate the population for GA"""

    perms = permutations(range(1, num_cities+1))
    tmp_list = []
    tmp_list.extend(perms)

    population = random.sample(tmp_list, pop_size)
    return population

def generate_encode_list(num_cities: int) -> dict :
    """Method to generate encodings for each city"""

    pad = len(bin(num_cities)[2:])
    res = {}
    for i in range(1, num_cities+1) :
        res[i] = bin(i)[2:].zfill(pad)

    print("Encoded cities: ")
    pp(res)
    print('\n')

    rev_dict = {v: k for k, v in res.items()}
    res.update(rev_dict)

    return res

def encode(route: tuple[int], encode_list: dict) -> tuple[str] :
    """Method to encode a route"""

    res = []
    for x in route :
        res.append(encode_list[x])

    return tuple(res)

def decode(route: tuple[str], encode_list: dict) -> tuple[int] :
    """Method to decode the route"""

    res = []
    for x in route :
        city = encode_list[x]
        res.append(city)

    return tuple(res)

def calc_fitness(route: tuple[str], distance_mat: np.ndarray, encode_list: dict, is_distance: bool=False) -> int :
    """Calculate total distance of a route"""

    distance = 0
    
    for i in range(len(route)-1) :
        city_A = encode_list[route[i]] - 1
        city_B = encode_list[route[i+1]] - 1

        distance += distance_mat[city_A][city_B]

    # Add distance for return trip
    city_A = encode_list[route[0]] - 1
    city_B = encode_list[route[-1]] - 1
    distance += distance_mat[city_A][city_B]

    if is_distance :
        return distance

    return 1 / distance

def selection(routes: dict) -> np.ndarray :
    """Method to select parents based on fitness scores"""

    # Change fitness values to probabilities
    probabilities = [f / sum(routes.values()) for f in routes.values()]
    parents_idx = np.random.choice(len(routes.keys()), 2, p=probabilities)
    parents = [list(routes.keys())[i] for i in parents_idx]

    return parents

def crossover(parentA: tuple[str], parentB: tuple[str], num_cities: int) -> tuple[str] :
    """Method to crossover two parents to produce two children
    
    Normal crossover in GA does not work for TSP as it could result in invalid routes.
    Invalid routes include duplicate cities and/or missing cities.
    This would result in a tour where only one or two city exists.

    Hence Ordered crossover(OX1) is used here. A subset of cities in parent 1 is chosen
    and are copied to child 1 and the rest of the cities are copied from parent 2.
    Vice versa happens for child 2.

    Order Based Crossover(OX2/OBX) can also be used where random set of cities in either parent
    are ordered as they appear in the other parent.
    """

    # Get subset location
    start, end = sorted(random.sample(range(num_cities), 2))
    child = ['-1'] * num_cities
    child[start:end] = parentA[start:end]

    fill_position = [idx for idx, c in enumerate(child) if c == '-1']
    fill_values = [c for c in parentB if c not in child]

    for pos, value in zip(fill_position, fill_values) :
        child[pos] = value
    
    return tuple(child)

def mutation(child: tuple[str], num_cities: int) -> tuple[str] :
    """Method to mutate a child"""

    pointA = np.random.randint(1, num_cities)
    pointB = np.random.randint(1, num_cities)

    child_res = list(child)
    child_res[pointA], child_res[pointB] = child[pointB], child[pointA]

    return tuple(child_res)


@click.command()
@click.option('--num', '-N', default=5, help='Number of cities')
@click.option('--pop_size', '-P', default=10, help='Population size')
@click.option('--gen_count', '-G', default=50, help='Number of generations')
@click.option('--mut_prob', '-M', default=0.2, help='Mutation probability')
@click.option('--seed', '-S', default=42, help='Seed for RNG')
def main(num, pop_size, gen_count, mut_prob, seed) :

    random.seed(seed)
    np.random.seed(seed)

    # Generate distance matrx
    distance_mat = np.random.randint(5, 40, (num, num))
    # Make the matrix symmetirc
    distance_mat = ((distance_mat + distance_mat.T) / 2).astype(np.uint8)
    np.fill_diagonal(distance_mat, 0)
    print(f"Distance Matrix:\n{distance_mat}\n")

    # Generate population
    population = generate_population(num, pop_size)
    # Generate encoding dictionary
    encoding_dict = generate_encode_list(num)
    # Encode each route and calculate fitness
    routes_dict = {}
    for route in population :
        encoded_route = encode(route, encoding_dict)
        fitness = calc_fitness(encoded_route, distance_mat, encoding_dict)
        routes_dict[encoded_route] = fitness

    # Start generational loop
    # Flag for low population check
    flag = False

    for i in trange(gen_count, colour='green') :
        # Check for low population
        if len(routes_dict) == 1 :
            flag = True
            break

        # Select parents
        parentA, parentB = selection(routes_dict)
        #Crossover
        child = crossover(parentA, parentB, num)
        # Mutation based on mutation probability
        if np.random.rand() < mut_prob :
            child = mutation(child, num)

        # Calculate children fitness
        child_fitness = calc_fitness(child, distance_mat, encoding_dict)

        # Sort routes to find out routes with poorest fitness
        routes_dict = {k: v for k, v in sorted(routes_dict.items(), key=lambda item: item[1], reverse=True)}
        routes_dict.popitem()

        # Add children to population
        routes_dict[child] = child_fitness

    # Retrieve the route with highest fitness
    if flag :
        print("Population has become too low, cannot procreate anymore. ABORTING!")

    print('\n' + '#'*30 + '\n')
    routes_dict = {k: v for k, v in sorted(routes_dict.items(), key=lambda item: item[1])}
    best_route = routes_dict.popitem()
    best_fitness = best_route[1]
    best_distance = calc_fitness(best_route[0], distance_mat, encoding_dict, True)
    print(f"Best route(encoded): {''.join(best_route[0])}, fitness: {best_fitness}")
    best_route = decode(best_route[0], encoding_dict)
    print(f"Best route(decoded): {best_route}, distance: {best_distance}")


# Sample run command: python GA.py -N 5 -P 10 -G 100 -M 0.3 -S 2024
if __name__ == '__main__' :
    main()