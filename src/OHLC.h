/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:34:45
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 01:06:09
 */
#ifndef OHLC_H
#define OHLC_H
#include <ctime>
#include <sstream>
#include <string>

#include "ohlc.pb.h"

class OHLC
{
public:
    OHLC(uint16_t tickerId, std::time_t interval);
    OHLC(uint16_t tickerId, std::time_t interval, std::time_t timestamp, double open, double high, double low, double close, uint64_t volume);
    OHLCData get_data() const;
    void update_OHLC(const OHLC& ohlc);
    bool is_initialized() { return initialized; }
    std::time_t get_timestamp() { return timestamp; }

private:
    bool initialized;
    std::time_t timestamp;
    uint16_t tickerId;
    double open;
    double high;
    double low;
    double close;
    uint64_t volume;
    std::time_t interval;
};

#endif  // OHLC_H
