import datetime
import json
import logging
import os
from logging import Logger
from pathlib import Path
from typing import Optional, Union

import cv2
import matplotlib.pyplot as plt
import numpy as np
import shapely
import tqdm
import trimesh
from PIL import Image
from shapely import LineString, MultiLineString, Polygon
from shapely.plotting import plot_line, plot_points, plot_polygon
from trimesh import Trimesh
from trimesh.visual import TextureVisuals

from tracing.color import Color
from tracing.island import Island
from tracing.point_3d import Point3D
from tracing.segment import Segment
from tracing.trace import Trace2D, Trace3D


class Tracer:
    def __init__(
            self,
            texture_path: Path,
            model_path: Path,
            palette: tuple[Color, ...],
            output_path: Path,
            debug: bool = False
    ):
        self.logger: Logger = logging.getLogger("Tracer")
        self.debug: bool = debug

        self.texture_path: Path = texture_path
        self.model_path: Path = model_path
        self.output_path: Path = output_path
        self.palette: tuple[Color, ...] = palette

        self.texture: Optional[Image.Image] = None
        self.paletted_texture: Optional[Image.Image] = None
        self.model: Optional[Trimesh] = None
        self.layers: list[Image.Image] = []

        self.islands: list[Island] = []
        self.traces_2d: list[Trace2D] = []
        self.traces_3d: list[Trace3D] = []

    def compute_traces(self) -> None:
        self.texture = self.load_texture(self.texture_path)
        self.model = self.load_model(self.model_path)
        self.paletted_texture = self.palettize_texture(self.texture, self.palette)
        self.layers = self.split_colors(self.paletted_texture, self.palette)

        for c, layer in tqdm.tqdm(
                enumerate(self.layers), desc="Island detection", unit="layer"
        ):
            islands: list[Island] = self.detect_islands(layer, c)
            self.islands.extend(islands)

        for island in tqdm.tqdm(
                self.islands, desc="Island segmentation", unit="island"
        ):
            self.traces_2d.append(Trace2D(
                color=island.color,
                path=island.border
            ))
            fill_slices: list[Trace2D] = self.compute_fill_slices(island)
            self.traces_2d.extend(fill_slices)

        img = np.array(self.texture.copy())
        size = (img.shape[1], img.shape[0])

        for trace_2d in tqdm.tqdm(self.traces_2d, desc="3D projection", unit="trace"):
            traces_3d: Optional[list[Trace3D]] = self.project_trace_to_3d(trace_2d, self.model)
            if traces_3d is not None:
                self.traces_3d.extend(traces_3d)

            if self.debug:
                pts: np.ndarray = self.uv_to_texture(trace_2d.path, size).astype(np.intp)
                for pt in pts:
                    cv2.circle(img, pt, 3, (0, 0, 255), -1)

                col = (255, 0, 255) if traces_3d is None else (255, 255, 0)
                cv2.polylines(img, [pts], True, col)

        if self.debug:
            cv2.imshow("Segments", img)
            pts2 = []
            segments = []
            for trace in self.traces_3d:
                pts2.extend(trace.path)
                segments.append(trimesh.load_path(np.vstack([trace.path, [trace.path[0]]])))
            cloud = trimesh.PointCloud(pts2, colors=[255, 0, 0, 255])
            scene = trimesh.Scene([self.model, cloud] + segments)
            scene.show()

        self.export_traces(self.traces_3d, self.model_path, self.texture_path, self.output_path)

    def load_texture(self, path: Path) -> Image.Image:
        """Load texture from file path

        Args:
            path (Path): path of the texture file to load

        Returns:
            Image.Image: texture loaded
        """
        self.logger.info(f"Loading image {path}")

        if not os.path.exists(path):
            self.logger.error(f"The file {path} does not exist")
            raise FileNotFoundError(f"The file {path} does not exist")

        im = Image.open(path).convert("RGB")
        return im

    def load_model(self, path: Path) -> Trimesh:
        """Load 3d model from its object file into a trimesh instance

        Args:
            path (Path): path of the 3d model file

        Returns:
            trimesh.base.Trimesh: trimesh object
        """
        self.logger.info(f"Loading model {path}")

        if not os.path.exists(path):
            self.logger.error(f"The file {path} does not exist")
            raise FileNotFoundError(f"The file {path} does not exist")

        mesh = trimesh.load_mesh(path)

        if self.debug:
            mesh.show()

        return mesh

    # https://stackoverflow.com/questions/29433243/
    def palettize_texture(
            self, img: Image.Image, palette: tuple[Color, ...]
    ) -> Image.Image:
        """Force textures colors to nearest one based of a given palette

        Args:
            img (Image.Image): the texture image
            palette (tuple[Color, ...]): the palette containing selected colors

        Returns:
            Image.Image: the color palettized texture image
        """
        self.logger.info("Palettizing texture colors")

        pil_palette = self.format_palette(palette)

        # pour forcer l'image à utiliser la palette souhaitée
        # Il faut d'abord injecter la palette choisie dans une dummy image
        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette(pil_palette)

        # s'assurer de la standardization "RGB"
        c_img = img.convert("RGB")
        # utilise quantize() pour palettizer
        output_img = c_img.quantize(palette=palette_image, dither=Image.Dither.NONE)

        if self.debug:
            cv2.imshow("input texture image", np.array(c_img)[..., ::-1])
            cv2.imshow("palettized texture image", np.array(output_img.convert("RGB"))[..., ::-1])

        return output_img

    # https://stackoverflow.com/questions/56942102
    def split_colors(self, img: Image.Image, palette: tuple[Color, ...]) -> list[Image.Image]:
        """ Split the paletted texture into one image per color from the palette

        Args:
            img (Image.Image): Paletted texture

        Returns:
            list[Image.Image]: A list of single color channel image
        """
        self.logger.info("Splitting colors channels")
        images = []

        for color in palette:
            # Assurer la standardisation
            np_img = np.array(img.convert('RGB'))

            # Créer le masque : True là où la couleur correspond sur les 3 canaux (R, G, B)
            mask = np.all(np_img == color, axis=-1)
            # Créer une image en appliquant le masque
            mask_img = Image.fromarray((mask * 255).astype(np.uint8))
            images.append(mask_img)

            if self.debug:
                cv2.imshow(f"splitted color image {color}", np.array(mask_img))

        return images

    def detect_islands(self, img: Image.Image, color: int) -> list[Island]:
        """Detects color islands and extracts its border as a polygon

        Args:
            img (Image.Image): input binary image
            color (int): color index for this layer

        Returns:
            list[Island]: list of islands in the layer
        """
        self.logger.info(f"Detecting islands for color {color}")

        layer: np.ndarray = np.asarray(img)

        contours, _ = cv2.findContours(layer, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.logger.debug(f"Found {len(contours)} contours")

        if self.debug:
            cv2.imshow("Input", layer)
            with_contours = cv2.cvtColor(layer, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(with_contours, contours, -1, (0, 0, 255), 1)
            cv2.imshow("Contours", with_contours)
            cv2.waitKey(-1)

        islands: list[Island] = []
        for i, contour in enumerate(contours):
            polygon_tex: np.ndarray = self.contour_to_polygon(contour)
            polygon_uv: np.ndarray = self.texture_to_uv(polygon_tex, (layer.shape[1], layer.shape[0]))
            island: Island = Island(i, color, polygon_uv)
            islands.append(island)

        return islands
    
    # https://shapely.readthedocs.io/en/stable/index.html
    def compute_fill_slices(self, island: Island) -> list[Trace2D]:
        """Compute the traces to fill the interior of an island

        Args:
            island (Island): Detected island of color

        Returns:
            list[Trace2D]: List of 2D traces filling the island
        """
        self.logger.info(f"Computing fill slices for island {island.idx}")

        polygon = Polygon(island.border)

        # BB du polygone
        minx, miny, maxx, maxy = polygon.bounds

        llBound = shapely.points([minx, miny])
        urBound = shapely.points([maxx, maxy])
        lrBound = shapely.points([maxx, miny])
        ulound = shapely.points([minx, maxy])

        if self.debug:
            fig, ax = plt.subplots()
            plot_polygon(polygon, ax=ax, facecolor='lightblue', edgecolor='blue', alpha=0.5)
            plot_points(llBound, ax=ax, color='red')
            plot_points(urBound, ax=ax, color='red')
            plot_points(lrBound, ax=ax, color='red')
            plot_points(ulound, ax=ax, color='red')
            plt.show()
        
        # génération d'une grille de ligne à superposer/intersecter avec l'island
        lines : list[LineString] = []
        spacing = 0.005 # TODO valeur à adapter dynamiquement plus tard ?
        c_y = miny + spacing
        while c_y < maxy:
            lines.append(LineString([(minx, c_y), (maxx, c_y)]))
            c_y += spacing

        # Intersection de la grille de lignes et du polygone
        fill_lines: list[Union[LineString, MultiLineString]] = [
            line.intersection(polygon)
            for line in lines
            if line.intersects(polygon)
        ]  # type: ignore]

        if self.debug:
            fig, ax = plt.subplots()
            plot_polygon(polygon, ax=ax, facecolor='lightblue', edgecolor='blue', alpha=0.5)
            for fill_line in fill_lines:
                plot_line(fill_line, ax=ax, color='green', linewidth=2)
            plt.show()
        
        # Tri entre LineString et MultiLineString et ajout à la variable de retour
        traces : list[Trace2D] = []
        for l in fill_lines:
            if l.geom_type == "LineString":
                trace = Trace2D(
                    color=island.color,
                    path=l.coords
                )
                traces.append(trace)
            else:
                for ls in l.geoms:
                    trace = Trace2D(
                        color=island.color,
                        path=ls.coords
                    )
                    traces.append(trace)
        return traces
    
    def export_traces(self, traces: list[Trace3D], model_path: Path, texture_path: Path, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            choice = input(f"File {output_path} already exists. Overwrite ? N/y")
            if choice.lower().strip() != "y":
                return

        traces_out: list[dict] = []
        for trace in traces:
            traces_out.append({
                "face": trace.face.tolist(),
                "color": trace.color,
                "path": trace.path.tolist()
            })

        with open(output_path, "w") as f:
            json.dump({
                "generated_at": datetime.datetime.now().isoformat(),
                "model": str(model_path),
                "texture": str(texture_path),
                "traces": traces_out
            }, f, indent=4)

    # Utility

    def resample_border(self, island: Island) -> list[Segment]:
        border: np.ndarray = self.resample_polygon(island.border, closed=True)
        segments: list[Segment] = []
        for i in range(border.shape[0]):
            p1: np.ndarray = border[i]
            p2: np.ndarray = border[(i + 1) % border.shape[0]]
            segments.append(Segment(p1, p2, island.color))
        return segments

    def resample_fill_segment(self, segment: Segment, n: int) -> list[Segment]:
        pts: np.ndarray = self.resample_polygon(np.array([
            segment.p1,
            segment.p2
        ]), n)
        segments: list[Segment] = []

        for i in range(pts.shape[0]):
            p1: np.ndarray = pts[i]
            p2: np.ndarray = pts[(i + 1) % pts.shape[0]]
            segments.append(Segment(p1, p2, segment.color))

        return segments

    def project_trace_to_3d(self, trace: Trace2D, mesh: Trimesh) -> Optional[list[Trace3D]]:
        """Projects a trace from UV space to 3D traces

        Args:
            trace (Trace2D): a trace in UV space
            mesh (Trimesh): the mesh

        Returns:
            Optional[list[Trace3D]]: the corresponding 3D traces, or None if a point could not be projected in 3D space
        """
        pts: np.ndarray = np.zeros((len(trace.path), 3), dtype=np.float64)
        face_idx: int = -1
        normal: np.ndarray = np.zeros(3)
        for i, pt in enumerate(trace.path):
            pt2: Optional[Point3D] = self.interpolate_position(pt, mesh)
            if pt2 is None:
                return None
            # TODO split at face edges
            if i == 0:
                face_idx = pt2.face_idx
                normal = mesh.face_normals[face_idx]
            elif face_idx != pt2.face_idx and np.linalg.norm(mesh.face_normals[pt2.face_idx] - normal) > 1e-6:
                print(f"Not on the same face: {face_idx} -> {pt2.face_idx} | {normal} -> {mesh.face_normals[pt2.face_idx]}")
                return None
            pts[i] = pt2.pos
        
        return [
            Trace3D(
                face=mesh.face_normals[face_idx],
                path=pts,
                color=trace.color,
            )
        ]

    def interpolate_position(self, uv_pos: np.ndarray, mesh: Trimesh) -> Optional[Point3D]:
        """Interpolates the UV position on the UV map and returns the corresponding 3D point

        Args:
            uv_pos (np.ndarray): a UV position (u,v)
            mesh (Trimesh): the mesh

        Returns:
            Optional[Point3D]: the corresponding 3D point, or None if a correspondance could not be found
        """
        if not isinstance(mesh.visual, TextureVisuals):
            # self.logger.error("Missing mesh UV coordinates")
            return None

        uv: np.ndarray = mesh.visual.uv
        faces: np.ndarray = mesh.faces
        vertices: np.ndarray = mesh.vertices
        uv_faces: np.ndarray = uv[faces]

        # Compute barycentric coordinates of uv_pos in each UV triangle
        # Using the 2D triangle test
        v0 = uv_faces[:, 0, :]  # (F, 2)
        v1 = uv_faces[:, 1, :]
        v2 = uv_faces[:, 2, :]

        # Barycentric coords in UV space
        denom = ((v1[:, 1] - v2[:, 1]) * (v0[:, 0] - v2[:, 0]) +
                 (v2[:, 0] - v1[:, 0]) * (v0[:, 1] - v2[:, 1]))

        w0 = ((v1[:, 1] - v2[:, 1]) * (uv_pos[0] - v2[:, 0]) +
              (v2[:, 0] - v1[:, 0]) * (uv_pos[1] - v2[:, 1])) / denom

        w1 = ((v2[:, 1] - v0[:, 1]) * (uv_pos[0] - v2[:, 0]) +
              (v0[:, 0] - v2[:, 0]) * (uv_pos[1] - v2[:, 1])) / denom

        w2 = 1.0 - w0 - w1

        # Find faces where point is inside the UV triangle
        eps = 1e-8
        inside = (w0 >= -eps) & (w1 >= -eps) & (w2 >= -eps)

        if not np.any(inside):
            return None  # UV point not found in any triangle

        # Take the first matching face
        idx = np.argmax(inside)
        bary = np.array([w0[idx], w1[idx], w2[idx]])

        # Interpolate 3D position using barycentric coords
        tri_verts = vertices[faces[idx]]  # (3, 3)
        pos = bary @ tri_verts
        return Point3D(pos, int(idx))

    def contour_to_polygon(self, contour: np.ndarray) -> np.ndarray:
        """Converts an OpenCV (Nx1x2) contour to a simple polygon (Nx2)

        Args:
            contour (np.ndarray): an OpenCV contour (Nx1x2)

        Returns:
            np.ndarray: a polygon (Nx2)
        """
        return contour[:, 0, :]

    # https://stackoverflow.com/a/70664846/11109181
    def resample_polygon(self, xy: np.ndarray, n_points: int = 100, closed: bool = False) -> np.ndarray:
        n = n_points

        # If closed, duplicate first point at end
        if closed:
            xy = np.vstack([xy, [xy[0]]])
            n += 1

        # Cumulative Euclidean distance between successive polygon points.
        # This will be the "x" for interpolation
        d = np.cumsum(np.r_[0, np.sqrt((np.diff(xy, axis=0) ** 2).sum(axis=1))])

        # get linearly spaced points along the cumulative Euclidean distance
        d_sampled = np.linspace(0, d.max(), n)

        # interpolate x and y coordinates
        xy_interp = np.c_[
            np.interp(d_sampled, d, xy[:, 0]),
            np.interp(d_sampled, d, xy[:, 1]),
        ]

        # If closed, ignore last point (duplicate of first point)
        if closed:
            xy_interp = xy_interp[:-1]

        return xy_interp

    def format_palette(self, palette: tuple[Color, ...]) -> list[int]:
        """Formatting an input palette to be used in  palettize_texture()

        Args:
            palette (tuple[Color, ...]): Raw palette containing selected colors

        Returns:
            list[int]: Formatted palette to 768 values (3*256)
        """

        # flatten tuple of colors (tuple of tuples) into a list of ints
        flat: list[int] = list(sum(palette, start=()))

        # completing missing values using green (as it's our current pen color)
        flat.extend((0, 0, 0) * (256 - len(palette)))

        return flat

    def texture_to_uv(self, texture_pos: np.ndarray, texture_size: tuple[int, int]) -> np.ndarray:
        """Converts texture coordinates to UV space

        Args:
            texture_pos (np.ndarray): 2D coordinates on the texture image (x,y), (...x2)
            texture_size (tuple[int, int]): size of the texture in pixels (w,h)

        Returns:
            np.ndarray: 2D coordinates in UV space (u,v), (...x2)
        """
        scaled = texture_pos / texture_size
        scaled[..., 1] = 1 - scaled[..., 1]
        return scaled

    def uv_to_texture(self, uv_pos: np.ndarray, texture_size: tuple[int, int]) -> np.ndarray:
        """Converts UV coordinates to texture space

        Args:
            uv_pos (np.ndarray): 2D coordinates in the UV space (u,v), (...x2)
            texture_size (tuple[int, int]): size of the texture in pixels (w,h)

        Returns:
            np.ndarray: 2D coordinates on the texture (x,y), (...x2)
        """
        flipped = np.copy(uv_pos)
        flipped[..., 1] = 1 - flipped[..., 1]
        return flipped * texture_size
