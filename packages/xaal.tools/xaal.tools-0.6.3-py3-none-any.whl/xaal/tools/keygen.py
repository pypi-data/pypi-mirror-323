"""
Tool to build a key pass for xAAL config file

You can use it to get a key for xaal configuration file.
This script support piping.

$ echo xaal |xaal-keygen 

"""

import binascii
import pysodium


def pass2key(passphrase: str) -> bytes:
    """Generate key from passphrase using libsodium"""
    # This function is a cut / paste from xaal.lib.tools pass2key function.
    # Check out this file for more information. This stuff avoid to import
    # xaal.tools and messing w/ the xaal configuration file at the first
    # install.
    buf = passphrase.encode("utf-8")
    KEY_BYTES = pysodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES  # 32
    salt = ('\00' * KEY_BYTES).encode('utf-8')
    opslimit = pysodium.crypto_pwhash_scryptsalsa208sha256_OPSLIMIT_INTERACTIVE
    memlimit = pysodium.crypto_pwhash_scryptsalsa208sha256_MEMLIMIT_INTERACTIVE
    key = pysodium.crypto_pwhash_scryptsalsa208sha256(KEY_BYTES, buf, salt, opslimit, memlimit)
    return key


def main():
    try:
        temp = input("Please enter your passphrase: ")
        key = pass2key(temp)
        print("Cut & Paste this key in your xAAL config-file")
        print("key=%s" % binascii.hexlify(key).decode('utf-8'))
    except KeyboardInterrupt:
        print("Bye Bye..")


if __name__ == '__main__':
    main()
