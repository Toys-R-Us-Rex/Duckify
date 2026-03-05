import os
import matplotlib.pyplot as plt
import torch
from PIL import Image
import open_clip
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification, AutoModelForCausalLM, AutoTokenizer
import argparse
from huggingface_hub import login
from dotenv import load_dotenv


"""
Pipeline de Similarité Image–Texte

Ce script combine un Large Language Model (LLM) et OpenCLIP afin d’évaluer
dans quelle mesure un prompt textuel correspond à une image.

Modèles utilisés
----------------

1. OpenCLIP (ViT-B/32, pré-entraîné sur LAION-2B)
   - OpenCLIP est un modèle vision-langage qui projette les images et les textes
     dans le même espace vectoriel.
   - L’architecture ViT-B/32 utilise un Vision Transformer pour encoder les images.
   - Le modèle a été entraîné sur des milliards de paires image–texte (dataset LAION),
     ce qui lui permet d’effectuer de la classification zero-shot et des tâches
     de similarité sémantique sans entraînement supplémentaire.
   - Dans ce script, OpenCLIP est utilisé pour encoder à la fois l’image et les
     prompts textuels, puis pour calculer la similarité cosinus entre eux.

2. Llama-3.2-1B-Instruct
   - Un modèle de langage léger, entraîné pour suivre des instructions,
     développé par :contentReference[oaicite:0]{index=0}.
   - Il est utilisé ici pour générer plusieurs variations courtes du prompt initial.
   - Les variations de prompt améliorent la robustesse car CLIP peut mieux
     correspondre à certaines formulations qu’à d’autres.
   - Cette technique est souvent appelée « prompt ensembling ».

Pipeline
--------

1. Chargement du modèle OpenCLIP et du prétraitement des images.
2. Encodage de l’image d’entrée en un vecteur d’embedding.
3. Utilisation de Llama pour générer des variations du prompt utilisateur.
4. Encodage de tous les prompts avec l’encodeur texte de CLIP.
5. Calcul de la similarité entre l’embedding de l’image et ceux des textes.
6. Affichage des scores de similarité et de la distribution de probabilité
   sur les différents prompts.

Pourquoi cette approche ?
-------------------------

- CLIP est très performant pour mesurer la similarité multimodale entre images et texte.
- Les variations de prompts générées par un LLM permettent de mieux couvrir
  les différentes descriptions possibles d’une image.
- La combinaison des deux améliore la fiabilité du matching image–texte
  en zero-shot sans nécessiter d’entraînement spécifique à la tâche.
"""

load_dotenv()

def load_openclip_model(model_name='ViT-B-32', pretrained='laion2b_s34b_b79k'):
    model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
    model.eval()
    tokenizer = open_clip.get_tokenizer(model_name)
    return model, tokenizer, preprocess

def encode_image(model, preprocess, img_path):
    image = preprocess(Image.open(img_path)).unsqueeze(0)
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features

def encode_text(model, tokenizer, prompts):
    tokenized = tokenizer(prompts)
    with torch.no_grad():
        text_features = model.encode_text(tokenized)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features

def compute_similarity(image_features, text_features):
    similarity = (image_features @ text_features.T).item()
    return similarity

def compute_label_probs(image_features, text_features):
    logits = 100.0 * image_features @ text_features.T
    probs = logits.softmax(dim=-1)
    return probs

def generate_text_variations(
    prompt: str,
    num_variations: int,
    model_name: str = "meta-llama/Llama-3.2-1B-Instruct",
    temperature: float = 0.7,
    top_p: float = 0.9,
    repetition_penalty: float = 1.2,
    max_new_tokens=200
):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN not found in environment variables.")

    login(token=token)

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")

    outputs = model.generate(
        inputs["input_ids"],
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        max_new_tokens=max_new_tokens
    )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    )

    response = response.split("assistant")[-1].strip()
    lines = [l.strip("0123456789. ").strip() for l in response.split("\n") if l.strip()]

    return lines[:num_variations]

def main():
    parser = argparse.ArgumentParser(description="OpenCLIP image-text similarity")
    parser.add_argument("--image", "-i", required=True, help="Path to the input image")
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt to compare with the image")
    parser.add_argument("--num_variations", "-n", type=int, required=True, help="Number of prompt variations")
    args = parser.parse_args()

    model, tokenizer, preprocess = load_openclip_model()

    image_features = encode_image(model, preprocess, args.image)

    # Generate prompt variations dynamically
    llm_prompt = (
        f"Give {args.num_variations} short variations of '{args.prompt}'.\n"
        f"Each variation must stay about a rubber duck.\n"
        "Maximum 5 words per variation.\n"
        "No numbering. No explanations."
    )
    print(f"llm_prompt: {llm_prompt}")

    
    generated_variations = generate_text_variations(
        prompt=llm_prompt,
        num_variations=args.num_variations
    )
    print(f"generated_variations: {generated_variations}")
    # Combine original prompt + generated variations
    text_prompts = [args.prompt] + generated_variations

    print("Generated prompts:", text_prompts)

    text_features = encode_text(model, tokenizer, text_prompts)
    text_features_solo = encode_text(model, tokenizer, [args.prompt])

    label_probs = compute_label_probs(image_features, text_features)
    similarity = compute_similarity(image_features, text_features_solo)

    print("Label probs:", label_probs[0].tolist())
    print(f"Cosine similarity with '{args.prompt}': {similarity:.4f}")

if __name__ == "__main__":
    main()