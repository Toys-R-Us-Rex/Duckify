from logging import Logger
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import tqdm
import trimesh
import os
from PIL import Image

from color import Color
from island import Island
from point_3d import Point3D
from segment import Segment
from trace import Trace


class Tracer:
    def __init__(
        self,
        texture_path: Path,
        model_path: Path,
        palette: tuple[Color, ...],
        debug: bool = False
    ):
        self.logger: Logger = logging.getLogger("Tracer")
        self.debug: bool = debug

        self.texture_path: Path = texture_path
        self.model_path: Path = model_path
        self.palette: tuple[Color, ...] = palette

        self.texture: Optional[Image.Image] = None
        self.layers: list[Image.Image] = []

        self.islands: list[Island] = []
        self.segments: list[Segment] = []
        self.traces: list[Trace] = []

    def compute_traces(self) -> list[Trace]:
        self.texture = self.load_texture(self.texture_path)
        self.texture = self.palettize_texture(self.texture, self.palette)
        self.layers = self.split_colors(self.texture, self.palette)

        for c, layer in tqdm.tqdm(
            enumerate(self.layers), desc="Island detection", unit="layer"
        ):
            islands: list[Island] = self.detect_islands(layer, c)
            self.islands.extend(islands)

        for island in tqdm.tqdm(
            self.islands, desc="Island segmentation", unit="island"
        ):
            border: list[Segment] = self.resample_border(island)
            self.segments.extend(border)
            fill_slices: list[Segment] = self.compute_fill_slices(island)
            self.segments.extend(fill_slices)

        for segment in tqdm.tqdm(self.segments, desc="3D projection", unit="segment"):
            trace: Trace = self.project_segment_to_3d(segment)
            self.traces.append(trace)

        return self.traces

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

        im = Image.open(path)
        return im

    def load_model(self, path: Path) -> trimesh.base.Trimesh:
        """Load 3d model from it's object file into a trimesh instance

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

        palette = self.format_palette(palette)

        # pour forcer l'image à utiliser la palette souhaitée 
        # Il faut d'abord injecter la palette choisie dans une dummy image
        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette(palette)

        # s'assurer de la standardization "RGB"
        c_img = img.convert("RGB")
        # utilise quantize() pour palettizer
        output_img = c_img.quantize(palette=palette_image, dither=0)

        if self.debug:
            img.show("input texture image")
            output_img.show("palettized texture image")
        
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

        for i in range(len(palette)):
            target = palette[i]
            # Assurer la standardisation
            np_img = np.array(img.convert('RGB'))

            # Créer le masque : True là où la couleur correspond sur les 3 canaux (R, G, B)
            mask = np.all(np_img == target, axis=-1)
            # Créer une image en appliquant le masque
            mask_img = Image.fromarray((mask * 255).astype(np.uint8))
            images.append(mask_img)

            if self.debug:
                mask_img.show("splitted color image")

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
            polygon: np.ndarray = self.contour_to_polygon(contour)
            island: Island = Island(i, color, polygon)
            islands.append(island)

        return islands

    def compute_fill_slices(self, island: Island) -> list[Segment]:
        self.logger.info(f"Computing fill slices for island {island.idx}")
        return [Segment(np.array([0, 0]), np.array([1, 1]), island.color)]

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

    def project_segment_to_3d(self, segment: Segment) -> Trace:
        return Trace(
            p1=self.interpolate_position(segment.p1),
            p2=self.interpolate_position(segment.p2),
            color=segment.color,
        )

    def interpolate_position(self, uv_pos: np.ndarray) -> Point3D:
        return Point3D(
            pos=np.array([uv_pos[0], uv_pos[1], 0]), normal=np.array([0, 0, 1])
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
    
    def format_palette(self, palette: tuple[Color, ...]) -> list:
        """Formatting an input palette to be used in  palettize_texture()

        Args:
            palette (tuple[Color, ...]): Raw palette containing selected colors

        Returns:
            tuple[Color, ...]: Formatted palette to 768 values (3*256)
        """
        # counting existing values
        count = len(palette) * 3

        # completing missing values using green (as it's our current pen color)
        palette = palette + (0, 255, 0) * ((768 - count)//3)

        # formatting
        f_palette = []
        for item in palette:
            if isinstance(item, tuple):
                f_palette.extend(item)
            else:
                f_palette.append(item)
        
        if self.debug:
            print(f"Reformatted palette : {f_palette}")

        return f_palette
