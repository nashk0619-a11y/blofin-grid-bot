import logging
from config import STOP_LOSS_PCT, GRID_RANGE_PCT

logger = logging.getLogger(__name__)


class RiskManager:
    def __init__(self, entry_price: float, capital: float):
        self.entry_price = entry_price
        self.capital = capital
        self.stop_loss_price = entry_price * (1 - STOP_LOSS_PCT / 100)
        self.upper_bound = entry_price * (1 + GRID_RANGE_PCT / 100)
        self.lower_bound = entry_price * (1 - GRID_RANGE_PCT / 100)

    def is_stop_loss_triggered(self, current_price: float) -> bool:
        if current_price <= self.stop_loss_price:
            logger.warning(
                f"STOP LOSS triggered: current={current_price:.1f} <= stop={self.stop_loss_price:.1f}"
            )
            return True
        return False

    def is_out_of_range(self, current_price: float) -> bool:
        return current_price < self.lower_bound or current_price > self.upper_bound

    def log_status(self, current_price: float, pnl: float):
        pnl_pct = (pnl / self.capital) * 100
        logger.info(
            f"Price: {current_price:.1f} | PnL: ${pnl:.2f} ({pnl_pct:.2f}%) | "
            f"Range: [{self.lower_bound:.1f} - {self.upper_bound:.1f}] | "
            f"StopLoss: {self.stop_loss_price:.1f}"
        )
