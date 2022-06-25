import bitarray.util as bit_util
from bitarray import bitarray


class Payload:
    domain_is_long = False
    query_flag = False
    interval = 0
    server_int = 0

    server_hex = property(lambda self: f"{self.server_int:x}")
    server_domain = property(lambda self: f"{self.server_hex}.a336.watermark.hbbtvdns.org")

    def __str__(self):
        return f"{self.__dict__} server_hex: {self.server_hex} server_domain: {self.server_domain}"


def parse_payload(bit_array: bitarray):
    payload = Payload()

    payload.domain_is_long = bool(bit_array[0])

    interval_start_bit = 24 if payload.domain_is_long else 32

    payload.server_int = bit_util.ba2int(bit_array[1:interval_start_bit])
    payload.interval = bit_util.ba2int(bit_array[interval_start_bit:49])
    payload.query_flag = bool(bit_array[49])

    return payload
