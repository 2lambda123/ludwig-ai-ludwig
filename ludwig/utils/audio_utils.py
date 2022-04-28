#! /usr/bin/env python
# Copyright (c) 2019 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import functools
import logging
import os
import sys
from typing import List, Optional, Tuple, Union

import torch
import torch.nn.functional as F
import torchaudio

from ludwig.constants import DEFAULT_AUDIO_TENSOR_LENGTH
from ludwig.utils.data_utils import get_abs_path
from ludwig.utils.fs_utils import is_http, upgrade_http

logger = logging.getLogger(__name__)


def get_default_audio(audio_lst: List[Tuple[torch.Tensor, int]]) -> Tuple[torch.Tensor, int]:
    sampling_rates = [audio[1] for audio in audio_lst]
    tensor_list = [audio[0] for audio in audio_lst]

    for i, tensor in enumerate(tensor_list):
        if tensor.shape[1] > DEFAULT_AUDIO_TENSOR_LENGTH:
            tensor_list[i] = tensor[:, :DEFAULT_AUDIO_TENSOR_LENGTH]
        else:
            pad_size = DEFAULT_AUDIO_TENSOR_LENGTH - tensor.shape[1]
            tensor_list[i] = F.pad(tensor, (0, pad_size))
    default_audio_tensor = torch.mean(torch.stack(tensor_list), dim=0)
    default_sampling_rate = calculate_mean(sum(sampling_rates), len(sampling_rates))

    return default_audio_tensor, default_sampling_rate


@functools.lru_cache(maxsize=32)
def read_audio(audio: Union[str, torch.Tensor], src_path):
    """Function for reading audio files.

    Args:
        src_path: Local file source path
        audio: Audio file input

    Returns: Audio converted into torch tensor.
    """
    if isinstance(audio, torch.Tensor):
        return audio
    if isinstance(audio, str):
        return read_audio_from_str(audio, src_path)


def read_audio_from_str(audio_path: str, src_path: str, retry: bool = True) -> Tuple[torch.Tensor, int]:
    try:
        from torchaudio.backend.sox_io_backend import load
    except ImportError:
        logger.error("torchaudio is not installed. " "Please install torchaudio to train models with audio features")
        sys.exit(-1)

    try:
        if is_http(audio_path):
            return load(audio_path)
        if src_path:
            filepath = get_abs_path(src_path, audio_path)
            return load(filepath)
        if src_path is None and os.path.isabs(audio_path):
            return load(audio_path)
        if src_path is None and not os.path.isabs(audio_path):
            raise ValueError("Audio file paths must be absolute")
    except Exception as e:
        upgraded = upgrade_http(audio_path)
        if upgraded:
            logger.info(f"{e}. upgrading to https and retrying")
            return read_audio_from_str(upgraded, src_path, False)
        if retry:
            logger.info(f"{e}, retrying...")
            return read_audio_from_str(audio_path, src_path, False)
        logger.info(e)
        return None


def _pre_emphasize_data(data: torch.Tensor, emphasize_value: float = 0.97):
    # Increase precision in order to achieve parity with scipy.signal.lfilter implementation
    filter_window = torch.tensor([1.0, -emphasize_value], dtype=torch.float64)
    pre_emphasized_data = torchaudio.functional.lfilter(
        data.to(dtype=torch.float64), torch.tensor([1, 0], dtype=torch.float64), filter_window, clamp=False
    ).to(torch.float32)
    return pre_emphasized_data


def get_length_in_samp(sampling_rate_in_hz: Union[float, int], length_in_s: Union[float, int]) -> int:
    return int(sampling_rate_in_hz * length_in_s)


def get_group_delay(
    raw_data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
):
    X_stft_transform = _get_stft(
        raw_data, sampling_rate_in_hz, window_length_in_s, window_shift_in_s, num_fft_points, window_type=window_type
    )
    Y_stft_transform = _get_stft(
        raw_data,
        sampling_rate_in_hz,
        window_length_in_s,
        window_shift_in_s,
        num_fft_points,
        window_type=window_type,
        data_transformation="group_delay",
    )
    X_stft_transform_real = torch.real(X_stft_transform)
    X_stft_transform_imag = torch.imag(X_stft_transform)
    Y_stft_transform_real = torch.real(Y_stft_transform)
    Y_stft_transform_imag = torch.imag(Y_stft_transform)
    nominator = torch.multiply(X_stft_transform_real, Y_stft_transform_real) + torch.multiply(
        X_stft_transform_imag, Y_stft_transform_imag
    )
    denominator = torch.square(torch.abs(X_stft_transform))
    group_delay = torch.divide(nominator, denominator + 1e-10)
    assert not torch.isnan(group_delay).any(), "There are NaN values in group delay"
    return torch.transpose(group_delay, 0, 1)


