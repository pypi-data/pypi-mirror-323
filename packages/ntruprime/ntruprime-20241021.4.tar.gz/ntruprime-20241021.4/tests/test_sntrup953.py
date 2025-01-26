from ntruprime import sntrup953


def test_sntrup953c():
    pk, sk = sntrup953.keypair()
    c, k1 = sntrup953.enc(pk)
    k2 = sntrup953.dec(c, sk)
    assert (k1 == k2)
