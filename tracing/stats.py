from dataclasses import dataclass


@dataclass
class TracingStats:
    duration: float
    n_islands: int
    n_2d_traces: int
    n_3d_traces: int
    n_points: int
