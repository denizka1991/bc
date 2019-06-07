import hashlib
import base58

# ECDSA bitcoin Public Key
#pubkey = 'cd7eb5027498e935812107857171c5c616f009c0f0af6823d94e4528a7ca98a0'
# See 'compressed form' at https://en.bitcoin.it/wiki/Protocol_documentation#Signatures



# def hash160(hex_str):
#     sha = hashlib.sha256()
#     rip = hashlib.new('ripemd160')
#     sha.update(hex_str)
#     rip.update( sha.digest() )
#     print ( "key_hash = \t" + rip.hexdigest() )
#     return rip.hexdigest()  # .hexdigest() is hex ASCII

def tt(pubkey):
    compress_pubkey = False
    if (compress_pubkey):
        if (ord(bytearray.fromhex(pubkey[-2:])) % 2 == 0):
            pubkey_compressed = '02'
        else:
            pubkey_compressed = '03'
        pubkey_compressed += pubkey[2:66]
        hex_str = bytearray.fromhex(pubkey_compressed)
    else:
        hex_str = bytearray.fromhex(pubkey)
    sha = hashlib.sha256()
    rip = hashlib.new('ripemd160')
    sha.update(hex_str)
    rip.update(sha.digest())
    print("key_hash = \t" + rip.hexdigest())
    tmp = rip.hexdigest()
    key_hash = '00' + tmp
    #key_hash = '00' + hash160(hex_str)
    sha = hashlib.sha256()
    sha.update(bytearray.fromhex(key_hash))
    checksum = sha.digest()
    sha = hashlib.sha256()
    sha.update(checksum)
    checksum = sha.hexdigest()[0:8]
    print("checksum = \t" + sha.hexdigest())
    print("key_hash + checksum = \t" + key_hash + ' ' + checksum)
    print(base58.b58encode(bytes(bytearray.fromhex(key_hash + checksum))))

def get_public(pubkey):
    sha_pub = hashlib.sha256()
    sha_pub.update(pubkey.encode('utf-8'))
    return sha_pub.hexdigest()

tt("95123e8c2fdcff4c43bdb0a18a4c118c56cc1182b73be782166b3f4049a0c0de")

print(get_public("95123e8c2fdcff4c43bdb0a18a4c118c56cc1182b73be782166b3f4049a0c0de"))