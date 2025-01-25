from abc import ABC, abstractmethod
from ..waproto.generated.WAProto_pb2 import HandshakeMessage

class ILogger(ABC):
    @abstractmethod
    def debug(self, msg: str): ...
    
    @abstractmethod
    def info(self, msg: str): ...
    
    @abstractmethod
    def error(self, msg: str): ...
    
class IConnectionManager(ABC):
    @abstractmethod
    async def connect(self, url: str):
        pass
    
    @abstractmethod
    async def send(self, data: bytes):
        pass
    
    @abstractmethod
    async def receive(self):
        pass

class ISecurityHandler(ABC):
    @abstractmethod
    def prepare_handshake(self) -> bytes:
        pass
    
    @abstractmethod
    def process_response(self, response: bytes) -> HandshakeMessage:
        pass