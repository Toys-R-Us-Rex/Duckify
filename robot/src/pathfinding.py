import pybullet as pb

from src.stage import Stage
from src.logger import DataStore
from src.utils import ask_yes_no
from src.config import *

from duckify_simulation.duckify_sim.robot_control import SimRobotControl

from src.safety import setup_checker
from src.transformation import extract_pybullet_pose
from src.pybullet_helpers import clear_bodies, find_hovers, preview_traces, split_into_runs, validate_surface_points, visualize_validation, visualize_runs, visualize_plan, animate_plan
from src.computation import assemble_segments, plan_travels, smoothing, plot_joint_plan

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
        joint_data = {}
        for s, d in data.items():
            joint_data[s] = {}
            for c, traces in d.items():
                self.ds.log(f"Processing {s} - {c}")
                joint_data[s][c] = []
                surface_tcps_per_trace = [t.waypoints for t in traces]
                
                preview_traces(checker, surface_tcps_per_trace)
                if not ask_yes_no("Do the trace are correct? y/n \n") and manual_flag:
                    if pb.isConnected(checker.cid):
                        pb.disconnect(checker.cid)
                    raise RuntimeError("The trace are not correct.")

                pb.removeAllUserDebugItems(physicsClientId=checker.cid)

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
                run_spheres = visualize_runs(checker, surface_tcps_per_trace, runs_per_trace)

                validated_runs = find_hovers(checker, robot, surface_tcps_per_trace, runs_per_trace, surface_joints, home=HOMEJ)
                segments = assemble_segments(robot, checker, validated_runs, surface_joints, HOMEJ, surface_tcps_per_trace)
                smoothing(robot, checker, segments, HOMEJ)
                plan_travels(checker, segments)


                input("Press Enter to see visualization...")

                clear_bodies(checker.cid, run_spheres)
                pb.removeAllUserDebugItems(physicsClientId=checker.cid)

                visualize_plan(checker, robot, segments, debug=True)
                animate_plan(checker, segments, delay=0.1)


                input("Press Enter to continue after visualization...")
                joint_data[s][c].append(segments)
                plot_joint_plan(segments, self.ds.data_path / "joint_plan.png")

        if pb.isConnected(checker.cid):
            pb.disconnect(checker.cid)
            print("PyBullet disconnected")

        self.ds.save_joint_segments(joint_data)
        
                             
    def fallback():
        raise NotImplementedError("Pathfinding is not implemented yet.")