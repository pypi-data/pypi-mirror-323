from __future__ import annotations
import numpy
import ostk.core.type
import ostk.physics.time
import typing
__all__ = ['FiniteDifferenceSolver', 'TemporalConditionSolver']
class FiniteDifferenceSolver:
    """
    
                A Finite Difference Solver to compute the gradient, state transition matrix, and jacobian of a function.
    
            
    """
    class Type:
        """
        
                    Type of finite difference scheme.
        
                
        
        Members:
        
          Forward : Forward difference scheme.
        
          Backward : Backward difference scheme.
        
          Central : Central difference scheme.
        """
        Backward: typing.ClassVar[FiniteDifferenceSolver.Type]  # value = <Type.Backward: 1>
        Central: typing.ClassVar[FiniteDifferenceSolver.Type]  # value = <Type.Central: 2>
        Forward: typing.ClassVar[FiniteDifferenceSolver.Type]  # value = <Type.Forward: 0>
        __members__: typing.ClassVar[dict[str, FiniteDifferenceSolver.Type]]  # value = {'Forward': <Type.Forward: 0>, 'Backward': <Type.Backward: 1>, 'Central': <Type.Central: 2>}
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def default() -> FiniteDifferenceSolver:
        """
                        Get the default Finite Difference Solver.
        
                        Returns:
                            FiniteDifferenceSolver: The default Finite Difference Solver.
        """
    @staticmethod
    def string_from_type(type: FiniteDifferenceSolver.Type) -> ostk.core.type.String:
        """
                        Convert a type to string.
        
                        Args:
                            type (FiniteDifferenceSolver.Type): The type.
        
                        Returns:
                            str: The string name of the type.
        """
    def __init__(self, type: FiniteDifferenceSolver.Type, step_percentage: ostk.core.type.Real, step_duration: ostk.physics.time.Duration) -> None:
        """
                        Construct a FiniteDifferenceSolver.
        
                        Args:
                            type (FiniteDifferenceSolver.Type): Type of finite difference scheme.
                            step_percentage (float): The step percentage to use for computing the STM/Jacobian.
                            step_duration (Duration): The step duration to use for computing the gradient.
        
                        Returns:
                            FiniteDifferenceSolver: The FiniteDifferenceSolver.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_gradient(self, state: ..., generate_state_coordinates: typing.Callable[[..., ostk.physics.time.Instant], numpy.ndarray[numpy.float64[m, 1]]]) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
                        Compute the gradient.
        
                        Args:
                            state (State): The state.
                            generate_state_coordinates (function): The function to generate the state coordinates.
        
                        Returns:
                            np.array: The gradient.
        """
    def compute_jacobian(self, state: ..., generate_state_coordinates: typing.Callable[[..., ostk.physics.time.Instant], numpy.ndarray[numpy.float64[m, 1]]]) -> numpy.ndarray[numpy.float64[m, n]]:
        """
                        Compute the jacobian.
        
                        Args:
                            state (State): The state.
                            generate_state_coordinates (function): The function to generate the state coordinates.
        
                        Returns:
                            np.array: The jacobian.
        """
    @typing.overload
    def compute_state_transition_matrix(self, state: ..., instants: list[ostk.physics.time.Instant], generate_states_coordinates: typing.Callable[[..., list[ostk.physics.time.Instant]], numpy.ndarray[numpy.float64[m, n]]]) -> list[numpy.ndarray[numpy.float64[m, n]]]:
        """
                        Compute a list of state transition matrix (STM) at the provided instants.
        
                        Args:
                            state (State): The state.
                            instants (Array(Instant)): The instants at which to calculate the STM.
                            generate_states_coordinates (callable): The function to get the states coordinates as a matrix. Each column is a set of state coordinates.
        
                        Returns:
                            np.array: The list of state transition matrices.
        """
    @typing.overload
    def compute_state_transition_matrix(self, state: ..., instant: ostk.physics.time.Instant, generate_state_coordinates: typing.Callable[[..., ostk.physics.time.Instant], numpy.ndarray[numpy.float64[m, 1]]]) -> numpy.ndarray[numpy.float64[m, n]]:
        """
                        Compute the state transition matrix (STM).
        
                        Args:
                            state (State): The state.
                            instant (Instant): The instant at which to calculate the STM.
                            generate_state_coordinates (callable): The function to get the state coordinates. Must be a column vector.
        
                        Returns:
                            np.array: The state transition matrix.
        """
    def get_step_duration(self) -> ostk.physics.time.Duration:
        """
                        Get the step duration used for computing the gradient.
        
                        Returns:
                            Duration: The step duration.
        """
    def get_step_percentage(self) -> ostk.core.type.Real:
        """
                        Get the step percentage used for computing the STM.
        
                        Returns:
                            float: The step percentage.
        """
    def get_type(self) -> FiniteDifferenceSolver.Type:
        """
                        Get the type.
        
                        Returns:
                            FiniteDifferenceSolver.Type: The type.
        """
class TemporalConditionSolver:
    """
    
                Given a set of conditions and a time interval, the solver computes all sub-intervals over which conditions are met.
    
            
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, time_step: ostk.physics.time.Duration, tolerance: ostk.physics.time.Duration, maximum_iteration_count: int = 500) -> None:
        """
                        Constructor.
        
                        Args:
                            time_step (Duration): The time step.
                            tolerance (Duration): The tolerance of the solver.
                            maximum_iteration_count (int): The maximum number of iterations allowed.
        """
    def get_maximum_iteration_count(self) -> int:
        """
                        Get the maximum number of iterations allowed.
        
                        Returns:
                            int: The maximum number of iterations allowed.
        """
    def get_time_step(self) -> ostk.physics.time.Duration:
        """
                        Get the time step.
        
                        Returns:
                            Duration: The time step.
        """
    def get_tolerance(self) -> ostk.physics.time.Duration:
        """
                        Get the tolerance.
        
                        Returns:
                            Duration: The tolerance.
        """
    @typing.overload
    def solve(self, condition: typing.Callable[[ostk.physics.time.Instant], bool], interval: ostk.physics.time.Interval) -> list[ostk.physics.time.Interval]:
        """
                        Solve a temporal condition.
        
                        Args:
                            condition (function): The condition to solve.
                            interval (Interval): The interval to solve the condition over.
        
                        Returns:
                            Duration: The time at which the condition is satisfied.
        """
    @typing.overload
    def solve(self, conditions: list[typing.Callable[[ostk.physics.time.Instant], bool]], interval: ostk.physics.time.Interval) -> list[ostk.physics.time.Interval]:
        """
                        Solve an array of temporal conditions.
        
                        Args:
                            conditions (list): The conditions to solve.
                            interval (Interval): The interval to solve the conditions over.
        
                        Returns:
                            list: The times at which the conditions are satisfied.
        """
