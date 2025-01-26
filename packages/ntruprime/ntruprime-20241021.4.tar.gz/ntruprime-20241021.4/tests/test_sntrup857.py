from ntruprime import sntrup857


def test_sntrup857c():
    pk, sk = sntrup857.keypair()
    c, k1 = sntrup857.enc(pk)
    k2 = sntrup857.dec(c, sk)
    assert (k1 == k2)
