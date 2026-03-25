from src.segment import SideType
from src.logger import DataStore, DataStoreForce

from URBasic.iscoin import ISCoin
from URBasic.urScript import UrScript
from URBasic.waypoint6d import TCP6D, Joint6D

from duckify_simulation.duckify_sim.robot_control import SimRobotControl

from src.config import *
from src.utils import ask_yes_no
from src.pen import PenState
import matplotlib.pyplot as plt

from src.stage import Stage

def move_simple(robot: SimRobotControl | UrScript, motion: dict, ds: DataStore = None, multipen: bool = False):
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


class Robot(Stage):
    """
    A class representing the robot in the simulation.
    """
    def __init__(self, datastore: DataStore, robot_ip: str, begin_side: SideType, default_calibration: str = None, multipen: bool = False):
        """
        Initializes the Robot instance.

        Parameters
        ----------
        datastore : DataStore
            The data store for managing simulation data.
        robot_ip : str
            The IP address of the robot.
        begin_side : SideType
            The side from which the robot starts.
        default_calibration : str
            The path to the default calibration file.
        multipen : bool
            Whether to use multiple pen or not.
        """
        super().__init__(name="Robot", datastore=datastore)
        self.robot_ip = robot_ip
        self.side = begin_side
        self.default_calibration = default_calibration
        self.multipen = multipen

    def run(self, manual_flag: bool=True):
        """
        Runs the robot simulation.

        Parameters
        ----------
        manual_flag : bool
            Whether to run the simulation manually.
        """
        if not manual_flag:
            self.ds.log("You can not run the robot simulation in automatic mode.")
            return

        if not ask_yes_no("Do you want to run the code on the REAL robot? y/n \n"):
            self.ds.log("You chose not to run on robot")
            raise ValueError("You chose not the run on robot")

        iscoin = ISCoin(host=self.robot_ip, opened_gripper_size_mm=40)
        robot = iscoin.robot_control

        _, tcp_offset = self.ds.load_calibration(self.default_calibration)
        robot.set_tcp(tcp_offset)

        motion = self.ds.load_joint_segments()

        if manual_flag:
            force_active = ask_yes_no("Do you want to start force logging? y/n \n")
        else:
            force_active = False

        if force_active:
            force = DataStoreForce(robot)
            force.start_logging()

        try:
            move_simple(robot, motion, self.ds)
        except Exception as e:
            self.ds.log(f"Exception with robot: {e}")
            raise
        
        if force_active:
            force.stop_logging()