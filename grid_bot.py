"""
Blofin BTCUSDT Grid Trading Bot
- Uses limit (maker) orders exclusively for lowest fees (0.02%)
- Auto-recalculates grid when price breaks range
- Stop-loss protection and live PnL tracking
"""

import time
import logging
import sys
import os
from blofin_client import BlofinClient
from risk_manager import RiskManager
from config import (
    SYMBOL, TOTAL_CAPITAL, LEVERAGE,
    GRID_LEVELS, GRID_RANGE_PCT, MAKER_FEE
)

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/grid_bot.log"),
    ],
)
logger = logging.getLogger(__name__)


class GridBot:
    def __init__(self):
        self.client = BlofinClient()
        self.symbol = SYMBOL
        self.capital = TOTAL_CAPITAL
        self.leverage = LEVERAGE
        self.grid_levels = GRID_LEVELS
        self.grid_range_pct = GRID_RANGE_PCT
        self.grids = []
        self.risk_manager = None
        self.total_pnl = 0.0
        self.trade_count = 0

    def calculate_grids(self, center_price: float) -> list:
        upper = center_price * (1 + self.grid_range_pct / 100)
        lower = center_price * (1 - self.grid_range_pct / 100)
        step = (upper - lower) / self.grid_levels
        grids = [round(lower + i * step, 1) for i in range(self.grid_levels + 1)]
        logger.info(f"Grid calculated: {len(grids)} levels | Range: [{lower:.1f} - {upper:.1f}] | Step: ${step:.1f}")
        return grids

    def calculate_order_size(self, price: float) -> float:
        capital_per_grid = (self.capital * self.leverage) / self.grid_levels
        size = capital_per_grid / price
        min_size = 0.001
        return max(round(size, 4), min_size)

    def place_grid_orders(self, current_price: float):
        logger.info("Placing grid orders...")
        self.client.cancel_all_orders(self.symbol)
        self.grids = self.calculate_grids(current_price)
        placed = 0
        for price in self.grids:
            if abs(price - current_price) / current_price < 0.001:
                continue
            side = "buy" if price < current_price else "sell"
            size = self.calculate_order_size(price)
            try:
                result = self.client.place_order(self.symbol, side, price, size)
                if result.get("code") == "0":
                    placed += 1
                    fee_cost = price * size * MAKER_FEE
                    logger.debug(f"  {side.upper()} @ {price:.1f} | Size: {size} BTC | Fee: ${fee_cost:.4f}")
                else:
                    logger.warning(f"Order failed @ {price:.1f}: {result}")
            except Exception as e:
                logger.error(f"Error placing order @ {price:.1f}: {e}")
        logger.info(f"Grid active: {placed} orders placed")

    def check_filled_orders(self) -> float:
        open_orders = self.client.get_open_orders(self.symbol)
        open_prices = {float(o["price"]) for o in open_orders}
        cycle_pnl = 0.0
        for grid_price in self.grids:
            if grid_price not in open_prices:
                step = (self.grids[-1] - self.grids[0]) / self.grid_levels if len(self.grids) > 1 else 0
                size = self.calculate_order_size(grid_price)
                gross_profit = step * size
                fee = grid_price * size * MAKER_FEE * 2
                net = gross_profit - fee
                cycle_pnl += net
                self.trade_count += 1
        return cycle_pnl

    def run(self):
        logger.info("=== Blofin Grid Bot Starting ===")
        logger.info(f"Symbol: {self.symbol} | Capital: ${self.capital} | Leverage: {self.leverage}x")
        logger.info(f"Grid Levels: {self.grid_levels} | Range: +/-{self.grid_range_pct}%")

        self.client.set_leverage(self.symbol, self.leverage)
        current_price = self.client.get_ticker(self.symbol)
        logger.info(f"Entry price: ${current_price:,.1f}")

        self.risk_manager = RiskManager(current_price, self.capital)
        self.place_grid_orders(current_price)

        poll_interval = 30
        rebalance_count = 0

        while True:
            try:
                time.sleep(poll_interval)
                current_price = self.client.get_ticker(self.symbol)

                if self.risk_manager.is_stop_loss_triggered(current_price):
                    logger.critical("STOP LOSS HIT - cancelling all orders and shutting down.")
                    self.client.cancel_all_orders(self.symbol)
                    break

                if self.risk_manager.is_out_of_range(current_price):
                    logger.warning(f"Price {current_price:.1f} out of range - rebalancing grid...")
                    self.risk_manager = RiskManager(current_price, self.capital)
                    self.place_grid_orders(current_price)
                    rebalance_count += 1

                cycle_pnl = self.check_filled_orders()
                self.total_pnl += cycle_pnl

                if rebalance_count % 10 == 0 or cycle_pnl > 0:
                    self.risk_manager.log_status(current_price, self.total_pnl)
                    logger.info(f"Total trades: {self.trade_count} | Total PnL: ${self.total_pnl:.2f}")

            except KeyboardInterrupt:
                logger.info("Bot stopped by user. Cancelling all orders...")
                self.client.cancel_all_orders(self.symbol)
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(60)


if __name__ == "__main__":
    bot = GridBot()
    bot.run()
