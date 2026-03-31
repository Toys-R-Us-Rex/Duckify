#set text(size: 11pt)
#set par(justify: true, leading: 0.6em)

#v(0.5em)

== Objectif
#block[
- Finetuner le modèle pré-entraîné pour améliorer la génération de mesh texturée.
]

#v(0.3em)

== Contraintes
#grid(
  columns: 2,
  gutter: 1em,

  [
  *Données*  
  - Meshes 3D texturés requis
  - Dataset limité par crédit
  - Peu de données open-source 
  ],

  [
  *Copyright*  
  - Difficulté avec IP (jeux vidéo/superhéro)   
  ],

  [
  *Modèle*    
  - Faible généralisation concepts récents ( fortnite / mr beast )  
  - Meilleur sur concepts génériques  
  ],

  [
  *Entraînement*  
  - Batch size = 1 (6 vues)  
  - Ressources limitées par limite de quota ( Disco ) 
  - Data augmentation nécessaire   
  ],
)

#v(0.3em)

== Outils et technologies
#grid(
  columns: 2,
  gutter: 1em,

  [
  *Génération 3D*  
  - Meshy (texturé, limité)  
  - Hunyuan3D-2 (non texturé)  
  - Hunyuan3D-2.1 (texturé, quota)  
  ],

  [
  *Dataset*  
  - MV-Adapter pipeline  
  - RGB, normales, positions  
  - Ortho10View  
  ],

  [
  *Modèle*  
  - MV-Adapter  
  - DreamShaper XL  
  - SDXL VAE (fp16)  
  - PyTorch Lightning  
  ],

  [
  *Infrastructure & scripting*  
  - Orchestration avec *Slurm*  
  - Entraînement distribué sur serveur *Disco*  
  - Collaboration technique avec *Marc Pignat* pour libérer des quotas
  - Mise en local de Hunyuan3D-2.1 pour ne plus avoir de quota
  ],
)

#v(0.3em)

== Observations clés
#block[
- Concepts connus → amélioration rapide.
- Concepts peu représentés → besoin élevé en données.
- Meilleures performances sur **catégories génériques non protégées**.
]

== Scalabilité
La pipeline mesh puis multiview puis training est facilement extensible. L’utilisation de Slurm permet d’automatiser les runs et de scaler les expérimentations.

== Apprentissage

Le modèle dépend fortement de ses connaissances initiales. Avec peu de données, il apprend des éléments simples (comme les couleurs) mais pas des concepts complexes.

== Décision  
Le finetuning actuel n’est pas suffisant pour une utilisation en production. Il est nécessaire de :
- augmenter fortement la taille du dataset,
- améliorer la qualité des meshes et des textures,
- affiner la stratégie de finetuning.



#v(0.5em)
#line(length: 100%)

#v(0.3em)

#text(size: 9pt, fill: gray)[
*Overview résumé généré via LLM — vue d’ensemble* ]




#set page(
  paper: "a4",
  margin: 1in,
)

#set par(justify: true)
#set heading(numbering: "1.")
#set text(size: 11pt)

= Finetuning MV-Adapter


== Overview

The goal is to have a broad understanding of the requirement in order to train our own custom adapter.

=== Dataset overview

The dataset architecture is given in the following form: 

#figure(
  image("images/dataset.JPG", width: 100%),
  caption: [dataset],
)

It's a folder containing reference folder and json files, the reference folder contains image generation.

There is 2 kind of dataset given. 

Ortho10View has 10 fixed views, always the same 10, it contains 10 fixed views of colored rendered of the mesh.

#figure(
  image("images/ortho.JPG", width: 30%),
  caption: [dataset ortho],
)


Rand6View has 6 random views. 

#figure(
  image("images/rand6.JPG", width: 30%),
  caption: [dataset rand6view],
)


The main difference is that in between object the views of rand6view will be randomized, this making it suitable for image conditioning.
While Ortho10View has fixed view, this making it usable for texture conditioning.



== Execution

This is the default code.

