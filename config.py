import preciceparameters as pp

solvers = [
    pp.SolverParameters(
        name="SolverA",
        executable_name="solver_a_executable",
        executable_path=".",
        solver_cmd_line=["-c", "precice-config.xml"],
        mpi_parameters=None,
    ),
    pp.SolverParameters(
        name="SolverB",
        executable_name="solver_b_executable",
        executable_path=".",
        solver_cmd_line=["-c", "precice-config.xml"],
        mpi_parameters=None,
    ),
]

run_timeout = 1000

# Output files to move
files_and_directories_to_move = [ "*.log", "precice-config.xml" ]
# Files to copy
files_and_directories_to_copy = [ ]

# Substitutions follow here as a map
parameter_study_parameters = {
    "COUPLINGTYPE": [pp.CouplingType.SERIAL_IMPLICIT],
    "ACCELERATORTYPE": [pp.ILSAccelerator, pp.IMVJAccelerator( pp.IMVJRestartType.RS_SVD, 8, 1e-3, 0, ignore_time_window_reuse=True )],
    "FILTERANDLIMIT": [
        pp.FilterSettings( pp.FilterType.QR2, 1e-3 ),
        pp.FilterSettings( pp.FilterType.QR2, 1e-4 ),
        pp.FilterSettings( pp.FilterType.QR2, 1e-5 ),
        pp.FilterSettings( pp.FilterType.QR1, 1e-3 ),
    ],
    "INITIALRELAXATION": [0.1, 0.5],
}

print( pp.FilterSettings( pp.FilterType.QR2, 1e-3 ) )

precice_config_template = """
"""
