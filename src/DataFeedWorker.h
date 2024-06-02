/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 20:24:03
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 19:32:09
 */

#ifndef DATA_FEED_WORKER_H
#define DATA_FEED_WORKER_H

#include <string>
#include <thread>
#include <unordered_map>
#include <vector>
#include <zmq.hpp>

#include "OHLC.h"

class DataFeedWorker
{
public:
    DataFeedWorker(uint16_t tickerId, std::vector<std::time_t> interval_list,
                   zmq::context_t& context, const std::string& file_name, const std::string& address);

    void run(const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double scaling_factor);
    bool is_done() const;

private:
    void _initialize_data_structure(uint16_t tickerId, std::vector<std::time_t> interval_list);
    void _initialize_file_and_mq(zmq::context_t& context, const std::string& file_name, const std::string& address);
    void send_ohlc_data(const zmq_message::OHLCData& data);
    void read_and_publish(const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double scaling_factor);
    void log_sent_count();  // Function to log sent count periodically

    zmq::socket_t publisher;
    std::time_t first_timestamp;
    bool first_timestamp_set;
    std::string file_name;
    std::unordered_map<std::time_t, OHLC> interval_to_OHLC;
    std::time_t base_interval;
    uint16_t tickerId;
    bool done;
    size_t sent_count = 0;
    std::thread log_thread;  // Thread for logging
};

#endif  // DATA_FEED_WORKER_H