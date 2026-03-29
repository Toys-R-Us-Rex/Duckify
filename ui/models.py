from typing import Callable

TCPPoint = tuple[float, float, float, float, float, float]
TCPReader = Callable[[], TCPPoint]
