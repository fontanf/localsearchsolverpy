from .commons import SolutionPool

import time


def restarting_local_search(local_scheme, **parameters):
    # Read parameters.
    start = time.time()
    maximum_pool_size = parameters.get(
            "maximum_pool_size", 1)
    maximum_number_of_restarts = parameters.get(
            "maximum_number_of_restarts", float('inf'))
    seed = parameters.get(
            "seed", 0)
    initial_solution_ids = parameters.get(
            "initial_solution_ids", [])
    initial_solutions = parameters.get(
            "initial_solutions", [])
    new_solution_callback = parameters.get(
            "new_solution_callback", None)
    time_limit = parameters.get(
            "time_limit", float('inf'))
    verbose = parameters.get(
            "verbose", True)

    if not initial_solution_ids and not initial_solutions:
        initial_solution_ids.append(0)

    if verbose:
        print("=======================================")
        print("          Local Search Solver          ")
        print("=======================================")
        print()
        print("Algorithm")
        print("---------")
        print("Restarting Local Search")
        print()
        print("Parameters")
        print("----------")
        print(f"Maximum number of restarts:  {maximum_number_of_restarts}")
        print(f"Seed:                        {seed}")
        print(f"Maximum pool size:           {maximum_pool_size}")
        print(f"Time limit:                  {time_limit}")

    # Setup structures.
    solution_pool = SolutionPool(local_scheme, maximum_pool_size)
    solution_pool.display_init(verbose)

    number_of_initial_solutions = (
            len(initial_solution_ids) + len(initial_solutions))
    number_of_restarts = 1
    while number_of_restarts < maximum_number_of_restarts:

        # Check time limit.
        current_time = time.time()
        if current_time - start > time_limit:
            break

        # Generate initial solution.
        initial_solution_pos = (
                (number_of_restarts - 1)
                % number_of_initial_solutions)
        if initial_solution_pos < len(initial_solution_ids):
            solution = local_scheme.initial_solution(
                    initial_solution_ids[initial_solution_pos])
        else:
            solution = initial_solutions[
                    initial_solution_pos - len(initial_solution_ids)]
        # Local Search.
        local_scheme.local_search(solution)

        # Check for a new best solution.
        if (
                len(solution_pool.solutions) == 0
                or local_scheme.global_cost(solution_pool.worst)
                > local_scheme.global_cost(solution)):
            new_best = solution_pool.add(solution)
            if new_best:
                message = "start " + str(number_of_restarts)
                solution_pool.display(message, start, verbose)
                if new_solution_callback is not None:
                    new_solution_callback(solution)

        number_of_restarts += 1

    # Final display.
    solution_pool.display_end(start, verbose)
    if verbose:
        print(f"Number of restarts:          {number_of_restarts}")

    end = time.time()

    return {"solution_pool": solution_pool,
            "number_of_restarts": number_of_restarts,
            "elapsed_time": end - start}
