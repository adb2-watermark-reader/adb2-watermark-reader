import zlib

import bitarray.util as bit_util
from bitarray import bitarray

from vp1.extended_vp1_message import ExtendedVp1Message


class WatermarkMessage:
    run_in_pattern: bitarray
    id: int
    block_length: int
    version: int
    fragment_number: int
    last_fragment: int
    message_crc_32: int
    crc_32: int
    entire_block: bitarray
    extended_vp1_message: ExtendedVp1Message

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __init__(self, bits: bitarray):
        """
        disassemble bitstream into WatermarkMessage
        corresponds to the Table 5.2 in A/336
        """

        assert len(bits) == 240

        self.run_in_pattern = bits[:16]
        self.id = bit_util.ba2int(bits[16:24])
        self.block_length = bit_util.ba2int(bits[24:32])

        remaining_bytes = self.block_length - 4

        self.version = bit_util.ba2int(bits[32:36])

        wm_message_bytes_start = 40
        if (self.id & 0x80) == 0:
            self.fragment_number = bit_util.ba2int(bits[36:38])
            self.last_fragment = bit_util.ba2int(bits[38:40])
            remaining_bytes -= 1
        else:
            self.fragment_number = bit_util.ba2int(bits[40:48])
            self.last_fragment = bit_util.ba2int(bits[48:56])
            remaining_bytes -= 3
            wm_message_bytes_start = 56

        is_last_fragment = self.fragment_number == self.last_fragment and self.fragment_number > 0
        if is_last_fragment:
            remaining_bytes -= 4  # message_crc_32
            pass

        wm_message_bytes_end = wm_message_bytes_start + remaining_bytes * 8
        self.bytes = bits[wm_message_bytes_start: wm_message_bytes_end]

        assert len(self.bytes) == 168
        assert self.fragment_number == 0
        assert self.id == 0x7

        if is_last_fragment:
            self.message_crc_32 = bit_util.ba2int(bits[wm_message_bytes_end: wm_message_bytes_end + 32])
            self.crc_32 = bit_util.ba2int(bits[wm_message_bytes_end + 32: wm_message_bytes_end + 64])
        else:
            self.crc_32 = bit_util.ba2int(bits[wm_message_bytes_end: wm_message_bytes_end + 32])
        self.entire_block = bits[16:wm_message_bytes_end]

        assert self.has_valid_crc

        self.extended_vp1_message = ExtendedVp1Message(self.bytes)

    @property
    def has_valid_crc(self):
        if self.crc_32:
            return self.crc_32 == zlib.crc32(self.entire_block)
        return False
