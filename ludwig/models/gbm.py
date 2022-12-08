import os
from typing import Dict, Optional, Tuple, Union

import lightgbm as lgb
import numpy as np
import torch
import torchmetrics
from hummingbird.ml import convert
from hummingbird.ml.operator_converters import constants as hb_constants

from ludwig.constants import BINARY, LOGITS, MODEL_GBM, NAME, NUMBER
from ludwig.features.base_feature import OutputFeature
from ludwig.globals import MODEL_WEIGHTS_FILE_NAME
from ludwig.models.base import BaseModel
from ludwig.schema.model_config import ModelConfig, OutputFeaturesContainer
from ludwig.utils import output_feature_utils
from ludwig.utils.torch_utils import get_torch_device
from ludwig.utils.types import TorchDevice


class GBM(BaseModel):
    @staticmethod
    def type() -> str:
        return MODEL_GBM

    def __init__(
        self,
        config_obj: ModelConfig,
        random_seed: int = None,
        **_kwargs,
    ):
        self.config_obj = config_obj
        self._random_seed = random_seed

        super().__init__(random_seed=self._random_seed)

        # ================ Inputs ================
        try:
            self.input_features.update(self.build_inputs(input_feature_configs=self.config_obj.input_features))
        except KeyError as e:
            raise KeyError(
                f"An input feature has a name that conflicts with a class attribute of torch's ModuleDict: {e}"
            )

        # ================ Outputs ================
        self.output_features.update(
            self.build_outputs(output_feature_configs=self.config_obj.output_features, input_size=self.input_shape[-1])
        )

        # ================ Combined loss metric ================
        self.eval_loss_metric = torchmetrics.MeanMetric()
        self.eval_additional_losses_metrics = torchmetrics.MeanMetric()

        self.lgbm_model: lgb.LGBMModel = None
        self.compiled_model: torch.nn.Module = None

    @classmethod
    def build_outputs(
        cls, output_feature_configs: OutputFeaturesContainer, input_size: int
    ) -> Dict[str, OutputFeature]:
        """Builds and returns output feature."""
        # TODO: only single task currently
        if len(output_feature_configs.to_dict()) > 1:
            raise ValueError("Only single task currently supported")

        output_feature_def = output_feature_configs.to_list()[0]
        output_features = {}

        setattr(getattr(output_feature_configs, output_feature_def[NAME]), "input_size", input_size)
        output_feature = cls.build_single_output(
            getattr(output_feature_configs, output_feature_def[NAME]), output_features
        )
        output_features[output_feature_def[NAME]] = output_feature

        return output_features

    def compile(self):
        """Convert the LightGBM model to a PyTorch model and store internally."""
        if self.lgbm_model is None:
            raise ValueError("Model has not been trained yet.")

        # explicitly use sigmoid for classification, so we can invert to logits at inference time
        extra_config = (
            {hb_constants.POST_TRANSFORM: hb_constants.SIGMOID}
            if isinstance(self.lgbm_model, lgb.LGBMClassifier)
            else {}
        )
        self.compiled_model = convert(self.lgbm_model, "torch", extra_config=extra_config)

    def forward(
        self,
        inputs: Union[
            Dict[str, torch.Tensor], Dict[str, np.ndarray], Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]
        ],
        mask=None,
    ) -> Dict[str, torch.Tensor]:
        # Invoke output features.
        output_logits = {}
        output_feature_name = self.output_features.keys()[0]
        output_feature = self.output_features[output_feature_name]

        # If `inputs` is a tuple, it should contain (inputs, targets). When using the LGBM sklearn interface, targets
        # is not needed, so we extract the inputs here.
        if isinstance(inputs, tuple):
            inputs, _ = inputs

        assert list(inputs.keys()) == self.input_features.keys()

        # The LGBM sklearn interface works with array-likes, so we place the inputs into a 2D numpy array.
        in_array = np.stack(list(inputs.values()), axis=0).T

        # Predict on the input batch. The predictions are then converted to torch tensors so that we can pass them to
        # the existing metrics modules.
        if output_feature.type() == NUMBER:
            # Input: 2D eval_batch_size x n_features array
            # Output: 1D eval_batch_size array
            preds = torch.from_numpy(self.lgbm_model.predict(in_array))
            logits = preds.view(-1)
        else:
            # Input: 2D eval_batch_size x n_features array
            # Output: 2D eval_batch_size x n_classes array
            probs = torch.from_numpy(self.lgbm_model.predict_proba(in_array))
            if output_feature.type() == BINARY:
                probs = torch.logit(probs[:, 1])
            logits = probs

        output_feature_utils.set_output_feature_tensor(output_logits, output_feature_name, LOGITS, logits)

        return output_logits

    def save(self, save_path):
        """Saves the model to the given path."""
        if self.lgbm_model is None:
            raise ValueError("Model has not been trained yet.")

        import joblib

        weights_save_path = os.path.join(save_path, MODEL_WEIGHTS_FILE_NAME)
        joblib.dump(self.lgbm_model, weights_save_path)

    def load(self, save_path):
        """Loads the model from the given path."""
        import joblib

        weights_save_path = os.path.join(save_path, MODEL_WEIGHTS_FILE_NAME)
        self.lgbm_model = joblib.load(weights_save_path)

        self.compile()

        device = torch.device(get_torch_device())
        self.compiled_model.to(device)

    def to_torchscript(self, device: Optional[TorchDevice] = None):
        """Converts the ECD model as a TorchScript model."""

        # Disable gradient calculation for hummingbird Parameter nodes.
        self.compiled_model.model.requires_grad_(False)

        return super().to_torchscript(device)

    def get_args(self):
        """Returns init arguments for constructing this model."""
        return self.config_obj.input_features.to_list(), self.config_obj.output_features.to_list(), self._random_seed
