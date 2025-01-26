from ntruprime import sntrup653


def test_sntrup653c():
    pk, sk = sntrup653.keypair()
    c, k1 = sntrup653.enc(pk)
    k2 = sntrup653.dec(c, sk)
    assert (k1 == k2)
