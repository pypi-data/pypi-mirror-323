Python wrapper around implementation of the Streamlined NTRU Prime cryptosystem.

To access the Python functions provided by ntruprime, import the library (for, e.g., sntrup1277):

    from ntruprime import sntrup1277

To generate a key pair:

    pk,sk = sntrup1277.keypair()

To generate a ciphertext c encapsulating a randomly generated session key k:

    c,k = sntrup1277.enc(pk)

To recover a session key from a ciphertext:

    k = sntrup1277.dec(c,sk)

As a larger example, the following test script creates a key pair, creates a ciphertext and session key, and then recovers the session key from the ciphertext:

    import ntruprime
    kem = ntruprime.sntrup1277
    pk,sk = kem.keypair()
    c,k = kem.enc(pk)
    assert k == kem.dec(c,sk)
