from ntruprime import sntrup1277


def test_sntrup1277c():
    pk, sk = sntrup1277.keypair()
    c, k1 = sntrup1277.enc(pk)
    k2 = sntrup1277.dec(c, sk)
    assert (k1 == k2)
