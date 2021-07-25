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


# Output files to move
files_and_directories_to_move = [ "*.log", "precice-config.xml" ]
# Files to copy
files_and_directories_to_copy = [ ]

# Substitutions follow here as a map
parameter_study_parameters = {
    "coupling_types": [pp.CouplingType.SERIAL_IMPLICIT],
    "accelerator_types": [pp.AcceleratorType.IQN_ILS],
    "filters_with_limits": [
        (pp.FilterType.QR2, 1e-3),
        (pp.FilterType.QR2, 1e-4),
        (pp.FilterType.QR2, 1e-5),
        (pp.FilterType.QR1, 1e-3),
    ],
    "initial_relaxations": [0.1, 0.5],
}

precice_config_template = """
"""
