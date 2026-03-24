from pathlib import Path

from src.logger import DataStore
from src.segment import TraceSegment, SideType
from src.computation import load_traces
from src.stage import Stage
from src.utils import ask_yes_no
import numpy as np

def rotation_matrix_z(deg: float) -> np.ndarray:
    """
    Creates a rotation matrix for rotation around the Z-axis.

    Parameters
    ----------
    deg : float
        The rotation angle in degrees.

    Returns
    -------
    np.ndarray
        The rotation matrix for rotation around the Z-axis.
    """
    theta = np.radians(deg)
    R = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0,              0,             1]
    ])
    return R


class Filter(Stage):
    """
    Filters trace segments based on their position relative to a threshold.
    """
    def __init__(self, dataStore: DataStore, json_path: Path, multipen: bool = False, turn_degree: float = 0.0):
        """
        Initializes the Filter stage.

        Parameters
        ----------
        dataStore : DataStore
            The data store containing the trace segments.
        json_path : Path
            The path to the JSON file containing the trace data.
        multipen : bool, optional
            If True, allows multiple pens to be used. Default is False.
        turn_degree : float, optional
            The turning degree for the robot. Default is 0.0.
        """
        super().__init__(name="Filter", datastore=dataStore)
        self.json_path = json_path
        self.multipen = multipen
        self.turn_degree = turn_degree

    def run(self, manual_flag: bool=True):
        """
        Runs the filter stage.
        
        Splits traces into left and right sides based on average Y-coordinate of points.
        Assumes traces have 'path' as list of [point, normal], where point is [x, y, z].
        Adjust the axis/threshold if the duck is oriented differently (e.g., use X or Z).

        Parameters
        ----------
        manual_flag : bool, optional
            If True, allows manual extraction of traces. Default is True.
        """
        if not manual_flag:
            if ask_yes_no("Did you already extract the traces? y/n \n"):
                s = self.ds.load_trace_segments()
                self.ds.log_trace_segment(s)
                return
        
        traces, _ = load_traces(self.json_path)
        left_traces = {}
        right_traces = {}

        for trace in traces:
            path = trace['path']
            color = trace['color']

            # Rotate the coordinate
            R = rotation_matrix_z(self.turn_degree)
            waypoints = [(R @ np.array(pt)).tolist() + pn for pt, pn in path]

            ys = [pt[1] for pt in waypoints]

            avg_y = sum(ys) / len(ys) if ys else 0
            # xs = [pt[2] for pt in waypoints]
            # avg_x = sum(xs) / len(xs) if xs else 0

        
            if avg_y >= 0:
                if self.multipen:
                    left_traces[f"color_{color}"] = left_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.LEFT, waypoints)]
                else:
                    left_traces["traces"] = left_traces.get("traces", []) + [TraceSegment(color, SideType.LEFT, waypoints)]
            else:
                if self.multipen:
                    right_traces[f"color_{color}"] = right_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.RIGHT, waypoints)]
                else:
                    right_traces["traces"] = right_traces.get("traces", []) + [TraceSegment(color, SideType.RIGHT, waypoints)]

        s = {
            "left": left_traces,
            "right": right_traces
        }
        self.ds.save_trace_segments(s)
        self.ds.log_trace_segment(s)
    
    def fallback(self):
        raise NotImplementedError("Filter fallback method not implemented.")