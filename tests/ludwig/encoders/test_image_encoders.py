import pytest
import torch

from ludwig.encoders.image_encoders import (
    HFResNetEncoder,
    MLPMixerEncoder,
    ResNetEncoder,
    Stacked2DCNN,
    TVResNetEncoder,
    TVVGGEncoder,
    ViTEncoder,
)
from ludwig.utils.misc_utils import set_random_seed
from tests.integration_tests.parameter_update_utils import check_module_parameters_updated

RANDOM_SEED = 1919


@pytest.mark.parametrize("height,width,num_conv_layers,num_channels", [(224, 224, 5, 3)])
def test_stacked2d_cnn(height: int, width: int, num_conv_layers: int, num_channels: int):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    stacked_2d_cnn = Stacked2DCNN(
        height=height, width=width, num_conv_layers=num_conv_layers, num_channels=num_channels
    )
    inputs = torch.rand(2, num_channels, height, width)
    outputs = stacked_2d_cnn(inputs)
    assert outputs["encoder_output"].shape[1:] == stacked_2d_cnn.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(stacked_2d_cnn, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("height,width,num_channels", [(224, 224, 1), (224, 224, 3)])
def test_resnet_encoder(height: int, width: int, num_channels: int):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    resnet = ResNetEncoder(height=height, width=width, num_channels=num_channels)
    inputs = torch.rand(2, num_channels, height, width)
    outputs = resnet(inputs)
    assert outputs["encoder_output"].shape[1:] == resnet.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(resnet, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("height,width,num_channels", [(224, 224, 3)])
def test_mlp_mixer_encoder(height: int, width: int, num_channels: int):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    mlp_mixer = MLPMixerEncoder(height=height, width=width, num_channels=num_channels)
    inputs = torch.rand(2, num_channels, height, width)
    outputs = mlp_mixer(inputs)
    assert outputs["encoder_output"].shape[1:] == mlp_mixer.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(mlp_mixer, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("image_size,num_channels", [(224, 3)])
@pytest.mark.parametrize("use_pretrained", [True, False])
def test_vit_encoder(image_size: int, num_channels: int, use_pretrained: bool):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    vit = ViTEncoder(
        height=image_size,
        width=image_size,
        num_channels=num_channels,
        use_pretrained=use_pretrained,
        output_attentions=True,
    )
    inputs = torch.rand(2, num_channels, image_size, image_size)
    outputs = vit(inputs)
    assert outputs["encoder_output"].shape[1:] == vit.output_shape
    config = vit.transformer.config
    num_patches = (224 // config.patch_size) ** 2 + 1  # patches of the image + cls_token
    attentions = outputs["attentions"]
    assert len(attentions) == config.num_hidden_layers
    assert attentions[0].shape == torch.Size([2, config.num_attention_heads, num_patches, num_patches])

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(vit, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("height,width,num_channels", [(224, 224, 3)])  # todo: do we need to specify
@pytest.mark.parametrize("remove_last_layer", [True, False])
@pytest.mark.parametrize(
    "use_pretrained_weights",
    [
        False,
    ],
)  # TODO: do we need to check download, True])
@pytest.mark.parametrize(
    "pretrained_model_type, pretrained_model_variant",
    [
        ("tv_resnet", 18),
        ("tv_resnet", 34),
        ("tv_resnet", 50),
        ("tv_resnet", 101),
        ("tv_resnet", 152),
    ],
)
def test_tv_resnet_encoder(
    pretrained_model_type: str,
    pretrained_model_variant: int,
    use_pretrained_weights: bool,
    remove_last_layer: bool,
    height: int,
    width: int,
    num_channels: int,
):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    pretrained_model = TVResNetEncoder(
        height=height,
        width=width,
        num_channels=num_channels,
        pretrained_model_type=pretrained_model_type,
        pretrained_model_variant=pretrained_model_variant,
        remove_last_layer=remove_last_layer,
        use_pretrained_weights=use_pretrained_weights,
    )
    inputs = torch.rand(2, num_channels, height, width)
    outputs = pretrained_model(inputs)
    assert outputs["encoder_output"].shape[1:] == pretrained_model.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(pretrained_model, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("height,width,num_channels", [(224, 224, 3)])  # todo: do we need to specify
@pytest.mark.parametrize("remove_last_layer", [True, False])
@pytest.mark.parametrize(
    "use_pretrained_weights",
    [
        False,
    ],
)  # TODO: do we need to check download, True])
@pytest.mark.parametrize(
    "pretrained_model_type, pretrained_model_variant",
    [
        ("vgg", 11),
        ("vgg", 16),
        ("vgg", 19),
    ]
)
def test_tv_vgg_encoder(
        pretrained_model_type: str,
        pretrained_model_variant: int,
        use_pretrained_weights: bool,
        remove_last_layer: bool,
        height: int,
        width: int,
        num_channels: int
):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    pretrained_model = TVVGGEncoder(
        height=height,
        width=width,
        num_channels=num_channels,
        pretrained_model_type=pretrained_model_type,
        pretrained_model_variant=pretrained_model_variant,
        remove_last_layer=remove_last_layer,
        use_pretrained_weights=use_pretrained_weights,
    )
    inputs = torch.rand(2, num_channels, height, width)
    outputs = pretrained_model(inputs)
    assert outputs["encoder_output"].shape[1:] == pretrained_model.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(pretrained_model, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."


@pytest.mark.parametrize("height,width,num_channels", [(224, 224, 3)])  # todo: do we need to specify
@pytest.mark.parametrize("use_pre_trained_weights", [False, True])  # TODO: do we need to check download, True])
@pytest.mark.parametrize("resnet_size", [18, 34, 50, 101, 152])
def test_hf_resnet_encoder(resnet_size: int, use_pre_trained_weights: bool, height: int, width: int, num_channels: int):
    # make repeatable
    set_random_seed(RANDOM_SEED)

    resnet = HFResNetEncoder(
        height=height,
        width=width,
        num_channels=num_channels,
        resnet_size=resnet_size,
        use_pre_trained_weights=use_pre_trained_weights,
    )
    inputs = torch.rand(2, num_channels, height, width)
    outputs = resnet(inputs)
    assert outputs["encoder_output"].shape[1:] == resnet.output_shape

    # check for parameter updating
    target = torch.randn(outputs["encoder_output"].shape)
    fpc, tpc, upc, not_updated = check_module_parameters_updated(resnet, (inputs,), target)

    assert tpc == upc, f"Not all expected parameters updated.  Parameters not updated {not_updated}."
