"""
NinjaTrader Client Module

A Python module for interacting with NinjaTrader trading platform through a socket connection.
Provides functionality for market data subscription, order management, and position tracking.

Classes:
    ConnectionConfig: Configuration dataclass for connection settings
    NTClient: Main client class for NinjaTrader interaction

Example:
    ```python
    client = NTClient()
    if client.set_up():
        # Subscribe to market data
        client.subscribe_market_data("ES-FUT")
        # Place an order
        client.command("PLACE", "Account1", "ES-FUT", "123", action="BUY", quantity=1)
    ```
"""

import socket
import threading
import time
import uuid
from collections import defaultdict
from typing import Optional, Dict, List, Union
from dataclasses import dataclass
from functools import wraps

from ntclient.socket import AtiSocket
from ntclient.utils import config_logging

logger = config_logging(__name__)


@dataclass
class ConnectionConfig:
    """Configuration settings for NinjaTrader connection.

    Attributes:
        host: Server hostname/IP (default: "127.0.0.1")
        port: Server port (default: 36973)
        retry_interval: Seconds between reconnection attempts
        connection_timeout: Max seconds to wait for connection
    """
    host: str = "127.0.0.1"
    port: int = 36973
    retry_interval: int = 10
    connection_timeout: float = 10.0


def connection_required(func):
    """Decorator ensuring socket connection exists before executing method.

    Returns default value for the method's return type if connection fails.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.set_up(True) != 0:
            return self._get_default_return_value(func)
        return func(self, *args, **kwargs)

    return wrapper


class NTClient:
    """NinjaTrader client for automated trading operations.

    Handles connection management, market data subscription, order placement/management,
    and position tracking through NinjaTrader's socket interface.
    """

    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize NTClient with optional custom configuration.

        Args:
            config: Connection settings (optional, uses defaults if None)
        """
        self.config = config or ConnectionConfig()
        self.socket: Optional[AtiSocket] = None
        self.timer: Optional[threading.Timer] = None
        self.values: Dict[str, str] = defaultdict(str)
        self.lock = threading.Lock()
        self.had_error = False
        self.showed_error = False

    def _get_default_return_value(self, func) -> Union[int, float, str, List, Dict, None]:
        """Determine appropriate default return value based on function return type."""
        return_type = func.__annotations__.get('return')
        defaults = {
            int: 0,
            float: 0.0,
            str: "",
            List[str]: [],
            Dict: {}
        }
        return defaults.get(return_type)

    def add_value(self, key: str, value: str) -> None:
        """Thread-safe method to update internal key-value store.

        Args:
            key: Value identifier
            value: New value to store
        """
        with self.lock:
            self.values[key] = value

    def set_up(self, show_message: bool = True) -> int:
        """Initialize connection if needed.

        Args:
            show_message: Whether to log connection errors

        Returns:
            0 on success, -1 on failure
        """
        if self.had_error:
            return -1
        if self.socket and self.socket.is_connected:
            return 0
        return self.set_up_now(show_message)

    def set_up_now(self, show_message):

        try:
            # Existing connection code...
            logger.info("Attempting to connect to the server...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            logger.info(f"Connected to {self.host}:{self.port}")
            self.socket = AtiSocket(sock, None, None, None, None, self.add_value)

            # Wait for the "ATI" key to be set
            # Wait for the "ATI" key to be set
            for _ in range(1000):
                if self.get_string("ATI"):
                    # print("Received 'ATI' key from server.")
                    break
                threading.Event().wait(0.01)
            else:
                logger.info("Timeout waiting for 'ATI' key from server.")

        except Exception as ex:
            self.socket = None
            self.had_error = True
            if not self.showedError:
                self.showedError = True
                if show_message:
                    logger.error(
                        f"Unable to connect to server ({self.host}/{self.port}): {ex}"
                    )
            self.timer = threading.Timer(10.0, self.on_timer_elapsed)
            self.timer.start()
            return -1
        self.had_error = False
        self.showedError = False
        return 0

    def _handle_connection_error(self, ex: Exception, show_message: bool) -> None:
        """Handle connection failures and schedule retry.

        Args:
            ex: Exception that caused connection failure
            show_message: Whether to log error
        """
        self.socket = None
        self.had_error = True
        if not self.showed_error and show_message:
            self.showed_error = True
            logger.error(f"Connection failed ({self.config.host}:{self.config.port}): {ex}")
        self.timer = threading.Timer(self.config.retry_interval, self.on_timer_elapsed)
        self.timer.start()

    @connection_required
    def send_command(self, command: Union[int, str], *args) -> int:
        """Send command to NinjaTrader server.

        Args:
            command: Command identifier
            *args: Command arguments

        Returns:
            0 on success, -1 on failure
        """
        self.socket.send(command)
        for arg in args:
            self.socket.send(arg)
        return 0

    @connection_required
    def get_string(self, key: str) -> str:
        """Get string value from internal store.

        Args:
            key: Value identifier

        Returns:
            Stored string value or empty string if not found
        """
        with self.lock:
            return self.values.get(key, "")

    @connection_required
    def get_double(self, key: str) -> float:
        """Get float value from internal store.

        Args:
            key: Value identifier

        Returns:
            Stored value as float or 0.0 if invalid/not found
        """
        value = self.get_string(key)
        try:
            return float(value) if value else 0.0
        except ValueError:
            return 0.0

    @connection_required
    def get_int(self, key: str) -> int:
        """Get integer value from internal store.

        Args:
            key: Value identifier

        Returns:
            Stored value as integer or 0 if invalid/not found
        """
        value = self.get_string(key)
        try:
            return int(value) if value else 0
        except ValueError:
            return 0

    def market_data(self, instrument: str, type_: MarketDataType) -> float:
        """Get market data value for instrument.

        Args:
            instrument: Trading instrument identifier
            type_: Type of market data (bid/ask/last etc.)

        Returns:
            Market data value as float
        """
        return self.get_double(f"MarketData|{instrument}|{type_.value}")

    @connection_required
    def all_orders(self, account_name: str, keyword: str = "") -> List[str]:
        """Get all orders for account, optionally filtered by keyword.

        Args:
            account_name: Trading account identifier
            keyword: Optional filter string

        Returns:
            List of order identifiers
        """
        orders = self.get_string(f"Orders|{account_name}").split("|")
        return [order for order in orders if keyword in order] if keyword else orders

    @connection_required
    def order_status(self, order_id: str) -> str:
        """Get current status of specific order.

        Args:
            order_id: Order identifier

        Returns:
            Order status string
        """
        return self.get_string(f"OrderStatus|{order_id}")

    @connection_required
    def open_orders(self, account_name: str) -> Dict[str, int]:
        """Get count of orders by status for account.

        Args:
            account_name: Trading account identifier

        Returns:
            Dictionary of status:count pairs
        """
        status_counts = defaultdict(int)
        for order_id in self.all_orders(account_name):
            status = self.order_status(order_id)
            status_counts[status] += 1
            logger.info(f"{order_id} - {status}")
        return dict(status_counts)

    def flat_instrument(self, account_name: str, instrument_name: str) -> None:
        """Close all positions and cancel all orders for instrument.

        Args:
            account_name: Trading account identifier
            instrument_name: Trading instrument identifier
        """
        try:
            self._execute_flat_sequence(account_name, instrument_name)
        except Exception as ex:
            logger.error(ex)
            self._execute_flat_sequence(account_name, instrument_name)

    def _execute_flat_sequence(self, account_name: str, instrument_name: str) -> None:
        """Execute sequence of operations to flatten position.

        Args:
            account_name: Trading account identifier
            instrument_name: Trading instrument identifier
        """
        self.close_all_positions(account_name, instrument_name)
        time.sleep(0.5)
        self.close_all_positions(account_name, instrument_name)
        self.cancel_all_orders(account_name)
        logger.info(f"Flatted: {account_name} {instrument_name}")

    def __del__(self):
        """Clean up resources on object destruction."""
        if self.socket:
            self.socket.Dispose()
        if self.timer:
            self.timer.cancel()