import os
os.environ["PYOPENGL_PLATFORM"] = "egl"

import argparse
import numpy as np
import trimesh
import pyrender
from PIL import Image


def look_at(camera_pos, target, up=np.array([0.0, 0.0, -1.0], dtype=np.float32)):
    camera_pos = np.array(camera_pos, dtype=np.float32)
    target = np.array(target, dtype=np.float32)

    forward = target - camera_pos
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)

    true_up = np.cross(right, forward)
    true_up = true_up / np.linalg.norm(true_up)

    pose = np.eye(4, dtype=np.float32)
    pose[:3, 0] = right
    pose[:3, 1] = true_up
    pose[:3, 2] = -forward
    pose[:3, 3] = camera_pos
    return pose


parser = argparse.ArgumentParser()
parser.add_argument("--glb_path", type=str, required=True, help="Path to input GLB file")
parser.add_argument("--output_dir", type=str, required=True, help="Directory to save rendered views")
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

loaded = trimesh.load(args.glb_path)

if isinstance(loaded, trimesh.Scene):
    meshes = [g for g in loaded.geometry.values()]
    bounds = loaded.bounds
else:
    meshes = [loaded]
    bounds = loaded.bounds

scene = pyrender.Scene(bg_color=[255, 255, 255, 0])

for m in meshes:
    scene.add(pyrender.Mesh.from_trimesh(m, smooth=False))

center = (bounds[0] + bounds[1]) / 2.0
extent = bounds[1] - bounds[0]
radius = float(np.max(extent)) * 2.0

camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
renderer = pyrender.OffscreenRenderer(1024, 1024)

camera_positions = [
    center + np.array([0, -radius, 0]),   # back
    center + np.array([radius, 0, 0]),    # right
    center + np.array([0, radius, 0]),    # front
    center + np.array([-radius, 0, 0]),   # left
]

names = ["back", "right", "front", "left"]

for name, cam_pos in zip(names, camera_positions):
    pose = look_at(cam_pos, center, up=np.array([0, 0, -1], dtype=np.float32))

    cam_node = scene.add(camera, pose=pose)
    light_node = scene.add(light, pose=pose)

    color, _ = renderer.render(scene)
    save_path = os.path.join(args.output_dir, f"{name}.png")
    Image.fromarray(color).save(save_path)

    scene.remove_node(cam_node)
    scene.remove_node(light_node)

renderer.delete()
print(f"Saved views to: {args.output_dir}")