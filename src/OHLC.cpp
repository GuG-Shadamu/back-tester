/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:34:36
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 23:36:57
 */

#include "OHLC.h"

#include <algorithm>  // for std::min and std::max
#include <limits>

#include "Exceptions.h"

OHLC::OHLC(uint16_t tickerId, std::time_t interval)
    : tickerId(tickerId), interval(interval), initialized(false)
{
    timestamp = 0;
    open = 0;
    high = 0;
    low = std::numeric_limits<double>::max();
    close = 0;
    volume = 0;
}

OHLC::OHLC(uint16_t tickerId, std::time_t interval, std::time_t timestamp, double open, double high, double low, double close, uint64_t volume)
    : tickerId(tickerId), interval(interval), initialized(true)
{
    timestamp = timestamp;
    open = open;
    high = high;
    low = low;
    close = close;
    volume = volume;
}

OHLCData OHLC::get_data() const
{
    return {timestamp, tickerId, open, high, low, close, volume, interval};
}

void OHLC::update_OHLC(const OHLC &base_ohlc)
{
    OHLCData base_data = base_ohlc.get_data();
    timestamp = std::max(base_data.timestamp, timestamp);
    open = std::min(base_data.open, open);
    high = std::max(base_data.high, high);
    low = std::min(base_data.low, low);
    close = base_data.close;
    volume += base_data.volume;
    initialized = true;
}