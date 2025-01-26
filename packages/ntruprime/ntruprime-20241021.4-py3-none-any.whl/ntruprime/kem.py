from typing import Tuple as _Tuple
import ctypes as _ct
from ._lib import _lib, _check_input


class _KEM:
    def __init__(self) -> None:
        '''
        '''
        self._c_keypair = getattr(_lib, '%s_keypair' % self._prefix)
        self._c_keypair.argtypes = [_ct.c_char_p, _ct.c_char_p]
        self._c_keypair.restype = None
        self._c_enc = getattr(_lib, '%s_enc' % self._prefix)
        self._c_enc.argtypes = [_ct.c_char_p, _ct.c_char_p, _ct.c_char_p]
        self._c_enc.restype = None
        self._c_dec = getattr(_lib, '%s_dec' % self._prefix)
        self._c_dec.argtypes = [_ct.c_char_p, _ct.c_char_p, _ct.c_char_p]
        self._c_dec.restype = None

    def keypair(self) -> _Tuple[bytes, bytes]:
        '''
        Keypair - randomly generates secret key 'sk' and corresponding public key 'pk'.
        Returns:
            pk (bytes): public key
            sk (bytes): secret key
        '''
        pk = _ct.create_string_buffer(self.PUBLICKEYBYTES)
        sk = _ct.create_string_buffer(self.SECRETKEYBYTES)
        self._c_keypair(pk, sk)
        return pk.raw, sk.raw

    def enc(self, pk: bytes) -> _Tuple[bytes, bytes]:
        '''
        Encapsulation - randomly generates a ciphertext 'c' and the corresponding session key 'k' given Alice's public key 'pk'.
        Parameters:
            pk (bytes): public key
        Returns:
            c (bytes): ciphertext
            k (bytes): session key
        '''
        _check_input(pk, self.PUBLICKEYBYTES, 'pk')
        c = _ct.create_string_buffer(self.CIPHERTEXTBYTES)
        k = _ct.create_string_buffer(self.BYTES)
        pk = _ct.create_string_buffer(pk)
        self._c_enc(c, k, pk)
        return c.raw, k.raw

    def dec(self, c: bytes, sk: bytes) -> bytes:
        '''
        Decapsulation - given Alice's secret key 'sk' computes the session key 'k' corresponding to a ciphertext 'c'.
        Parameters:
            c (bytes): ciphertext
            sk (bytes): secret key
        Returns:
            k (bytes): session key
        '''
        _check_input(c, self.CIPHERTEXTBYTES, 'c')
        _check_input(sk, self.SECRETKEYBYTES, 'sk')
        k = _ct.create_string_buffer(self.BYTES)
        c = _ct.create_string_buffer(c)
        sk = _ct.create_string_buffer(sk)
        self._c_dec(k, c, sk)
        return k.raw


class sntrup653(_KEM):
    PUBLICKEYBYTES = 994
    SECRETKEYBYTES = 1518
    CIPHERTEXTBYTES = 897
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup653"


sntrup653 = sntrup653()


class sntrup761(_KEM):
    PUBLICKEYBYTES = 1158
    SECRETKEYBYTES = 1763
    CIPHERTEXTBYTES = 1039
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup761"


sntrup761 = sntrup761()


class sntrup857(_KEM):
    PUBLICKEYBYTES = 1322
    SECRETKEYBYTES = 1999
    CIPHERTEXTBYTES = 1184
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup857"


sntrup857 = sntrup857()


class sntrup953(_KEM):
    PUBLICKEYBYTES = 1505
    SECRETKEYBYTES = 2254
    CIPHERTEXTBYTES = 1349
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup953"


sntrup953 = sntrup953()


class sntrup1013(_KEM):
    PUBLICKEYBYTES = 1623
    SECRETKEYBYTES = 2417
    CIPHERTEXTBYTES = 1455
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup1013"


sntrup1013 = sntrup1013()


class sntrup1277(_KEM):
    PUBLICKEYBYTES = 2067
    SECRETKEYBYTES = 3059
    CIPHERTEXTBYTES = 1847
    BYTES = 32
    _prefix = "ntruprime_kem_sntrup1277"


sntrup1277 = sntrup1277()
