from dataclasses import dataclass

import bitarray.util as bit_util
from bitarray import bitarray


@dataclass
class Vp1Payload:
    domain_is_long: bool
    query_flag: bool
    interval: int
    server_int: int

    server_hex: str
    server_hex = property(lambda self: f"{self.server_int:x}")

    server_domain: str
    server_domain = property(lambda self: f"{self.server_hex}.a336.watermark.hbbtvdns.org")

    def __init__(self, bits: bitarray):
        assert len(bits) == 50

        self.domain_is_long = bool(bits[0])

        interval_start_bit = 24 if self.domain_is_long else 32

        self.server_int = bit_util.ba2int(bits[1:interval_start_bit])
        self.interval = bit_util.ba2int(bits[interval_start_bit:49])
        self.query_flag = bool(bits[49])
