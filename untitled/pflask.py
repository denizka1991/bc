from random import SystemRandom
from binascii import hexlify
from struct import Struct

SYS_RAN = SystemRandom()
PACKER = Struct('>QQQQ')
MIN_VAL = 0x1
MAX_VAL = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

def mkprivkey():
       key = SYS_RAN.randint(MIN_VAL, MAX_VAL)
       key0 = key >> 192
       key1 = (key >> 128) & 0xffffffffffffffff
       key2 = (key >> 64) & 0xffffffffffffffff
       key3 = key & 0xffffffffffffffff

       return hexlify(PACKER.pack(key0, key1, key2, key3))

print(mkprivkey())