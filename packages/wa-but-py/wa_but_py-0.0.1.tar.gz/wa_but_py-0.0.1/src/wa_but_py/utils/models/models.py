from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

class KeyPair:
    """X25519 key pair container"""
    def __init__(self, private: X25519PrivateKey, public: X25519PublicKey):
        self.private = private
        self.public = public