import json
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import trimesh
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from PyQt6.QtCore import QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QWidget
from trimesh import Trimesh
from trimesh.visual import TextureVisuals

GlColor = tuple[float, float, float, float]


class Animation(QWidget):
    COOLDOWN_MS: int = 3000
    FRAME_RATE_MS: int = 50
    
    def __init__(self, callback: Callable[[int], None]) -> None:
        super().__init__()
        self.frame: int = 0
        self.callback: Callable[[int], None] = callback
        
        self.cooldown_timer: QTimer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)
        self.cooldown_timer.timeout.connect(self.on_cooldown_finished)
        
        self.animation_timer: QTimer = QTimer(self)
        self.animation_timer.setInterval(self.FRAME_RATE_MS)
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.reset_cooldown()
    
    def on_cooldown_finished(self):
        self.animation_timer.start()
    
    def update_animation(self):
        self.callback(self.frame)
        self.frame += 1
    
    def reset_cooldown(self):
        self.animation_timer.stop()
        self.frame = 0
        self.cooldown_timer.start(self.COOLDOWN_MS)


class MeshVisualizer(QOpenGLWidget):
    BACKGROUND_COLOR: GlColor = (0.12, 0.12, 0.14, 1.0)
    LIGHT_COLOR: GlColor = (0.9, 0.9, 0.9, 1.0)
    AMBIENT_COLOR: GlColor = (0.3, 0.3, 0.3, 1.0)
    FOV: float = 45.0
    LIMIT_NEAR: float = 0.1
    LIMIT_FAR: float = 10.0
    ZOOM: float = 3.0
    
    def __init__(self, parent) -> None:
        QOpenGLWidget.__init__(self, parent)

        self._pending_model: Optional[Path] = None
        self._pending_texture: Optional[Path] = None
        self._pending_traces: Optional[Path] = None
        
        self._initialized: bool = False

        self.offset: np.ndarray = np.array([0.0, 0.0, 0.0])
        self.scale: float = 1.0
        self.mesh_loaded: bool = False
        self.has_texture: bool = False
        self.texture_loaded: bool = False
        self.texture_id: int = 0
        self.traces_loaded: bool = False
        self.trace_vbos: list[int] = []
        self.trace_vertex_counts: list[int] = []
        self.altitude: float = 0.0
        self.azimuth: float = 0.0
        
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.num_indices: int = 0
        
        self.animation: Animation = Animation(self.rotate)
    
    def rotate(self, frame: int):
        self.azimuth += 1
        self.azimuth %= 360
        self.update()

    def set_altitude(self, altitude: float):
        self.altitude = altitude
        self.update()
        self.animation.reset_cooldown()

    def set_azimuth(self, azimuth: float):
        self.azimuth = azimuth
        self.update()
        self.animation.reset_cooldown()

    def load_model(self, path: Path):
        if not self._initialized:
            self._pending_model = path
            return

        self.makeCurrent()
        if self.mesh_loaded:
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])
            glDeleteBuffers(1, [self.ebo])

        mesh: Trimesh = trimesh.load_mesh(path)

        self.offset = mesh.bounding_box.centroid
        mesh.vertices -= self.offset
        self.scale = np.max(np.linalg.norm(mesh.vertices, axis=1))
        if self.scale > 0:
            mesh.vertices /= self.scale

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
        if not self._initialized:
            self._pending_texture = path
            return

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
    
    def load_traces(self, path: Path):
        if not self._initialized:
            self._pending_traces = path
            return

        if not self.mesh_loaded:
            print("Loading traces but mesh is not loaded")

        self.makeCurrent()
        if self.traces_loaded:
            glDeleteBuffers(len(self.trace_vbos), self.trace_vbos)

        with open(path, "r") as f:
            traces: list = json.load(f)["traces"]
        
        self.trace_vbos: list[int] = []
        self.trace_vertex_counts: list[int] = []
        for trace in traces:
            pts: np.ndarray = np.array(trace["path"]).astype(np.float32)
            pos = pts[:, 0]
            pos -= self.offset
            pos /= self.scale
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, pos.nbytes, pos, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            self.trace_vbos.append(vbo)
            self.trace_vertex_counts.append(len(pos))

        self.traces_loaded = True
        self.update()

    def paintGL(self) -> None:
        glClearColor(*self.BACKGROUND_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        if not self.mesh_loaded:
            return

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.ZOOM)
        # Correct axes: X+ out of the screen, Z+ up
        glRotatef(-90.0, 0.0, 1.0, 0.0)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glRotatef(self.altitude, 0.0, 1.0, 0.0)
        glRotatef(-self.azimuth, 0.0, 0.0, 1.0)
        
        if self.has_texture and self.texture_loaded:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.num_indices, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        if self.has_texture and self.texture_loaded:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
        
        self._draw_paths()

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(*self.BACKGROUND_COLOR)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 4.0, 3.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.LIGHT_COLOR)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.AMBIENT_COLOR)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.FOV, 4 / 3, self.LIMIT_NEAR, self.LIMIT_FAR)
        glMatrixMode(GL_MODELVIEW)
        
        self._initialized = True
        
        if self._pending_model:
            self.load_model(self._pending_model)
        
        if self._pending_texture:
            self.load_texture(self._pending_texture)
        
        if self._pending_traces:
            self.load_traces(self._pending_traces)

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.FOV, w / max(h, 1), self.LIMIT_NEAR, self.LIMIT_FAR)
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_paths(self):
        if not self.traces_loaded:
            return
        glDisable(GL_LIGHTING)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        glColor3f(1.0, 0.4, 0.0)

        glEnableClientState(GL_VERTEX_ARRAY)
        for vbo, count in zip(self.trace_vbos, self.trace_vertex_counts):
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glVertexPointer(3, GL_FLOAT, 0, None)
            glDrawArrays(GL_LINE_STRIP, 0, count)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
