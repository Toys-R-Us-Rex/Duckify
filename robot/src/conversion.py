"""
Conversion Stage Module

This module provides functionality for converting trace segments to TCP segments.

MIT License

Copyright (c) 2026 Mariéthoz Cédric

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author:     Mariéthoz Cédric, with assistance from Copilot AI (Microsoft)
Course:     HES-SO Valais-Wallis, Engineering Track 304
"""

from pathlib import Path

from URBasic.waypoint6d import TCP6D

from src.logger import DataStore
from src.stage import Stage
from src.utils import ask_yes_no
from src.segment import SideType, TCPSegment, MotionType
from src.config import DRAW_A, DRAW_V


class Conversion(Stage):
    """
    A stage for converting trace segments to TCP segments.
    """
    def __init__(self, datastore: DataStore, json_path: Path = None):
        """
        Initialize the Conversion stage.

        Parameters
        ----------
        datastore : DataStore
            The data store instance.
        json_path : Path
            The path to the JSON object file.
        """
        super().__init__(name="Conversion", datastore=datastore)
        self.json_path = json_path

    def run(self, manual_flag: bool=True):
        """
        Run the conversion stage.

        Parameters
        ----------
        manual_flag : bool
            Whether to run the stage in manual mode.
        """
        if manual_flag:
            if ask_yes_no("Do you have a conversion already saved? y/n\n"):
                segments = self.ds.load_tcp_segments()
                return

            if not ask_yes_no("Do you want to  convert the traces? y/n \n"):
                self.ds.log("You chose not to convert the traces")
                if not self.ds.check_tcp_segments():
                    raise RuntimeError("You don't have any converted TCP segments.")
        else:
            self.ds.log("Run in automatic mode.")
            if self.ds.check_tcp_segments():
                if self.json_path.exists():
                    self.ds.log("Existing converted TCP segments overridden.")
                else:
                    self.ds.log("Using existing converted TCP segments.")
                    return
            elif self.ds.check_trace_segments():
                raise RuntimeError("No existing trace segments found.")


        objtorobot = self.ds.load_transformation()
        data = self.ds.load_trace_segments()
        conversion = {}
        for s, d in data.items():
            conversion[s] = {}
            for c, trace in d.items():
                segments = []
                for t in trace:
                    color = t.color
                    side = t.side
                    waypoints = t.waypoints
                    segments.append(
                        TCPSegment(
                            color=color,
                            side=side,
                            
                            waypoints=[TCP6D.createFromMetersRadians( *objtorobot(p)) for p in waypoints],
                            motion_type=MotionType.DRAW,
                            v=DRAW_V,
                            a=DRAW_A
                        )
                    )
                conversion[s][c] = segments
        
        self.ds.save_tcp_segments(conversion)
    
    
    def fallback(self):
        """
        Fallback method for the conversion stage.
        """
        raise NotImplementedError("Conversion fallback not implemented yet.")