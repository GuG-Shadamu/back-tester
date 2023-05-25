# Back Tester

Pet-project for quant trading self-training.

This project serves as a robust and efficient quantitative trading backtester, built from the ground up with Python. It has been carefully designed to accurately simulate the intricacies of real-world trading, helping to validate trading strategies

## Key Features

- **Event-Driven Architecture**: The backtester operates on an event-driven system that accurately simulates the order of market events, providing a strong foundation for concurrent processing.
- **Asynchronous Programming**: The backtester uses asyncio for writing single-threaded concurrent code, which allows for efficient multiplexing of I/O access over various resources.
- **Data Handling with Polars**: Leveraging the power of Polars, a lightning-fast DataFrame library implemented in Rust, for efficient and effective data handling.
- **Flexible and Powerful**: The backtester is designed to be adaptable, allowing for the testing of a wide variety of trading strategies, from simple moving average cross-overs to complex machine learning-based approaches.

## Main Components

- **Data Feed**: The data feed component is responsible for providing the backtester with market data. This can be historical data for backtesting purposes or live data for paper trading.
- **Strategy**: This component is where you define your trading strategy. It processes market data and generates trading signals.
- **Execution Handler**: The execution handler simulates order execution. It takes trading signals from the strategy component and simulates the execution of the corresponding orders.
- **Performance Tracking**: The backtester includes functionality for tracking the performance of a strategy over the course of a backtest. This includes calculating various performance metrics and generating performance charts.
- **Risk Management** : involving setting limits on the total exposure to any one asset, ensuring that the portfolio is sufficiently diversified, rebalancing the portfolio periodically, etc.

## Future Development

- [x] [Polars](https://www.pola.rs/) as data handller
- [ ] [Redis](https://redis.io/) as historical data & store frequently used data (e.g. like the latest prices or indicators calculated over a rolling window)
- [ ] Restful API to fetch real-time or historical data from an external source

## Main Idea

[![infra](assets/fig1.png)](assets/fig1.png)
