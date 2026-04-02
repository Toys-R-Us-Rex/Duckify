from robot.src.computation import simplify_path
from robot.src.safety import setup_checker
from robot.src.transformation import extract_pybullet_pose
from pybullet_planning import plan_joint_motion
from robot.src.segment import MotionType, SideType
from robot.src.logger import DataStore, DataStoreForce_2
from robot.src.kinematics import get_fk, pose_to_matrix

from URBasic.iscoin import ISCoin
from URBasic.urScript import UrScript
from URBasic.waypoint6d import TCP6D, Joint6D, Joint6DDescriptor, TCP6DDescriptor

from robot.duckify_simulation.duckify_sim import DuckifySim

from robot.src.config import *
from robot.src.utils import *
from robot.src.pen import PenState
import matplotlib.pyplot as plt

from robot.src.stage import Stage

def intermediar_calibration_tcp_test(robot_ctr: UrScript, ds: DataStore):
    j = robot_ctr.get_actual_joint_positions()
    if any(j.toList() != HOMEJ.toList()):
        ds.log(f"Joint positions are not at home: {j} - {HOMEJ}")
    else:
        actual_tcp = robot_ctr.get_actual_tcp_pose()
        move_down = TCP6D.createFromMetersRadians(
            actual_tcp.x,
            0.3,
            MINIMAL_DISTANCE,
            FACING_DOWN[0],
            FACING_DOWN[1],
            FACING_DOWN[2]
        )
        move_above = TCP6D.createFromMetersRadians(
            actual_tcp.x,
            actual_tcp.y,
            0.3,
            FACING_DOWN[0],
            FACING_DOWN[1],
            FACING_DOWN[2]

        )
        robot_ctr.movel(move_above)
        robot_ctr.movel(move_down)
        while not ask_yes_no("Proceed with calibration? y/n \n"):
            pass
        robot_ctr.movel(move_above)
        robot_ctr.movel(actual_tcp)

def intermediar_calibration_joint_test(robot_ctr: UrScript, ds: DataStore):
    j = robot_ctr.get_actual_joint_positions()
    if any(j.toList() != HOMEJ.toList()):
        ds.log(f"Joint positions are not at home: {j} - {HOMEJ}")
    elif ds.check_test_position():
        robot_ctr.movej(HOMEJ)
        test_pos = ds.load_test_position()

        obj2robot = ds.load_transformation()
        pos, quat, scale = extract_pybullet_pose(obj2robot)
        obstacles = OBSTACLE_STLS
        for obs in obstacles:
            if 'position' not in obs:
                obs['position'] = pos
                obs['orientation'] = quat
        checker = setup_checker(obstacles, gui=False)
        checker.set_joint_angles(HOMEJ.toList())
        path = plan_joint_motion(
            checker.robot_id, checker.joint_indices, test_pos,
            obstacles=checker.obstacle_ids,
            self_collisions=True,
            resolutions=[0.02, 0.02, 0.02, 0.02, 0.02, 0.02],
            # weights=[0.5, 0.5, 0.5, 1, 0.1, 0.1]
        )
        if path is not None:
            path = simplify_path(path)
            w = [Joint6D.createFromRadians(*conf) for conf in path]
            waypoints = Joint6DDescriptor.createFromJointsList(w)
            robot_ctr.movej_waypoints(waypoints)

    else:
        ds.log("ERROR: No test position found.")

