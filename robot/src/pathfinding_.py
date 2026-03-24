import pybullet as pb

from src.stage import Stage
from src.logger import DataStore
from src.utils import ask_yes_no
from src.config import *

from duckify_simulation.duckify_sim import DuckifySim

from src.safety import setup_checker
from src.transformation import extract_pybullet_pose
from src.pybullet_helpers import clear_bodies, find_hovers, preview_traces, split_into_runs, validate_surface_points, visualize_validation
from src.computation import assemble_segments, smoothing

class Pathfinding(Stage):
    def __init__(self, datastore: DataStore, default_calibration: Path = None, obstacles: list = OBSTACLE_STLS, verbose: bool = True):
        """
        Initialize the pathfinding stage.

        Parameters
        ----------
        datastore : DataStore
            The data store to use.
        default_calibration : Path, optional
            The path to the default calibration file.
        obstacles : list, optional
            List of obstacle STL files to load.
        side : SideType, optional
            The side for which to find paths.
        verbose : bool, optional
            Whether to display verbose output.
        """
        super().__init__(name="Pathfinding", datastore=datastore)
        self.default_calibration = default_calibration
        self.obstacles = obstacles
        self.verbose = verbose
    
    def run(self, manual_flag: bool=True):
        if not ask_yes_no("Do you want to launch a pathfinding? y/n \n"):
            self.ds.load_joint_segments()
            return
        
        obj2robot = self.ds.load_transformation()
        data = self.ds.load_tcp_segments()
        
        _, tcp_offset = self.ds.load_calibration(self.default_calibration)
        duckify_sim = DuckifySim()
        robot = duckify_sim.robot_control

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
                if not ask_yes_no("Do the trace are correct? y/n \n"):
                    if pb.isConnected(checker.cid):
                        pb.disconnect(checker.cid)
                    raise RuntimeError("The trace are not correct.")

                valid_masks, surface_joints = validate_surface_points(
                    checker, robot, surface_tcps_per_trace, HOMEJ,
                )
                validation_spheres = visualize_validation(checker, surface_tcps_per_trace, valid_masks)

                if not ask_yes_no("Judge and tell if the traces valid ? y/n \n"):
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