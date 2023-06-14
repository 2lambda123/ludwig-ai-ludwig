from typing import Dict, Tuple

import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer, GPT2TokenizerFast, LlamaTokenizer, LlamaTokenizerFast, PreTrainedTokenizer

from ludwig.constants import LOGITS, PREDICTIONS, PROBABILITIES


def has_padding_token(input_tensor: torch.Tensor, tokenizer: PreTrainedTokenizer):
    """Checks if the input tensor contains any padding tokens.

    Args:
        input_tensor (torch.Tensor): The input tensor.
        tokenizer (PreTrainedTokenizer): The tokenizer used to encode the input.

    Returns:
        bool: True if the input tensor contains any padding tokens, False otherwise.

    Example:
        >>> import torch
        >>> from transformers import PreTrainedTokenizer
        >>> tokenizer = PreTrainedTokenizer.from_pretrained('bert-base-uncased')
        >>> input_sentence = "This is an example sentence."
        >>> input_ids = tokenizer.encode(input_sentence, add_special_tokens=True)
        >>> padded_input_ids = torch.nn.functional.pad(input_ids, (0, 10 - len(input_ids)))
        >>> has_padding = has_padding_token(padded_input_ids, tokenizer)
        >>> has_padding
        True
    """
    return torch.any(input_tensor == tokenizer.pad_token_id).item()


def add_left_padding(input_ids, max_length, pad_value=0):
    """Adds left padding to the input_ids tensor.

    Args:
        input_ids (torch.Tensor): The input tensor.
        max_length (int): The maximum length of the tensor after padding.
        pad_value (int, optional): The value used for padding. Defaults to 0.

    Returns:
        torch.Tensor: The input_ids tensor with left padding.

    Example:
        >>> input_ids = torch.tensor([1, 2, 3])
        >>> max_length = 5
        >>> padded_tensor = add_left_padding(input_ids, max_length)
        >>> padded_tensor
        tensor([0, 0, 1, 2, 3])
    """
    padding = torch.tensor([pad_value] * (max_length - input_ids.shape[0]), dtype=torch.int64, device=input_ids.device)
    return torch.cat((padding, input_ids), dim=-1)


def set_pad_token(tokenizer: PreTrainedTokenizer):
    """Sets the pad token for the tokenizer if it is not already set.

    Args:
        tokenizer (PreTrainedTokenizer): The tokenizer.

    Example:
        >>> from transformers import GPT2Tokenizer, GPT2TokenizerFast, LlamaTokenizer, LlamaTokenizerFast # noqa
        >>> tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        >>> set_pad_token(tokenizer)
    """
    # Tokenizers might have the pad token id attribute since they tend to use the same base class, but
    # it can be set to None so we check for this explicitly.
    if hasattr(tokenizer, "pad_token_id") and tokenizer.pad_token_id is not None:
        return

    # HACK(Arnav): gpt, gpt2 and llama tokenizers had no pad tokens.
    # These recommend using eos tokens instead
    # https://github.com/huggingface/transformers/issues/2648#issuecomment-616177044
    # https://github.com/huggingface/transformers/issues/2630#issuecomment-1290809338
    if any(isinstance(tokenizer, t) for t in [GPT2Tokenizer, GPT2TokenizerFast, LlamaTokenizer, LlamaTokenizerFast]):
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id


def remove_left_padding(input_ids_sample: torch.Tensor, tokenizer: PreTrainedTokenizer):
    """Removes left padding and other tokens until the first BOS token from the input_ids tensor.

    Args:
        input_ids_sample (torch.Tensor): The input tensor with padding and other tokens.
        tokenizer (PreTrainedTokenizer): The tokenizer used to encode the input.

    Returns:
        torch.Tensor: The input tensor without left padding and other tokens until the first BOS token.

    Example:
        >>> import torch
        >>> from transformers import PreTrainedTokenizer
        >>> tokenizer = PreTrainedTokenizer.from_pretrained('bert-base-uncased')
        >>> input_sentence = "This is an example sentence."
        >>> input_ids = tokenizer.encode(input_sentence, add_special_tokens=True)
        >>> padded_input_ids = torch.nn.functional.pad(input_ids, (10 - len(input_ids), 0))
        >>> input_ids_no_padding = remove_left_padding(padded_input_ids, tokenizer)
        >>> input_ids_no_padding
        tensor([[1, 2, 3]])
    """
    # Remove all PAD tokens
    pad_idxs = torch.where(input_ids_sample == tokenizer.pad_token_id)[0]  # all PAD token locations
    input_ids_no_padding = input_ids_sample
    if len(pad_idxs) != 0:
        pad_idx = pad_idxs[-1]  # get last PAD token location
        input_ids_no_padding = input_ids_sample[pad_idx + 1 :]

    # Start from the first BOS token
    bos_idxs = torch.where(input_ids_no_padding == tokenizer.bos_token_id)[0]  # all BOS token locations
    if len(bos_idxs) != 0:
        bos_idx = bos_idxs[0]  # get first BOS token location
    else:
        bos_idx = 0

    input_ids_no_bos = input_ids_no_padding[bos_idx:].unsqueeze(0)
    return input_ids_no_bos


