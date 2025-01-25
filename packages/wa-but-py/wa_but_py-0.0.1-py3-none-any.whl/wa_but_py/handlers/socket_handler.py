import logging
from cryptography.hazmat.primitives.asymmetric import x25519
import websockets
from ..waproto.generated import WAProto_pb2 as WAProto
from ..utils.exceptions.noise_handshake_exceptions import NoiseHandshakeError
from wa_but_py import NoiseHandler
from wa_but_py import KeyPair
from ..types.socket import ( IConnectionManager, ISecurityHandler, ILogger )

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NullLogger(ILogger):
    def debug(self, msg: str): pass
    def info(self, msg: str): pass
    def error(self, msg: str): pass

# ---------------------
# Concrete Implementations
# ---------------------
class WebSocketConnectionManager(IConnectionManager):
    def __init__(self):
        self.websocket = None
    
    async def connect(self, url: str):
        self.websocket = await websockets.connect(url)
        return self
    
    async def send(self, data: bytes):
        await self.websocket.send(data)
    
    async def receive(self):
        return await self.websocket.recv()

class WhatsAppSecurityHandler(ISecurityHandler):
    def __init__(self, logger: ILogger = NullLogger()):
        self.logger = logger
        self.noise = None
        self.key_pair = self._generate_key_pair()
    
    def _generate_key_pair(self) -> KeyPair:
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        return KeyPair(private=private_key, public=public_key)
    
    def prepare_handshake(self) -> bytes:
        self.noise = NoiseHandler(key_pair=self.key_pair, logger=self.logger)
        hello_msg = WAProto.HandshakeMessage(
            clientHello=WAProto.HandshakeMessage.ClientHello(
                ephemeral=self.key_pair.public
            )
        )
        return hello_msg.SerializeToString()
    
    def process_response(self, response: bytes) -> (WAProto.HandshakeMessage, bytes):
        decoded = self.noise.decode_frame(response)
        handshake = WAProto.HandshakeMessage()
        handshake.ParseFromString(decoded)
        
        if not handshake.serverHello:
            raise NoiseHandshakeError.protocol_error(
                "Invalid server response",
                received_message=handshake
            )
        
        # Generate ClientFinish message
        client_finish = WAProto.HandshakeMessage(
            clientFinish=WAProto.HandshakeMessage.ClientFinish(
                # Populate necessary fields according to protocol
            )
        )
        client_finish_data = client_finish.SerializeToString()
        encoded_finish = self.noise.encode_frame(client_finish_data)
        
        return handshake, encoded_finish

# ---------------------
# Protocol Handler 
# ---------------------
class HandshakeProtocol:
    def __init__(self, security: ISecurityHandler, 
                 connection: IConnectionManager,
                 logger: ILogger = NullLogger()):
        self.security = security
        self.connection = connection
        self.logger = logger
    
    async def perform_handshake(self, url: str) -> bool:
        try:
            await self.connection.connect(url)
            handshake_data = self.security.prepare_handshake()
            await self.connection.send(handshake_data)
            
            response = await self.connection.receive()
            parsed_response, next_handshake_data = self.security.process_response(response)
            await self.connection.send(next_handshake_data)
            
            return True
            
        except NoiseHandshakeError as e:
            self.logger.error(f"Security violation: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Handshake failed: {str(e)}")
            raise

# ---------------------
# Client 
# ---------------------
class WhatsAppClient:
    def __init__(self, logger: ILogger = NullLogger(), silent: bool = False):
        self.logger = NullLogger() if silent else logger
        self.connection = WebSocketConnectionManager()
        self.security = WhatsAppSecurityHandler(self.logger)
        self.protocol = HandshakeProtocol(
            self.security, 
            self.connection,
            self.logger
        )
    
    async def connect(self, url: str = "wss://web.whatsapp.com/ws/chat"):
        try:
            success = await self.protocol.perform_handshake(url)
            if success:
                logger.info("Secure connection established")
            return self
        except Exception as e:
            ErrorHandler(self.logger).handle(e, {"stage": "handshake"})
            raise
    
    async def send(self, data: bytes):
        encoded = self.security.noise.encode_frame(data)
        await self.connection.send(encoded)
    
    async def receive(self) -> bytes:
        data = await self.connection.receive()
        return self.security.noise.decode_frame(data)

# ---------------------
# Error Handler
# ---------------------
class ErrorHandler:
    def __init__(self, logger: ILogger = NullLogger()):
        self.logger = logger
        
    def handle(self, error: Exception, context: dict = None):
        self.logger.error(f"Error: {str(error)} | Context: {context}")