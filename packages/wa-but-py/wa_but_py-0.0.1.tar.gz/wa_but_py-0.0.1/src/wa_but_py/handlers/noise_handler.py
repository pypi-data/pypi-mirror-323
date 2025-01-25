"""
Noise Protocol Handler for WhatsApp WebSocket Communication

Implements WhatsApp's customized Noise Protocol XX handshake with AEAD encryption.
Designed to replicate the exact handshake process observed in WhatsApp Web v2.2351+.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PublicKey
)
from typing import Optional, Tuple, Callable, Dict
import struct
import hashlib
import logging

from wa_but_py import (
    NOISE_PROTOCOL,
    HASH_LENGTH,
    HKDF_LENGTH,
    IV_PREFIX,
    WA_NOISE_HEADER,
    FRAME_HEADER,
)
from wa_but_py.utils.exceptions.noise_handshake_exceptions import NoiseHandshakeError
from wa_but_py.utils.models.models import KeyPair

class NoiseHandler:
    """Handles WhatsApp's Noise Protocol implementation with following characteristics:
    
    - Noise XX pattern (XX_25519_AESGCM_SHA256)
    - Custom frame formatting with routing headers
    - Three-phase handshake with certificate verification
    - AEAD encryption with message counters
    - HKDF key chaining for forward secrecy
    
    Typical Flow:
    1. Initialize with client static key pair
    2. Process server hello (ephemeral, static, cert)
    3. Verify server certificate chain
    4. Derive session keys
    5. Handle message encryption/decryption
    """
    
    def __init__(
        self,
        key_pair: KeyPair,
        logger: logging.Logger,
        noise_header: bytes = NOISE_PROTOCOL,
        routing_info: Optional[bytes] = None
    ):
        """Initialize Noise protocol state machine
        
        Args:
            key_pair: Long-term client static key pair
            logger: Parent logger instance
            noise_header: Protocol identifier bytes (default: WhatsApp standard)
            routing_info: Optional edge routing info from WhatsApp servers
        """
        self.logger = logger.getChild('noise')
        self.routing_info = routing_info
        self.private_key = key_pair.private
        self.public_key = key_pair.public
        
        try:
            self.hash = self._initial_hash(noise_header)
            self.salt = self.hash 
            self.enc_key = self.dec_key = self.hash  
            
            self.read_counter = self.write_counter = 0
            self.handshake_complete = False
            self.sent_intro = False
            self.buffer = bytearray()
            
            self._update_hash(self.public_key)
            
            self.logger.debug("Noise handler initialized. Hash: %s", 
                            self.hash.hex()[:12])
            
        except Exception as e:
            self.logger.error("Initialization failed: %s", str(e), exc_info=True)
            raise NoiseHandshakeError.crypto_error(
                "initialization", 
                cause=e,
                context={
                    "noise_header": noise_header.hex()[:20],
                    "pubkey": self.public_key.public_bytes().hex()[:8]
                }
            ) from e

    def _generate_iv(self, counter: int) -> bytes:
        """Generate 12-byte IV per WhatsApp's specification:
        
        Structure:
        - 8 byte static prefix (IV_PREFIX)
        - 4 byte big-endian counter
        
        Args:
            counter: Monotonically increasing message counter
            
        Returns:
            IV suitable for AES-GCM
        """
        return IV_PREFIX + struct.pack('>I', counter)

    def _initial_hash(self, noise_header: bytes) -> bytes:
        """Generate initial hash state as per Noise protocol spec"""
        if not isinstance(noise_header, bytes):
            raise NoiseHandshakeError.protocol_error(
                "Invalid noise header type",
                expected_type=bytes,
                actual_type=type(noise_header)
            )
            
        return hashlib.sha256(noise_header).digest()[:HASH_LENGTH]

    def _hkdf(self, input_key: bytes) -> Tuple[bytes, bytes]:
        """HKDF key derivation with current salt
        
        WhatsApp-specific modifications:
        - Fixed output length of 64 bytes
        - SHA-256 as hash function
        - Empty info parameter
        
        Args:
            input_key: ECDH shared secret or previous key material
            
        Returns:
            Tuple of (new_write_key, new_read_key)
        """
        try:
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=HKDF_LENGTH,
                salt=self.salt,
                info=b'',
            )
            key = hkdf.derive(input_key)
            return key[:32], key[32:]
        except Exception as e:
            self.logger.error("HKDF derivation failed: %s", str(e))
            raise NoiseHandshakeError.crypto_error(
                "hkdf_derive",
                cause=e,
                context={
                    "input_key": input_key.hex()[:8],
                    "salt": self.salt.hex()[:8]
                }
            ) from e
        
    def _update_hash(self, data: bytes) -> None:
        """Update hash state following Noise protocol chaining
        
        Hash = SHA256(old_hash || data)
        """
        combined = self.hash + data
        self.hash = hashlib.sha256(combined).digest()
        self.logger.debug("Hash updated to %s...", self.hash.hex()[:12])

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt message with current write key and increment counter
        
        Args:
            plaintext: Raw message to encrypt
            
        Returns:
            ciphertext: Encrypted bytes with 16-byte authentication tag
            
        Raises:
            NoiseHandshakeError: On encryption failure or counter overflow
        """
        try:
            if self.write_counter >= 0xFFFFFFFF:
                raise ValueError("Write counter overflow - reset required")
                
            iv = self._generate_iv(self.write_counter)
            self.logger.debug("Encrypting with IV %s...", iv.hex()[:12])
            
            ciphertext = AESGCM(self.enc_key).encrypt(iv, plaintext, None)
            self.write_counter += 1
            
            self._update_hash(ciphertext)
            
            return ciphertext
            
        except Exception as e:
            self.logger.error("Encryption failed: %s", str(e), exc_info=True)
            raise NoiseHandshakeError.crypto_error(
                "encrypt",
                cause=e,
                context={
                    "plaintext_length": len(plaintext),
                    "counter": self.write_counter,
                    "key": self.enc_key.hex()[:8]
                }
            ) from e

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt message with current read key and increment counter
        
        Args:
            ciphertext: Encrypted message with authentication tag
            
        Returns:
            plaintext: Decrypted raw bytes
            
        Raises:
            NoiseHandshakeError: On decryption failure or invalid tag
        """
        try:
            iv_counter = self.read_counter
            if iv_counter >= 0xFFFFFFFF:
                raise ValueError("Read counter overflow - reset required")
                
            iv = self._generate_iv(iv_counter)
            self.logger.debug("Decrypting with IV %s...", iv.hex()[:12])
            
            plaintext = AESGCM(self.dec_key).decrypt(iv, ciphertext, None)
            self.read_counter += 1
            
            self._update_hash(ciphertext)
            
            return plaintext
            
        except Exception as e:
            self.logger.error("Decryption failed: %s", str(e), exc_info=True)
            raise NoiseHandshakeError.crypto_error(
                "decrypt",
                cause=e,
                context={
                    "ciphertext_length": len(ciphertext),
                    "counter": self.read_counter,
                    "key": self.dec_key.hex()[:8]
                }
            ) from e

    def process_handshake(self, server_hello: Dict[str, bytes]) -> bytes:
        """Handle server handshake message (phase 2 of XX pattern)
        
        Steps:
        1. Verify server hello structure
        2. Perform ECDH with server ephemeral
        3. Decrypt server static key
        4. Perform ECDH with server static 
        5. Verify server certificate
        6. Prepare client finish message
        
        Args:
            server_hello: Dict containing 'ephemeral', 'static', and 'payload'
            
        Returns:
            client_finish: Encrypted client authentication payload
            
        Raises:
            NoiseHandshakeError: For any protocol violations
        """
        try:
            required_keys = {'ephemeral', 'static', 'payload'}
            if missing := required_keys - server_hello.keys():
                raise NoiseHandshakeError.protocol_error(
                    "Invalid server hello",
                    missing_keys=missing,
                    received_keys=server_hello.keys()
                )

            server_eph = X25519PublicKey.from_public_bytes(
                server_hello['ephemeral']
            )
            self._update_hash(server_hello['ephemeral'])
            
            shared_secret = self.private_key.exchange(server_eph)
            self._update_keys(shared_secret)
            self.logger.debug("After server_eph ECDH: enc_key=%s...", 
                            self.enc_key.hex()[:8])

            static_plain = self.decrypt(server_hello['static'])
            server_static = X25519PublicKey.from_public_bytes(static_plain)
            
            shared_secret = self.private_key.exchange(server_static)
            self._update_keys(shared_secret)
            self.logger.debug("After server_static ECDH: dec_key=%s...", 
                            self.dec_key.hex()[:8])

            cert_plain = self.decrypt(server_hello['payload'])
            if not self._verify_certificate(cert_plain):
                raise NoiseHandshakeError.authentication_error(
                    "Certificate verification failed",
                    cert_data=cert_plain.hex()[:20]
                )

            client_finish = self.encrypt(self.public_key.public_bytes())
            
            shared_secret = self.private_key.exchange(server_eph)
            self._update_keys(shared_secret)
            
            return client_finish
            
        except Exception as e:
            self.logger.error("Handshake processing failed: %s", str(e))
            if not isinstance(e, NoiseHandshakeError):
                raise NoiseHandshakeError.protocol_error(
                    "Handshake failure",
                    cause=e,
                    handshake_stage="server_hello"
                ) from e
            raise

    def _update_keys(self, input_key: bytes) -> None:
        """Update session keys using HKDF and reset counters
        
        WhatsApp-specific behavior:
        - Always uses previous salt for HKDF
        - Does NOT clear hash state after key updates
        - Resets message counters to zero
        """
        try:
            write_key, read_key = self._hkdf(input_key)
            
            self.enc_key = write_key
            self.dec_key = read_key
            self.salt = write_key 
            
            self.read_counter = self.write_counter = 0
            
            self.logger.debug("Keys rotated: enc=%s... dec=%s...", 
                            write_key.hex()[:8], read_key.hex()[:8])
            
        except Exception as e:
            self.logger.error("Key update failed: %s", str(e))
            raise NoiseHandshakeError.crypto_error(
                "key_update",
                cause=e,
                context={
                    "input_key": input_key.hex()[:8],
                    "handshake_stage": "active"
                }
            ) from e

    def _verify_certificate(self, cert_data: bytes) -> bool:
        """Validate WhatsApp server certificate chain
        
        Placeholder implementation - should verify:
        1. Certificate chain signatures
        2. Domain validation
        3. Certificate transparency
        4. Known public key pins
        
        Args:
            cert_data: Raw certificate chain bytes
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            NoiseHandshakeError: For invalid formats or verification failures
        """
        try:
            # Basic format check
            if not cert_data.startswith(b'-----BEGIN CERTIFICATE-----'):
                raise ValueError("Invalid certificate header")
                
            # TODO: Actual certificate parsing and verification
            # This should use cryptography.x509 and WhatsApp's root CAs
            
            return True  # Temporarily bypass verification
            
        except Exception as e:
            self.logger.error("Certificate verification failed: %s", str(e))
            raise NoiseHandshakeError.authentication_error(
                "Certificate invalid",
                cause=e,
                cert_fingerprint=hashlib.sha256(cert_data).hexdigest()[:16]
            ) from e

    def finalize_handshake(self) -> None:
        """Complete handshake and derive final session keys
        
        Called after successful handshake to derive long-term session keys
        """
        try:
            write_key, read_key = self._hkdf(b'')
            
            self.enc_key = write_key
            self.dec_key = read_key
            self.hash = b''  
            self.handshake_complete = True
            
            self.logger.info("Handshake finalized. Session keys established")
            
        except Exception as e:
            self.logger.error("Handshake finalization failed: %s", str(e))
            raise NoiseHandshakeError.crypto_error(
                "finalization",
                cause=e,
                context={"handshake_stage": "complete"}
            ) from e

    def encode_frame(self, data: bytes) -> bytes:
        """Package data into WhatsApp's WebSocket frame format
        
        Frame structure:
        [Header (optional)][3-byte length][encrypted payload]
        
        Header is only sent once, containing routing information
        """
        try:
            if self.handshake_complete:
                data = self.encrypt(data)
            
            if len(data) > 0xFFFFFF:  
                raise ValueError("Payload exceeds maximum size")
            
            frame = bytearray()
            
            if not self.sent_intro:
                frame.extend(self._build_frame_header())
                self.sent_intro = True
                
            frame.extend(struct.pack('>I', len(data))[1:])
            frame.extend(data)
            
            return bytes(frame)
            
        except Exception as e:
            self.logger.error("Frame encoding failed: %s", str(e))
            raise NoiseHandshakeError.frame_error(
                "encoding",
                cause=e,
                context={"data_length": len(data)}
            ) from e

    def _build_frame_header(self) -> bytes:
        """Construct initial frame header with routing information
        
        WhatsApp header format:
        [FRAME_HEADER][3-byte routing length][routing info][WA_NOISE_HEADER]
        """
        try:
            if not self.routing_info:
                return WA_NOISE_HEADER
                
            if len(self.routing_info) > 0xFFFFFF:
                raise ValueError("Routing info too large")
                
            header = bytearray()
            header.extend(FRAME_HEADER)
            header.extend(struct.pack('>I', len(self.routing_info))[1:])
            header.extend(self.routing_info)
            header.extend(WA_NOISE_HEADER)
            
            return bytes(header)
            
        except Exception as e:
            self.logger.error("Header build failed: %s", str(e))
            raise NoiseHandshakeError.frame_error(
                "header_construction",
                cause=e,
                context={"routing_length": len(self.routing_info)}
            ) from e

    def decode_frame(self, data: bytes) -> bytes:
        """Extract and decrypt payload from WebSocket frame"""
        try:
            if len(data) < 3:
                raise ValueError("Incomplete frame header")
                
            length = int.from_bytes(data[:3], 'big')
            
            if len(data) < 3 + length:
                raise ValueError("Incomplete payload")
                
            payload = data[3:3+length]
            
            if self.handshake_complete:
                return self.decrypt(payload)
                
            return payload
            
        except Exception as e:
            self.logger.error("Frame decoding failed: %s", str(e))
            raise NoiseHandshakeError.frame_error(
                "decoding",
                cause=e,
                context={"data_length": len(data)}
            ) from e

    def decode_frames(self, new_data: bytes, callback: Callable[[bytes], None]) -> None:
        """Process stream of WebSocket data into complete frames
        
        WhatsApp WebSocket characteristics:
        - Frames are length-prefixed (3 bytes)
        - Multiple frames may arrive in single read
        - Frames can be interleaved with control messages
        """
        try:
            self.buffer.extend(new_data)
            
            while len(self.buffer) >= 3:
                length = int.from_bytes(self.buffer[:3], 'big')
                
                if length > 10 * 1024 * 1024: 
                    raise ValueError("Frame size exceeds limit")
                    
                if len(self.buffer) < 3 + length:
                    return  
                    
                frame = bytes(self.buffer[3:3+length])
                del self.buffer[:3+length]
                
                if self.handshake_complete:
                    frame = self.decrypt(frame)
                    
                callback(frame)
                
        except Exception as e:
            self.logger.error("Stream processing failed: %s", str(e))
            raise NoiseHandshakeError.frame_error(
                "stream_processing",
                cause=e,
                context={"buffer_size": len(self.buffer)}
            ) from e