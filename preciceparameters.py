from enum import Enum
from typing import NamedTuple

import internals.datatypes as internal

class SolverMPIParameters():
    def __init__(self, num_ranks: int, extra_options_list: list = None ):
        self.num_ranks = num_ranks
        self.extra_options_list = extra_options_list

    def get_number_of_ranks(self) -> int:
        return self.num_ranks

    def get_extra_options_list(self) -> list:
        return self.extra_options_list

    def to_string(self) -> str:
        return "MPI options:\n  Number of Ranks: {0}\n  Extra options: {1}".format( self.num_ranks, self.extra_options_list )



class SolverParameters(NamedTuple):
    name: str
    executable_name: str
    executable_path: str = ""
    solver_cmd_line: list=None
    mpi_parameters: SolverMPIParameters = None

    def __repr__(self):
        return f"Solver: {self.name}\n  Executable: {self.executable_name}\n  Executable path: {self.executable_path}\n  Solver command line: {self.solver_cmd_line}\n  MPI parameters: {self.mpi_parameters}"

#class SolverParameters():
#
#    def __init__(self, name: str, executable_name: str, executable_path: str = "", solver_cmd_line: list=None, mpi_parameters: SolverMPIParameters = None ):
#        self.name = name
#        self.executable_name = executable_name
#        self.executable_path = executable_path
#        self.solver_cmd_line = solver_cmd_line
#        self.mpi_parameters = mpi_parameters
#
#    def get_name(self) -> str:
#        return self.name
#
#    def get_executable_name(self) -> str:
#        return self.executable_name
#
#    def get_executable_path(self) -> str:
#        return self.executable_path
#
#    def get_solver_cmd_line(self) -> list:
#        return self.solver_cmd_line
#
#    def to_string(self) -> str:
#        return "Solver: {0}\n  Executable: {1}\n  Executable path: {2}".format( self.name, self.executable_name, self.executable_path )


class InterfaceQuasiNewtonMethod():

    def __init__(self, ignore_time_window_reuse=False):
        self.ignore_time_window_reuse = ignore_time_window_reuse

class ILSAccelerator(internal.InterfaceQuasiNewtonMethod):

    def __init__(self,  reuse: int):
        self.reuse = reuse

    def __repr__(self):
        return f"ILS"

    def to_string(self) -> str:
        return "Accelerator type: ILS\n  Reuse: {}".format( reuse )


class IMVJRestartType(Enum):
    NO_RESTART = "no-restart"
    RS_0 = "RS-0"
    RS_LS = "RS-LS"
    RS_SVD = "RS-SVD"
    RS_SLIDE = "RS-SLIDE"

class IMVJOptions(NamedTuple):
    type: IMVJRestartType=IMVJRestartType.RS_SVD
    chunk_size: int = 8
    truncation_threshold: float = 1e-4
    reused_time_windows: int = 0

#    def __repr__(self):
#        return f""

    #def __init__(self, type: IMVJRestartType=IMVJRestartType.RS_SVD, chunk_size: int = 8, truncation_threshold: float = 1e-4, reused_time_windows: int = 0 ):
    #    self.type = type
    #    self.chunk_size = chunk_size
    #    self.truncation_threshold = truncation_threshold
    #    self.reused_time_windows = reused_time_windows


class IMVJAccelerator(internal.InterfaceQuasiNewtonMethod):

    def __init__(self, type: IMVJRestartType=IMVJRestartType.RS_SVD, chunk_size: int = 8, truncation_threshold: float = 1e-4, reused_time_windows: int = 0, ignore_time_window_reuse: bool=True):
        super().__init__(ignore_time_window_reuse)
        self.options = IMVJOptions( type=type, chunk_size=chunk_size, truncation_threshold=truncation_threshold, reused_time_windows=reused_time_windows )

    def __repr__(self):
        return f"{self.options.type.value}"


class FilterType(Enum):
    QR1 = "QR1"
    QR2 = "QR2"

class FilterSettings():

    def __init__(self, filter_type: FilterType, filter_limit: float ):
        self.filter_type = filter_type
        self.filter_limit = filter_limit

    def get_type(self) -> FilterType:
        return self.filter_type

    def get_limit(self) -> float:
        return self.filter_limit

    def __repr__(self):
        return f"{self.filter_type.value}-{self.filter_limit}"

    def to_string(self) -> str:
        return "Filter type: {}, Filter Limit: {}".format( self.filter_type, self.filter_limit )


