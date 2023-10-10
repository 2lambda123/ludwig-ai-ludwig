import torch
from ludwig.api import LudwigModel
from abc import ABC, abstractmethod
from ludwig.model_export.base_model_exporter import BaseModelExporter
import torch
import coremltools as ct

class CoreMLExporter(BaseModelExporter):

    @abstractmethod
    def forward(self, x):
        return self.model({"image_path": x})

    def export_classifier(self, model_path, export_path):
        ludwig_model = LudwigModel.load(model_path)
        model = CoreMLExporter(ludwig_model.model)  # Wrap the model

        width = ludwig_model.config["input_features"][0]["preprocessing"]["width"]
        height = ludwig_model.config["input_features"][0]["preprocessing"]["height"]
        example_input = torch.randn(1, 3, width, height, requires_grad=True)

        # Create the model and load the weights
        ludwig_model.load_state_dict(torch.load(model_path))
        # Trace the model
        traced_model = torch.jit.trace(model, example_input)
        # Create the input image type
        input_image = ct.ImageType(name=example_input, shape=(1, 3, width, height), scale=1/255)
        # Convert the model
        coreml_model = ct.convert(traced_model, inputs=[input_image])

        # Modify the output's name to "my_output" in the spec
        spec = coreml_model.get_spec()
        ct.utils.rename_feature(spec, "81", export_path)

        # Re-create the model from the updated spec
        coreml_model_updated = ct.models.MLModel(spec)

        # Save the CoreML model
        coreml_model_updated.save(export_path)