"""A local scheme example for the Knapsack Problem.

Usage:

Generate the instances:
python3 knapsack.py -a generator -i instance

Run the algorithm on an instance:
python3 knapsack.py -i instance_100.json -a iterated_local_search -c sol.json

"""

import localsearchsolverpy

import json
import random

random.seed(0)


class Item:
    id = -1
    weight = 0
    profit = 0


class Instance:

    def __init__(self, filepath=None):
        self.items = []
        self.capacity = 0
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                self.capacity = data["capacity"]
                items = zip(
                        data["weights"],
                        data["profits"])
                for (weight, profit) in items:
                    self.add_item(weight, profit)

    def add_item(self, weight, profit):
        item = Item()
        item.id = len(self.items)
        item.weight = weight
        item.profit = profit
        self.items.append(item)

    def write(self, filepath):
        data = {"capacity": self.capacity,
                "weights": [item.weight for item in self.items],
                "profits": [item.profit for item in self.items]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            n = len(self.items)
            data = json.load(json_file)
            items = data["items"]
            weight = sum(self.items[j].weight for j in items)
            profit = sum(self.items[j].profit for j in items)
            number_of_items = len(set(items))
            number_of_duplicates = len(items) - len(set(items))
            is_feasible = (
                    (number_of_duplicates == 0)
                    and weight <= self.capacity)
            print(f"Number of items: {number_of_items} / {n}")
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"Weight: {weight} / {self.capacity}")
            print(f"Feasible: {is_feasible}")
            print(f"Profit: {profit}")
            return (is_feasible, profit)


class LocalScheme:
    """An elementary local scheme for the Knapsack Problem.

    The neighborhood consists in adding or removing an item from the knapsack.

    Removing items might be required since we allow solutions to violate the
    capacity constraint.

    The global cost first minimizes the over-capacity, and then maximizes the
    profit.

    The perturbation consists in forcing an item in or out of the solution.
    Then, in the local search, we ensure not modifying the status of the item
    concerned by the perturbation.

    """

    class Solution:

        def __init__(self):
            self.items = None
            self.weight = None
            self.profit = None

    def __init__(self, instance, **kwargs):
        self.instance = instance

    def initial_solution(self, initial_solution_id):
        """For each item, add it to the initial solution with probability 1/2.
        """

        n = len(self.instance.items)
        solution = self.Solution()
        solution.items = [False for _ in range(n)]
        solution.profit = 0
        solution.weight = 0

        for item_id in range(n):
            if random.randint(0, 1) == 0:
                solution.items[item_id] = True
                solution.profit += self.instance.items[item_id].profit
                solution.weight += self.instance.items[item_id].weight
        return solution

    def global_cost(self, solution):
        return (
                # First, minimize over-capacity.
                max(0, solution.weight - self.instance.capacity),
                # Then, maximize profit.
                -solution.profit)

    class Move:

        def __init__(self):
            self.item_id = None

    def perturbations(self, solution):
        n = len(self.instance.items)
        moves = []
        for item_id in range(n):
            w = self.instance.items[item_id].weight
            p = self.instance.items[item_id].profit
            move = self.Move()
            move.item_id = item_id
            if solution.items[item_id]:
                move.global_cost = (
                        max(0, solution.weight - w - self.instance.capacity),
                        - (solution.profit))
            else:
                move.global_cost = (
                        max(0, solution.weight - self.instance.capacity),
                        - (solution.profit + p))
            moves.append(move)
        return moves

    def apply_move(self, solution, move):
        # If the item is already in the solution, we remove it.
        if solution.items[move.item_id]:
            solution.items[move.item_id] = False
            solution.profit -= self.instance.items[move.item_id].profit
            solution.weight -= self.instance.items[move.item_id].weight
        # If the item is not in the solution yet, we add it.
        else:
            solution.items[move.item_id] = True
            solution.profit += self.instance.items[move.item_id].profit
            solution.weight += self.instance.items[move.item_id].weight

    def local_search(self, solution, perturbation=None):
        n = len(self.instance.items)
        c = self.instance.capacity
        while True:
            # Variables that store the best move.
            item_id_best = None
            global_cost_best = self.global_cost(solution)
            # Iterate over all items.
            for item_id in range(n):
                # Don't change the status of the item from the perturbation.
                if perturbation is not None \
                        and perturbation.item_id == item_id:
                    continue
                w = self.instance.items[item_id].weight
                p = self.instance.items[item_id].profit
                # Compute the cost of the solution is the move is applied.
                # If the current solution already contains item 'item_id', we
                # try to remove it.
                if solution.items[item_id]:
                    global_cost = (
                            max(0, solution.weight - w - c),
                            - (solution.profit - p))
                # If the current solution doesn't contain item 'item_id', we
                # try to add it.
                else:
                    global_cost = (
                            max(0, solution.weight + w - c),
                            - (solution.profit + p))
                # Update best move.
                if global_cost < global_cost_best:
                    item_id_best = item_id
                    global_cost_best = global_cost
            # If an improving move has been found, we update the current
            # solution.
            if item_id_best is not None:
                # If the item is already in the solution, we remove it.
                if solution.items[item_id_best]:
                    solution.items[item_id_best] = False
                    solution.profit -= self.instance.items[item_id_best].profit
                    solution.weight -= self.instance.items[item_id_best].weight
                # If the item is not in the solution yet, we add it.
                else:
                    solution.items[item_id_best] = True
                    solution.profit += self.instance.items[item_id_best].profit
                    solution.weight += self.instance.items[item_id_best].weight
                continue
            break

    def write(self, solution):
        n = len(self.instance.items)
        data = {"items": [j for j in range(n) if solution.items[j]]}
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
        for number_of_items in range(1, 101):
            instance = Instance()
            total_weight = 0
            for capacity in range(number_of_items):
                weight = random.randint(0, 1000000)
                profit = random.randint(weight, weight + 10000)
                total_weight += weight
                instance.add_item(weight, profit)
            instance.capacity = random.randint(
                    total_weight * 1 // 4,
                    total_weight * 3 // 4)
            instance.write(
                    args.instance + "_" + str(number_of_items) + ".json")

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
