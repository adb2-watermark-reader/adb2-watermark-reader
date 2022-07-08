import bitarray.util as bit_util
from bitarray import bitarray

from vp1.vp1_message import Vp1Message


class ExtendedVp1Message:
    time_offset: int
    vp1_message: Vp1Message

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __init__(self, bits: bitarray):
        assert len(bits) == 168

        self.time_offset = bit_util.ba2int(bits[:8])
        self.vp1_message = Vp1Message(bits[8:168], alternate_scramble=True)
