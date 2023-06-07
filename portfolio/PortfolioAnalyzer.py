# maintain two views of your portfolio: a 'real-time' view and a 'lagging' view.
# The real-time view processes events as they come in, ignoring the timestamps,
# while the lagging view processes events sorted by their timestamps.


from engine.EventHandler import EventHandler
from EventBus import EventBus
from model import Asset, EventType, PortfolioConstituent, PortfolioMetrics
from log import LOG


import polars as pl


from collections import defaultdict


class PortfolioAnalyzer(EventHandler):
    def __init__(self, bus: EventBus):
        super().__init__(bus)
        self.df_mtm = pl.DataFrame(
            {
                "timestamp": pl.Series([], dtype=pl.Datetime),
                "mtm": pl.Series([], dtype=pl.Float64),
            }
        )

        self.df_constituents: dict[Asset, pl.DataFrame] = defaultdict(
            lambda: pl.DataFrame(
                {
                    "asset": pl.Series([], dtype=pl.Object),
                    "timestamp": pl.Series([], dtype=pl.Datetime),
                    "price": pl.Series([], dtype=pl.Float64),
                    "amount": pl.Series([], dtype=pl.Float64),
                    "mtm": pl.Series([], dtype=pl.Float64),
                }
            )
        )

    @EventHandler.register(EventType.PORTFOLIO_CONSTITUENT_UPDATE)
    def update_df_constituents(self, constituent: PortfolioConstituent):
        LOG.debug(f"Portfolio constituent updated: {constituent.asset.name}")
        asset = constituent.asset
        self.df_constituents[asset] = self.df_constituents[asset].vstack(
            pl.DataFrame(
                {
                    "asset": pl.Series([asset], dtype=pl.Object),
                    "timestamp": pl.Series(
                        [self.bus.get_timestamp()], dtype=pl.Datetime
                    ),
                    "price": pl.Series([constituent.price], dtype=pl.Float64),
                    "amount": pl.Series([constituent.amount], dtype=pl.Float64),
                    "mtm": pl.Series([constituent.mtm], dtype=pl.Float64),
                }
            )
        )

    @EventHandler.register(EventType.PORTFOLIO_METRICS_UPDATE)
    def update_df_mtm(self, metrics: PortfolioMetrics):
        LOG.debug(f"Portfolio updated: {metrics}")
        self.df_mtm = self.df_mtm.vstack(
            pl.DataFrame(
                {
                    "timestamp": pl.Series(
                        [self.bus.get_timestamp()], dtype=pl.Datetime
                    ),
                    "mtm": pl.Series([metrics.mtm], dtype=pl.Float64),
                }
            )
        )
