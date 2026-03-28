"""

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

from operator import index
from pathlib import Path
import queue
import threading
import time
import csv
import pickle

from src.config import DEFAULT_DATA_DIR, DEFAULT_FORCE_PATH
from src.segment import *
from src.utils import AtoB

from URBasic.iscoin import ISCoin
from URBasic.urScript import UrScript
from duckify_simulation.duckify_sim.duckify_sim import DuckifySim
from duckify_simulation.duckify_sim.robot_control import SimRobotControl


class DataStore:
    """
    A class for storing and managing data logs.
    """
    def __init__(self, data_path: Path=DEFAULT_DATA_DIR, log_file: str="log.log"):
        """
        Initialize the DataStore.

        Parameters
        ----------
        data_path : Path, optional
            The path to the directory where data will be stored.
        log_file : Path, optional
            The name of the log file.
        """
        self.log_path = data_path / log_file
        self.data_path = data_path
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
        self.log_path.touch()
    
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._writer, daemon=True)
        self.running = True
        self.worker.start()

    def __del__(self):
        """
        Cleanup the DataStore.
        """
        self.running = False
        try:
            while self.queue.empty():
                pass
            self.worker.join()
        except Exception:
            pass

    def log_calibration(self, tcps: list[TCP6D], tcp_offset: TCP6D):
        """
        Log the calibration measurements.
        
        Parameters
        ----------
        tcps : list[TCP6D]
            List of TCP points.
        tcp_offset : TCP6D
            The calibrated offset.
        """
        s = "\n"
        for p in range(len(tcps)):
            s += str(tcps[p])
            s += "\n"
        self.log(f"Calibration measure:\n" + s)
        self.log(f"Calibred offset:" + str(tcp_offset))
    
    def log_pen_calibration(self, first_pen_position: TCP6D, second_pen_position: TCP6D):
        """
        Log the pen calibration position.

        Parameters
        ----------
        first_pen_position : TCP6D
            The position of the first pen.
        second_pen_position : TCP6D
            The position of the second pen.
        """
        self.log(f"Pen calibration position: {first_pen_position}")
        self.log(f"Pen calibration position: {second_pen_position}")

    def log_worldtcp(self, pworld: list[TCP6D], tcps: list[TCP6D]):
        """
        Log the world TCP points.
        
        Parameters
        ----------
        pworld : list[TCP6D]
            List of world TCP points.
        tcps : list[TCP6D]
            List of robot TCP points.
        """
        s = "\n"
        for p in range(len(pworld)):
            s += "("
            s += str(pworld[p])
            s += " => "
            s += str(tcps[p])
            s += ")\n"
        self.log(f"Object Calibration (world,robot):\n" + s)

    def log_transformation(self, AtoB: AtoB):
        """
        Log the transformation matrix.
        
        Parameters
        ----------
        AtoB : AtoB
            The transformation matrix.
        """
        self.log(f"Transformation (world => robot):\n" + str(AtoB.T_position) + "\n" + str(AtoB.T_orientation))

    def log_test_position(self, position: TCP6D):
        """
        Log the test position.

        Parameters
        ----------
        position : TCP6D
            The test position.
        """
        self.log(f"Test position: {position}")

    def log(self, message: str):
        """
        Log a message to the log file.
        
        Parameters
        ----------
        message : str
            The message to log.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} - {message}\n"
        self.queue.put(entry)
    
    def _writer(self):
        """
        Background thread that writes logs in order.
        """
        with open(self.log_path, "a", encoding="utf-8") as f:
            while self.running or not self.queue.empty():
                try:
                    entry = self.queue.get(timeout=0.2)
                    f.write(entry + "\n")
                    f.flush()
                except queue.Empty:
                    continue

    # ----------------------------------------------------
    #                SAVE / LOAD HELPER
    # ----------------------------------------------------

    def _indexed_file(self, key: str, index: int) -> Path:
        """
        Get the file path for a indexed file.
        
        Parameters
        ----------
        key : str
            The key for the file.
        index : int
            The index for the file.
            
        Returns
        -------
        Path
            The file path.
        """
        return self.data_path / f"{key}_{index}.pkl"

    def _next_index(self, key: str) -> int:
        """
        Get the next available index for a given key.
        
        Parameters
        ----------
        key : str
            The key for the file.
            
        Returns
        -------
        int
            The next available index.
        """
        # List all matching files in the directory
        files = [p for p in self.data_path.iterdir() if p.name.startswith(f"{key}_")]
        if not files:
            return 0
        # Extract numeric suffixes
        indices = []
        for p in files:
            stem = p.stem
            suffix = stem.split("_")[-1]
            if suffix.isdigit():
                indices.append(int(suffix))
        return max(indices) + 1 if indices else 0
    
    def save_history(self, key: str, obj: dict):
        """
        Save a history entry.

        Parameters
        ----------
        key : str
            The key for the file.
        obj : dict
            The object to save.
        """
        idx = self._next_index(key)
        file_path = self._indexed_file(key, idx)
        with file_path.open("wb") as f:
            pickle.dump(obj, f)
        self.log(f"Saved history entry {idx} for {key} -> {file_path}")

    def load_history_latest(self, key: str) -> dict:
        """
        Load the latest history entry for a given key.

        Parameters
        ----------
        key : str
            The key for the file.

        Returns
        -------
        dict or None
            The loaded object or None if not found.
        """
        idx = self._next_index(key) - 1
        if idx < 0:
            self.log(f"No history found for {key}")
            raise FileNotFoundError(f"History file not found: {key}")
        return self.load_history_index(key, idx)

    def load_history_index(self, key: str, index: int) -> dict:
        """
        Load a history entry for a given key and index.

        Parameters
        ----------
        key : str
            The key for the file.
        index : int
            The index for the file.

        Returns
        -------
        dict or None
            The loaded object or None if not found.
        """
        if index == -1:
            return self.load_history_latest(key)
        file_path = self._indexed_file(key, index)
        if not file_path.exists():
            self.log(f"History file not found: {file_path}")
            raise FileNotFoundError(f"History file not found: {file_path}")
        with file_path.open("rb") as f:
            return pickle.load(f)

    def check_history(self, key: str, index: int) -> bool:
        """
        Check if a history entry exists for a given key and index.

        Parameters
        ----------
        key : str
            The key for the file.
        index : int
            The index for the file.

        Returns
        -------
        bool
            True if the history entry exists, False otherwise.
        """
        if index == -1:
            index = self._next_index(key) - 1
        if index < 0:
            self.log(f"No history found for {key}")
            return False
        file_path = self._indexed_file(key, index)
        self.log(f"Checking history for {key} at index {index}: {file_path}")
        return file_path.exists()


    # ----------------------------------------------------
    #                SAVE / LOAD DATA
    # ----------------------------------------------------

    def save_calibration(self, tcps: list[float], tcp_offset: TCP6D, file_path: Path=None):
        """
        Save calibration data.

        Parameters
        ----------
        tcps : list[float]
            The TCP positions.
        tcp_offset : TCP6D
            The TCP offset.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"tcps": tcps, "tcp_offset": tcp_offset}
        if file_path:
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)
            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved calibration data to file {file_path}")
        else:
            self.save_history("calibration", data)

    def load_calibration(self, file_path: Path=None, index: int=-1) -> tuple[list[float], TCP6D]:
        """
        Load calibration data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        tuple[list[float], TCP6D] or tuple[None, None]
            The loaded TCP positions and offset, or (None, None) if not found.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Calibration data file not found {file_path}")
                raise RuntimeError(f"Calibration data file not found: {file_path}")
            with file_path.open("rb") as f:
                data = pickle.load(f)
            self.log(f"Loaded calibration data from file {file_path}")
        else:
            data = self.load_history_index("calibration", index)
        tcps = data["tcps"]
        tcp_offset = data["tcp_offset"]
        return tcps, tcp_offset

    def check_calibration(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if calibration data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the calibration data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("calibration", index)
    
    def return_tcp_offset(self, default_calibration: Path =None) -> TCP6D:
        """
        Returns the TCP offset based on the available calibration.

        Parameters
        ----------
        default_calibration : Path, optional
            The path to the default calibration file.

        Returns
        -------
        TCP6D
            The TCP offset.
        """
        if not self.check_calibration() and default_calibration is not None:
            _, tcp_offset = self.load_calibration(default_calibration)
        elif self.check_calibration():
            _, tcp_offset = self.load_calibration()
        elif default_calibration is not None:
            _, tcp_offset = self.load_calibration(default_calibration)
        else:
            raise ValueError("No valid calibration found.")
        
        return tcp_offset

    def save_pen_calibration(self, first_pen_position: TCP6D, second_pen_position: TCP6D, file_path: Path=None):
        """
        Save pen calibration data.

        Parameters
        ----------
        first_pen_position : TCP6D
            The first calibrated pen position.
        second_pen_position : TCP6D
            The second calibrated pen position.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"first_pen_position": first_pen_position, "second_pen_position": second_pen_position}
        if file_path:
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)
            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved pen calibration data to file {file_path}")
        else:
            self.save_history("pen_calibration", data)

    def load_pen_calibration(self, file_path: Path=None, index: int=-1) -> tuple[TCP6D, TCP6D]:
        """
        Load pen calibration data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        tuple[TCP6D, TCP6D] or tuple[None, None]
            The loaded pen positions, or (None, None) if not found.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Pen calibration data file not found {file_path}")
                raise RuntimeError(f"Pen calibration data file not found: {file_path}")
            with file_path.open("rb") as f:
                data = pickle.load(f)
            self.log(f"Loaded pen calibration data from file {file_path}")
        else:
            data = self.load_history_index("pen_calibration", index)
        first_pen_position = data["first_pen_position"]
        second_pen_position = data["second_pen_position"]
        return first_pen_position, second_pen_position

    def check_pen_calibration(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if pen calibration data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the pen calibration data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("pen_calibration", index)


    def save_worldtcp(self, pworld: list[float], tcps: list[float], file_path: Path=None):
        """
        Save worldtcp data.

        Parameters
        ----------
        pworld : list[float]
            The world positions.
        tcps : list[float]
            The TCP positions.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"pworld": pworld, "tcps": tcps}
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved worldtcp data to file {file_path}")
        
        else:
            self.save_history("worldtcp", data)

    def load_worldtcp(self, file_path: Path=None, index: int=-1) -> tuple[list[float], list[float]]:
        """
        Load worldtcp data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        tuple[list[float], list[float]] or tuple[None, None]
            The loaded world positions and TCP positions, or (None, None) if not found.
        """
        if file_path:

            if not file_path.exists():
                self.log(f"Worldtcp data file not found {file_path}")
                raise RuntimeError(f"Worldtcp data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            self.log(f"Loaded worldtcp data from file {file_path}")
        else:
            data = self.load_history_index("worldtcp", index)
        pworld = data["pworld"]
        tcps = data["tcps"]
        return pworld, tcps

    def check_worldtcp(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if worldtcp data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the worldtcp data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("worldtcp", index)


    def save_transformation(self, obj_to_robot: AtoB, file_path: Path=None):
        """
        Save transformation data.

        Parameters
        ----------
        obj_to_robot : AtoB
            The transformation object.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"T_position": obj_to_robot.T_position, "T_normal": obj_to_robot.T_orientation}
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved transformation data to file {file_path}")
        
        else:
            self.save_history("transformation", data)

    def load_transformation(self, file_path: Path=None, index: int=-1) -> AtoB:
        """
        Load transformation data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        AtoB
            The loaded transformation object.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Transformation data file not found {file_path}")
                raise RuntimeError(f"Transformation data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            self.log(f"Loaded transformation data from file {file_path}")
        else:
            data = self.load_history_index("transformation", index)
    
        T_position = data["T_position"]
        T_normal = data["T_normal"]
        return AtoB(T_position, T_normal)
    
    def check_transformation(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if transformation data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the transformation data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("transformation", index)


    def save_waypoints(self, waypoints: list[TCP6D|Joint6D], file_path: Path=None):
        """
        Save waypoints data.

        Parameters
        ----------
        waypoints : list[TCP6D|Joint6D]
            The list of waypoints to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"waypoints": waypoints}
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved waypoints data to file {file_path}")
        
        else:
            self.save_history("waypoints", data)

    def load_waypoints(self, file_path: Path=None, index: int=-1) -> list[TCP6D|Joint6D]:
        """
        Load waypoints data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        list[TCP6D|Joint6D]
            The loaded waypoints.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Waypoints data file not found {file_path}")
                raise RuntimeError(f"Waypoints data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            self.log(f"Loaded waypoints data from file {file_path}")
        else:
            data = self.load_history_index("waypoints", index)

        waypoints = data["waypoints"]
        return waypoints

    def check_waypoints(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if waypoints data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the waypoints data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("waypoints", index)


    def save_tcp_segments(self, data: dict, file_path: Path=None):
        """
        Save TCP segments data.

        Parameters
        ----------
        data : dict
            The data to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved TCP segments data to file {file_path}")
        
        else:
            self.save_history("tcp_segments", data)

    def load_tcp_segments(self, file_path: Path=None, index: int=-1) -> dict:
        """
        Load TCP segments data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        dict
            The loaded TCP segments data.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"TCP segments data file not found {file_path}")
                raise RuntimeError(f"TCP segments data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            self.log(f"Loaded TCP segments data from file {file_path}")
        else:
            data = self.load_history_index("tcp_segments", index)
            
        return data

    def check_tcp_segments(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if TCP segments data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the TCP segments data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("tcp_segments", index)


    def save_joint_segments(self, segments: list[JointSegment], file_path: Path=None):
        """
        Save Joint segments data.

        Parameters
        ----------
        segments : list[JointSegment]
            The list of Joint segments to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"segments": segments}
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved Joint segments data to file {file_path}")
        
        else:
            self.save_history("joint_segments", data)

    def load_joint_segments(self, file_path: Path=None, index: int=-1) -> list[JointSegment]:
        """
        Load Joint segments data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        list[JointSegment]
            The loaded Joint segments.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Joint segments data file not found {file_path}")
                raise RuntimeError(f"Joint segments data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            segments = data["segments"]
            self.log(f"Loaded Joint segments data from file {file_path}")
        else:
            data = self.load_history_index("joint_segments", index)

        segments = data["segments"]
        return segments

    def check_joint_segments(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if Joint segments data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the Joint segments data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("joint_segments", index)


    def save_trace_segments(self, data: dict, file_path: Path=None):
        """
        Save Trace segments data.

        Parameters
        ----------
        data : dict
            The data to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved Trace segments data to file {file_path}")
        
        else:
            self.save_history("trace_segments", data)

    def load_trace_segments(self, file_path: Path=None, index: int=-1) -> dict:
        """
        Load Trace segments data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        dict
            The loaded Trace segments data.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Trace segments data file not found {file_path}")
                raise RuntimeError(f"Trace segments data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            self.log(f"Loaded Trace segments data from file {file_path}")
        else:
            data = self.load_history_index("trace_segments", index)
            
        return data

    def check_trace_segments(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if Trace segments data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the Trace segments data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("trace_segments", index)


    def save_run_segments(self, segments: list[RunSegment], file_path: Path=None):
        """
        Save Run segments data.

        Parameters
        ----------
        segments : list[RunSegment]
            The list of Run segments to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"segments": segments}
        if file_path:
            # Ensure folder exists
            folder = file_path.parent
            if not folder.exists():
                self.log(f"Create folder {folder}")
                folder.mkdir(parents=True, exist_ok=True)

            with file_path.open("wb") as f:
                pickle.dump(data, f)
            self.log(f"Saved Run segments data to file {file_path}")
        
        else:
            self.save_history("run_segments", data)

    def load_run_segments(self, file_path: Path=None, index: int=-1) -> list[RunSegment]:
        """
        Load Run segments data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        list[RunSegment]
            The loaded Run segments.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Run segments data file not found {file_path}")
                raise RuntimeError(f"Run segments data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
    
            segments = data["segments"]
            self.log(f"Loaded Run segments data from file {file_path}")
        else:
            data = self.load_history_index("run_segments", index)
            
        segments = data["segments"]
        return segments

    def check_run_segments(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if Run segments data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the Run segments data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("run_segments", index)

    def save_test_position(self, position: TCP6D, file_path: Path = None):
        """
        Save the test position.

        Parameters
        ----------
        position : TCP6D
            The test position to save.
        file_path : Path, optional
            The file path to save the data to.
        """
        data = {"position": position}
        if file_path:
            with file_path.open("wb") as f:
                pickle.dump(data, f)
        else:
            self.save_history("test_position", data)

    def load_test_position(self, file_path: Path=None, index: int=-1) -> TCP6D:
        """
        Load the test position.

        Parameters
        ----------
        file_path : Path, optional
            The file path to load the data from.
        index : int, optional
            The index of the history entry to load.

        Returns
        -------
        TCP6D
            The loaded test position.
        """
        if file_path:
            if not file_path.exists():
                self.log(f"Test position data file not found {file_path}")
                raise RuntimeError(f"Test position data file not found: {file_path}")

            with file_path.open("rb") as f:
                data = pickle.load(f)
        else:
            data = self.load_history_index("test_position", index)

        position = data["position"]
        self.log(f"Loaded test position from file {file_path}")
        return position

    def check_test_position(self, file_path: Path=None, index: int=-1) -> bool:
        """
        Check if Test position data exists.

        Parameters
        ----------
        file_path : Path, optional
            The file path to check.
        index : int, optional
            The index of the history entry to check.

        Returns
        -------
        bool
            True if the Test position data exists, False otherwise.
        """
        if file_path:
            return file_path.exists()
        else:
            return self.check_history("test_position", index)

class DataStoreForce_2:
    def __init__(self, robot_control: UrScript | SimRobotControl, file_path: Path = None):
        self.robot_ctr = robot_control
        self.thread = None
        self.stop_thread = None
        self.file_path = file_path
        self._lock = threading.Lock()

    def __del__(self):
        try:
            self.stop_measures()
        except Exception:
            pass

    def start_measures(self, file_path: Path = DEFAULT_FORCE_PATH):
        with self._lock:
            if self.thread is not None and self.thread.is_alive():
                raise RuntimeError(
                    f"Logging already running, writing to: {self.file_path}"
                )

            if not isinstance(file_path, Path):
                raise TypeError("file_path must be a pathlib.Path")

            self.stop_thread = threading.Event()
            self.file_path = file_path

            self.thread = threading.Thread(
                target=self._measures,
                daemon=True
            )
            self.thread.start()

    def stop_measures(self):
        with self._lock:
            if self.stop_thread is None:
                return  # Already stopped or never started

            self.stop_thread.set()

            if self.thread is not None and self.thread.is_alive():
                self.thread.join(timeout=2)

            # Reset state
            self.thread = None
            self.stop_thread = None

    def _measures(self):
        time_start = time.time()

        with self.file_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "Fx", "Fy", "Fz", "Tx", "Ty", "Tz", "Wrench", "Magnitude"])

            while not self.stop_thread.is_set():
                tcp = self.robot_ctr.get_actual_tcp_pose(wait=False)
                wrench = self.robot_ctr.get_tcp_force(wait=False)
                magnitude = self.robot_ctr.force(wait=False)
                timestamp = time.time() - time_start

                row = [timestamp] + tcp.toList() + [wrench] + [magnitude]
                writer.writerow(row)
                f.flush()

                time.sleep(0.1)

class DataStoreForce:
    """
    A class for managing force logging data.
    """
    def __init__(self, robot: ISCoin | DuckifySim):
        """
        Initialize the DataStoreForce.

        Parameters
        ----------
        robot : ISCoin | DuckifySim
            The robot instance to log force data for.
        """
        self.robot = robot
        self.stop_event = None
        self.t = None
        self.current_file_path = None

    def start_logging(self, file_path: Path=DEFAULT_FORCE_PATH):
        """
        Start logging force data.

        Parameters
        ----------
        file_path : Path, optional
            The file path to save the force data to.
        """
        # Prevent starting twice
        if self.t is not None and self.t.is_alive():
            raise RuntimeError(
                f"Logging already running, writing to: {self.current_file_path}"
            )

        # Create a new stop event
        self.stop_event = threading.Event()
        self.current_file_path = file_path

        # Start thread
        self.t = threading.Thread(
            target=self._log_force,
            args=(self.robot, self.stop_event, file_path),
            daemon=True
        )
        self.t.start()

    def stop_logging(self):
        """
        Stop logging force data.
        """
        if self.stop_event is None:
            return  # Nothing to stop

        self.stop_event.set()
        if self.t is not None:
            self.t.join()

        # Reset state
        self.t = None
        self.stop_event = None
        self.current_file_path = None

    def _log_force(self, robot: ISCoin | DuckifySim, stop_event: threading.Event, file_path: Path):
        """
        Log force data.
        
        Parameters
        ----------
        robot : ISCoin | DuckifySim
            The robot instance to log force data for.
        stop_event : threading.Event
            The event to signal when to stop logging.
        file_path : Path
            The file path to save the force data to.
        """
        time_start = time.time()
        robot_ctr = robot.robot_control

        # Open file once and keep it open
        with file_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "Fx", "Fy", "Fz", "Tx", "Ty", "Tz", "Force"])

            while not stop_event.is_set():
                tcp = robot_ctr.get_actual_tcp_pose(wait=False)
                wrench = robot_ctr.get_tcp_force(wait=False)
                magnitude = robot_ctr.force(wait=False)
                timestamp = time.time() - time_start

                row = [timestamp] + tcp.toList() + wrench + [magnitude]
                writer.writerow(row)
                f.flush()  # ensure data is physically written

                time.sleep(0.01)  # 100 Hz logging
