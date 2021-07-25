#!/usr/bin/env python3

import preciceparameters as pp
import internals.helperfunctions as helperfunctions
import subprocess as sp

# from multiprocessing import Process, Queue
import itertools
import os
import signal
import shutil
import glob
from timeit import default_timer as timer

import config


# https://stackoverflow.com/questions/38721847/how-to-generate-all-combination-from-values-in-dict-of-lists-in-python
def create_all_parameter_permutations(parameter_dict: dict) -> dict:
    keys, values = zip(*parameter_dict.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print("Found {} parameter sets.".format(len(permutations_dicts)))

    for idx, permutation in enumerate(permutations_dicts):
        accelerator = permutation["ACCELERATORTYPE"]
        if (
            type(accelerator) is pp.IMVJAccelerator
            and accelerator.ignores_time_window_reuse()
        ):
            permutations_dicts[idx]["REUSEDTIMEWINDOWS"] = 0

    # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    permutations_dicts = [
        dict(t) for t in {tuple(d.items()) for d in permutations_dicts}
    ]
    print("Found {} distinctive parameter sets.".format(len(permutations_dicts)))

    return permutations_dicts


end_time = "25e-1"
# end_time = "1e-5"
time_step_size = "1e-1"
# initial_relaxation = "0.001"
is_serial_implicit = False


def get_filter_type(filter):
    if filter == "QR1":
        return pp.FilterType.QR1
    elif filter == "QR2":
        return pp.FilterType.QR2
    else:
        raise "Wrong filter type specified!"


def move_to_dir(target_dir, expr):
    for to_move in glob.glob(expr):
        print(to_move)
        try:
            shutil.move(to_move, target_dir)
        except:
            print("Failed to move {} to {}".format(to_move, target_dir))


def copy_to_dir(target_dir, expr):
    for to_copy in glob.glob(expr):
        print(to_copy)
        try:
            shutil.copy(to_copy, target_dir)
        except:
            print("Failed to copy {} to {}".format(to_copy, target_dir))


def start_solver(solver_parameters: pp.SolverParameters):
    print("Starting {}".format(solver_parameters.name))

    f = open("{}.log".format(solver_parameters.name), "w")

    mpi_params = []
    if solver_parameters.mpi_parameters != None:
        mpi_params = ["mpirun", *solver_parameters.mpi_parameters.extra_options_list]

    full_cmd_line = [
        "time",
        *mpi_params,
        "{executable_path}/{executable_name}".format(
            executable_path=solver_parameters.executable_path,
            executable_name=solver_parameters.executable_name,
        ),
        *solver_parameters.solver_cmd_line,
    ]
    print(*full_cmd_line)
    proc = sp.Popen(
        full_cmd_line,
        stdout=f,
        stderr=f,
        preexec_fn=os.setpgrp,
    )

    return [proc, f]


def wait_for_solver(
    solver, proc_and_fptr, solver_start_time, solver_walltimes, timeout
):
    print("Checking on {}".format(solver.name))
    proc, fptr = proc_and_fptr
    # fptr = proc_and_fptr[1]
    try:
        proc.wait(timeout=timeout)
        # biot_proc.wait(timeout=proc_timeout)
    except sp.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    solver_walltimes[solver.name] = timer() - solver_start_time
    fptr.close()

    return solver_walltimes


def wait_for_solvers(
    solvers, process_ids, solver_start_times, solver_walltimes, timeout
):
    for solver in solvers:
        solver_walltimes = wait_for_solver(
            solver,
            process_ids[solver.name],
            solver_start_times[solver.name],
            solver_walltimes,
            timeout,
        )
    return solver_walltimes


def main():

    configuration_generator = helperfunctions.PreciceConfigurationGenerator(
        config.precice_config_template
    )

    # print( create_all_parameter_permutations(config.parameter_study_parameters) )
    substitution_dict = create_all_parameter_permutations(
        config.parameter_study_parameters
    )

    compact_results_dir = "coupling_behavior_results"

    try:
        os.mkdir(compact_results_dir)
    except:
        print("Directory ", compact_results_dir, "exists already!")

    with open("timings.txt", "a+") as timings_file:

        timings_file.write("case,biot,flow\n")

    for case in substitution_dict:

        print("Running testcase:")
        print(case)
        # print( **case )
        case_id = config.case_identifier.format(**case)
        print(case_id)
        # print(testcase.to_string())

        try:
            shutil.rmtree("precice-run/")
        except:
            print('no directory "precice-run/" to delete')

        # Save results
        target_dir = case_id + "/"

        try:
            os.mkdir(target_dir)
        except:
            print("Directory ", target_dir, "exists already.")

            # Getting the file list of the directory
            dir = os.listdir(target_dir)
            # Checking if the list is empty or not
            if len(dir) == 0:
                print("Empty directory! Rerurn simulation")
            else:
                print("Skipping test case as directory is NOT empty.")
                continue

        # Setup precice configpreexec_fn=os.setpgrp
        configuration_generator.generate_configuration("precice-config.xml", case)
        # helperfunctions.write_precice_configuration_file(
        #    testcase, "precice-config.xml", is_serial_implicit
        # )

        solver_start_times = {}
        solver_walltimes = {}
        solver_proc_and_file_ptr = {}

        for solver in config.solvers:
            # print(solver)
            solver_start_times[solver.name] = timer()
            solver_proc_and_file_ptr[solver.name] = start_solver(solver)

        first_solver, *remaining_solvers = config.solvers
        # print(first_solver, remaining_solvers)
        # First solver we check on gets full timeout period. All other solver we check afterwards will
        # has 10 seconds of time to terminate before we kill it.
        solver_walltimes = wait_for_solver(
            first_solver,
            solver_proc_and_file_ptr[first_solver.name],
            solver_start_times[solver.name],
            solver_walltimes,
            config.run_timeout,
        )
        solver_walltimes = wait_for_solvers(
            remaining_solvers,
            solver_proc_and_file_ptr,
            solver_start_times,
            solver_walltimes,
            10,
        )

        with open("timings.txt", "a+") as timings_file:
            timings_file.write(
                "{case},{min},{max}\n".format(
                    case=case_id,
                    min=min(solver_walltimes.values()),
                    max=max(solver_walltimes.values()),
                )
            )

        for f in config.files_and_directories_to_copy:
            copy_to_dir(target_dir, f)

        for f in config.files_and_directories_to_move:
            move_to_dir(target_dir, f)


if __name__ == "__main__":
    main()
