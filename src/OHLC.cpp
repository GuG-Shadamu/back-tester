/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:34:36
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 10:20:27
 */

#include "OHLC.h"

#include <algorithm>  // for std::min and std::max
#include <limits>

#include "Exceptions.h"
#include "zmq_message.pb.h"

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
    : tickerId(tickerId), interval(interval), initialized(true), timestamp(timestamp), open(open), high(high), low(low), close(close), volume(volume)
{
}

zmq_message::OHLCData OHLC::get_data() const
{
    zmq_message::OHLCData data;
    data.set_timestamp(static_cast<int64_t>(timestamp));
    data.set_tickerid(tickerId);
    data.set_open(open);
    data.set_high(high);
    data.set_low(low);
    data.set_close(close);
    data.set_volume(volume);
    data.set_interval(static_cast<int64_t>(interval));
    return data;
}

void OHLC::update_OHLC(const OHLC &base_ohlc)
{
    timestamp = std::max(base_ohlc.timestamp, timestamp);
    open = std::min(base_ohlc.open, open);
    high = std::max(base_ohlc.high, high);
    low = std::min(base_ohlc.low, low);
    close = base_ohlc.close;
    volume += base_ohlc.volume;
    initialized = true;
}