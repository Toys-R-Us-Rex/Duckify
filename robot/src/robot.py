from src.segment import SideType
from src.logger import DataStore, DataStoreForce

from URBasic.iscoin import ISCoin
from URBasic.urScript import UrScript
from URBasic.waypoint6d import TCP6D, Joint6D

from duckify_simulation.duckify_sim.robot_control import SimRobotControl

from src.config import *
from src.utils import ask_yes_no

import matplotlib.pyplot as plt

from src.stage import Stage

def move_simple(robot: SimRobotControl | UrScript, motion, ds: DataStore = None, multipen: bool = False):
    robot.movej(HOMEJ)

    # Create six empty joint lists
    j1, j2, j3, j4, j5, j6 = ([] for _ in range(6))

    for s, segment in enumerate(motion):
        for i, m in enumerate(segment.waypoints):
            print(s, i, type(m), Joint6D)
            if isinstance(m, TCP6D):
                if not robot.movel(m, wait=True) and ds:
                    ds.log("TCP not reached: " + str(m))

            elif isinstance(m, Joint6D):
                # Collect joint values
                j1.append(m.j1)
                j2.append(m.j2)
                j3.append(m.j3)
                j4.append(m.j4)
                j5.append(m.j5)
                j6.append(m.j6)

                if not robot.movej(m, wait=True) and ds:
                    ds.log("JOINT not reached: " + str(m))

            else:
                raise NotImplementedError("Only TCP6D or Joint6D points allowed.")

    # Plot joint evolution
    fig, axs = plt.subplots(6, sharex=True)
    joint_lists = [j1, j2, j3, j4, j5, j6]

    for i, j in enumerate(joint_lists):
        axs[i].plot(j)
        axs[i].set_ylabel(f"J{i+1}")

    axs[-1].set_xlabel("Waypoint index")
    plt.tight_layout()
    plt.show()


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
        if not ask_yes_no("Do you want to run the code on the REAL robot? y/n \n"):
            self.ds.log("You chose not to run on robot")
            raise ValueError("You chose not the run on robot")

        iscoin = ISCoin(host=self.robot_ip, opened_gripper_size_mm=40)
        robot = iscoin.robot_control

        _, tcp_offset = self.ds.load_calibration(self.default_calibration)
        robot.set_tcp(tcp_offset)

        waypoint = self.ds.load_waypoints()

        if manual_flag:
            force_active = ask_yes_no("Do you want to start force logging? y/n \n")
        else:
            force_active = False

        if force_active:
            force = DataStoreForce(robot)
            force.start_logging()

        try:
            move_simple(robot, waypoint, self.ds)
        except Exception as e:
            self.ds.log(f"Exception with robot: {e}")
            raise
        
        if force_active:
            force.stop_logging()