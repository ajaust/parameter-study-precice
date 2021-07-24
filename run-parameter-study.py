#!/usr/bin/env python3

import preciceparameters as pp
import subprocess as sp
#from multiprocessing import Process, Queue
import tempfile
import os
import signal
import shutil
import glob
from timeit import default_timer as timer

import config

for k, dk in config.parameter_study_parameters.items():
    for x in dk:
        #print( k, dk, x )
        print(x)
        # whatever with k, x


#import CouplingType as ct
#
#Set up test cases

testcases = {}

proc_timeout = 400000

nthreads_biot=64
nthreads_flow=12

accelerator_type = pp.AcceleratorType.IQN_ILS
coupling_types = [ pp.CouplingType.SERIAL_IMPLICIT ]

filters_and_limits = [ ( pp.FilterType.QR2, 1e-3 ) ]


#svd_truncation_thresholds = [1e-3, 1e-2, 1e-1, 1e0]
iqn_timewindow_reuse = [8]
#svd_truncation_thresholds = [1e-3, 1e-2, 1e-1]
#initial_relaxations = [ 0.001, 0.01, 0.1 ]
initial_relaxations = [ 0.1 ]

end_time = "25e-1"
#end_time = "1e-5"
time_step_size = "1e-1"
#initial_relaxation = "0.001"
is_serial_implicit = False

def get_filter_type( filter ):
    if filter == "QR1":
        return pp.FilterType.QR1
    elif filter == "QR2":
        return pp.FilterType.QR2
    else:
        raise "Wrong filter type specified!"

# IQN-ILS
for ct in coupling_types:
    print( "Coupling type: {}".format( ct.value )  )
    for filter_type, filter_limit in filters_and_limits:
        print( "{} {}".format( filter_type.name, filter_limit ) )
        for initial_relaxation in initial_relaxations:
            if accelerator_type == pp.AcceleratorType.IQN_ILS:
                for timewindow_reuse in iqn_timewindow_reuse:
                    hashname = "{}_".format( ct.value ) + "{}_".format( accelerator_type.value ) + filter_type.name + "_" + str(filter_limit) + "_reuse_" + str(timewindow_reuse) + "_relax_" + str(initial_relaxation)
                    print(hashname)
                    testcases[hashname] = pp.TestCase( accelerator_type.value, end_time, time_step_size, initial_relaxation, ct, accelerator_type, filter_type, filter_limit, timewindow_reuse )
            elif accelerator_type == pp.AcceleratorType.IQN_IMVJ:
                for truncation_threshold in svd_truncation_thresholds:
                    hashname = "{}_".format( ct.value ) + "{}_".format( accelerator_type.value ) + filter_type.name + "_" + str(filter_limit) + "_threshold_" + str(truncation_threshold) + "_relax_" + str(initial_relaxation)
                    print(hashname)
                    testcases[hashname] = pp.TestCase( accelerator_type.value, end_time, time_step_size, initial_relaxation, ct, accelerator_type, filter_type, filter_limit, 0, truncation_threshold )

def preq_is_good():

    return True

def move_to_dir(target_dir, expr):
    for to_move in glob.glob(expr):
        print( to_move )
        shutil.move( to_move, target_dir)

def copy_to_dir(target_dir, expr):
    for to_copy in glob.glob(expr):
        print( to_copy )
        shutil.copy( to_copy, target_dir)


def run_biot_solver():
    print( "Starting Biot solver" )
    f = open("biot_solver.log", 'w')
#    proc = sp.Popen(["time", "mpirun", "--report-bindings", "-n", str(nthreads_biot), "python3", "./biot_solver.py", "-c", "precice-config.xml"], stdout=f, stderr=f, preexec_fn=os.setpgrp)
#    proc = sp.Popen(["time", "mpirun", "--bind-to", "hwthread", "--report-bindings", "-n", str(nthreads_biot), "python3", "./biot_solver.py", "-c", "precice-config.xml"], stdout=f, stderr=f, preexec_fn=os.setpgrp)
    proc = sp.Popen(["time", "mpirun", "--map-by", "core", "--report-bindings", "-n", str(nthreads_biot), "python3", "./biot_solver.py", "-c", "precice-config.xml"], stdout=f, stderr=f, preexec_fn=os.setpgrp)
