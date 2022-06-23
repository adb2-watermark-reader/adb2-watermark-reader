from bitarray import bitarray
import bitarray.util as bit_util
import cv2 as cv
import numpy as np
import zlib
import json


#see Table 5.2 A/336
def disassemble_bitarray_into_components(bits:bitarray) -> dict[str: bitarray]:
    """"disassemble_bitstream_into_components(bits) -> dict

    Disassembles a watermark message bitarray (240 bits) into a dictionary wm_message
    The keys of the dictionary correspond to the Table 5.2 in A/336
    """
    wm_message = {}
    wm_message["run_in_pattern"] = bits[:16]
    wm_message["id"] = bits[16:24]
    wm_message["block_length"] = bits[24:32]
    wm_message_remaining_bytes = bit_util.ba2int(wm_message["block_length"])
    wm_message_remaining_bytes -= 4 #crc_32
    wm_message["version"] = bits[32:36]
    wm_message_bytes_start = 40
    if (wm_message["id"] & bitarray('10000000')) == bitarray('00000000'): 
        wm_message["fragment_number"] = bits[36:38]
        wm_message["last_fragment"] = bits[38:40]
        wm_message_remaining_bytes -= 1
    else:
        wm_message["reserved"] = bits[36:40]
        wm_message["fragment_number"] = bits[40:48]
        wm_message["last_fragment"] = bits[48:56]
        wm_message_remaining_bytes -= 3
        wm_message_bytes_start = 56
    if (wm_message["fragment_number"] == wm_message["last_fragment"] and wm_message["fragment_number"].any()):
        wm_message_remaining_bytes -= 4 #message_crc_32
    wm_message_bytes_end = wm_message_bytes_start + (wm_message_remaining_bytes * 8)
    wm_message["bytes"] = bits[wm_message_bytes_start: wm_message_bytes_end]
    if (wm_message["fragment_number"] == wm_message["last_fragment"] and wm_message["fragment_number"].any()):
        wm_message["message_crc_32"] = bits[wm_message_bytes_end: wm_message_bytes_end + 32]
        wm_message["crc_32"] = bits[wm_message_bytes_end + 32: wm_message_bytes_end + 64]
    else:
        wm_message["crc_32"] = bits[wm_message_bytes_end: wm_message_bytes_end + 32] 
    wm_message["entire_block"] = bits[16:wm_message_bytes_end]
    return wm_message



def gammaCorrection(src, gamma):
    invGamma = 1 / gamma
 
    table = [((i / 255) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)
 
    return cv.LUT(src, table)


def reduce(bins, resized):
    """
    returns bins with the reduced resized array added to it
    """
    for i in range(len(bins)):
        bins[i] += (resized == i).sum()
    return bins


def number_of_different_bits(bit_array: bitarray, reference: bitarray) -> int:
    return abs(bit_array.count(True), reference.count(True))

def check_crc(message: dict[str: bitarray]) -> bool:
    if message["crc_32"].any():
        return bit_util.ba2int(message["crc_32"]) == zlib.crc32(message["entire_block"])
    else:
        return False

def print_to_file(messages: list):
    with open("messages.json", "w") as f:
        f.write('[')
        for dictionary, i in zip(messages, range(len(messages))):
            f.write('{')
            j = 0
            for key, value in dictionary.items():
                f.write('"%s":"%s"\n' % (key, str(value)))
                j+=1
                if j < len(dictionary.items()):
                    f.write(',')
            f.write('}')
            if i < len(messages)-1:
                f.write(',')
        f.write(']')