from bitarray import bitarray, frozenbitarray

from vp1.vp1_payload import Vp1Payload
import spec_constants as consts


class Vp1Packet:
    parity: bitarray
    vp1_payload: Vp1Payload

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __init__(self, bits: bitarray, alternate_scramble=False):
        """
        Input the scrambled bits, set alternate_scramble to True if this came from
        an extended_vp1_message

        one day one should probably utilize the parity but not on this day
        """

        assert len(bits) == 127

        self.parity = bits[:50]

        payload_whitening_sequence = frozenbitarray(
            consts.alternate_payload_whitening_sequence if alternate_scramble else consts.payload_whitening_sequence)
        unscrambled_payload = payload_whitening_sequence ^ bits[77:]

        self.vp1_payload = Vp1Payload(unscrambled_payload)