#    proc = sp.Popen(["time", "mpirun", "--map-by", "hwthread", "--bind-to", "hwthread", "--report-bindings", "-n", str(nthreads_biot), "python3", "./biot_solver.py", "-c", "precice-config.xml"], stdout=f, stderr=f, preexec_fn=os.setpgrp)
    return proc, f

def run_flow_solver():
    print( "Starting Flow solver" )
    f = open("flow_solver.log", 'w')
    proc = sp.Popen(["time", "mpirun", "-n", str(nthreads_flow), "python3", "./flow_solver.py", "-c", "precice-config.xml"], stdout=f, stderr=f, preexec_fn=os.setpgrp)
    return proc, f


print( "Number of test configurations to run: \n {}".format( len(testcases) ) )


compact_results_dir = "coupling_behavior_results"

try:
    os.mkdir( compact_results_dir )
except:
    print("Directory ", compact_results_dir, "exists already!")

with open("timings.txt", "a+") as timings_file:

    timings_file.write( "case,biot,flow\n" )

for key in testcases:
    testcase = testcases[key]

    print("Running testcase:")
    print( testcase.to_string() )

#    print( pde_filename )


    if ( preq_is_good() == False ):
        #read_errors( testcase )
        continue

    try:
        shutil.rmtree("precice-run/")
    except:
        print("no directory \"precice-run/\" to delete")

    #Save results
    target_dir = key+"/"

    try:
        os.mkdir( target_dir )
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

    #Setup precice configpreexec_fn=os.setpgrp
    pp.write_precice_configuration_file( testcase, "precice-config.xml", is_serial_implicit )

    # Start thread for Biot solver in background
    biot_time_start = timer()
    biot_proc, biot_output = run_biot_solver()

    # Start thread for flow solver in background
    flow_time_start = timer()
    flow_proc, flow_output = run_flow_solver()

    try:
        biot_proc.wait(timeout=proc_timeout)
    except sp.TimeoutExpired:
        os.killpg(os.getpgid(biot_proc.pid), signal.SIGTERM)

    #biot_proc.wait()
    biot_run_time = timer() - biot_time_start

    try:
        flow_proc.wait(timeout=10)
    except sp.TimeoutExpired:
        os.killpg(os.getpgid(flow_proc.pid), signal.SIGTERM)

    #flow_proc.wait()
    flow_run_time = timer() - flow_time_start

    #print( "Runtime: {}".format( biot_run_time ) )

    with open("timings.txt", "a+") as timings_file:
        timings_file.write( "{case},{biot},{flow}\n".format( case=key, biot=biot_run_time, flow=flow_run_time  ) )


    shutil.copy( "precice-BiotSolver-iterations.log", "{dir}/{name}".format( dir=compact_results_dir, name="{}-it-Biot.log".format(key) ) )
    shutil.copy( "precice-BiotSolver-convergence.log", "{dir}/{name}".format( dir=compact_results_dir, name="{}-conv-Biot.log".format(key) ) )
    shutil.copy( "precice-HDFlowSolver-iterations.log", "{dir}/{name}".format( dir=compact_results_dir, name="{}-it-Flow.log".format(key) ) )
    move_to_dir( target_dir, '*.json')
    move_to_dir( target_dir, '*.log')
    copy_to_dir( target_dir, '*.input')

    try:
        shutil.move( "res_biot/", target_dir)
    except:
        print( "Could not move res_biot/")
    try:
        shutil.move( "res_flow/", target_dir)
    except:
        print( "Could not move res_flow/")
    try:
        shutil.move( "precice-config.xml", target_dir)
    except:
        print( "Could not move precice-config.xml")



