#!/usr/bin/env python3

import preciceparameters as pp
import subprocess as sp

# from multiprocessing import Process, Queue
import tempfile
import os
import signal
import shutil
import glob
from timeit import default_timer as timer

import config

for k, dk in config.parameter_study_parameters.items():
    for x in dk:
        # print( k, dk, x )
        print(x)
        # whatever with k, x


# import CouplingType as ct
#
# Set up test cases

testcases = {}

proc_timeout = 400000

nthreads_biot = 64
nthreads_flow = 12

accelerator_type = pp.AcceleratorType.IQN_ILS
coupling_types = [pp.CouplingType.SERIAL_IMPLICIT]

filters_and_limits = [(pp.FilterType.QR2, 1e-3)]


# svd_truncation_thresholds = [1e-3, 1e-2, 1e-1, 1e0]
iqn_timewindow_reuse = [8]
# svd_truncation_thresholds = [1e-3, 1e-2, 1e-1]
# initial_relaxations = [ 0.001, 0.01, 0.1 ]
initial_relaxations = [0.1]

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


# IQN-ILS
for ct in coupling_types:
    print("Coupling type: {}".format(ct.value))
    for filter_type, filter_limit in filters_and_limits:
        print("{} {}".format(filter_type.name, filter_limit))
        for initial_relaxation in initial_relaxations:
            if accelerator_type == pp.AcceleratorType.IQN_ILS:
                for timewindow_reuse in iqn_timewindow_reuse:
                    hashname = (
                        "{}_".format(ct.value)
                        + "{}_".format(accelerator_type.value)
                        + filter_type.name
                        + "_"
                        + str(filter_limit)
                        + "_reuse_"
                        + str(timewindow_reuse)
                        + "_relax_"
                        + str(initial_relaxation)
                    )
                    print(hashname)
                    testcases[hashname] = pp.TestCase(
                        accelerator_type.value,
                        end_time,
                        time_step_size,
                        initial_relaxation,
                        ct,
                        accelerator_type,
                        filter_type,
                        filter_limit,
                        timewindow_reuse,
                    )
            elif accelerator_type == pp.AcceleratorType.IQN_IMVJ:
                for truncation_threshold in svd_truncation_thresholds:
                    hashname = (
                        "{}_".format(ct.value)
                        + "{}_".format(accelerator_type.value)
                        + filter_type.name
                        + "_"
                        + str(filter_limit)
                        + "_threshold_"
                        + str(truncation_threshold)
                        + "_relax_"
                        + str(initial_relaxation)
                    )
                    print(hashname)
                    testcases[hashname] = pp.TestCase(
                        accelerator_type.value,
                        end_time,
                        time_step_size,
                        initial_relaxation,
                        ct,
                        accelerator_type,
                        filter_type,
                        filter_limit,
                        0,
                        truncation_threshold,
                    )


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
    print("Starting {}".format(solver_parameters.get_name()))

    f = open("{}.log".format(solver.get_name()), "w")

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
        "-c",
        "precice-config.xml",
    ]
    print(*full_cmd_line)
    proc = sp.Popen(
        full_cmd_line,
        stdout=f,
        stderr=f,
        preexec_fn=os.setpgrp,
    )

    return [proc, f]


print("Number of test configurations to run: \n {}".format(len(testcases)))


compact_results_dir = "coupling_behavior_results"

try:
    os.mkdir(compact_results_dir)
except:
    print("Directory ", compact_results_dir, "exists already!")

with open("timings.txt", "a+") as timings_file:

    timings_file.write("case,biot,flow\n")

for key in testcases:
    testcase = testcases[key]

    print("Running testcase:")
    print(testcase.to_string())

    try:
        shutil.rmtree("precice-run/")
    except:
        print('no directory "precice-run/" to delete')

    # Save results
    target_dir = key + "/"

    try:
        os.mkdir(target_dir)
    except:
        print("Directory ", target_dir, "exists already!")

        # Getting the file list of the directory
        dir = os.listdir(target_dir)
        # Checking if the list is empty or not
        if len(dir) == 0:
            print("Empty directory! Rerurn simulation")
        else:
            print("Skipping test case as directory is NOT empty!")
            continue

    # Setup precice configpreexec_fn=os.setpgrp
    pp.write_precice_configuration_file(
        testcase, "precice-config.xml", is_serial_implicit
    )

    solver_start_times = {}
    solver_walltimes = {}
    solver_proc_and_file_ptr = {}

    for solver in config.solvers:
        print(solver.get_name())
        solver_start_times[solver] = timer()
        solver_proc_and_file_ptr[solver] = start_solver(solver)

    def wait_for_solver(solver, solver_walltimes, timeout):
        print("Checking on {}".format(solver.get_name()))
        proc = solver_proc_and_file_ptr[solver][0]
        try:
            proc.wait(timeout=timeout)
            # biot_proc.wait(timeout=proc_timeout)
        except sp.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        solver_walltimes[solver.get_name()] = timer() - solver_start_times[solver]

        return solver_walltimes

    def wait_for_solvers(solvers, solver_walltimes, timeout):
        for solver in solvers:
            solver_walltimes = wait_for_solver(solver, solver_walltimes, timeout)
        return solver_walltimes

    first_solver, *remaining_solvers = config.solvers
    print(first_solver, remaining_solvers)
    # First solver we check on gets full timeout period. All other solver we check afterwards will
    # has 10 seconds of time to terminate before we kill it.
    solver_walltimes = wait_for_solver(first_solver, solver_walltimes, proc_timeout)
    solver_walltimes = wait_for_solvers(remaining_solvers, solver_walltimes, 10)

    with open("timings.txt", "a+") as timings_file:
        timings_file.write(
            "{case},{min},{max}\n".format(
                case=key,
                min=min(solver_walltimes.values()),
                max=max(solver_walltimes.values()),
            )
        )

    for f in config.files_and_directories_to_copy:
        copy_to_dir(target_dir, f)

    for f in config.files_and_directories_to_move:
        move_to_dir(target_dir, f)