def get_phase_stft_magnitude(
    raw_data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
) -> torch.Tensor:
    stft = _get_stft(
        raw_data, sampling_rate_in_hz, window_length_in_s, window_shift_in_s, num_fft_points, window_type=window_type
    )
    abs_stft = torch.abs(stft)
    phase = torch.angle(stft)
    stft_phase = torch.cat([phase, abs_stft], dim=1)
    return torch.transpose(stft_phase, 0, 1)


def get_stft_magnitude(
    raw_data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
):
    stft = _get_stft(
        raw_data, sampling_rate_in_hz, window_length_in_s, window_shift_in_s, num_fft_points, window_type=window_type
    )
    stft_magnitude = torch.abs(stft)
    return torch.transpose(stft_magnitude, 0, 1)


################################################################################
# The following code for FBank is adapted from jameslyons/python_speech_features
# MIT licensed implementation
# https://github.com/jameslyons/python_speech_features/blob/40c590269b57c64a8c1f1ddaaff2162008d1850c/python_speech_features/base.py#L84################################################################################
################################################################################
def get_fbank(
    raw_data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
    num_filter_bands: int,
) -> torch.Tensor:
    stft = _get_stft(
        raw_data,
        sampling_rate_in_hz,
        window_length_in_s,
        window_shift_in_s,
        num_fft_points,
        window_type=window_type,
        zero_mean_offset=True,
    )
    stft_power = torch.abs(stft) ** 2
    upper_limit_freq = int(sampling_rate_in_hz / 2)
    upper_limit_mel = _convert_hz_to_mel(upper_limit_freq)
    lower_limit_mel = 0
    list_mel_points = torch.linspace(lower_limit_mel, upper_limit_mel, num_filter_bands + 2)
    mel_fbank_matrix = _get_mel_fbank_matrix(list_mel_points, num_filter_bands, num_fft_points, sampling_rate_in_hz)
    mel_fbank_feature = torch.matmul(stft_power, torch.transpose(mel_fbank_matrix, 0, 1))
    log_mel_fbank_feature = torch.log(mel_fbank_feature + 1.0e-10)
    return torch.transpose(log_mel_fbank_feature, 0, 1)


def _get_mel_fbank_matrix(
    list_mel_points: torch.Tensor, num_filter_bands: int, num_fft_points: int, sampling_rate_in_hz: int
) -> torch.Tensor:
    num_ess_fft_points = get_non_symmetric_length(num_fft_points)
    freq_scale = (num_fft_points + 1) / sampling_rate_in_hz
    freq_bins_on_mel_scale = torch.floor(freq_scale * _convert_mel_to_hz(list_mel_points))
    mel_scaled_fbank = torch.zeros((num_filter_bands, num_ess_fft_points), dtype=torch.float32)
    for filt_idx in range(num_filter_bands):
        start_bin_freq = freq_bins_on_mel_scale[filt_idx]
        middle_bin_freq = freq_bins_on_mel_scale[filt_idx + 1]
        end_bin_freq = freq_bins_on_mel_scale[filt_idx + 2]
        mel_scaled_fbank[filt_idx] = _create_triangular_filter(
            start_bin_freq, middle_bin_freq, end_bin_freq, num_ess_fft_points
        )
    return mel_scaled_fbank


def _create_triangular_filter(
    start_bin_freq: torch.Tensor, middle_bin_freq: torch.Tensor, end_bin_freq: torch.Tensor, num_ess_fft_points: int
):
    filter_window = torch.zeros(num_ess_fft_points, dtype=torch.float32)
    filt_support_begin = middle_bin_freq - start_bin_freq
    filt_support_end = end_bin_freq - middle_bin_freq
    for freq in range(int(start_bin_freq), int(middle_bin_freq)):
        filter_window[freq] = (freq - start_bin_freq) / filt_support_begin
    for freq in range(int(middle_bin_freq), int(end_bin_freq)):
        filter_window[freq] = (end_bin_freq - freq) / filt_support_end
    return filter_window


def _convert_hz_to_mel(hz: int) -> float:
    return float(2595.0 * torch.log10(torch.tensor(1 + hz / 700.0)))


def _convert_mel_to_hz(mel):
    return 700.0 * (10 ** (mel / 2595.0) - 1)


def _get_stft(
    raw_data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
    data_transformation: Optional[str] = None,
    zero_mean_offset: bool = False,
) -> torch.Tensor:
    pre_emphasized_data = _pre_emphasize_data(raw_data)
    stft = _short_time_fourier_transform(
        pre_emphasized_data,
        sampling_rate_in_hz,
        window_length_in_s,
        window_shift_in_s,
        num_fft_points,
        window_type,
        data_transformation,
        zero_mean_offset,
    )
    non_symmetric_stft = get_non_symmetric_data(stft)
    return non_symmetric_stft


