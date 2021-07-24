import preciceparameters as pp

solver_a_name = ( "SolverA", "solver_a_executable" )
solver_b_name = ( "SolverB", "solver_b_executable" )

solver_a_ranks = 1
solver_b_ranks = 1

# Substitutions follow here as a map
parameter_study_parameters = {
    "coupling_types": [ pp.CouplingType.SERIAL_IMPLICIT ],
    "accelerator_types": [pp.AcceleratorType.IQN_ILS],
    "filters_with_limits": [
        (pp.FilterType.QR2, 1e-3),
        (pp.FilterType.QR2, 1e-4),
        (pp.FilterType.QR2, 1e-5),
        (pp.FilterType.QR1, 1e-3),
    ],
    "initial_relaxations": [ 0.1, 0.5 ]
}

precice_config_template = """
"""
