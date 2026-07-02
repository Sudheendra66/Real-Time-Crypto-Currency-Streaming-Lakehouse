from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class MarketEvent:

    symbol: str
    asset_class: str

    trade_id: int

    trade_price: float
    trade_quantity: float

    event_type: str

    trade_timestamp: int

    source: str
    loaded_at: str
    batch_id: str

    @classmethod
    def from_binance(cls, event):

        trade = event["data"]

        return cls(

            symbol=trade["s"],

            asset_class="crypto",

            trade_id=trade["t"],

            trade_price=float(trade["p"]),

            trade_quantity=float(trade["q"]),

            event_type=trade["e"],

            trade_timestamp=trade["T"],

            source="binance",

            loaded_at=datetime.utcnow().isoformat(),

            batch_id=str(uuid.uuid4())
        )

    def to_dict(self):

        return {
            "symbol": self.symbol,
            "asset_class": self.asset_class,

            "trade_id": self.trade_id,

            "trade_price": self.trade_price,
            "trade_quantity": self.trade_quantity,

            "event_type": self.event_type,

            "trade_timestamp": self.trade_timestamp,

            "_source": self.source,
            "_loaded_at": self.loaded_at,
            "_batch_id": self.batch_id
        }