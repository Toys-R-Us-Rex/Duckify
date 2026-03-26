import argparse
from pathlib import Path
import time

from src.logger import DataStore
from src.segment import SideType
from src.stage import Stage, run_stage

from src.config import DEFAULT_JSON_SOCLE, ROBOT_IP, DEFAULT_JSON_OBJECT, DEFAULT_CALIBRATION_PATH, OUTPUT_DIR

from src.calibration import Calibration
from src.transformation import Transformation
from src.filter import Filter
from src.conversion import Conversion
from src.pathfinding import Pathfinding
from src.gazebo import Gazebo
from src.robot import Robot


def maybe_run(stage_name: str, skip_flag: bool, stage_obj: Stage, on_error: str, dry_run: bool, manual_flag: bool, data_store: DataStore):
    if skip_flag:
        print(f"--- {stage_name:<20} (skipped)")
        if not dry_run:
            data_store.log(f"--- {stage_name:<20} (skipped) ---")
        return
    if dry_run:
        print(f"RUN {stage_name:<20} (would run)")
        return
    print(f">>> {stage_name:<20} (running)")
    data_store.log(f">>> {stage_name:<20} (running) >>>")
    run_stage(stage_obj, on_error, manual_flag)

def main(
    robot_ip: str,
    output_dir: str|Path,
    json_object: str|Path,
    json_socle: str|Path,

    side: SideType,

    default_calibration: str|Path = DEFAULT_CALIBRATION_PATH,

    multipen: bool = False,

    x_position: float = 0.0,
    y_position: float = 0.0,
    z_position: float = 0.0,
    turn_degree: float = 0.0,

    manual: bool = False,
    skip_calibration: bool = False,
    skip_transformation: bool = False,
    skip_filter: bool = False,
    skip_conversion: bool = False,
    skip_pathfinding: bool = False,
    skip_gazebo: bool = False,
    skip_robot: bool = False,

    dry_run: bool = False,
):
    day = time.strftime("%Y%m%d")
    output_dir = Path(output_dir)
    ds = DataStore(output_dir / day)
    ds.log("Pipeline started")

    # Stage table: (name, skip_flag, builder, on_error)
    pipeline = [
        ("Calibration",    skip_calibration,    Calibration(ds, robot_ip, Path(default_calibration), multipen), "continue"),
        ("Transformation", skip_transformation, Transformation(ds, robot_ip, Path(json_socle),
                                    custom_transformation=[x_position, y_position, z_position, turn_degree]),   "fallback"),
        ("Filter",         skip_filter,         Filter(ds, Path(json_object), multipen),           "stop"),
        ("Conversion",     skip_conversion,     Conversion(ds, Path(json_object)),                                                 "stop"),
        ("Pathfinding",    skip_pathfinding,    Pathfinding(ds, Path(default_calibration)),                     "stop"),
        ("Gazebo",         skip_gazebo,         Gazebo(ds, Path(default_calibration), multipen),                "stop"),
        ("Robot",          skip_robot,          Robot(ds, robot_ip, side, Path(default_calibration), multipen), "continue"),
    ]

    for stage in pipeline:
        maybe_run(*stage, dry_run=dry_run, manual_flag=manual, data_store=ds)

    ds.log("Pipeline finished")

    ds.log("Pipeline finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
        "Run the robot pipeline;\n"
        "The pipeline consists of several stages: calibration, transformation, filter, conversion, pathfinding, gazebo, and robot.\n\n"
        "Calibration     will allow the user to calibrate the robot's TCP (Tool Center Point).\n"
        "Transformation  will compute the transformation matrix to convert the object coordinates to the robot's coordinate system.\n"
        "Filter          will apply filters to the data; Currently, determine left and right sides.\n"
        "Conversion      will convert the object coordinates to the robot's coordinate system.\n"
        "Pathfinding     will generate a path for the robot to follow, given the robot motion in joint space.\n"
        "Gazebo          will simulate the robot in a Gazebo environment (make sure the environment is running, see project README.md).\n"
        "Robot           will control the actual robot and execute the planned path."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Overrides
    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIR / "save_data",
        help="The output directory for the pipeline results"
    )
    parser.add_argument(
        "--socle",
        type=str,
        default=DEFAULT_JSON_SOCLE,
        metavar="<FILE>",
        help="Override the default socle JSON file"
    )
    parser.add_argument(
        "--calibration",
        type=str,
        default=DEFAULT_CALIBRATION_PATH,
        metavar="<FILE>",
        help="Override the default calibration JSON file"
    )
    parser.add_argument(
        "--multipen",
        action="store_true",
        help="Use multiple pen"
    )

    # Parameters
    parser.add_argument(
        "--robot-ip",
        type=str,
        default=ROBOT_IP,
        metavar="<IP>",
        help="The robot IP address"
    )

    parser.add_argument(
        "--side",
        type=str,
        choices=["left", "right"],
        default="right"
    )

    parser.add_argument(
        "--object",
        type=str,
        default=DEFAULT_JSON_OBJECT,
        metavar="<FILE>",
        help="The JSON object file: The drawing path"
    )

    parser.add_argument(
        "--turn-degree",
        type=float,
        default=0.0,
        metavar="<DEGREE>",
        help="The turning degree of the object coordinates"
    )

    parser.add_argument(
        "--x-position",
        type=float,
        default=None,
        metavar="<X>",
        help="The x-position of the object coordinates"
    )

    parser.add_argument(
        "--y-position",
        type=float,
        default=None,
        metavar="<Y>",
        help="The y-position of the object coordinates"
    )

    parser.add_argument(
        "--z-position",
        type=float,
        default=None,
        metavar="<Z>",
        help="The z-position of the object coordinates"
    )

    parser.add_argument(
        "--manual",
        action="store_true",
        help="Run the pipeline in manual mode"
    )

    # Skipper
    parser.add_argument(
        "--skip",
        type=str,
        default="ctfv",
        metavar="ctfv",
        help=(
            "Stages to skip: \n"
            "c=calibration, t=transformation, f=filter, "
            "v=conversion, p=pathfinding, g=gazebo, r=robot, "
            "a=all except gazebo + robot, "
            "n=none"
        )
    )

    # Helper
    parser.add_argument(
        "--list-stages",
        action="store_true",
        help="List all available pipeline stages and exit"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which stages would run without executing them"
    )

    args = parser.parse_args()

    # Convert side string to your enum
    side_enum = SideType.RIGHT if args.side == "right" else SideType.LEFT

    # Check skipped
    skip = args.skip
    if "a" in skip:
        skip_calibration    = True
        skip_transformation = True
        skip_filter         = True
        skip_conversion     = True
        skip_pathfinding    = True
        skip_gazebo         = False
        skip_robot          = False
    else:
        skip_calibration    = "c" in skip
        skip_transformation = "t" in skip
        skip_filter         = "f" in skip
        skip_conversion     = "v" in skip
        skip_pathfinding    = "p" in skip
        skip_gazebo         = "g" in skip
        skip_robot          = "r" in skip

    if args.list_stages:
        print("Available stages:")
        print("  c  Calibration")
        print("  t  Transformation")
        print("  f  Filter")
        print("  v  Conversion")
        print("  p  Pathfinding")
        print("  g  Gazebo")
        print("  r  Robot")
        exit(0)
    
    main(
        robot_ip=args.robot_ip,
        output_dir=args.output_dir,
        json_object=args.object,
        json_socle=args.socle,
        
        side=side_enum,
        default_calibration=args.calibration,

        manual=args.manual,
        multipen=args.multipen,

        x_position=args.x_position,
        y_position=args.y_position,
        z_position=args.z_position,
        turn_degree=args.turn_degree,


        # Skip
        skip_calibration=skip_calibration,
        skip_transformation=skip_transformation,
        skip_filter=skip_filter,
        skip_conversion=skip_conversion,
        skip_pathfinding=skip_pathfinding,
        skip_gazebo=skip_gazebo,
        skip_robot=skip_robot,

        dry_run=args.dry_run
    )