```yaml
data_cls: mvadapter.data.multiview.MultiviewDataModule
data:
  root_dir: data/Ortho10View/data
  scene_list: data/Ortho10View/list_6w.json
  background_color: gray
  image_names: ["0000", "0001", "0002", "0003", "0004", "0005"]
  image_modality: color
  num_views: 6

  prompt_db_path: data/Ortho10View/captions.json
  return_prompt: true

  projection_type: ORTHO

  source_image_modality: ["position", "normal"]
  position_offset: 0.5
  position_scale: 1.0

  train_indices: [0, -8]
  val_indices: [-8, null]
  test_indices: [-8, null]

  height: 768
  width: 768

  batch_size: 1
  num_workers: 16)

  
system_cls: mvadapter.systems.mvadapter_text_sdxl.MVAdapterTextSDXLSystem
system:
  check_train_every_n_steps: 1000
  cleanup_after_validation_step: true
  cleanup_after_test_step: true

  # Model / Adapter
  pretrained_model_name_or_path: "Lykon/dreamshaper-xl-1-0"
  pretrained_vae_name_or_path: "madebyollin/sdxl-vae-fp16-fix"
  pretrained_adapter_name_or_path: "/home/marco.caporizzi/MV-Adapter_mine/weight/mvadapter_tg2mv_sdxl.safetensors"
  init_adapter_kwargs:
    # Multi-view adapter
    self_attn_processor: "mvadapter.models.attention_processor.DecoupledMVRowColSelfAttnProcessor2_0"
    # Condition encoder
    cond_in_channels: 6
    # For training
    copy_attn_weights: true
    zero_init_module_keys: ["to_out_mv"]

  # Training
  train_cond_encoder: true
  trainable_modules: ["_mv"]
  prompt_drop_prob: 0.1
  image_drop_prob: 0.1
  cond_drop_prob: 0.1

  # Noise sampler
  shift_noise: true
  shift_noise_mode: interpolated
  shift_noise_scale: 8

  # Evaluation
  eval_seed: 42
  eval_num_inference_steps: 30
  eval_guidance_scale: 3.0
  eval_height: ${data.height}
  eval_width: ${data.width}

  # optimizer definition
  # you can set different learning rates separately for each group of parameters, but note that if you do this you should specify EVERY trainable parameters
  optimizer:
    name: AdamW
    args:
      lr: 5e-5
      betas: [0.9, 0.999]
      weight_decay: 0.01
    params:
      cond_encoder:
        lr: 5e-5
      unet:
        lr: 5e-5

  scheduler:
    name: SequentialLR
    interval: step
    schedulers:
      - name: LinearLR
        interval: step
        args:
          start_factor: 1e-6
          end_factor: 1.0
          total_iters: 2000
      - name: ConstantLR
        interval: step
        args:
          factor: 1.0
          total_iters: 9999999
    milestones: [2000]

trainer:
  max_epochs: 10
  log_every_n_steps: 10
  num_sanity_val_steps: 1
  val_check_interval: null # changed this to not hit 
  check_val_every_n_epoch: 1
  enable_progress_bar: true
  precision: bf16-mixed
  gradient_clip_val: 1.0
  strategy: ddp
  accumulate_grad_batches: 1

checkpoint:
  save_last: true # whether to save at each validation time
  save_top_k: -1
  every_n_epochs: 9999 # do not save at all for debug purpose```

= Problem analysis

Notre génération de canard est basé sur des poids de modèles pré-entrainés.

On souhaiterais dans un premier temps finetune notre modèle afin qu'il soit très bon sur la génération de canard.

On a identifié que le modèle pouvait être finetune sur le point suivant: génération de texture copyrighted. 

Les données avec une IP active sont difficiles à trouver pour les jeux-video par example elles sont toujours actives.
En effet, lors de notre batch d'execution, les résultats étaient bien plus concluant sur les héro que sur les jeux-vidéo.
Ceci peut s'expliquer par le fait que les ip de super-héro sont plus vieille que les données de jeux-video qui sont probablement active.
C'est pourquoi il est difficile de générer un canard mario ou un canard sonic plutôt qu'un canard batman ou superman.

C'est pourquoi l'un de nos angles d'attaque est de pouvoir nourrir de modele de données qui sont copyright. 

== Génération des données

Afin de pouvoir entraîner notre modèle, l'entrainement de MV-Adapter nous oblige à avoir des meshs texturés.

C'est pour cela que dans une première phase, il faut trouver une solution de génération de meshs texturés qui puissent être gratuites et réutilisation.

=== Meshy

Une solution est de se tourner vers [Meshy](https://www.meshy.ai/fr/discover) qui permet de la génération de mesh et de texture.

#image("image.png")

Il y a 100 crédits par mois pour le gratuit.

Le nombre de téléchargement à 10 par mois.


=== Hunyuan3D-2: High Resolution Textured 3D Assets Generation

Ici, une solution sur un espace hugginsface.

#figure(
  image("images/2.JPG", width: 80%),
  caption: [dataset ortho],
)

Mais le mesh est généré sans texture.

=== Hunyuan-3D-2.1

Ici, le modèle plus récent de Hunyuan de chez tencent qui permet jusqu'à 10 mesh texturées par jour avec la version pro à 9chf par mois.

#image("image (1).png")

=== Décision pour la génération de texture

On préfère épuiser les crédits gratuit de meshy et de Hunyuan3D-2 afin de collecter le plus de données possibles.

Suite à la mise en pause du space, une solution plus axé sur la production a été mise en place, du temps a été pris pour la mise en place de Hunyuan3D-2 avec l'execution sur disco. Ceci est une solution gratuite car elle n'utilise pas de crédit.

