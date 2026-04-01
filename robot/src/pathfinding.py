import numpy as np
import pybullet as pb

from src.stage import Stage
from src.logger import DataStore
from src.utils import *
from src.config import *
from src.kinematics import pose_to_matrix

from src.safety import setup_checker
from src.transformation import extract_pybullet_pose
from src.pybullet_helpers import clear_bodies, display_transformation_points, find_hovers, preview_traces, split_into_runs, validate_surface_points, visualize_validation, visualize_runs, visualize_plan, animate_plan
from src.computation import assemble_segments, plan_travels, smoothing, plot_joint_plan, plot_smoothing_comparison, hotfix_j6_correction, add_angle_continuity

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
        """
        Run the full pathfinding pipeline.

        Loads the transformation and TCP segments, sets up the pybullet
        collision checker, then for each side and color: validates the
        surface points, finds valid runs, assembles segments, runs
        smoothing, plans the travel paths and saves everything.

        If manual_flag is True the user gets asked to confirm at each
        step (trace placement, validation, visualization).

        Parameters
        ----------
        manual_flag : bool, optional
            Whether to ask for user confirmation at each step. Default True.
        """
        if not ask_yes_no("Do you want to launch a pathfinding? y/n \n"):
            if not self.ds.check_joint_segments():
                raise ValueError("No joint segments found.")
            return
        
        obj2robot = self.ds.load_transformation()
        data = self.ds.load_tcp_segments()
        
        tcp_offset = self.ds.return_tcp_offset(self.default_calibration)
        tcp_offset_mat = pose_to_matrix(tcp_offset)

        position, quat, scale = extract_pybullet_pose(obj2robot)
        checker = setup_checker(self.obstacles, obj_position=position, obj_orientation=quat, gui=self.verbose)
        checker.set_joint_angles(HOMEJ.toList())

        display_transformation_points(checker, obj2robot, self.ds, DEFAULT_JSON_SOCLE)

        joint_data = {}
        is_flipped = False

        for side, colors in data.items():
            if manual_flag and not ask_yes_no(f"Draw on side {side}? y/n \n"):
                continue

            pb.removeAllUserDebugItems(physicsClientId=checker.cid)

            workspace_id = checker.obstacle_ids[1] if len(checker.obstacle_ids) > 1 else None
            exclude = {workspace_id} if workspace_id else None
            if side == 'right' and not is_flipped:
                checker.flip_obstacles_z(exclude_ids=exclude)
                is_flipped = True
            elif side == 'left' and is_flipped:
                checker.flip_obstacles_z(exclude_ids=exclude)
                is_flipped = False

            joint_data[side] = {}
            for color, traces in colors.items():
                print(f"Processing {side} - {color}")

                self.ds.log(f"Processing {side} - {color}")
                trace_waypoints = []
                default_normals = []
                for t in traces:
                    trace_waypoints.append(t.waypoints)
                    default_normals.append(t.default_normals)

                preview_traces(checker, trace_waypoints)
                if manual_flag:
                    if not ask_yes_no("Are the traces correctly placed ? y/n \n"):
                        if pb.isConnected(checker.cid):
                            pb.disconnect(checker.cid)
                        raise RuntimeError("The trace are not correctly placed")
                pb.removeAllUserDebugItems(physicsClientId=checker.cid)

                valid_masks, surface_joints = validate_surface_points(
                    checker, tcp_offset_mat, trace_waypoints, HOMEJ,
                )
                validation_spheres = visualize_validation(checker, trace_waypoints, valid_masks)

                if manual_flag:
                    if not ask_yes_no("Judge and tell if the traces valid ? y/n \n"):
                        if pb.isConnected(checker.cid):
                            pb.disconnect(checker.cid)
                        raise RuntimeError("The trace are not correct.")

                clear_bodies(checker.cid, validation_spheres)

                runs_per_trace = split_into_runs(valid_masks)
                run_spheres = visualize_runs(checker, trace_waypoints, runs_per_trace)
                validated_runs = find_hovers(checker, tcp_offset_mat, trace_waypoints, runs_per_trace, surface_joints, home=HOMEJ)

                segments = assemble_segments(tcp_offset_mat, checker, validated_runs, surface_joints, HOMEJ, trace_waypoints, default_normals)

                before_waypoints = smoothing(tcp_offset_mat, checker, segments, HOMEJ)

                smoothing_plot_index = 0
                while (self.ds.data_path / f"smoothing_{smoothing_plot_index}.png").exists():
                    smoothing_plot_index += 1
                plot_smoothing_comparison(segments, before_waypoints, self.ds.data_path / f"smoothing_{smoothing_plot_index}.png")

                plan_travels(checker, segments)
                add_angle_continuity(segments)

                segments = hotfix_j6_correction(segments)

                if manual_flag:
                    input("Press Enter to see visualization...")
                    clear_bodies(checker.cid, run_spheres)
                    pb.removeAllUserDebugItems(physicsClientId=checker.cid)
                    visualize_plan(checker, tcp_offset_mat, segments, debug=True)

                    # animate_plan(checker, segments, delay=0.1)
                    input("Press Enter to continue after visualization...")

                joint_data[side][color] = segments
                plot_index = 0
                while (self.ds.data_path / f"joint_plan_{plot_index}.png").exists():
                    plot_index += 1
                plot_joint_plan(segments, self.ds.data_path / f"joint_plan_{plot_index}.png")

        if pb.isConnected(checker.cid):
            pb.disconnect(checker.cid)
            print("PyBullet disconnected")

        self.ds.save_joint_segments(joint_data)
        
                             
    def fallback(self):
        """Not implemented, just raises an error."""
        raise NotImplementedError("Pathfinding is not implemented yet.")