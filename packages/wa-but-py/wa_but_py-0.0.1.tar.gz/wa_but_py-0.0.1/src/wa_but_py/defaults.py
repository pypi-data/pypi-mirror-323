# WhatsApp-specific protocol constants
NOISE_PROTOCOL = b'Noise_XX_25519_AESGCM_SHA256\x00\x00\x00\x00'
WA_NOISE_HEADER = b'\x57\x41\x06\x02'  # WhatsApp's noise protocol header
FRAME_HEADER = b'ED\x00\x01'  # Frame header prefix for routing info
CERT_SERIAL = 0  # WhatsApp's expected certificate serial number
HASH_LENGTH = 32  # SHA256 hash length
HKDF_LENGTH = 64  # HKDF output length for key derivation
IV_PREFIX = b'\x00'*8  # IV generation prefix
MAX_FRAME_HEADER_SIZE = 7  # Maximum frame header size in bytes