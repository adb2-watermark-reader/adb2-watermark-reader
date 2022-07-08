from bitarray import bitarray

from vp1.vp1_packet import Vp1Packet


class Vp1Message:
    header: bitarray
    packet: Vp1Packet

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __init__(self, bits: bitarray, alternate_scramble=False):
        assert len(bits) == 160

        self.header = bits[:32]
        self.packet = Vp1Packet(bits[32:159], alternate_scramble)
