import time


class SolutionPool:

    def __init__(self, local_scheme, maximum_size=1):
        self.local_scheme = local_scheme
        self.maximum_size = maximum_size
        self.best = None
        self.worst = None
        self.solutions = []

    def add(self, node):
        # If the new solution is worse than the worst solution of the pool,
        # don't add it and stop.
        if len(self.solutions) >= self.maximum_size:
            if self.local_scheme.global_cost(node) \
                    >= self.local_scheme.global_cost(self.worst):
                return 0
        # If the new solution is already in the pool, don't add it and stop.
        for solution in self.solutions:
            if node == solution:
                return 0
        # Add the new solution to solutions.
        self.solutions.append(node)
        # Update best solution.
        new_best = False
        if self.best is None \
                or self.local_scheme.global_cost(node) \
                < self.local_scheme.global_cost(self.best):
            new_best = True
            self.best = node
        # Check the size of the solution pool.
        if len(self.solutions) > self.maximum_size:
            # Remove worst solution.
            i = 0
            while i < len(self.solutions):
                if self.solutions[i] == self.worst:
                    self.solutions[i] = self.solutions[-1]
                    self.solutions.pop()
                    break
                else:
                    i += 1
        # Compute new worst solutions.
        self.worst = self.solutions[0]
        for solution in self.solutions:
            if self.local_scheme.global_cost(solution) \
                    > self.local_scheme.global_cost(self.worst):
                self.worst = solution

        if new_best:
            return 2
        else:
            return 1

    def display_init(self, verbose):
        if verbose:
            print()
            print(
                    '{:>11}'.format("Time")
                    + '{:>32}'.format("Value")
                    + '{:>32}'.format("Comment"))
            print(
                    '{:>11}'.format("----")
                    + '{:>32}'.format("-----")
                    + '{:>32}'.format("-------"))

    def display(self, message, start, verbose):
        if verbose:
            value = self.local_scheme.global_cost(self.best)
            print(
                    '{:>11.3f}'.format(time.time() - start)
                    + '{:>32}'.format(value)
                    + '{:>32}'.format(message))

    def display_end(self, start, verbose):
        if verbose:
            current_time = time.time() - start
            value = self.local_scheme.global_cost(self.best)
            # print("-"*75)
            print()
            print("Final statistics")
            print("----------------")
            print(f"Value:                       {value}")
            print("Time:" + " " * 24 + '{:<11.3f}'.format(current_time))


def update_move_cost(global_cost, global_cost_cur):
    if type(global_cost) is not tuple:
        return global_cost
    gc = global_cost
    for pos in range(len(global_cost) - 2):
        gc[pos] = min(global_cost[pos], global_cost_cur[pos])
    return gc
