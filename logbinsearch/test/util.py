# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import bitstring
def readbit(fio, bitpos, readbit=48):
    bytepos, bit = divmod(bitpos, 8)
    fio.seek(bytepos)
    data = bitstring.BitStream(bytes=fio.read(readbit / 8 + 1))
    data.read(bit)
    return data.read(readbit)
def getbits(fio):
    pass