== Objectif du finetuning 

Le modèle sait générer des superhéros et personnages de jeux-vidéos, le modèle sait générer des canards mais il ne sait pas générer des canards superhéro ou canards jeux-videos.

=== Création dataset itération sur les personnages de jeux-video

Un des premiers aspect qu'on souhaitait améliorer est la génération d'image copyright. Par exemple, des canards de jeux video: mario, bowser, samus, kratos, sonic.

Cependant, le modèle pré-entrainé n'a pas de résultat concluant de base. 

Dans le cas d'un canard mario, l'idée d'un canard avec une casquette rouge et une salopette bleu n'est pas facile à générer.

C'est pour cela, on préfère se diriger vers une génération déjà satisfaisant comme les superhéro.

#image("image (2).png", width: 30%, )

https://hessoit-my.sharepoint.com/:x:/g/personal/marco_caporizz_hes-so_ch/IQDrMgm9IqLhQ6puCEYr6sdQAXm-EBmT_VTb7w8GNZKG67A?e=BeQ7Bx

=== Conclusion local

L'une des contraintes rencontré est de bien définir les capacités du modèles pré-entrainé: si le modèle ne génère pas des images copyrightés facilement ( mario, sonic ), la phase de finetuning devra comprendre la phase d'apprentissage d'un mario et d'un sonic. Ceci implique plus de données d'apprentissage que pour un concept que le modèle sait déjà généré.



=== Création du dataset itération sur les superhéros

Les générations de canard sur les superhéro sont les plus réussis. Les ip sont anciennes, il y a plus de données et les logos sont réussis.

Cependant, les données copyrightés ont été exclus car les prompts donnée à notre modèle de diffusion ( GPT image ) était sous copyright donc la génération était annulée.

#image("image (3).png", width: 30%)

=== Conclusion local 

Un dataset ne doit pas contenir de copyright pour assurer la reproduction.

=== Création du dataset itération sur les métiers

Les canards pompiers, de chantier ou astronaute ne sont pas soumis à copyright. 

Leur générations pour les modèles pré-entraîné est satisfaisante, comme montrer dans la figure 5,6,7.

#figure(
  image("images/astro.JPG", width: 100%),
  caption: [Astronaute model pré-trained],
)

#figure(
  image("images/fire.JPG", width: 100%),
  caption: [Pompier model pré-trained],
)

#figure(
  image("images/consworker.JPG", width: 100%),
  caption: [Chantier model pré-trained],
)

Alors afin de récolter des données, j'ai généré les meshs correspondantes.

#figure(
  image("images/as.JPG", width: 30%),
  caption: [Astronaute Hunyuan Textured Mesh Generator],
)

#figure(
  image("images/fi.JPG", width: 30%),
  caption: [Pompier Hunyuan Textured Mesh Generator],
)

#figure(
  image("images/co.JPG", width: 30%),
  caption: [Chantier Hunyuan Textured Mesh Generator],
)

Puis j'ai passé chaque meshs texturés dans le multiview creator pour le training.

#figure(
  image("images/asmv.JPG", width: 100%),
  caption: [Astronaute MV-Adapter Multiview Generator],
)

#figure(
  image("images/fimv.JPG", width: 100%),
  caption: [Pompier MV-Adapter Multiview Generator],
)

#figure(
  image("images/comv.JPG", width: 100%),
  caption: [Chantier MV-Adapter Multiview Generator],
)

la normal et la position du canard en 3d.

=== Finetuning params

Mon set est divisé en 80% pour le training, 10% pour la validation et 10% pour le test. 

Mon batch est de 1 mais il comprend toujours 6 views.

Lors de la phase de validation de l'entraînement, on remarque que le modèle génère des canards différents, on suppose qu'il apprend.

#figure(
  image("images/it72-validation-0_2.jpg", width: 100%),
  caption: [Phase de validation],
)

#figure(
  image("images/it144-validation-0_2.jpg", width: 100%),
  caption: [Phase de validation],
)

#figure(
  image("images/it216-validation-0_2.jpg", width: 100%),
  caption: [Phase de validation],
)

#pagebreak()
== Finetuning 

Le dataset est maintenant composé de 200 canards de textures différentes. 

Le but est maintenant d'entrainer le modèle pré-entrainé sur les multiview des canards présentés.

== Inference

Le canard chantier:

#figure(
  image("images/ftune_1_cowr.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

#figure(
  image("images/ftune_1_cowr2.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

#figure(
  image("images/ftune_1_cowr3.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

#figure(
  image("images/ftune_1_cowr4.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

#figure(
  image("images/ftune_1_cowr5.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

Le canard pompier:

#figure(
  image("images/ftune_1_fire.png", width: 100%),
  caption: [Inference avec prompt pompier gen1],
)

#figure(
  image("images/ftune_1_fire2.png", width: 100%),
  caption: [Inference avec prompt pompier gen1],
)

#figure(
  image("images/ftune_1_fire3.png", width: 100%),
  caption: [Inference avec prompt pompier gen1],
)

#figure(
  image("images/ftune_1_fire4.png", width: 100%),
  caption: [Inference avec prompt pompier gen1],
)

#figure(
  image("images/ftune_1_fire5.png", width: 100%),
  caption: [Inference avec prompt pompier gen1],
)

