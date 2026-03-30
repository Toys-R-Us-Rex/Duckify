from pathlib import Path
from typing import Optional

from robot.src.logger import DataStore
from robot.src.segment import TraceSegment, SideType
from robot.src.computation import load_traces, correct_bottom_values, filterout_bottom_values
from robot.src.stage import Stage
from robot.src.utils import ask_yes_no
from robot.src.config import *


def filter_traces(json_path: Path, multipen: bool, side: SideType) -> dict:
    traces, _ = load_traces(json_path)
    left_traces = {}
    right_traces = {}

    max_per_side = 50
    left_count = 0
    right_count = 0

    for trace in traces:
        path = trace['path']
        color = trace['color']
        color = color if multipen else 0


        # Rotate the coordinate
        # waypoints = [pt+ pn for pt, pn in path[::5]]
        waypoints = [pt+ pn for pt, pn in path]

        waypoints = filterout_bottom_values(waypoints)
        waypoints = correct_bottom_values(waypoints)

        # waypoints = waypoints[2:-2]

        ys = [pt[1] for pt in waypoints]

        avg_y = sum(ys) / len(ys) if ys else 0
        # xs = [pt[2] for pt in waypoints]
        # avg_x = sum(xs) / len(xs) if xs else 0

        is_left = avg_y >= 0
        if side != SideType.LEFT:
            is_left = not is_left

        if is_left:
            if left_count >= max_per_side:
                continue
            if side == SideType.LEFT:
                left_traces[f"color_{color}"] = left_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.LEFT, [[w[0], w[1], OFFSET_Z_HOTFIX + w[2], w[3], w[4], w[5]] for w in waypoints])]
            else:
                left_traces[f"color_{color}"] = left_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.LEFT, [[-w[0], -w[1], OFFSET_Z_HOTFIX + w[2], -w[3], -w[4], w[5]] for w in waypoints])]
            left_count += 1
        else:
            if right_count >= max_per_side:
                continue
            if side == SideType.LEFT:
                right_traces[f"color_{color}"] = right_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.RIGHT, [[-w[0], -w[1], OFFSET_Z_HOTFIX + w[2], -w[3], -w[4], w[5]] for w in waypoints])]
            else:
                right_traces[f"color_{color}"] = right_traces.get(f"color_{color}", []) + [TraceSegment(color, SideType.RIGHT, [[w[0], w[1], OFFSET_Z_HOTFIX + w[2], w[3], w[4], w[5]] for w in waypoints])]
            right_count += 1

    s = {
        "left": left_traces,
        "right": right_traces
    }
    return s


class Filter(Stage):
    """
    Filters trace segments based on their position relative to a threshold.
    """
    def __init__(self, dataStore: DataStore, json_path: Optional[Path] = None, multipen: bool = False, duck_side: SideType = SideType.LEFT):
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
        duck_side : SideType, optional
            The side of the duck facing the robot.
        """
        super().__init__(name="Filter", datastore=dataStore)
        self.json_path = json_path
        self.multipen = multipen
        self.side = duck_side

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

        s = filter_traces(self.json_path, self.multipen, self.side)
        self.ds.save_trace_segments(s)
    
    def fallback(self):
        raise NotImplementedError("Filter fallback method not implemented.")