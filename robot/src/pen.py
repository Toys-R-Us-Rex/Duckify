import time
from enum import Enum, auto

from src.utils import ask_yes_no
from src.config import *

from URBasic import TCP6D, TCP6DDescriptor
from URBasic import ISCoin

from duckify_simulation.duckify_sim import DuckifySim

class GripperAction(Enum):
    CLOSE = auto()  # Close gripper
    OPEN  = auto()  # Open gripper

class PenState():
    """
    PenState handles to HandE Gripper pen transitions and state.
    ```
    from src.pen import PenState

    home = home_position()
    ps = PenState(home=home, robot=iscoin)

    ps.run_moves(
        ps.change_pen(target_pen_id=0)
    )

    ps.run_moves(
        ps.change_pen(target_pen_id=1)
    )
    ```
    """
    def __init__(self, home: TCP6D, robot: ISCoin|DuckifySim, support_position: TCP6D = None):
        self.home = home
        self.support_position = support_position

        self.active_pen_id = None
        self.robot = robot

    def record_pen_position(self):
        if isinstance(self.robot, DuckifySim):
            self.robot.gripper.open()
            if ask_yes_no("Does it is the first pen support? y/n \n"):
                self.support_position = FIRST_SIMULATION_PEN_SUPPORT
            else:
                self.support_position = SECOND_SIMULATION_PENSUPPORT
            self.support_position = TCP6D.createFromMetersRadians(-0.31030073427776544, -0.12772318658605364, 0.1691221791937419, -3.123526746656135, 0.06494033931935389, 0.0007571664234476744)
            return
        
        self.robot.robot_control.freedrive_mode()

        if not ask_yes_no("Does the pen is in the gripper? (WARNING: Gripper will open) y/n \n"):
            self.robot.gripper.open()

            while not ask_yes_no("Did you place the pen in the gripper? (WARNING: Gripper will close) y/n \n"):
                pass

            self.robot.gripper.close()

        while not ask_yes_no("Are you in the correct position for calibration on the support? y/n \n"):
            pass

        self.support_position = self.robot.robot_control.get_actual_tcp_pose()
            
        print(f"Support position: {self.support_position}")

        while not ask_yes_no("Does the robot is close to the home position? y/n \n"):
            pass

        self.robot.robot_control.end_freedrive_mode()


    def get_pen_by_id(self, pen_id: int):
        """
        This function will upgrade the function "get pen" from Nathan Antonietti to be able to go to a pen base on an id we choose:
        
        The id = 0 will be the pen in the support with waypoint and every id > 0 will be at 50mm from the id 0 in Y axis
        """

        print(f"PEN 0 POS: {self.support_position}")

        to_top_of_pen = TCP6D.createFromMetersRadians(
            self.support_position[0],
            self.support_position[1] - LEGNTH_BETWEEN_PENS * pen_id,
            self.support_position[2] + SECURITY_APPROACH,
            FACING_DOWN[0],
            FACING_DOWN[1],
            FACING_DOWN[2]
        )

        to_pen = TCP6D.createFromMetersRadians(
            self.support_position[0],
            self.support_position[1] - LEGNTH_BETWEEN_PENS * pen_id,
            MINIMAL_DISTANCE,
            FACING_DOWN[0],
            FACING_DOWN[1],
            FACING_DOWN[2]
        )

        side_of_pen = TCP6D.createFromMetersRadians(
            self.support_position[0] + SECURITY_APPROACH,
            self.support_position[1] - LEGNTH_BETWEEN_PENS * pen_id,
            self.support_position[2] + SECURITY_APPROACH,
            FACING_DOWN[0],
            FACING_DOWN[1],
            FACING_DOWN[2]
        )

        return to_top_of_pen, to_pen, side_of_pen

    def return_pen(self):
        move_list = []
        v = 0.2
    
        if self.active_pen_id is None:
            print("No pen to return")
            return move_list

        top_active_pen, to_active_pen, side_of_pen = self.get_pen_by_id(self.active_pen_id)
        waypoints_to_active_pen = [
            TCP6DDescriptor(side_of_pen, v=v),
            TCP6DDescriptor(top_active_pen, v=v),
            TCP6DDescriptor(to_active_pen, v=v)
        ]
        waypoints_move_out_active_pen = [
            TCP6DDescriptor(top_active_pen, v=v),
            TCP6DDescriptor(side_of_pen, v=v)
        ]
 
        move_list.append(waypoints_to_active_pen)
        move_list.append(GripperAction.OPEN)
        move_list.append(waypoints_move_out_active_pen)

        self.active_pen_id = None
        return move_list

    def change_pen(self, target_pen_id: int):
        move_list = []
        v = 0.2
        
        if target_pen_id == self.active_pen_id:
            print(f"Pen {target_pen_id} already in use")
            return move_list

        # return pen to support if one is active
        move_list = self.return_pen()

        # Get target pen position
        top_target_pen, to_target_pen, side_of_pen = self.get_pen_by_id(target_pen_id)

        waypoints_to_target_pen = [
            TCP6DDescriptor(side_of_pen, v=v),
            TCP6DDescriptor(top_target_pen, v=v),
            TCP6DDescriptor(to_target_pen, v=v)
        ]
        
        waypoints_move_out_target_pen = [
            TCP6DDescriptor(top_target_pen, v=v),
            TCP6DDescriptor(side_of_pen, v=v)
        ]

        waypoints_home = [
            TCP6DDescriptor(self.home, v=v),
        ]

        move_list.append(waypoints_to_target_pen)
        move_list.append(GripperAction.CLOSE)
        move_list.append(waypoints_move_out_target_pen)
        move_list.append(waypoints_home)

        # set new active pen
        self.active_pen_id = target_pen_id
        return move_list
    
    def run_moves(self, move_list: list[list[TCP6DDescriptor | GripperAction]]):
        """
        move_list: list[list[TCP6DDescriptor]]
        Usage:
            `run_moves( change_pen(0, 1) )`
            `run_moves( return_pen(1) )`
        """
        for m in move_list:
            if m is GripperAction.CLOSE:
                self.robot.gripper.close()
                time.sleep(1)
            elif m is GripperAction.OPEN:
                self.robot.gripper.open()
                time.sleep(1)
            else:
                self.robot.robot_control.movel_waypoints(m, wait=True)