Le canard astronaute:

#figure(
  image("images/ftune_1_nasa.png", width: 100%),
  caption: [Inference avec prompt astronaute gen1],
)

#figure(
  image("images/ftune_1_nasa2.png", width: 100%),
  caption: [Inference avec prompt astronaute gen1],
)

#figure(
  image("images/ftune_1_nasa3.png", width: 100%),
  caption: [Inference avec prompt astronaute gen1],
)

#figure(
  image("images/ftune_1_nasa4.png", width: 100%),
  caption: [Inference avec prompt astronaute gen1],
)

#figure(
  image("images/ftune_1_nasa5.png", width: 100%),
  caption: [Inference avec prompt astronaute gen1],
)

== Evaluation 

L'évaluation humaine est de constater que les traits qui concernent un pompier, astronaute ou du chantier n'apparaissent plus. 

Il a cependant très bien appris à placer les couleurs au niveau de la tête.

== Finetuning data augmented

Le dataset est maintenant composé de 200 canards de textures différentes. 

Les canards ont été dupliqué par 10. Les données de couleur ont été légerment haltéré.

Le but est maintenant d'entrainer le modèle pré-entrainé sur les multiview des canards présentés.


=== Inference

Ici l'inférence avec nos poids custom issue de l'entraînement.

Le canard chantier:

#figure(
  image("images/ftune_2_cowr.png", width: 100%),
  caption: [Inference avec prompt chantier gen1],
)

#figure(
  image("images/ftune_2_cowr2.png", width: 100%),
  caption: [Inference avec prompt chantier gen2],
)

#figure(
  image("images/ftune_2_cowr3.png", width: 100%),
  caption: [Inference avec prompt chantier gen3],
)

#figure(
  image("images/ftune_2_cowr4.png", width: 100%),
  caption: [Inference avec prompt chantier],
)

#figure(
  image("images/ftune_2_cowr5.png", width: 100%),
  caption: [Inference avec prompt chantier],
)

#pagebreak()
Le canard pompier

#figure(
  image("images/ftune_2_fire.png", width: 100%),
  caption: [Inference avec prompt pompier],
)

#figure(
  image("images/ftune_2_fire2.png", width: 100%),
  caption: [Inference avec prompt pompier],
)

#figure(
  image("images/ftune_2_fire3.png", width: 100%),
  caption: [Inference avec prompt pompier],
)

#figure(
  image("images/ftune_2_fire4.png", width: 100%),
  caption: [Inference avec prompt pompier],
)

#figure(
  image("images/ftune_2_fire5.png", width: 100%),
  caption: [Inference avec prompt pompier],
)

#pagebreak()

Le canard astronaute:

#figure(
  image("images/ftune_2_nasa.png", width: 100%),
  caption: [Inference avec prompt astronaute],
)

#figure(
  image("images/ftune_2_nasa2.png", width: 100%),
  caption: [Inference avec prompt astronaute],
)

#figure(
  image("images/ftune_2_nasa3.png", width: 100%),
  caption: [Inference avec prompt astronaute],
)

#figure(
  image("images/ftune_2_nasa4.png", width: 100%),
  caption: [Inference avec prompt astronaute],
)

#figure(
  image("images/ftune_2_nasa5.png", width: 100%),
  caption: [Inference avec prompt astronaute],
)


== Evaluation 

Précédent finetuning:
L'évaluation humaine est de constater que les traits qui concernent un pompier, astronaute ou du chantier n'apparaissent plus. 

Il a cependant très bien appris à placer les couleurs au niveau de la tête.

Ici, il n'y pas d'amélioration lors de l'inférence après l'augmentation de donnée.

#pagebreak()
= Décision Finetuning

L'inférence n'a pas donné les résultats attendues.

L'apprentissage suite au finetuning réduit la qualité des canards générés. En effet, le prompt est moins bien respecté.

== Phase de production

Plus de temps doit être accordé au finetuning, afin de pouvoir remplacer le modèle pré-entrainé par un modèle custom.
Un dataset plus grand et plus varié doit être généré.
La génération de données (mesh puis multiview puis training) peut être facilement étendue.
Les scripts SLURM permettent d'automatiser les runs

== Apprentissage

Le finetuning dépend fortement de ce que le modèle sait déjà faire.
Peu de données, le modèle apprend surtout des patterns simples comme des couleurs, mais pas des concepts complexes.
