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

from ntclient.enums import MarketDataType, NTCommand
from ntclient.socket import AtiSocket
from ntclient.utils import config_logging

logger = config_logging(__name__)




def connection_required(show_message=True, equal=True):
    """
        Decorator ensuring socket connection exists before executing method.


    :param show_message:
    :param equal:
    :return:
            The decorated function or a default return value if connection check fails.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            connection_status = self.set_up(show_message)
            if (equal and connection_status != 0) or (not equal and connection_status == 0):
                return self._get_default_return_value(func)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator



def connection_requireds(func, show_message=True, equal=True):
    """
    Decorator ensuring socket connection exists before executing method.

    Parameters:
        show_message (bool): Whether or not to show a message if the connection check fails. Defaults to True.
        equal (bool): Additional parameter for future use, defaults to True.

    Returns:
        The decorated function or a default return value if connection check fails.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Perform connection check once
        connection_status = self.set_up(show_message)

        # Check if connection status matches expectations
        if (equal and connection_status == 0) or (not equal and connection_status != 0):
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
            0 means the client is connected to the server
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

    def set_up_now(self, show_message: bool) -> int:
        """Establish socket connection immediately.

        Args:
            show_message: Whether to log connection errors

        Returns:
            0 on success, -1 on failure
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.config.host, self.config.port))
            self.socket = AtiSocket(sock, None, None, None, None, self.add_value)

            # Wait for the "ATI" key to be set
            for _ in range(1000):
                if self.get_string("ATI"):
                    break
                threading.Event().wait(0.01)
            else:
                logger.info("Timeout waiting for 'ATI' key from server.")
                return -1

        except Exception as ex:
            self._handle_connection_error(ex, show_message)
            return -1

        self.had_error = False
        self.showed_error = False
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

    def on_timer_elapsed(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.set_up_now(True)


    def get_string(self, key: str) -> str:
        """Get string value from internal store.

        Args:
            key: Value identifier

        Returns:
            Stored string value or empty string if not found
        """
        if self.set_up(True) != 0:
            # connection is lost here
            return ""

        # if it reached here, it means the connection is established
        with self.lock:
            return self.values.get(key, "")

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


    @connection_required
    def get_cash_value(self, account_name: str) -> float:
            return self.get_double(f"CashValue|{account_name}")

    @connection_required
    def buying_power(self, account_name: str):
            return self.get_double(f"BuyingPower|{account_name}")



    def _execute_flat_sequence(self, account_name: str, instrument_name: str) -> None:
        """Execute sequence of operations to flatten position.

        Args:
            account_name: Trading account identifier
            instrument_name: Trading instrument identifier
        """
        self.close_all_positions(account_name, instrument_name)
        time.sleep(0.2)
        self.close_all_positions(account_name, instrument_name)
        self.cancel_all_orders(account_name)
        logger.info(f"Flatted: {account_name} {instrument_name}")

    # TODO: not used
    def dispose(self):
        if self.socket:
            self.socket.Dispose()
            self.socket = None
        if self.timer:
            self.timer.cancel()
            self.timer = None

    # region Fucntion :
    def send_command(self, command: int, *args) -> int:
        if self.set_up(True) != 0:
            return -1

        self.socket.send(command)
        for arg in args:
            self.socket.send(arg)
        return 0

    def ask(self, instrument: str, price: float, size: int) -> int:
        return self.send_command(1, 0, instrument, price, size, "")

    def bid(self, instrument, price, size):
        return self.send_command(1, 1, instrument, price, size, "")

    def last(self, instrument, price, size):
        return self.send_command(1, 2, instrument, price, size, "")

    def subscribe_market_data(self, instrument: str) -> int:
        """
                # Subscribe to market data if needed
        :param instrument:
        :return:
        """
        if self.get_last_price(instrument) == 0:
            logger.debug(f"Subscribing to market data for {instrument}")
            return self.send_command(4, instrument, 1)
        else:
            logger.debug(f"Already subscribed to market data for {instrument}")

    def unsubscribe_market_data(self, instrument:str):
        return self.send_command(4, instrument, 0)

    def command(
        self,
        command,
        account,
        instrument,
        order_id,
        oco="",
        action="",
        quantity=0,
        order_type="",
        limit_price=0,
        stop_price=0,
        time_in_force="",
        tpl="",
        strategy="",
    )-> int:

        #     # Prepare a list of parameters that are not None (or empty) and build the cmd_string
        #     params = [
        #         command,
        #         account,
        #         instrument,
        #         action or "",  # Default to empty string if None
        #         quantity,
        #         order_type or "",
        #         limit_price,
        #         stop_price,
        #         time_in_force or "",
        #         oco or "",
        #         order_id,
        #         tpl or "",
        #         strategy or "",
        #     ]
        #
        #     cmd_string = ";".join(map(str, params))

        cmd_string = f"{command};{account};{instrument};{action};{quantity};{order_type};{limit_price};{stop_price};{time_in_force};{oco};{order_id};{tpl};{strategy}"
        return self.send_command(0, cmd_string)

    def flat_accounts_instrument(self, account_names: list[str], instrument_name: str)  -> None:
        for account_name in account_names:
            # Close all positions for the specified account and instrument.
            self.close_all_positions(account_name, instrument_name)

            # Cancel all orders for the specified account.
            self.cancel_all_orders(account_name)



    def close_all_positions(self, account_name: str, instrument_name: str) -> None:
        """
        Close all positions for a specified account and instrument.
        """
        self.command(
            NTCommand.ClosePosition.value,
            account_name,
            instrument_name,
            "FLAT",
            0,
            "",
            0.0,
            0.0,
            "",
            "",
            "",
            "",
            "",
        )

    def cancel_all_orders(self, account_name: str):
        """
        Cancel all orders for a specified account.
        """
        self.command(
            NTCommand.CancelAllOrders.value,
            account_name,
            "",
            "",
            0,
            "",
            0,
            0,
            "GTC",
            "",
            "",
            "",
            "",
        )

    def cancel_order_adv(self, account_name: str, instrument_name: str, order_id: str):
        """
        Cancel a specific order for a specified account and instrument.
        """
        # Send the command to cancel the specified order.
        self.command(
            NTCommand.Cancel.value,
            account_name,
            instrument_name,
            "",
            0,
            "",
            0,
            0,
            "GTC",
            "",
            order_id,
            "",
            "",
        )
        logger.info(f"* Order {order_id} is Cancelled ********************")
        time.sleep(0.1)
        self.command(
            NTCommand.Cancel.value,
            account_name,
            instrument_name,
            "",
            0,
            "",
            0,
            0,
            "GTC",
            "",
            order_id,
            "",
            "",
        )
        logger.info(f"* Order {order_id} is Cancelled ********************")


    def connected(self, show_message: bool = True) -> int:
        if (
            self.set_up(show_message == 1) == 0
            and not self.showed_error
            and self.socket
            and self.socket.is_connected
        ):
            if self.get_string("ATI") == "True":
                return 0
        return -1

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

    # endregion




    # region Order Management
    def market_data(self, instrument: str, type_: MarketDataType) -> float:
        """Get market data value for instrument.

        Args:
            instrument: Trading instrument identifier
            type_: Type of market data (bid/ask/last etc.)

        Returns:
            Market data value as float
        """
        return self.get_double(f"MarketData|{instrument}|{type_.value}")

    def market_position(self, instrument_name: str, account_name: str) -> int:
        key = f"MarketPosition|{instrument_name}|{account_name}"
        return self.get_int(key)

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

    @connection_required(equal=True)
    def order_status(self, order_id: str) -> str:
        """Get current status of specific order.

        Args:
            order_id: Order identifier

        Returns:
            Order status string
        """
        return self.get_string(f"OrderStatus|{order_id}")

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

    def get_last_price(self, instrument_name: str) -> float:
        return self.market_data(instrument_name, MarketDataType.Last)

    @connection_required(equal=True)
    def target_orders(self, strategy_id: str) -> int:
        return self.get_int(f"TargetOrders|{strategy_id}")

    @connection_required
    def filled(self, order_id: str) -> int:
        return self.get_int(f"Filled|{order_id}")


    @connection_required
    def get_orders_brackets_ids(self, account_name: str) -> []:
        """
        Retrieve the stop and profit order IDs
        """
        _orders = self.get_string("Orders|" + account_name)
        return _orders.split("|")[-2:]



    # endregion

    def __del__(self):
        """Clean up resources on object destruction."""
        if self.socket:
            self.socket.Dispose()
        if self.timer:
            self.timer.cancel()