class CouplingType(Enum):
    SERIAL_EXPLICIT = "serial-explicit"
    SERIAL_IMPLICIT = "serial-implicit"
    PARALLEL_EXPLICIT = "parallel-explicit"
    PARALLEL_IMPLICIT = "parallel-implicit"

    def __repr__(self):
        return f"{self.value}"


#class TestCase:
#    def __init__(
#        self,
#        name,
#        max_time,
#        time_step_size,
#        initial_relaxation,
#        coupling_type,
#        accelerator=AcceleratorType.IQN_ILS,
#        filter_type=FilterType.QR1,
#        filter_limit="1e-5",
#        time_windows_reused=0,
#        svd_truncation_threshold=None,
#    ):
#        self.name = name
#
#        self.max_time = max_time
#        self.time_step_size = time_step_size
#        self.initial_relaxation = initial_relaxation
#
#        self.coupling_type = coupling_type
#        self.accelerator = accelerator
#        self.filter_type = filter_type
#        self.filter_limit = filter_limit
#        self.time_windows_reused = time_windows_reused
#
#        self.imvj_restart_mode = IMVJRestartType.RS_SVD
#        self.svd_truncation_threshold = svd_truncation_threshold
#        if svd_truncation_threshold == None:
#            assert self.accelerator == AcceleratorType.IQN_ILS, "SVD Trunction value is set, but using IQN-ILS accelerator!"
#
#        assert self.imvj_restart_mode == IMVJRestartType.RS_SVD, "Only rs-svd restart mode is supported at the moment!"
#
#    def to_string(self):
#        return "  Name: {0},\n  End time: {1},\n  dt: {2},\n  Initial relaxation: {3},\n  Accelerator: {4},\n  Filter type: {5},\n  Filter limit: {6},\n  Time windows reused: {7},\n  SVD truncation threshold: {8}".format(
#            self.name,
#            self.max_time,
#            self.time_step_size,
#            self.initial_relaxation,
#            self.accelerator.name,
#            self.filter_type.name,
#            self.filter_limit,
#            self.time_windows_reused,
#            self.svd_truncation_threshold,
#        )
#
#    def get_config_header(self):
#        return """<?xml version="1.0"?>
#
#<precice-configuration>
#  <log>
#    <sink type="stream" output="stdout"  filter= "(%Severity% > debug) or (%Severity% >= trace and %Module% contains SolverInterfaceImpl)"  enabled="false" />
#    <sink type="stream" output="stdout"  enabled="false" />
#  </log>
#
#  <solver-interface dimensions="3">
#
#    <data:scalar name="Pressure"/>
#    <data:scalar name="Displacement"/>
#
#    <mesh name="HDFlowMeshTop">
#      <use-data name="Pressure" />
#      <use-data name="Displacement" />
#    </mesh>
#
#    <mesh name="HDFlowMeshBottom">
#      <use-data name="Pressure" />
#      <use-data name="Displacement" />
#    </mesh>
#
#    <mesh name="FractureMeshTop">
#      <use-data name="Pressure" />
#      <use-data name="Displacement" />
#    </mesh>
#
#    <mesh name="FractureMeshBottom">
#      <use-data name="Pressure" />
#      <use-data name="Displacement" />
#    </mesh>
#
#    <participant name="HDFlowSolver">
#      <use-mesh name="HDFlowMeshTop" provide="yes"/>
#      <use-mesh name="HDFlowMeshBottom" provide="yes"/>
#      <use-mesh name="FractureMeshTop" from="BiotSolver"/>
#      <use-mesh name="FractureMeshBottom" from="BiotSolver"/>
#
#      <write-data name="Pressure" mesh="HDFlowMeshTop"/>
#      <write-data name="Pressure" mesh="HDFlowMeshBottom"/>
#      <read-data name="Displacement" mesh="HDFlowMeshTop"/>
#      <read-data name="Displacement" mesh="HDFlowMeshBottom"/>
#
#      <mapping:nearest-neighbor direction="read" from="FractureMeshTop" to="HDFlowMeshTop" constraint="consistent" timing="initial"/>
#      <mapping:nearest-neighbor direction="read" from="FractureMeshBottom" to="HDFlowMeshBottom" constraint="consistent" timing="initial"/>
#
#      <master:mpi-single/>
#
#    </participant>
#
#    <participant name="BiotSolver">
#      <use-mesh name="FractureMeshTop" provide="yes"/>
#      <use-mesh name="FractureMeshBottom" provide="yes"/>
#
#      <use-mesh name="HDFlowMeshTop" from="HDFlowSolver"/>
#      <use-mesh name="HDFlowMeshBottom" from="HDFlowSolver"/>
#
#      <!---      <use-mesh name="HDFlowMesh" from="HDFlowSolver"/>  -->
#      <write-data name="Displacement" mesh="FractureMeshTop"/>
#      <write-data name="Displacement" mesh="FractureMeshBottom"/>
#      <read-data name="Pressure" mesh="FractureMeshTop"/>
#      <read-data name="Pressure" mesh="FractureMeshBottom"/>
#
#      <mapping:nearest-neighbor direction="read" from="HDFlowMeshBottom" to="FractureMeshBottom" constraint="consistent" timing="initial"/>
#      <mapping:nearest-neighbor direction="read" from="HDFlowMeshTop" to="FractureMeshTop" constraint="consistent" timing="initial"/>
#
#      <master:mpi-single/>
#    </participant>
#
#    <m2n:sockets from="HDFlowSolver" to="BiotSolver" exchange-directory="." />
#
#    <coupling-scheme:{COUPLING_TYPE}>
#        <participants first="HDFlowSolver" second="BiotSolver"/>
#        <max-time value="{MAX_TIME}"/>
#        <time-window-size value="{TIME_STEP_SIZE}" />
#        <max-iterations value="150"/>
#
#        <exchange data="Pressure" mesh="HDFlowMeshTop" from="HDFlowSolver" to="BiotSolver" initialize="false"/>
#        <exchange data="Pressure" mesh="HDFlowMeshBottom" from="HDFlowSolver" to="BiotSolver" initialize="false"/>
#
#        <exchange data="Displacement" mesh="FractureMeshTop" from="BiotSolver" to="HDFlowSolver" initialize="true"/>
#        <exchange data="Displacement" mesh="FractureMeshBottom" from="BiotSolver" to="HDFlowSolver" initialize="true" />
#
#        <relative-convergence-measure limit="1e-3" data="Pressure" mesh="HDFlowMeshTop" strict="1" />
#        <relative-convergence-measure limit="1e-3" data="Pressure" mesh="HDFlowMeshBottom" strict="1"/>
#        <relative-convergence-measure limit="1e-3" data="Displacement" mesh="FractureMeshTop" strict="1"/>
#        <relative-convergence-measure limit="1e-3" data="Displacement" mesh="FractureMeshBottom" strict="1"/>
#
#        <extrapolation-order value="0"/>
#    """.format(
#            COUPLING_TYPE=self.coupling_type.value,
#            MAX_TIME=self.max_time,
#            TIME_STEP_SIZE=self.time_step_size,
#        )
#
#    def set_up_acceleration(self):
#        accelerator_string = ""
#
#        accelerator_setup_str = ""
#        if self.accelerator == AcceleratorType.IQN_ILS:
#            accelerator_setup_str = ""
#        elif self.accelerator == AcceleratorType.IQN_IMVJ:
#            accelerator_setup_str = """<imvj-restart-mode type="RS-SVD" truncation-threshold="{TRUNCATION_THRESHOLD}" chunk-size="8" />""".format(
#                TRUNCATION_THRESHOLD=self.svd_truncation_threshold
#            )
#
#        preconditioner_setup_str = (
#            """<preconditioner type="residual-sum" freeze-after="1"/>"""
#        )
#        # if self.accelerator == AcceleratorType.IQN_IMVJ:
#        #    preconditioner_setup_str = """<preconditioner type="residual-sum" freeze-after="1"  />"""
#
#        if (self.accelerator == AcceleratorType.IQN_ILS) and (
#            self.coupling_type == CouplingType.PARALLEL_IMPLICIT
#        ):
#            #    preconditioner_setup_str = """<preconditioner type="residual-sum" freeze-after="1"  />"""
#            preconditioner_setup_str = """<preconditioner type="value"/>"""
#            # preconditioner_setup_str = """<preconditioner type="constant"/>"""
#
#        if self.coupling_type == CouplingType.SERIAL_IMPLICIT:
#            accelerator_string = """
#        <acceleration:{ACCELERATOR_TYPE}>
#          <data name="Displacement" mesh="FractureMeshTop"/>
#          <data name="Displacement" mesh="FractureMeshBottom"/>
#
#          <initial-relaxation value="{INITIAL_RELAXATION}"/>
#          <max-used-iterations value="10000"/>
#          <time-windows-reused value="{TIME_WINDOWS_REUSED}"/>
#
#          {PRECONDITIONER}
#          <filter type="{FILTER_TYPE}" limit="{FILTER_LIMIT}"/>
#
#          {ACCELERATOR_SETUP_STRING}
#        </acceleration:{ACCELERATOR_TYPE}>""".format(
#                ACCELERATOR_TYPE=self.accelerator.value,
#                INITIAL_RELAXATION=self.initial_relaxation,
#                TIME_WINDOWS_REUSED=self.time_windows_reused,
#                PRECONDITIONER=preconditioner_setup_str,
#                FILTER_TYPE=self.filter_type.value,
#                FILTER_LIMIT=self.filter_limit,
#                ACCELERATOR_SETUP_STRING=accelerator_setup_str,
#            )
#        elif self.coupling_type == CouplingType.PARALLEL_IMPLICIT:
#            accelerator_string = """
#        <acceleration:{ACCELERATOR_TYPE}>
#          <data name="Displacement" mesh="FractureMeshTop"/>
#          <data name="Displacement" mesh="FractureMeshBottom"/>
#          <data name="Pressure" mesh="HDFlowMeshTop"/>
#          <data name="Pressure" mesh="HDFlowMeshBottom"/> 1
#
#          <initial-relaxation value="{INITIAL_RELAXATION}"/>
#          <max-used-iterations value="10000"/>
#          <time-windows-reused value="{TIME_WINDOWS_REUSED}"/>
#
#          {PRECONDITIONER}
#          <filter type="{FILTER_TYPE}" limit="{FILTER_LIMIT}"/>
#
#          {ACCELERATOR_SETUP_STRING}
#        </acceleration:{ACCELERATOR_TYPE}>""".format(
#                ACCELERATOR_TYPE=self.accelerator.value,
#                INITIAL_RELAXATION=self.initial_relaxation,
#                TIME_WINDOWS_REUSED=self.time_windows_reused,
#                PRECONDITIONER=preconditioner_setup_str,
#                FILTER_TYPE=self.filter_type.value,
#                FILTER_LIMIT=self.filter_limit,
#                ACCELERATOR_SETUP_STRING=accelerator_setup_str,
#            )
#
#        return accelerator_string
#
#    def get_config_footer(self):
#        return """
#      </coupling-scheme:{COUPLING_TYPE}>
#
#  </solver-interface>
#</precice-configuration>""".format(
#            COUPLING_TYPE=self.coupling_type.value
#        )
#
#
#def write_precice_configuration_file(testcase, filename, is_serial_coupling=True):
#
#    # if (is_serial_coupling):
#    #    file_prefix = "serial-implicit-"
#    # else:
#    #    file_prefix = "parallel-implicit-"
#
#    # if ( testcase.accelerator == AcceleratorType.IQN_ILS ):
#    #    file_suffix = "ILS-TEMPLATE.xml"
#    #     fstr = open( "precice-config-ILS-TEMPLATE.xml", "r")
#    # elif (testcase.accelerator == AcceleratorType.IQN_IMVJ ):
#    #    file_suffix = "IMVJ-TEMPLATE.xml"
#    #        fstr = open( "precice-config-IMVJ-TEMPLATE.xml", "r")
#    # else:
#    #    raise "Could not find template for testcase: {}".format( testcase.accelerator )
#
#    # fstr = open( file_prefix + file_suffix, "r")
#    # lines = fstr.readlines()
#    # fstr.close()
#
#    fstr = open(filename, "w")
#
#    fstr.write(testcase.get_config_header())
#    fstr.write(testcase.set_up_acceleration())
#    fstr.write(testcase.get_config_footer())
#
#    fstr.close()
#
#
