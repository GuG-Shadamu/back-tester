/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:20:00
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-06-01 02:01:03
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

int main()
{
    // Initialize logger
    Logger::init("Back-Tester_LoadData.log", spdlog::level::info);
    Logger::info("Starting ...");
    zmq::context_t context(1);

    DataFeedWorker worker1(1, {300, 1800, 3600}, context, "data_example/DAT_ASCII_USDCAD_M1_2022.csv", "tcp://*:5555");
    DataFeedWorker worker2(2, {100, 1200, 2000}, context, "data_example/DAT_ASCII_USDCAD_M1_2023.csv", "tcp://*:5556");

    std::vector<DataFeedWorker*> workers = {&worker1, &worker2};

    auto start_time = std::chrono::high_resolution_clock::now();
    const double scaling_factor = 360000.0;
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
