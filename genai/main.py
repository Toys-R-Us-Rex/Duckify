from pathlib import Path
from source.model import TextureModel
from dotenv import load_dotenv
import os
def main():
    load_dotenv()
    base_path = Path("workspace")
    

    texture_model = TextureModel(base_path=base_path, hf_token=os.environ.hf_token)

    obj_file = Path("models/my_mesh.obj")  


    text_prompt = "A blue duck with a red nose"

    try:

        experiment_path = texture_model.run(text_prompt=text_prompt, obj_file=obj_file)
        print(f"Finished! Results are in: {experiment_path.resolve()}")
    except Exception as e:
        print("Error running TEXTure:", e)


if __name__ == "__main__":
    main()