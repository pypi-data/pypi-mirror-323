import os
from dataclasses import dataclass

@dataclass
class ConnectionConfig:
    """Configuration settings for NinjaTrader connection.

    Attributes:
        host: Server hostname/IP (default: "127.0.0.1")
        port: Server port (default: 36973)
        retry_interval: Seconds between reconnection attempts
        connection_timeout: Max seconds to wait for connection
    """

    host: str =  os.getenv('NT_HOST',"127.0.0.1")
    port: int = os.getenv('NT_PORT',36973)
    retry_interval: int =  os.getenv('RETRY_INTERVAL',10)
    connection_timeout: float = os.getenv('CONN_TIMEOUT',10.0)