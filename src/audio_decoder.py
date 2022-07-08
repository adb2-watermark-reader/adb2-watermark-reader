import sys
from typing import IO

import numpy as np
import pandas as pd
from bitarray import bitarray
from numba import njit

import spec_constants as consts
from math_utils import butter_bandpass_filter
from vp1.vp1_message import Vp1Message


def handle_audio_pipe(pipe: IO, samplerate: int):
    buffer = bytearray()

    while True:
        in_bytes = pipe.read(int(samplerate * consts.sec_per_vp1_cell * 2))  # 1 cell

        if not in_bytes:
            break
        buffer.extend(in_bytes)

        buffer = buffer[-int(samplerate * consts.sec_per_vp1_cell * 3 * 2):]  # 4.5 seconds or 3 cells

        try:
            audio_payload = decode(np.frombuffer(buffer, dtype='<i2'), samplerate)
            print(f"audio {audio_payload.packet.vp1_payload}")
        except Exception as err:
            print(err, file=sys.stderr)


def decode(signal: np.ndarray, samplerate: int) -> Vp1Message:
    samples_per_symbol = samplerate / consts.symbols_per_sec

    signal = butter_bandpass_filter(signal, consts.butter_pass_lower, consts.butter_pass_higher, samplerate)
    signal = get_autocorrelated_signal(signal, samplerate, samples_per_symbol)

    starting_point = get_best_starting_point(signal, samples_per_symbol)

    if starting_point is None:
        raise ValueError("no audio watermark found")

    cell_bytes = get_cell_bytes_from_signal(signal, starting_point, samples_per_symbol)
    cell_bits = bitarray()
    cell_bits.frombytes(cell_bytes)
    if not cell_bytes.hex().startswith("ae0ab9e4"):
        raise AssertionError("watermark broke")

    vp1_message = Vp1Message(cell_bits)

    return vp1_message


def get_cell_bytes_from_signal(signal: np.ndarray, starting_point, samples_per_symbol):
    data_cell = np.full(int(consts.sec_per_vp1_cell * consts.symbols_per_sec), False)
    for i in range(data_cell.shape[0]):
        data_cell[i] = signal[round(starting_point + i * samples_per_symbol)] > 0

    return np.packbits(data_cell).tobytes()


def get_autocorrelated_signal(signal: np.ndarray, samplerate, samples_per_symbol):
    half_symbol = int(samples_per_symbol / 2)
    offset_frames = round(samplerate * consts.offset_sec)

    df_first = pd.DataFrame(signal[:-offset_frames - half_symbol])
    df_first_2 = pd.DataFrame(signal[half_symbol:-offset_frames])
    df_delayed = pd.DataFrame(signal[offset_frames: - half_symbol])
    df_delayed_2 = pd.DataFrame(signal[offset_frames + half_symbol:])

    rolling_corr_1 = df_first.rolling(offset_frames).corr(df_delayed)
    rolling_corr_2 = df_first_2.rolling(offset_frames).corr(df_delayed_2)

    return (rolling_corr_1 - rolling_corr_2).to_numpy()


@njit
def get_best_starting_point(signal: np.ndarray, samples_per_symbol):
    possible_starting_points = []

    # we don't need to search for it in the second half because there can't
    # be a full message (or only without padding)
    for i in range(int(signal.shape[0] - samples_per_symbol * (
            consts.sec_per_vp1_cell * consts.symbols_per_sec - len(consts.message_header)))):
        is_correct = True
        for j in range(len(consts.message_header)):
            if not (signal[int(j * samples_per_symbol + i)] >= 0 and consts.message_header[j] == '1'
                    or signal[int(j * samples_per_symbol + i)] < 0 and consts.message_header[j] == '0'):
                is_correct = False
                break
        if is_correct:
            possible_starting_points.append(i)

    if len(possible_starting_points) == 0:
        return None
    median = np.median(np.array(possible_starting_points))

    # avoid the case that the cell starts so late that it can't detect the entire thing
    if median + samples_per_symbol * ((consts.symbols_per_sec * consts.sec_per_vp1_cell) - 1) + 1 >= signal.shape[0]:
        return None

    return median
