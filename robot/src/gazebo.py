from pathlib import Path

from src.logger import DataStore
from src.robot import move_simple

from URBasic.urScript import UrScript
from URBasic.waypoint6d import TCP6D, Joint6D

from duckify_simulation.duckify_sim import DuckifySim
from duckify_simulation.duckify_sim.robot_control import SimRobotControl
from src.segment import Segment
from src.stage import Stage

def test_waypoints(waypoints: list[Segment], ds: DataStore, default_calibration: Path = None) -> bool:
    """
    Tests the waypoints in Gazebo.

    Parmaters
    ---------
    waypoints : list[Segment]
        The list of waypoints to test.
    ds : DataStore
        The data store for managing transformation data.
    default_calibration : Path, optional
        The path to the default calibration file.
    
    
    Returns
    -------
    bool
        True if the test succeeded, False otherwise.
    """
    try:
        duckify_sim = DuckifySim()
        robot_sim = duckify_sim.robot_control
        _, tcp_offset = ds.load_calibration(default_calibration)
        robot_sim.set_tcp(tcp_offset)

        move_simple(robot_sim, waypoints, ds)
        
        answer = input("Do the Gazebo test succed? y/n \n")
        
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            ds.log("Gazebo test skipped: no clear answer")
            return True
    except Exception as e:
        ds.log(f"Gazebo test skipped: {e}")
        raise
    
class Gazebo(Stage):
    """
    A stage for running Gazebo tests.
    """
    def __init__(self, datastore: DataStore, default_calibration: Path = None):
        """
        Initializes the Gazebo stage.

        Parameters
        ----------
        datastore : DataStore
            The data store for managing transformation data.
        default_calibration : Path
            The path to the default calibration file.
        """
        super().__init__(name="Gazebo", datastore=datastore)
        self.default_calibration = default_calibration

    def run(self, manual_flag: bool=True):
        """
        Runs the Gazebo test.

        Parameters
        ----------
        manual_flag : bool
            Whether to run the test manually.
        """
        if not manual_flag:
            return

        waypoints = self.ds.load_joint_segments()

        answer = input("Do you want to skip Gazebo test? y/n \n")
        if answer == 'y':
            self.ds.log("Gazebo test skipped.")
            raise RuntimeError("You can not avoid gazebot.")

        gazebo = test_waypoints(waypoints, self.ds, self.default_calibration)

        if gazebo:
            self.ds.log("Gazebo test successed.")
        else:
            self.ds.log("Gazebo test failed.")

    def fallback(self):
        raise NotImplementedError("Gazebo fallback method not implemented.")