def move_simple(robot: ISCoin | DuckifySim, motion: dict, ds: DataStore = None, multipen: bool = False):
    robot_ctr = robot.robot_control
    robot_ctr.movej(HOMEJ)

    _, tcp_offset = ds.load_calibration()
    tcp_matrix = pose_to_matrix(tcp_offset)

    if multipen:
        pen_1, pen_2 = ds.load_pen_calibration()
        MAX_PEN_BY_RACK = 4
        pen_state_1 = PenState(HOMEJ, robot, pen_1)
        pen_state_2 = PenState(HOMEJ, robot, pen_2)

    for s, d in motion.items():
        if not ask_yes_no(f"Draw on side {s}? y/n \n"):
            continue
        for c, traces in d.items():
            c_idx = int(c.split("_")[-1])
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
            if not ask_yes_no(f"Proceed with color {c_idx}? y/n \n"):
                ds.log(f"User chose not to proceed motion: (side: {s} , color: {c_idx})")
                continue

            if ask_yes_no("Do you want to test calibration? y/n \n"):
                intermediar_calibration_joint_test(robot_ctr, ds)

            # Conversion in waypoint
            for trace in traces:
                motion_type = trace.motion_type
                if motion_type is MotionType.DRAW:
                    motion = [get_fk(joint_angles, tcp_matrix) for joint_angles in trace.waypoints]
                else:
                    motion = trace.waypoints
                waypoints = []
                for m in motion:
                    if isinstance(m, Joint6D):
                        waypoints.append(Joint6DDescriptor(m, a=DRAW_A, v=DRAW_V))
                    elif isinstance(m, TCP6D):
                        waypoints.append(TCP6DDescriptor(m, a=DRAW_A, v=DRAW_V))
                    else:
                        ds.log(f"WARNING: Unknown waypoint type for waypoint: {type(m)}")
                        raise TypeError(f"Unknown waypoint type for waypoint: {type(m)}")

                if FORCE_ENABLE:
                    if motion_type == MotionType.DRAW and isinstance(robot_ctr, UrScript):
                        ds.log("Activating force mode for DRAW segment")
                        robot_ctr.force_mode(
                            task_frame=[0,0,0,0,0,0],
                            selection_vector=[0,0,1,0,0,0],  # compliance en Z
                            wrench=[0,0,0,0,0,0],
                            f_type=2,
                            limits=[2, 2, 1.5, 1, 1, 1]
                        )

                    elif motion_type == MotionType.APPROACH and isinstance(robot_ctr, UrScript):
                        ds.log("Soft approach: enabling light force mode")
                        robot_ctr.force_mode(
                            task_frame=[0,0,0,0,0,0],
                            selection_vector=[0,0,1,0,0,0],  # compliance en Z
                            wrench=[0,0,0,0,0,0],
                            f_type=2,
                            limits=[0.5, 0.5, 0.3, 0.2, 0.2, 0.2]  # plus doux
                        )
                
                if isinstance(waypoints[0], Joint6DDescriptor):
                    robot_ctr.movej_waypoints(waypoints)
                elif isinstance(waypoints[0], TCP6DDescriptor):
                    robot_ctr.movel_waypoints(waypoints)
                else:
                    ds.log(f"WARNING: Unknown waypoint type for waypoints: {type(waypoints[0])}")
                    raise TypeError(f"Unknown waypoint type: {type(waypoints[0])}")
                
                if FORCE_ENABLE:
                    if motion_type in (MotionType.DRAW, MotionType.APPROACH) and isinstance(robot_ctr, UrScript):
                        ds.log("Deactivating force mode")
                        robot_ctr.force_mode_stop()


class Robot(Stage):
    """
    A class representing the robot in the simulation.
    """
    def __init__(self, datastore: DataStore, robot_ip: str, default_calibration: str = None, multipen: bool = False):
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

        tcp_offset = self.ds.return_tcp_offset(self.default_calibration)
        iscoin.robot_control.set_tcp(tcp_offset)

        motion = self.ds.load_joint_segments()

        if manual_flag:
            force_active = ask_yes_no("Do you want to start force logging? y/n \n")
        else:
            force_active = False

        if force_active:
            force = DataStoreForce_2(iscoin.robot_control)
            force.start_measures()

        try:
            move_simple(iscoin, motion, self.ds, self.multipen)
        except Exception as e:
            self.ds.log(f"Exception with robot: {e}")
            raise
        
        if force_active:
            force.stop_measures()
