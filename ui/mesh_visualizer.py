from pathlib import Path

import numpy as np
import trimesh
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from trimesh import Trimesh


class MeshVisualizer(QOpenGLWidget):
    def __init__(self, parent) -> None:
        QOpenGLWidget.__init__(self, parent)

        self.loaded: bool = False
        self.altitude: float = 0.0
        self.azimuth: float = 0.0

    def set_altitude(self, altitude: float):
        self.altitude = altitude
        self.update()

    def set_azimuth(self, azimuth: float):
        self.azimuth = azimuth
        self.update()

    def load_model(self, path: Path):
        self.makeCurrent()
        if self.loaded:
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])
            glDeleteBuffers(1, [self.ebo])

        mesh: Trimesh = trimesh.load_mesh(path)

        mesh.vertices -= mesh.bounding_box.centroid
        scale = np.max(np.linalg.norm(mesh.vertices, axis=1))
        if scale > 0:
            mesh.vertices /= scale

        vertices = mesh.vertices.astype(np.float32)
        faces = mesh.faces.astype(np.uint32)
        normals = mesh.vertex_normals.astype(np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        vertex_data = np.hstack([vertices, normals]).astype(np.float32)
        stride = vertex_data.shape[1] * vertex_data.itemsize

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, stride, ctypes.c_void_p(0))

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, stride, ctypes.c_void_p(12))

        glBindVertexArray(0)

        self.num_indices = faces.size

        self.loaded = True

        self.update()

    def paintGL(self) -> None:
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        if not self.loaded:
            return

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.0)

        glRotatef(self.altitude, 1.0, 0.0, 0.0)
        glRotatef(self.azimuth, 0.0, 1.0, 0.0)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.num_indices, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 4.0, 3.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.15, 0.15, 0.15, 1.0])

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, 4 / 3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / max(h, 1), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
