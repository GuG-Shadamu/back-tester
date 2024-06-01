/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:34:45
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 22:41:28
 */
#ifndef OHLC_H
#define OHLC_H

#include <ctime>
#include <sstream>
#include <string>

struct OHLCData
{
    std::time_t timestamp;
    uint16_t tickerId;
    double open;
    double high;
    double low;
    double close;
    uint64_t volume;
    std::time_t interval;
    // Serialize OHLCData to a delimited string
    std::string to_string() const
    {
        std::stringstream ss;
        ss << timestamp << ";" << tickerId << ";" << open << ";" << high << ";" << low << ";" << close << ";" << volume << ";" << interval;
        return ss.str();
    }

    // Deserialize OHLCData from a delimited string
    static OHLCData from_string(const std::string& str)
    {
        std::stringstream ss(str);
        OHLCData data;
        std::string token;
        // Capture ss by reference to use it inside the lambda
        auto read_and_ignore = [&ss, &token](auto& field)
        {
            std::getline(ss, token, ';');
            std::stringstream(token) >> field;
        };

        read_and_ignore(data.timestamp);
        read_and_ignore(data.tickerId);
        read_and_ignore(data.open);
        read_and_ignore(data.high);
        read_and_ignore(data.low);
        read_and_ignore(data.close);
        read_and_ignore(data.volume);
        read_and_ignore(data.interval);

        return data;
    }
};

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
