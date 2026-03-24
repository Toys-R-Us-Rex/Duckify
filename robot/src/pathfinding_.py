import pybullet as pb

from src.stage import Stage
from src.logger import DataStore
from src.utils import ask_yes_no
from src.config import *

from duckify_simulation.duckify_sim.robot_control import SimRobotControl

from src.safety import setup_checker
from src.transformation import extract_pybullet_pose
from src.pybullet_helpers import clear_bodies, find_hovers, preview_traces, split_into_runs, validate_surface_points, visualize_validation
from src.computation import assemble_segments, smoothing

class Pathfinding(Stage):
    def __init__(self, datastore: DataStore, default_calibration: Path = None, json_path: Path = None, obstacles: list = OBSTACLE_STLS, verbose: bool = True):
        """
        Initialize the pathfinding stage.

        Parameters
        ----------
        datastore : DataStore
            The data store to use.
        default_calibration : Path, optional
            The path to the default calibration file.
        json_path : Path, optional
            The path to the JSON object file.
        obstacles : list, optional
            List of obstacle STL files to load.
        side : SideType, optional
            The side for which to find paths.
        verbose : bool, optional
            Whether to display verbose output.
        """
        super().__init__(name="Pathfinding", datastore=datastore)
        self.default_calibration = default_calibration
        self.json_path = json_path
        self.obstacles = obstacles
        self.verbose = verbose
    
    def run(self, manual_flag: bool=True):
        """
        Run the pathfinding stage.

        Parameters
        ----------
        manual_flag : bool
            Whether to run the stage in manual mode.
        """

        
        if manual_flag:
            if not ask_yes_no("Do you want to launch a pathfinding? y/n \n"):
                self.ds.load_joint_segments()
                return
        else:
            self.ds.log("Run in automatic mode.")
            if self.ds.check_joint_segments():
                if self.json_path.exists():
                    self.ds.log("Existing joint path segments overridden.")
                else:
                    self.ds.log("Using existing joint path segments.")
                    return
            elif not self.ds.check_tcp_segments():
                raise RuntimeError("No existing converted TCP segments found.")
        
        obj2robot = self.ds.load_transformation()
        data = self.ds.load_tcp_segments()
        
        _, tcp_offset = self.ds.load_calibration(self.default_calibration)

        robot = SimRobotControl()
        robot.set_tcp(tcp_offset)

        pos, quat, scale = extract_pybullet_pose(obj2robot)
        for obs in self.obstacles:
            if 'position' not in obs:
                obs['position'] = pos
                obs['orientation'] = quat

        checker = setup_checker(self.obstacles, gui=self.verbose)
        pb.resetDebugVisualizerCamera(
            cameraDistance=0.6, cameraYaw=45, cameraPitch=-30,
            cameraTargetPosition=pos, physicsClientId=checker.cid,
        )

        checker.set_joint_angles(HOMEJ.toList())
        
        for k, d in data.items():
            for k, trace in d.items():
                surface_tcps_per_trace = [t.waypoints for t in trace]
                
                preview_traces(checker, surface_tcps_per_trace)
                if not ask_yes_no("Do the trace are correct? y/n \n") and manual_flag:
                    if pb.isConnected(checker.cid):
                        pb.disconnect(checker.cid)
                    raise RuntimeError("The trace are not correct.")

                valid_masks, surface_joints = validate_surface_points(
                    checker, robot, surface_tcps_per_trace, HOMEJ,
                )
                validation_spheres = visualize_validation(checker, surface_tcps_per_trace, valid_masks)

                if not ask_yes_no("Judge and tell if the traces valid ? y/n \n") and manual_flag:
                    if pb.isConnected(checker.cid):
                        pb.disconnect(checker.cid)
                    raise RuntimeError("The trace are not correct.")
                
                clear_bodies(checker.cid, validation_spheres)

                
                runs_per_trace = split_into_runs(valid_masks)
                validated_runs = find_hovers(checker, robot, surface_tcps_per_trace, runs_per_trace, surface_joints)
                segments = assemble_segments(robot, checker, validated_runs, surface_joints, HOMEJ)
                smoothing(robot, checker, segments, HOMEJ)

                self.ds.save_joint_segments(segments)
                
                if pb.isConnected(checker.cid):
                    pb.disconnect(checker.cid)
                    print("PyBullet disconnected")

                return
        
                             
    def fallback():
        raise NotImplementedError("Pathfinding is not implemented yet.")