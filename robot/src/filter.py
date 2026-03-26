from pathlib import Path

from src.logger import DataStore
from src.segment import TraceSegment, SideType
from src.computation import load_traces, correct_bottom_values
from src.stage import Stage
from src.utils import ask_yes_no, rotation_matrix_z
import numpy as np

class Filter(Stage):
    """
    Filters trace segments based on their position relative to a threshold.
    """
    def __init__(self, dataStore: DataStore, json_path: Path = None, multipen: bool = False):
        """
        Initializes the Filter stage.

        Parameters
        ----------
        dataStore : DataStore
            The data store containing the trace segments.
        json_path : Path, optional
            The path to the JSON file containing the trace data.
        multipen : bool, optional
            If True, allows multiple pens to be used. Default is False.
        turn_degree : float, optional
            The turning degree for the robot. Default is 0.0.
        """
        super().__init__(name="Filter", datastore=dataStore)
        self.json_path = json_path
        self.multipen = multipen

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
            self.ds.log("Run in automatic mode.")
            if self.ds.check_trace_segments():
                if self.json_path.exists():
                    self.ds.log("Existing trace segments overridden.")
                else:
                    self.ds.log("Using existing trace segments.")
                    return
            elif not self.json_path.exists():
                self.ds.log("No existing trace segments file or no JSON file found.")
                raise RuntimeError("No existing trace segments file or no JSON file found.")
        else:
            if ask_yes_no("Did you already extract the traces? y/n \n"):
                s = self.ds.load_trace_segments()
                return


        traces, _ = load_traces(self.json_path)
        left_traces = {}
        right_traces = {}

        for trace in traces:
            path = trace['path']
            color = trace['color']
            color = color if self.multipen else 0


            # Rotate the coordinate
            # waypoints = [pt+ pn for pt, pn in path[::5]]
            waypoints = [pt+ pn for pt, pn in path]

            waypoints = correct_bottom_values(waypoints)

            # waypoints = waypoints[2:-2]

            ys = [pt[1] for pt in waypoints]

            avg_y = sum(ys) / len(ys) if ys else 0
            # xs = [pt[2] for pt in waypoints]
            # avg_x = sum(xs) / len(xs) if xs else 0

            if avg_y >= 0:
                left_traces[f"color_{color}"] = left_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.LEFT, waypoints)]
            else:
                right_traces[f"color_{color}"] = right_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.RIGHT, waypoints)]

        s = {
            "left": left_traces,
            "right": right_traces
        }
        self.ds.save_trace_segments(s)
    
    def fallback(self):
        raise NotImplementedError("Filter fallback method not implemented.")