def create_attention_mask(input_ids: torch.Tensor, tokenizer: PreTrainedTokenizer):
    """Creates an attention mask for the input_ids tensor.

    Args:
        input_ids (torch.Tensor): The input tensor.
        tokenizer (PreTrainedTokenizer): The tokenizer used to encode the input.

    Returns:
        torch.Tensor: The attention mask tensor.

    Example:
        >>> import torch # noqa
        >>> from transformers import PreTrainedTokenizer
        >>> tokenizer = PreTrainedTokenizer.from_pretrained('bert-base-uncased')
        >>> input_sentence = "This is an example sentence."
        >>> input_ids = tokenizer.encode(input_sentence, add_special_tokens=True)
        >>> attention_mask = create_attention_mask(input_ids, tokenizer)
        >>> attention_mask
        tensor([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    """
    attention_mask = input_ids != tokenizer.pad_token_id
    # Last token may not be padding if we've already hit the max sequence length
    if not attention_mask[-1]:
        # last token is padding, always attended to even if it is padding
        attention_mask[-1] = 1
    attention_mask = attention_mask.to(torch.int64)
    return attention_mask


def find_last_matching_index(tensor_a: torch.Tensor, tensor_b: torch.Tensor):
    """Returns the last index of `tensor_a` that matches `tensor_b`.

    Args:
        tensor_a (torch.Tensor): The first tensor.
        tensor_b (torch.Tensor): The second tensor.

    Returns:
        int: The last index of `tensor_a` that matches `tensor_b`. Returns -1 if there is no matching index.

    Example:
        >>> import torch
        >>> tensor_a = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8])
        >>> tensor_b = torch.tensor([6, 7, 8])
        >>> last_matching_index = find_last_matching_index(tensor_a, tensor_b)
        >>> last_matching_index
        5
    """
    last_index = -1

    tensor_a_length = tensor_a.shape[0]
    tensor_b_length = tensor_b.shape[0]

    # Get the last tensor_b_length elements of tensor_a.
    tensor_a_truncated = tensor_a[-tensor_b_length:]

    # Find the last matching index.
    for i in range(tensor_b_length):
        if torch.equal(tensor_a_truncated[i:], tensor_b[: tensor_b_length - i]):
            last_index = tensor_a_length - tensor_b_length + i
            break

    return last_index


def realign_target_and_prediction_tensors(
    targets: Dict[str, torch.Tensor],
    predictions: Dict[str, torch.Tensor],
    model_inputs: torch.Tensor,
    of_name: str,
    tokenizer: PreTrainedTokenizer,
    pad_direction: str = "right",
    pad_value: int = None,
) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
    """Realigns the target tensor with the predictions.

    This is necessary for text metrics that require the target and prediction
    to be of the same length.
    Args:
        targets: The target tensor.
        predictions: The prediction tensor.
        of_name: The output feature's name.
        pad_direction: The direction to pad the tensors. Can be 'left' or 'right'.
            Defaults to 'right'.

    Returns:
        The realigned target tensor.
    """
    target_length = targets.get(of_name).size()[1]
    prediction_length = predictions[of_name].get(PREDICTIONS).size()[1]

    if target_length == prediction_length:
        return targets, predictions

    if pad_direction not in {"left", "right"}:
        raise ValueError(f'pad_direction must be either "left" or "right". Got {pad_direction}.')

    if not pad_value:
        pad_value = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id

    # Align target and prediction tensors for text to text metric computation
    if target_length > prediction_length:
        # Pad the predictions.
        zeros_to_add = target_length - prediction_length

        if pad_direction == "right":
            predictions[of_name][PREDICTIONS] = F.pad(
                predictions[of_name][PREDICTIONS], (0, zeros_to_add), value=pad_value
            )
            predictions[of_name][PROBABILITIES] = F.pad(predictions[of_name][PROBABILITIES], (0, 0, 0, zeros_to_add))
            predictions[of_name][LOGITS] = F.pad(predictions[of_name][LOGITS], (0, 0, 0, zeros_to_add))
        elif pad_direction == "left":
            predictions[of_name][PREDICTIONS] = F.pad(
                predictions[of_name][PREDICTIONS], (zeros_to_add, 0), value=pad_value
            )
            predictions[of_name][PROBABILITIES] = F.pad(predictions[of_name][PROBABILITIES], (0, 0, zeros_to_add, 0))
            predictions[of_name][LOGITS] = F.pad(predictions[of_name][LOGITS], (0, 0, zeros_to_add, 0))

    else:
        updated_targets = []
        for idx, target in enumerate(targets[of_name]):
            if pad_direction == "right":
                updated_targets.append(
                    F.pad(target, (0, prediction_length - target_length), value=pad_value).to(torch.int64)
                )

            # This code path is traversed when we're fine-tuning a LLM.
            elif pad_direction == "left":
                # Remove any leading -100s in the target that were temporarily added for alignment
                end_index = (target != -100).nonzero()[0]
                target = target[end_index:]

                # See if target was in the tensor passed into the model's forward pass
                last_matching_index = find_last_matching_index(model_inputs[idx], target)

                # If the last matching index is -1, it means that the input tensor passed into the model was truncated
                # and did not contain the target tensor. In this case, we need to truncate the target tensors as well
                # and just set it to a tensor of -100 so that we don't compute loss on this target tensor.
                if last_matching_index == -1:
                    updated_targets.append(torch.full((prediction_length,), pad_value, dtype=torch.int64))

                # If the last matching index is not -1, it means that the input tensor passed into the model was not
                # truncated and contained either a part of the target tensor or the entire target tensor. In this case,
                # we need to set the target tensor to the part of the target tensor that was passed into the model while
                # also padding it to the correct length with -100.
                else:
                    padding = torch.full((last_matching_index,), pad_value)
                    updated_targets.append(torch.cat((padding, target), dim=-1).to(torch.int64)[:prediction_length])

        targets[of_name] = torch.stack(updated_targets)

    # This is important since metric computation requires float32 tensors and we may use quantization during training.
    predictions[of_name][PROBABILITIES] = predictions[of_name][PROBABILITIES].type(torch.float32)
    predictions[of_name][LOGITS] = predictions[of_name][LOGITS].type(torch.float32)

    return targets, predictions
