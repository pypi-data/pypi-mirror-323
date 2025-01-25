class NoiseHandshakeError(Exception):
    """
    Base exception for noise protocol errors with enhanced diagnostics
    
    Attributes:
        error_code (int): Categorized error code
        context (dict): Additional context about the error
        cause (Exception): Original exception that triggered this error
    """
    BASE_CODE = 1000

    def __init__(
        self,
        message: str = "Noise protocol operation failed",
        *,
        error_code: int = BASE_CODE,
        context: dict | None = None,
        cause: Exception | None = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause

    def __str__(self) -> str:
        base = f"[{self.error_code}] {super().__str__()}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k,v in self.context.items())
            base += f" | Context: {context_str}"
        if self.cause:
            base += f" | Caused by: {self.cause}"
        return base

    @classmethod
    def authentication_error(cls, message: str, **context) -> "NoiseHandshakeError":
        return cls(
            f"Authentication failed: {message}",
            error_code=cls.BASE_CODE + 1,
            context=context
        )

    @classmethod
    def protocol_error(cls, message: str, **context) -> "NoiseHandshakeError":
        return cls(
            f"Protocol violation: {message}",
            error_code=cls.BASE_CODE + 2,
            context=context
        )

    @classmethod
    def crypto_error(cls, operation: str, cause: Exception, context: dict | None = None) -> "NoiseHandshakeError":
        return cls(
            f"Cryptographic operation failed: {operation}",
            error_code=cls.BASE_CODE + 3,
            context=context,
            cause=cause
        )

    @classmethod
    def frame_error(cls, message: str, **context) -> "NoiseHandshakeError":
        return cls(
            f"Frame error: {message}",
            error_code=cls.BASE_CODE + 4,
            context=context
        )