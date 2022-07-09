from dataclasses import dataclass

import bitarray.util as bit_util
from bitarray import bitarray

from vp1.vp1_message import Vp1Message


@dataclass
class ExtendedVp1Message:
    time_offset: int
    vp1_message: Vp1Message

    def __init__(self, bits: bitarray):
        assert len(bits) == 168

        self.time_offset = bit_util.ba2int(bits[:8])
        self.vp1_message = Vp1Message(bits[8:168], alternate_scramble=True)
