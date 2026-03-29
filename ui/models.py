from typing import Callable

TCPPoint = tuple[float, float, float, float, float, float]
TCPReader = Callable[[], TCPPoint]
Point3D = tuple[float, float, float]
