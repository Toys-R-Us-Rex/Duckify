import argparse
import os
import sys
import random
import torch
import datetime
from mvadapter.pipelines.pipeline_texture import ModProcessConfig, TexturePipeline
from mvadapter.utils import make_image_grid

import json
from PIL import PngImagePlugin
from pygltflib import GLTF2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--variant", type=str, default="sdxl", choices=["sdxl", "sd21"])
    # I/O
    parser.add_argument("--mesh", type=str, required=True)
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument("--save_dir", type=str, default="./output")
    parser.add_argument("--save_name", type=str, default="t2tex_sample")
    parser.add_argument("--guidance_scale", type=float, default=7.0)
    parser.add_argument("--num_inference_steps", type=int, default=50)
    parser.add_argument("--negative_text", type=str, default="watermark, ugly, deformed, noisy, blurry, low contrast")
    
    # Extra
    parser.add_argument("--preprocess_mesh", action="store_true")
    args = parser.parse_args()

    if args.variant == "sdxl":
        from .inference_tg2mv_sdxl import prepare_pipeline, run_pipeline

        base_model = "Lykon/dreamshaper-xl-1-0"
        vae_model = "madebyollin/sdxl-vae-fp16-fix"
        height = width = 768
        uv_size = 1024
    elif args.variant == "sd21":
        from .inference_tg2mv_sd import prepare_pipeline, run_pipeline

        base_model = "stabilityai/stable-diffusion-2-1-base"
        vae_model = None
        height = width = 512
        uv_size = 4096
    else:
        raise ValueError(f"Invalid variant: {args.variant}")

    device = args.device
    num_views = 6

    # Prepare pipelines
    pipe = prepare_pipeline(
        base_model=base_model,
        vae_model=vae_model,
        unet_model=None,
        lora_model=None,
        adapter_path="huanngzh/mv-adapter",
        scheduler=None,
        num_views=num_views,
        device=device,
        dtype=torch.float16,
    )
    texture_pipe = TexturePipeline(
        upscaler_ckpt_path="./checkpoints/RealESRGAN_x2plus.pth",
        inpaint_ckpt_path="./checkpoints/big-lama.pt",
        device=device,
    )
    print("Pipeline ready.")

    os.makedirs(args.save_dir, exist_ok=True)
    
    if args.seed == -1:
        args.seed = random.randint(0, 2147483647)
    images, pos_images, normal_images = run_pipeline(
        pipe,
        mesh_path=args.mesh,
        num_views=num_views,
        text=args.text,
        height=height,
        width=width,
        num_inference_steps=args.num_inference_steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        negative_prompt=args.negative_text,
        device=device,
    )
    mv_path = os.path.join(args.save_dir, f"{args.save_name}.png")
    
    metadata_dict = {
        "prompt": args.text,
        "negative_prompt": args.negative_text,
        "seed": args.seed,
        "steps": args.num_inference_steps,
        "guidance": args.guidance_scale,
        "base_model": base_model,
        "height": height,
        "width": width,
        "vae_model": vae_model,
        "uv_size": uv_size,
        "num_views": num_views,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    metadata_png = PngImagePlugin.PngInfo()
    metadata_png.add_text("parameters", json.dumps(metadata_dict))
    
    make_image_grid(images, rows=1).save(mv_path, pnginfo=metadata_png)
    
    json_path = os.path.join(args.save_dir, f"{args.save_name}_meta.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata_dict, f, indent=4)

    torch.cuda.empty_cache()

    out = texture_pipe(
        mesh_path=args.mesh,
        save_dir=args.save_dir,
        save_name=args.save_name,
        uv_unwarp=False,
        preprocess_mesh=True,
        uv_size=uv_size,
        rgb_path=mv_path,
        rgb_process_config=ModProcessConfig(view_upscale=True, inpaint_mode="view"),
        debug_mode=False
    )
    print(f"Output saved to {out.shaded_model_save_path}")
    