def _short_time_fourier_transform(
    data: torch.Tensor,
    sampling_rate_in_hz: int,
    window_length_in_s: float,
    window_shift_in_s: float,
    num_fft_points: int,
    window_type: str,
    data_transformation: Optional[str] = None,
    zero_mean_offset: bool = False,
) -> torch.Tensor:
    window_length_in_samp: int = get_length_in_samp(window_length_in_s, sampling_rate_in_hz)
    window_shift_in_samp: int = get_length_in_samp(window_shift_in_s, sampling_rate_in_hz)
    preprocessed_data_matrix = _preprocess_to_padded_matrix(
        data[0], window_length_in_samp, window_shift_in_samp, zero_mean_offset=zero_mean_offset
    )
    weighted_data_matrix = _weight_data_matrix(
        preprocessed_data_matrix, window_type, data_transformation=data_transformation
    )
    fft = torch.fft.fft(weighted_data_matrix, n=num_fft_points)
    return fft


def _preprocess_to_padded_matrix(
    data: torch.Tensor, window_length_in_samp: int, window_shift_in_samp: int, zero_mean_offset: bool = False
) -> torch.Tensor:
    num_input = data.shape[0]
    num_output = get_num_output_padded_to_fit_input(num_input, window_length_in_samp, window_shift_in_samp)
    zero_padded_matrix = torch.zeros((num_output, window_length_in_samp), dtype=torch.float32)
    for num_output_idx in range(num_output):
        start_idx = window_shift_in_samp * num_output_idx
        is_last_output = num_output_idx == num_output - 1
        end_idx = start_idx + window_length_in_samp if not is_last_output else num_input
        end_padded_idx = window_length_in_samp if not is_last_output else end_idx - start_idx
        window_data = data[start_idx:end_idx]
        if zero_mean_offset:
            window_data = window_data - torch.mean(window_data)
        zero_padded_matrix[num_output_idx, :end_padded_idx] = window_data
    return zero_padded_matrix


def get_num_output_padded_to_fit_input(num_input: int, window_length_in_samp: int, window_shift_in_samp: int) -> int:
    num_output_valid = torch.tensor((num_input - window_length_in_samp) / window_shift_in_samp + 1)
    return int(torch.ceil(num_output_valid))


def get_window(window_type: str, window_length_in_samp: int) -> torch.Tensor:
    if window_type == "hann":
        return torch.hann_window(window_length_in_samp, dtype=torch.float32)
    elif window_type == "hamming":
        return torch.hamming_window(window_length_in_samp, dtype=torch.float32)
    elif window_type == "blackman":
        return torch.blackman_window(window_length_in_samp, dtype=torch.float32)
    elif window_type == "bartlett":
        return torch.bartlett_window(window_length_in_samp, dtype=torch.float32)
    elif window_type == "kaiser":
        return torch.kaiser_window(window_length_in_samp, dtype=torch.float32)
    else:
        raise ValueError(f"Unknown window type: {window_type}")


def _weight_data_matrix(
    data_matrix: torch.Tensor, window_type: str, data_transformation: Optional[str] = None
) -> torch.Tensor:
    window_length_in_samp = data_matrix[0].shape[0]
    window = get_window(window_type, window_length_in_samp)
    if data_transformation is not None and data_transformation == "group_delay":
        window *= torch.arange(window_length_in_samp).float()
    return data_matrix * window


def get_non_symmetric_length(symmetric_length: int) -> int:
    return int(symmetric_length / 2) + 1


def get_non_symmetric_data(data: torch.Tensor) -> torch.Tensor:
    num_fft_points = data.shape[-1]
    num_ess_fft_points = get_non_symmetric_length(num_fft_points)
    return data[:, :num_ess_fft_points]


def get_max_length_stft_based(length_in_samp, window_length_in_s, window_shift_in_s, sampling_rate_in_hz):
    window_length_in_samp = get_length_in_samp(window_length_in_s, sampling_rate_in_hz)
    window_shift_in_samp = get_length_in_samp(window_shift_in_s, sampling_rate_in_hz)
    return get_num_output_padded_to_fit_input(length_in_samp, window_length_in_samp, window_shift_in_samp)


def calculate_incr_var(var_prev, mean_prev, mean, length):
    return var_prev + (length - mean_prev) * (length - mean)


def calculate_incr_mean(count, mean, length):
    return mean + (length - mean) / float(count)


def calculate_var(sum1, sum2, count):
    return (sum2 - ((sum1 * sum1) / float(count))) / float(count - 1) if count > 1 else 0.0


def calculate_mean(sum1, count):
    return sum1 / float(count)
