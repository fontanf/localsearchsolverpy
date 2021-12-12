from .commons import SolutionPool, update_move_cost

import time
import copy


def iterated_local_search(local_scheme, **parameters):
    # Read parameters.
    start = time.time()
    maximum_pool_size = parameters.get(
            "maximum_pool_size", 1)
    maximum_number_of_iterations = parameters.get(
            "maximum_number_of_iterations", float('inf'))
    maximum_number_of_restarts = parameters.get(
            "maximum_number_of_restarts", float('inf'))
    minimum_number_of_perturbations = parameters.get(
            "minimum_number_of_perturbations", 1)
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
        print("Iterated Local Search")
        print()
        print("Parameters")
        print("----------")
        print(f"Maximum number of iterations:     "
              f"{maximum_number_of_iterations}")
        print(f"Maximum number of restarts:       "
              f"{maximum_number_of_restarts}")
        print(f"Minimum number of perturbations:  "
              f"{minimum_number_of_perturbations}")
        print(f"Seed:                             {seed}")
        print(f"Maximum pool size:                {maximum_pool_size}")
        print(f"Time limit:                       {time_limit}")

    # Setup structures.
    solution_pool = SolutionPool(local_scheme, maximum_pool_size)
    solution_pool.display_init(verbose)

    number_of_initial_solutions = (
            len(initial_solution_ids) + len(initial_solutions))
    initial_solutions_tmp = []
    number_of_restarts = 1
    number_of_iterations = 0
    while number_of_restarts < maximum_number_of_restarts:

        # Check time limit.
        current_time = time.time()
        if current_time - start > time_limit:
            break

        # Generate initial solutions.
        if not initial_solutions_tmp:
            for initial_solution_pos in range(number_of_initial_solutions):
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

                initial_solutions_tmp.append(solution)

            initial_solutions_tmp.sort(
                    key=lambda solution: local_scheme.global_cost(solution),
                    reverse=True)

        solution = initial_solutions_tmp[-1]
        initial_solutions_tmp.pop()
        perturbation_id = 0
        perturbations = local_scheme.perturbations(solution)
        global_cost_cur = local_scheme.global_cost(solution)
        for move in perturbations:
            move.global_cost = update_move_cost(
                    move.global_cost, global_cost_cur)
        # Sort moves.
        perturbations.sort(key=lambda move: move.global_cost)
        depth = 1
        solution_next = solution
        better_found = False
        while True:
            number_of_iterations += 1

            if perturbation_id >= minimum_number_of_perturbations \
                    and better_found:
                solution = solution_next
                better_found = False
                perturbation_id = 0
                depth += 1
                perturbations = local_scheme.perturbations(solution)
                global_cost_cur = local_scheme.global_cost(solution)
                for move in perturbations:
                    move.global_cost = update_move_cost(
                            move.global_cost, global_cost_cur)
                # Sort moves.
                perturbations.sort(key=lambda move: move.global_cost)

            if perturbation_id >= len(perturbations):
                break

            # Apply perturbation and local search.
            solution_tmp = copy.deepcopy(solution)
            move = perturbations[perturbation_id]
            local_scheme.apply_move(solution_tmp, move)
            local_scheme.local_search(solution_tmp, move)

            # Check for a new best solution.
            if (
                    len(solution_pool.solutions) == 0
                    or local_scheme.global_cost(solution_pool.worst)
                    > local_scheme.global_cost(solution_tmp)):
                new_best = solution_pool.add(solution_tmp)
                if new_best:
                    message = (
                            "start " + str(number_of_restarts)
                            + " iteration " + str(number_of_iterations))
                    solution_pool.display(message, start, verbose)
                    if new_solution_callback is not None:
                        new_solution_callback(solution_tmp)

            if (
                    local_scheme.global_cost(solution_next)
                    > local_scheme.global_cost(solution_tmp)):
                solution_next = solution_tmp
                better_found = True

            perturbation_id += 1

        number_of_restarts += 1

    # Final display.
    solution_pool.display_end(start, verbose)
    if verbose:
        print(f"Number of restarts:          {number_of_restarts}")
        print(f"Number of iterations:        {number_of_iterations}")

    end = time.time()

    return {"solution_pool": solution_pool,
            "number_of_restarts": number_of_restarts,
            "number_of_iterations": number_of_iterations,
            "elapsed_time": end - start}
