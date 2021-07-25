#import preciceparameters as pp
from preciceparameters import *

solvers = [
    SolverParameters(
        name="SolverA",
        executable_name="solver_a_executable",
        executable_path=".",
        solver_cmd_line=["-c", "precice-config.xml"],
        mpi_parameters=None,
    ),
    SolverParameters(
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
    "COUPLINGTYPE": [CouplingType.SERIAL_IMPLICIT],
    "ACCELERATORTYPE": [
        ILSAccelerator(),
        IMVJAccelerator( IMVJRestartType.RS_SVD, 8, 1e-3, 0, ignore_time_window_reuse=True ),
        IMVJAccelerator( IMVJRestartType.RS_SVD, 8, 1e-3, 0, ignore_time_window_reuse=False )
    ],
    "FILTERANDLIMIT": [
        FilterSettings( FilterType.QR2, 1e-3 ),
        FilterSettings( FilterType.QR2, 1e-4 ),
        FilterSettings( FilterType.QR2, 1e-5 ),
        FilterSettings( FilterType.QR1, 1e-3 ),
    ],
    "REUSEDTIMEWINDOWS": [0, 8],
    "INITIALRELAXATION": [0.1, 0.5],
}

case_identifier="{COUPLINGTYPE}-{ACCELERATORTYPE}-{FILTERANDLIMIT}-{REUSEDTIMEWINDOWS}-{INITIALRELAXATION}"

precice_config_template = """<?xml version="1.0" encoding="UTF-8" ?>
<precice-configuration>
  <log>
    <sink
      type="stream"
      output="stdout"
      filter="%Severity% > debug"
      format="preCICE:%ColorizedSeverity% %Message%"
      enabled="true" />
  </log>

  <solver-interface dimensions="3">
    <data:vector name="dataOne" />
    <data:vector name="dataTwo" />

    <mesh name="MeshOne">
      <use-data name="dataOne" />
      <use-data name="dataTwo" />
    </mesh>

    <mesh name="MeshTwo">
      <use-data name="dataOne" />
      <use-data name="dataTwo" />
    </mesh>

    <participant name="SolverOne">
      <use-mesh name="MeshOne" provide="yes" />
      <write-data name="dataOne" mesh="MeshOne" />
      <read-data name="dataTwo" mesh="MeshOne" />
    </participant>

    <participant name="SolverTwo">
      <use-mesh name="MeshOne" from="SolverOne" />
      <use-mesh name="MeshTwo" provide="yes" />
      <mapping:nearest-neighbor
        direction="write"
        from="MeshTwo"
        to="MeshOne"
        constraint="conservative" />
      <mapping:nearest-neighbor
        direction="read"
        from="MeshOne"
        to="MeshTwo"
        constraint="consistent" />
      <write-data name="dataTwo" mesh="MeshTwo" />
      <read-data name="dataOne" mesh="MeshTwo" />
    </participant>

    <m2n:sockets from="SolverOne" to="SolverTwo" />

    <coupling-scheme:{COUPLINGTYPE}>
      <participants first="SolverOne" second="SolverTwo" />
      <max-time-windows value="2" />
      <time-window-size value="1.0" />
      <max-iterations value="2" />
      <min-iteration-convergence-measure min-iterations="5" data="dataOne" mesh="MeshOne" />
      <exchange data="dataOne" mesh="MeshOne" from="SolverOne" to="SolverTwo" />
      <exchange data="dataTwo" mesh="MeshOne" from="SolverTwo" to="SolverOne" />
    </coupling-scheme:{COUPLINGTYPE}>
  </solver-interface>
</precice-configuration>
"""
