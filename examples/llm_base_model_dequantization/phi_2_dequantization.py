import logging

import yaml

from ludwig.api import LudwigModel
from ludwig.utils.hf_utils import upload_folder_to_hfhub

base_model_name = "microsoft/phi-2"
dequantized_path = "microsoft-phi-2-dequantized"
save_path = "/home/ray/" + dequantized_path
hfhub_repo_id = "arnavgrg/" + dequantized_path


config = yaml.safe_load(
    """
    model_type: llm
    base_model: microsoft/phi-2

    quantization:
      bits: 4

    input_features:
      - name: instruction
        type: text

    output_features:
      - name: output
        type: text

    trainer:
        type: none

    backend:
      type: local
  """
)

# Define Ludwig model object that drive model training
model = LudwigModel(config=config, logging_level=logging.INFO)
model.save_dequantized_base_model(save_path=save_path)

# Optional: Upload to Huggingface Hub
upload_folder_to_hfhub(repo_id=hfhub_repo_id, folder_path=save_path)
