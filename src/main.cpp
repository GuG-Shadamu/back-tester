/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:20:00
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 00:05:00
 */
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <zmq.hpp>

#include "DataFeedWorker.h"
#include "Logger.h"
#include "OHLC.h"
#include "TimeUtility.h"

void send_ohlc_data(zmq::context_t& context, const std::string& address, const std::vector<OHLC> ohlc_list)
{
    zmq::socket_t publisher(context, ZMQ_PUB);
    publisher.bind(address);

    for (const auto& ohlc : ohlc_list)
    {
        OHLCData data = ohlc.get_data();
        std::string message = data.to_string();
        zmq::message_t zmq_message(message.size());
        memcpy(zmq_message.data(), message.c_str(), message.size());
        publisher.send(zmq_message, zmq::send_flags::none);
    }
}

int main()
{
    // Initialize logger
    Logger::init("Back-Tester.log", spdlog::level::info);
    Logger::info("Starting ...");
    zmq::context_t context(1);

    DataFeedWorker worker1(1, {300, 1800, 3600}, context, "data_example/DAT_ASCII_USDCAD_M1_2022.csv", "tcp://*:5555");
    DataFeedWorker worker2(2, {300, 1800, 3600}, context, "data_example/DAT_ASCII_USDCAD_M1_2023.csv", "tcp://*:5556");

    std::vector<DataFeedWorker*> workers = {&worker1, &worker2};

    auto start_time = std::chrono::high_resolution_clock::now();
    const double scaling_factor = 36000.0;
    Logger::info("Starting shreads for workers");
    std::vector<std::thread> threads;
    for (DataFeedWorker* worker : workers)
    {
        threads.emplace_back(&DataFeedWorker::run, worker, std::cref(start_time), scaling_factor);
    }

    // Wait for all workers to finish
    for (auto& thread : threads)
    {
        thread.join();
    }
    return 0;
}
