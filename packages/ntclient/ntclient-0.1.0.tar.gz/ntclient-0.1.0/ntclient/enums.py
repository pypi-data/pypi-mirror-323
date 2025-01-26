from enum import Enum


class Message(Enum):
    """Enum for message types in a communication protocol."""
    COMMAND = 0
    DATA = 1
    VALUE = 2
    CONFIRMORDERS = 3
    SUBSCRIBE = 4


class StrategyCommands(Enum):
    """Enum for trading strategy commands."""
    START = "START"
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    SET_PARAMETER = "SET_PARAMETER"


class ActionTypes(Enum):
    """Enum for different action types used in trading strategies."""
    # Entry actions
    BUY = "BUY"
    SELL = "SELL"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    # Exit actions
    EXIT_LONG = "EXIT_LONG"
    EXIT_SHORT = "EXIT_SHORT"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    # Neutral state
    FLAT = "FLAT"


class OrderTypes(Enum):
    """Enum for supported order types."""
    MARKET = "MARKET"
    STOP_MARKET = "STOPMARKET"
    MIT = "MIT"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOPLIMIT"
    TRAIL_STOP = "TRAILSTOP"
    TRAIL_STOP_LIMIT = "TRAILSTOPLIMIT"


class TradingStrategy(Enum):
    """Enum for predefined trading strategies."""
    ST5PT_50SL = "ST5PT_50SL"  # 5-point target, 50-point stop loss
    ST30PT_50SL = "ST30PT_50SL"  # 30-point target, 50-point stop loss
    ST2Q2PT_20SL = "ST2Q2PT_20SL"  # 2-quarter point target, 20-point stop loss
    ST30_PT_30SL = "ST30_PT_30SL"  # 30-point target, 30-point stop loss
    ST12PT_200SL = "ST12PT_200SL"  # 12-point target, 200-point stop loss


class NTOrderStatus(Enum):
    """Enum for NinjaTrader order statuses."""
    WORKING = "Working"
    ACCEPTED = "Accepted"
    SUBMITTED = "Submitted"
    FILLED = "Filled"
    PARTIALLY_FILLED = "Partiallyfilled"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"
    EXPIRED = "Expired"
    PENDING = "Pending"
    TRIGGERED = "Triggered"
    AMENDED = "Amended"
    MARKET_ORDER = "Marketorder"


class OrcaOrderStatus(Enum):
    """Enum for Orca trading system order statuses."""
    PLACED = "PLACED"
    FILLED = "FILLED"
    PENDING = "PENDING"


class MarketDataType(Enum):
    """Enum for different types of market data."""
    Ask = 0
    Bid = 1
    Last = 2
    DailyHigh = 3
    DailyLow = 4
    DailyVolume = 5
    LastClose = 6
    Opening = 7
    OpenInterest = 8
    Settlement = 9
    Unknown = 10


class OrderCommands(Enum):
    """Enum for commands related to order handling."""
    PLACE = 0
    CANCEL = 1
    CHANGE = 2
    CLOSEPOSITION = 3
    CLOSESTRATEGY = 4
    CANCELALLORDERS = 5

class NTCommand(Enum):
    Place = "Place"
    Cancel = "Cancel"
    Change = "Change"
    ClosePosition = "ClosePosition"
    CloseStrategy = "CloseStrategy"
    CancelAllOrders = "CancelAllOrders"

