import localsearchsolverpy

import json
import math
import random

random.seed(0)


class Location:
    id = -1
    x = 0
    y = 0


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["xs"],
                        data["ys"])
                for (x, y) in locations:
                    self.add_location(x, y)

    def add_location(self, x, y):
        location = Location()
        location.id = len(self.locations)
        location.x = x
        location.y = y
        self.locations.append(location)

    def distance(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            n = len(self.locations)
            data = json.load(json_file)
            locations = data["locations"]
            length = sum(self.distance(
                    locations[pos],
                    locations[pos + 1])
                for pos in range(n))
            number_of_locations = len(set(locations))
            number_of_duplicates = len(locations[:-1]) - len(set(locations))
            is_feasible = (
                    (number_of_duplicates == 0)
                    and number_of_locations == n
                    and locations[0] == locations[-1])
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"Number of locations: {number_of_locations} / {n}")
            print(f"Feasible: {is_feasible}")
            print(f"Length: {length}")
            return (is_feasible, length)


class LocalScheme:
    """An elementary local scheme for the Travelling Salesman Problem."""

    class Solution:

        def __init__(self):
            self.locations = None
            self.length = None

    def __init__(self, instance, **kwargs):
        self.instance = instance

    def initial_solution(self, initial_solution_id):
        n = len(self.instance.locations)
        solution = self.Solution()
        solution.locations = [i for i in range(n)]
        random.shuffle(solution.locations)
        solution.locations.append(solution.locations[0])
        solution.length = sum(self.instance.distance(
                solution.locations[pos],
                solution.locations[pos + 1])
            for pos in range(n))
        return solution

    def global_cost(self, solution):
        return (solution.length)

    def local_search(self, solution, perturbation=None):
        n = len(self.instance.locations)
        while True:
            # print(solution.locations)
            # print(solution.length)
            pos_1_best = None
            pos_2_best = None
            l_best = solution.length
            for pos_1 in range(n):
                i1 = solution.locations[pos_1]
                j1 = solution.locations[pos_1 + 1]
                for pos_2 in range(pos_1 + 2, n):
                    i2 = solution.locations[pos_2]
                    j2 = solution.locations[pos_2 + 1]
                    l_new = (solution.length
                             - self.instance.distance(i1, j1)
                             - self.instance.distance(i2, j2)
                             + self.instance.distance(i1, i2)
                             + self.instance.distance(j1, j2))
                    if l_new < l_best:
                        l_best = l_new
                        pos_1_best = pos_1
                        pos_2_best = pos_2
            if pos_1_best is not None:
                locations = []
                for p in range(pos_1_best + 1):
                    locations.append(solution.locations[p])
                for p in range(pos_2_best, pos_1_best, -1):
                    locations.append(solution.locations[p])
                for p in range(pos_2_best + 1, n + 1):
                    locations.append(solution.locations[p])
                solution.locations = locations
                solution.length = l_best
                continue
            break

    class Move:

        def __init__(self):
            self.pos_1 = None
            self.pos_2 = None
            self.pos_3 = None
            self.pos_4 = None

    def perturbations(self, solution):
        n = len(self.instance.locations)
        moves = []
        for _ in range(32):
            edges = random.sample(range(0, n), 4)
            edges.sort()
            move = self.Move()
            move.pos_1 = edges[0]
            move.pos_2 = edges[1]
            move.pos_3 = edges[2]
            move.pos_4 = edges[3]
            move.global_cost = self.global_cost(solution)
            moves.append(move)
        return moves

    def apply_move(self, solution, move):
        n = len(self.instance.locations)
        locations = []
        for p in range(move.pos_1 + 1):
            locations.append(solution.locations[p])
        for p in range(move.pos_3 + 1, move.pos_4 + 1):
            locations.append(solution.locations[p])
        for p in range(move.pos_2 + 1, move.pos_3 + 1):
            locations.append(solution.locations[p])
        for p in range(move.pos_1 + 1, move.pos_2 + 1):
            locations.append(solution.locations[p])
        for p in range(move.pos_4 + 1, n + 1):
            locations.append(solution.locations[p])
        solution.locations = locations
        solution.length = sum(self.instance.distance(
                solution.locations[pos],
                solution.locations[pos + 1])
            for pos in range(n))

    def write(self, solution):
        data = {"locations": solution.locations}
        with open(args.certificate, 'w') as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="restarting_local_search",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default=None,
            help='')

    args = parser.parse_args()

    if args.algorithm == "generator":
        random.seed(0)
        for number_of_locations in range(1, 101):
            instance = Instance()
            total_weight = 0
            for location_id in range(number_of_locations):
                x = random.randint(0, 1000)
                y = random.randint(0, 1000)
                instance.add_location(x, y)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)

    else:
        instance = Instance(args.instance)
        local_scheme = LocalScheme(instance)
        if args.algorithm == "restarting_local_search":
            output = localsearchsolverpy.restarting_local_search(
                    local_scheme,
                    time_limit=10)
        elif args.algorithm == "iterated_local_search":
            output = localsearchsolverpy.iterated_local_search(
                    local_scheme,
                    time_limit=10)
        if args.certificate is not None:
            local_scheme.write(output["solution_pool"].best)
            print()
            instance.check(args.certificate)
