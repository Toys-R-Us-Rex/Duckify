from pathlib import Path

import numpy as np
import trimesh
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from trimesh import Trimesh
from trimesh.visual import TextureVisuals


class MeshVisualizer(QOpenGLWidget):
    def __init__(self, parent) -> None:
        QOpenGLWidget.__init__(self, parent)

        self.mesh_loaded: bool = False
        self.has_texture: bool = False
        self.texture_loaded: bool = False
        self.texture_id: int = 0
        self.altitude: float = 0.0
        self.azimuth: float = 0.0
        
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.num_indices: int = 0

    def set_altitude(self, altitude: float):
        self.altitude = altitude
        self.update()

    def set_azimuth(self, azimuth: float):
        self.azimuth = azimuth
        self.update()

    def load_model(self, path: Path):
        self.makeCurrent()
        if self.mesh_loaded:
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
        
        self.has_texture = (
            hasattr(mesh, "visual") and
            hasattr(mesh.visual, "uv") and
            isinstance(mesh.visual, TextureVisuals) and
            mesh.visual.uv is not None
        )
        
        if self.has_texture:
            uvs = mesh.visual.uv.astype(np.float32) # type: ignore
            vertex_data = np.hstack([vertices, normals, uvs])
        else:
            vertex_data = np.hstack([vertices, normals])
        
        vertex_data = vertex_data.astype(np.float32)
        stride = vertex_data.shape[1] * vertex_data.itemsize

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

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
        
        if self.has_texture:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(2, GL_FLOAT, stride, ctypes.c_void_p(24))

        glBindVertexArray(0)

        self.num_indices = faces.size
        self.mesh_loaded = True

        self.update()
    
    def load_texture(self, path: Path):
        self.makeCurrent()
        if self.texture_loaded:
            glDeleteTextures([self.texture_id])
        
        image: Image.Image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(image, dtype=np.uint8)
        
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        fmt = GL_RGBA if img_data.shape[2] == 4 else GL_RGB
        glTexImage2D(GL_TEXTURE_2D, 0, fmt, image.width, image.height, 0, fmt, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        
        self.texture_loaded = True
        self.update()

    def paintGL(self) -> None:
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        if not self.mesh_loaded:
            return

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -3.0)
        glRotatef(self.altitude, 1.0, 0.0, 0.0)
        glRotatef(self.azimuth, 0.0, 1.0, 0.0)
        
        if self.has_texture and self.texture_loaded:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.num_indices, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        if self.has_texture and self.texture_loaded:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.12, 0.12, 0.14, 1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

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
