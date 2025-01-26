from ntruprime import sntrup761


def test_sntrup761c():
    pk, sk = sntrup761.keypair()
    c, k1 = sntrup761.enc(pk)
    k2 = sntrup761.dec(c, sk)
    assert (k1 == k2)
