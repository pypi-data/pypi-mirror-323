from ntruprime import sntrup1013


def test_sntrup1013c():
    pk, sk = sntrup1013.keypair()
    c, k1 = sntrup1013.enc(pk)
    k2 = sntrup1013.dec(c, sk)
    assert (k1 == k2)
