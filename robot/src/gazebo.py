from pathlib import Path

from src.config import *
from src.pen import PenState
from src.utils import *
from src.logger import DataStore
from src.robot import move_simple

from URBasic.urScript import UrScript
from URBasic.waypoint6d import TCP6D, Joint6D

from duckify_simulation.duckify_sim import DuckifySim
from duckify_simulation.duckify_sim.robot_control import SimRobotControl
from src.segment import MotionType, Segment
from src.stage import Stage


def move_simple_gazebo(robot: SimRobotControl, motion: dict, ds: DataStore = None, multipen: bool = False):
    """
    Moves the robot in Gazebo according to the specified motion.

    Parameters
    ----------
    robot : SimRobotControl
        The robot control instance.
    motion : dict
        The motion data.
    ds : DataStore, optional
        The data store for managing transformation data.
    multipen : bool, optional
        Whether to use multiple pen or not.
    """
    robot.movej(HOMEJ)

    if multipen:
        pen_1, pen_2 = ds.load_pen_calibration()
        MAX_PEN_BY_RACK = 4
        pen_state_1 = PenState(HOMEJ, robot, pen_1)
        pen_state_2 = PenState(HOMEJ, robot, pen_2)

    for s, d in motion.items():
        for c, traces in d.items():
            c_idx = c.split("_")[-1]
            if multipen:
                if MAX_PEN_BY_RACK <= c_idx < 2 * MAX_PEN_BY_RACK:
                    pen_motion = pen_state_2.change_pen(c_idx%MAX_PEN_BY_RACK)
                    pen_state_2.run_moves(pen_motion)
                elif 0 <= c_idx < MAX_PEN_BY_RACK:
                    pen_motion = pen_state_1.change_pen(c_idx)
                    pen_state_1.run_moves(pen_motion)
                else:
                    ds.log(f"WARNING: Invalid pen index for color: {c_idx}")

            ds.log(f"Processing motion side: {s} - color: {c_idx}")
            for trace in traces:
                motion_type = trace.motion_type
                ds.log(f"\tProcessing motion type: {motion_type}")
                if motion_type is MotionType.DRAW:
                    continue
                motion = trace.waypoints
                for m in motion:
                    if isinstance(m, Joint6D):
                        if not robot.movej(m):
                            ds.log(f"ERROR: Position not reached for waypoint: {m}")
                    elif isinstance(m, TCP6D):
                        if not robot.movel(m):
                            ds.log(f"ERROR: Position not reached for waypoint: {m}")
                    else:
                        ds.log(f"WARNING: Unknown waypoint type for waypoint: {m}")
                        raise TypeError(f"Unknown waypoint type for waypoint: {m}")

def test_waypoints(data: dict, ds: DataStore, default_calibration: Path = None, multipen: bool = False) -> bool:
    """
    Tests the data in Gazebo.

    Parmaters
    ---------
    data : dict
        The data to test in Gazebo.
    ds : DataStore
        The data store for managing transformation data.
    default_calibration : Path, optional
        The path to the default calibration file.
    multipen : bool, optional
        Whether to use multiple pen or not.

    Returns
    -------
    bool
        True if the test succeeded, False otherwise.
    """
    try:
        duckify_sim = DuckifySim()
        robot_sim = duckify_sim.robot_control

        tcp_offset = ds.return_tcp_offset(default_calibration)
        robot_sim.set_tcp(tcp_offset)

        if ask_yes_no("Do you want to avoid the DRAW path? y/n \n"):
            move_simple_gazebo(robot_sim, data, ds, multipen=multipen)
        else:
            move_simple(robot_sim, data, ds, multipen=multipen)    

        return ask_yes_no("Do the Gazebo test succeed? y/n \n")
    except Exception as e:
        ds.log(f"Gazebo test skipped: {e}")
        raise
    
class Gazebo(Stage):
    """
    A stage for running Gazebo tests.
    """
    def __init__(self, datastore: DataStore, default_calibration: Path = None, multipen: bool = False):
        """
        Initializes the Gazebo stage.

        Parameters
        ----------
        datastore : DataStore
            The data store for managing transformation data.
        default_calibration : Path
            The path to the default calibration file.
        multipen : bool
            Whether to use multiple pen.
        """
        super().__init__(name="Gazebo", datastore=datastore)
        self.default_calibration = default_calibration
        self.multipen = multipen

    def run(self, manual_flag: bool=True):
        """
        Runs the Gazebo test.

        Parameters
        ----------
        manual_flag : bool
            Whether to run the test manually.
        """
        if not manual_flag:
            self.ds.log("You can not run the Gazebo test in automatic mode.")
            return


        if ask_yes_no("Do you want to skip Gazebo test? y/n \n"):
            self.ds.log("Gazebo test skipped.")
            raise RuntimeError("You can not avoid gazebot.")

        data = self.ds.load_joint_segments()

        gazebo = test_waypoints(data, self.ds, self.default_calibration, self.multipen)

        if gazebo:
            self.ds.log("Gazebo test successed.")
        else:
            self.ds.log("Gazebo test failed.")

    def fallback(self):
        raise NotImplementedError("Gazebo fallback method not implemented.")