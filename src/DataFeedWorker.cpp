/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 22:39:40
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 20:15:31
 */
#include "DataFeedWorker.h"

#include <fstream>
#include <queue>

#include "Logger.h"
#include "TimeUtility.h"
#include "zmq_message.pb.h"

void DataFeedWorker::_initialize_data_structure(uint16_t tickerId, std::vector<std::time_t> interval_list)
{
    base_interval = interval_list[0];
    this->tickerId = tickerId;
    for (const auto& interval : interval_list)
    {
        interval_to_OHLC.emplace(interval, OHLC(tickerId, interval));
    }
};

void DataFeedWorker::_initialize_file_and_mq(zmq::context_t& context, const std::string& file_name, const std::string& address)
{
    publisher = zmq::socket_t(context, ZMQ_PUB);
    publisher.bind(address);
    this->file_name = file_name;
};

DataFeedWorker::DataFeedWorker(uint16_t tickerId, std::vector<std::time_t> interval_list,
                               zmq::context_t& context, const std::string& file_name, const std::string& address)
{
    _initialize_file_and_mq(context, file_name, address);
    _initialize_data_structure(tickerId, interval_list);
    Logger::info("Initialized DataFeedWorker for tickerId: " + std::to_string(tickerId));
    log_thread = std::thread(&DataFeedWorker::log_sent_count, this);
}

void DataFeedWorker::send_ohlc_data(const zmq_message::OHLCData& data)
{
    zmq_message::Wrapper message_wrapper;
    message_wrapper.set_type(zmq_message::MessageType::MESSAGE_OHLCData);
    *message_wrapper.mutable_data() = data;  // Use mutable_data to set the OHLCData field

    std::string serialized_message_wrapper;
    message_wrapper.SerializeToString(&serialized_message_wrapper);

    zmq::message_t zmq_message(serialized_message_wrapper.size());
    memcpy(zmq_message.data(), serialized_message_wrapper.data(), serialized_message_wrapper.size());
    publisher.send(zmq_message, zmq::send_flags::none);
}

void DataFeedWorker::read_and_publish(const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double scaling_factor)
{
    std::ifstream file(file_name);
    if (!file.is_open())
    {
        Logger::error("Failed to open CSV file: " + file_name);
        return;
    }
    std::string line;
    std::queue<OHLC> ready_to_send;
    while (std::getline(file, line))
    {
        std::stringstream ss(line);
        std::string datetime, open_str, high_str, low_str, close_str, volume_str;
        std::getline(ss, datetime, ';');
        std::getline(ss, open_str, ';');
        std::getline(ss, high_str, ';');
        std::getline(ss, low_str, ';');
        std::getline(ss, close_str, ';');
        std::getline(ss, volume_str, ';');

        double open = std::stod(open_str);
        double high = std::stod(high_str);
        double low = std::stod(low_str);
        double close = std::stod(close_str);
        uint64_t volume = std::stoull(volume_str);

        std::time_t timestamp = parse_timestamp(datetime);

        if (!first_timestamp_set)
        {
            first_timestamp = timestamp;
            first_timestamp_set = true;
            Logger::info("First timestamp set: " + std::to_string(first_timestamp));
        }

        OHLC& base_ohlc = interval_to_OHLC.at(base_interval);
        for (auto& [interval, ohlc] : interval_to_OHLC)
        {
            if (!ohlc.is_initialized())
            {
                ohlc.update_OHLC(base_ohlc);
                continue;
            }

            if (timestamp - ohlc.get_timestamp() < interval)
            {
                ohlc.update_OHLC(base_ohlc);
                continue;
            }

            ready_to_send.push(std::move(ohlc));
            ohlc = {tickerId, interval, timestamp, open, high, low, close, volume};  // Reuse the existing object
        }

        while (true)
        {
            auto current_time = std::chrono::high_resolution_clock::now();
            auto elapsed_real_time = std::chrono::duration_cast<std::chrono::seconds>(current_time - start_time).count();
            auto scaled_elapsed_time = static_cast<std::time_t>(elapsed_real_time * scaling_factor);

            if (scaled_elapsed_time >= (timestamp - first_timestamp))
            {
                while (!ready_to_send.empty())
                {
                    try
                    {
                        send_ohlc_data(ready_to_send.front().get_data());
                        ready_to_send.pop();
                    }
                    catch (const std::exception& e)
                    {
                        Logger::error("Exception in send_ohlc_data: " + std::string(e.what()));
                        raise;
                    }
                    sent_count += 1;
                }
                break;
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(1));  // Sleep briefly to avoid busy-waiting
        }
    }
    Logger::info("Finished processing file: " + file_name);
    file.close();
    done = true;  // Mark as done after processing all data

    // Ensure logging thread completes
    if (log_thread.joinable())
    {
        log_thread.join();
    }
}

void DataFeedWorker::run(const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double scaling_factor)
{
    read_and_publish(start_time, scaling_factor);
}

bool DataFeedWorker::is_done() const
{
    return done;
}

void DataFeedWorker::log_sent_count()
{
    while (!is_done())
    {
        std::this_thread::sleep_for(std::chrono::seconds(5));
        Logger::info("TickerID: " + std::to_string(tickerId) + " has sent " + std::to_string(sent_count) + " OHLC so far.");
    }
    // Log the final count when done
    Logger::info("TickerID " + std::to_string(tickerId) + " sent count in total: " + std::to_string(sent_count));
}