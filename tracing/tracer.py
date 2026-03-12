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
from tracing.config import TracerConfig
from tracing.hierarchy import Hierarchy
from tracing.island import Island
from tracing.point_3d import Point3D
from tracing.trace import Trace2D, Trace3D


class Tracer:
    def __init__(
            self,
            config: TracerConfig,
            texture_path: Path,
            model_path: Path,
            palette: tuple[Color, ...],
            ignored_color: Color
    ):
        self.logger: Logger = logging.getLogger("Tracer")
        self.config: TracerConfig = config

        self.texture_path: Path = texture_path
        self.model_path: Path = model_path
        self.palette: tuple[Color, ...] = palette
        self.ignored_color: Color = ignored_color

        self.texture: Optional[Image.Image] = None
        self.paletted_texture: Optional[Image.Image] = None
        self.model: Optional[Trimesh] = None
        self.layers: list[Image.Image] = []

        self.islands: list[Island] = []
        self.traces_2d: list[Trace2D] = []
        self.traces_3d: list[Trace3D] = []

        self.next_trace_id: int = 0
    
    def trace_id(self) -> int:
        i = self.next_trace_id
        self.next_trace_id += 1
        return i

    def compute_traces(self) -> None:
        # 1. Load assets
        self.texture = self.load_texture(self.texture_path)
        self.model = self.load_model(self.model_path)

        if not self.mesh_has_uv_map(self.model):
            self.logger.error("Missing mesh UV coordinates")
            return

        # 2. Quantize and split colors
        self.texture = self.mask_outside_UV_texture(self.texture, self.model)
        self.paletted_texture = self.palettize_texture(self.texture, self.palette, self.ignored_color)
        self.layers = self.split_colors(self.paletted_texture, self.palette)

        # 3. Identify color islands
        for c, layer in tqdm.tqdm(
                enumerate(self.layers), desc="Island detection", unit="layer"
        ):
            islands: list[Island] = self.detect_islands(layer, c)
            self.islands.extend(islands)

        # 4. Compute border and fill traces (2D)
        for i, island in tqdm.tqdm(
                enumerate(self.islands), desc="Island segmentation", unit="island"
        ):
            self.traces_2d.append(Trace2D(
                color=island.color,
                path=np.vstack([island.outer_border, [island.outer_border[0]]]),
                i=self.trace_id()
            ))
            for inner_border in island.inner_borders:
                self.traces_2d.append(Trace2D(
                    color=island.color,
                    path=inner_border,
                    i=self.trace_id()
                ))
            if self.config.enable_fill_slicing:
                fill_slices: list[Trace2D] = self.compute_fill_slices(island)
                self.logger.debug(f"Island {i}: {len(fill_slices)} fill slices")
                self.traces_2d.extend(fill_slices)

        img = np.array(self.texture.copy())
        size = (img.shape[1], img.shape[0])

        # 5. Project 2D traces in 3D
        for i, trace_2d in tqdm.tqdm(enumerate(self.traces_2d), desc="3D projection", unit="trace"):
            self.logger.debug(f"Processing trace {i}")
            traces_3d: Optional[list[Trace3D]] = self.project_trace_to_3d(trace_2d, self.model)
            if traces_3d is not None:
                self.traces_3d.extend(traces_3d)
                if len(traces_3d) == 0:
                    self.logger.warning(f"2D trace {i} did not produce any 3D trace")

            if self.config.debug:
                pts: np.ndarray = self.uv_to_texture(trace_2d.path, size).astype(np.intp)
                for pt in pts:
                    cv2.circle(img, pt, 3, (0, 0, 255), -1)

                col = (255, 0, 255) if traces_3d is None or len(traces_3d) == 0 else (255, 255, 0)
                cv2.polylines(img, [pts], True, col)

        if self.config.debug:
            cv2.imshow("Segments", img)
            clouds = []
            segments = []
            for trace in self.traces_3d:
                color = self.palette[trace.color]
                polygon = trace.get_polygon()
                path = trimesh.load_path(polygon)
                for entity in path.entities:
                    entity.color = color
                segments.append(path)
                cloud = trimesh.PointCloud(polygon, colors=color)
                clouds.append(cloud)
            scene = trimesh.Scene([self.model] + segments + clouds)
            scene.show()

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
        return im.resize(self.config.image_size)

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

        if self.config.debug:
            mesh.show(resolution = (800,600))

        return mesh

    # https://stackoverflow.com/questions/29433243/
    def palettize_texture(self, img: Image.Image, palette: tuple[Color, ...], ignored_color: Color) -> Image.Image:
        """Force textures colors to nearest one based of a given palette

        Args:
            img (Image.Image): the texture image
            palette (tuple[Color, ...]): the palette containing selected colors
            ignored_color Color: the color to ignore when palettizing

        Returns:
            Image.Image: the color palettized texture image
        """
        self.logger.info("Palettizing texture colors")
        
        c_img_arr = np.array(img.convert("RGB"))
        
        ignored_color_rgb = np.array([ignored_color])
        mask = np.any(c_img_arr != ignored_color_rgb, axis=-1)
        # récupérer les pixels des couleurs de la palette sans l'ignored_color
        pixels_to_quantize = c_img_arr[mask]

        palettized_pixels = self.quantize_to_palette(pixels_to_quantize, np.array(palette))
        # Réinjection des pixels palettizés dans image de base
        output_arr = c_img_arr.copy()
        output_arr[mask] = palettized_pixels

        output_img = Image.fromarray(output_arr.astype(np.uint8), "RGB")

        if self.config.debug:
            cv2.imshow("input texture image", c_img_arr[..., ::-1])
            cv2.imshow("palettized texture image", output_arr[..., ::-1])
            
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

            if self.config.debug:
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

        contours, hierarchy = cv2.findContours(layer, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        self.logger.debug(f"Found {len(contours)} contours")

        if self.config.debug:
            print("\nLa hiérarchie de l'image :\n", hierarchy)
            
            cv2.imshow("Input", layer)
            with_contours = cv2.cvtColor(layer, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(with_contours, contours, -1, (0, 0, 255), 1)
            cv2.imshow("Contours", with_contours)
            cv2.waitKey(-1)

        # gérer la hierarchie : https://learnopencv.com/contour-detection-using-opencv-python-c/
        hierarchies: list[Hierarchy] = []
        if hierarchy is not None:
            for idx, (contour, values) in enumerate(zip(contours, hierarchy[0])):
                hierarch: Hierarchy = Hierarchy (
                    index= idx,
                    next=int(values[0]),
                    previous=int(values[1]),
                    first_child=int(values[2]),
                    parent=int(values[3]),
                    polygon=self.contour_to_polygon(contour)
                )
                hierarchies.append(hierarch)
        
        islands: list[Island] = []

        # border simple
        for h in hierarchies:
            if not h.has_parent and not h.has_child:
                polygon_uv = self.texture_to_uv(h.polygon, (layer.shape[1], layer.shape[0]))
                islands.append(Island(color=color, outer_border=polygon_uv))

       # multi-border (outer+inner)
        parents = {h.index: h for h in hierarchies 
                    if not h.has_parent and h.has_child}

        for parent in parents.values():
            outer = self.texture_to_uv(parent.polygon, (layer.shape[1], layer.shape[0]))
            inner_borders = [
                self.texture_to_uv(h.polygon, (layer.shape[1], layer.shape[0]))
                for h in hierarchies
                if h.parent == parent.index
            ]
            islands.append(Island(
                color=color,
                outer_border=outer,
                inner_borders=inner_borders
            ))

        return islands
    
    # https://shapely.readthedocs.io/en/stable/index.html
    def compute_fill_slices(self, island: Island) -> list[Trace2D]:
        """Compute the traces to fill the interior of an island

        Args:
            island (Island): Detected island of color

        Returns:
            list[Trace2D]: List of 2D traces filling the island
        """
        self.logger.info(f"Computing fill slices for island : {island}")
        
        polygon = Polygon(island.outer_border, island.inner_borders)

        # BB du polygone
        minx, miny, maxx, maxy = polygon.bounds

        if self.config.debug:
            llBound = shapely.points([minx, miny])
            urBound = shapely.points([maxx, maxy])
            lrBound = shapely.points([maxx, miny])
            ulBound = shapely.points([minx, maxy])

            fig, ax = plt.subplots()
            plot_polygon(polygon, ax=ax, facecolor='lightblue', edgecolor='blue', alpha=0.5)
            plot_points(llBound, ax=ax, color='red')
            plot_points(urBound, ax=ax, color='red')
            plot_points(lrBound, ax=ax, color='red')
            plot_points(ulBound, ax=ax, color='red')
            plt.show()
        
        # génération d'une grille de ligne à superposer/intersecter avec l'island
        lines : list[LineString] = []
        spacing: float = self.config.fill_slice_spacing
        c_y = miny + spacing
        while c_y < maxy:
            lines.append(LineString([(minx, c_y), (maxx, c_y)]))
            c_y += spacing

        # Intersection de la grille de lignes et du polygone
        fill_lines: list[Union[LineString, MultiLineString]] = [
            line.intersection(polygon)
            for line in lines
            if line.intersects(polygon)
        ]  # type: ignore

        if self.config.debug:
            fig, ax = plt.subplots()
            plot_polygon(polygon, ax=ax, facecolor='lightblue', edgecolor='blue', alpha=0.5)
            for fill_line in fill_lines:
                plot_line(fill_line, ax=ax, color='green', linewidth=2)
            plt.show()
        
        # Tri entre LineString et MultiLineString et ajout à la variable de retour
        traces : list[Trace2D] = []
        for l in fill_lines:  # noqa: E741
            if l.geom_type == "LineString":
                trace = Trace2D(
                    color=island.color,
                    path=l.coords,
                    i=self.trace_id()
                )
                traces.append(trace)
            else:
                for ls in l.geoms:
                    trace = Trace2D(
                        color=island.color,
                        path=ls.coords,
                        i=self.trace_id()
                    )
                    traces.append(trace)
        return traces
    
    def export_traces(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            choice = input(f"File {output_path} already exists. Overwrite ? N/y")
            if choice.lower().strip() != "y":
                return

        traces_out: list[dict] = []
        for trace in self.traces_3d:
            traces_out.append({
                "color": trace.color,
                "path": [
                    (pt.pos.tolist(), pt.normal.tolist())
                    for pt in trace.path
                ]
            })

        with open(output_path, "w") as f:
            json.dump({
                "generated_at": datetime.datetime.now().isoformat(),
                "model": str(self.model_path),
                "texture": str(self.texture_path),
                "traces": traces_out
            }, f, indent=4)
    
    def show_graphs(self):
        seps = [0]
        for trace in self.traces_3d:
            seps.append(seps[-1] + len(trace.path))
        
        i = range(seps[-1])
        traces_pos = []
        traces_normals = []
        
        for trace in self.traces_3d:
            traces_pos.append(trace.get_polygon())
            traces_normals.append(np.array([
                p.normal
                for p in trace.path
            ]))
        
        pos = np.vstack(traces_pos)
        normals = np.vstack(traces_normals)
        
        fig, ax = plt.subplots(2)
        ax[0].set_ylabel("Position")
        ax[0].plot(i, pos[..., 0], label="X")
        ax[0].plot(i, pos[..., 1], label="Y")
        ax[0].plot(i, pos[..., 2], label="Z")
        ax[0].legend()
        ax[1].set_ylabel("Normal")
        ax[1].plot(i, normals[..., 0], label="NX")
        ax[1].plot(i, normals[..., 1], label="NY")
        ax[1].plot(i, normals[..., 2], label="NZ")
        ax[1].legend()
        
        for i in seps:
            ax[0].axvline(i)
            ax[1].axvline(i)
        plt.show()

    # Utility

    def project_trace_to_3d(self, trace: Trace2D, mesh: Trimesh) -> Optional[list[Trace3D]]:
        """Projects a trace from UV space to 3D traces

        Args:
            trace (Trace2D): a trace in UV space
            mesh (Trimesh): the mesh

        Returns:
            Optional[list[Trace3D]]: the corresponding 3D traces, or None if a point could not be projected in 3D space
        """
        pts: list[Point3D] = []
        
        for i, pt in enumerate(trace.path):
            pt2: Optional[Point3D] = self.interpolate_position(np.array(pt), mesh)
            if pt2 is None:
                return None
            
            if i != 0:
                pts.extend(self.compute_edge_points(pts[-1], pt2, mesh))
            pts.append(pt2)
        
        return [
            Trace3D(
                path=pts,
                color=trace.color,
            )
        ]

    def compute_edge_points(self, p1: Point3D, p2: Point3D, mesh: Trimesh, depth: int = 0) -> list[Point3D]:
        pts: list[Point3D] = []
        if p1.face_idx == p2.face_idx:
            return pts
        
        mid_uv: np.ndarray = (p1.uv + p2.uv) / 2
        mid: Optional[Point3D] = self.interpolate_position(mid_uv, mesh)
        if mid is None:
            return pts

        dist = np.linalg.norm(p2.pos - p1.pos)
        if (dist < self.config.min_segment_length or
            depth > self.config.max_edge_recursion_depth):
            diff = np.dot(p1.normal, p2.normal)
            if diff < self.config.sharp_edge_threshold:
                pts.append(mid.with_normal(p1))
                pts.append(mid)
                pts.append(mid.with_normal(p2))
            else:
                pts.append(mid)
        else:
            if p1.face_idx != mid.face_idx:
                pts.extend(self.compute_edge_points(p1, mid, mesh, depth + 1))
            if p2.face_idx != mid.face_idx:
                pts.extend(self.compute_edge_points(mid, p2, mesh, depth + 1))
        return pts

    def interpolate_position(self, uv_pos: np.ndarray, mesh: Trimesh) -> Optional[Point3D]:
        """Interpolates the UV position on the UV map and returns the corresponding 3D point

        Args:
            uv_pos (np.ndarray): a UV position (u,v)
            mesh (Trimesh): the mesh

        Returns:
            Optional[Point3D]: the corresponding 3D point, or None if a correspondance could not be found
        """
        if not isinstance(mesh.visual, TextureVisuals):
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
        eps: float = self.config.barycentric_epsilon
        inside = (w0 >= -eps) & (w1 >= -eps) & (w2 >= -eps)

        if not np.any(inside):
            return None  # UV point not found in any triangle

        # Take the first matching face
        idx = np.argmax(inside)
        bary = np.array([w0[idx], w1[idx], w2[idx]])

        # Interpolate 3D position using barycentric coords
        tri_verts = vertices[faces[idx]]  # (3, 3)
        pos = bary @ tri_verts
        return Point3D(
            pos=pos,
            face_idx=int(idx),
            normal=mesh.face_normals[idx],
            uv=uv_pos
        )

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

    def mesh_has_uv_map(self, mesh: Trimesh) -> bool:
        return isinstance(mesh.visual, TextureVisuals)

    # This fonction was as such, re-used from https://stackoverflow.com/questions/73666119/open-cv-python-quantize-to-a-given-color-palette
    def quantize_to_palette(self, image: np.ndarray, palette: tuple[Color, ...]) -> Image.Image:
        """Quantize color value in an image to the one in the given palette

        Args:
            image (np.ndarray): The texture image
            palette (tuple[Color, ...]): the list of colors available in the draw processing

        Returns:
            np.ndarray: the palettized texture
        """
        X_query = image.reshape(-1, 3).astype(np.float32)
        X_index = palette.astype(np.float32)

        knn = cv2.ml.KNearest_create()
        knn.train(X_index, cv2.ml.ROW_SAMPLE, np.arange(len(palette)))
        ret, results, neighbours, dist = knn.findNearest(X_query, 1)

        quantized_image = np.array([palette[idx] for idx in neighbours.astype(int)])
        quantized_image = quantized_image.reshape(image.shape)
        return quantized_image
    
    def mask_outside_UV_texture(self, img: Image.Image,  mesh: Trimesh) -> Image.Image:
        """Mask out regions of the given texture not covered by the UV map

        Args:
            img (Image.Image): the raw texture
            mesh (Trimesh): the model's mesh

        Returns:
            Image.Image: the masked texture
        """
        uv = mesh.visual.uv
        faces = mesh.faces
        width, height = img.size
        # normalisation des coordonnées UV aux dimensions de textures
        pixel_coords = uv * np.array([width - 1, height - 1])
        # inverse coordonée vertical (format de base UV est zero=bottom-left et on veut zero=top-left)
        pixel_coords[:, 1] = (height - 1) - pixel_coords[:, 1]
        
        uv_faces = pixel_coords[faces].astype(np.int32)
        np_img = np.array(img.convert('RGB'))
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, uv_faces, 255)
        masked_texture = cv2.bitwise_and(np_img, np_img, mask=mask)
        
        if self.config.debug:
            cv2.namedWindow('Mask', cv2.WINDOW_KEEPRATIO)
            cv2.imshow('Mask', mask)
            cv2.resizeWindow('Mask', 600, 600)

            cv2.namedWindow('Masked texture', cv2.WINDOW_KEEPRATIO)
            cv2.imshow('Masked texture', masked_texture)
            cv2.resizeWindow('Masked texture', 600, 600)
            cv2.waitKey(-1)
        
        return Image.fromarray(masked_texture)