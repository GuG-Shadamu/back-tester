/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 18:25:00
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 23:33:23
 */

#ifndef LOGGER_H
#define LOGGER_H

#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/spdlog.h>

#include <memory>

class Logger
{
public:
    static void init(const std::string &file_name, spdlog::level::level_enum log_level)
    {
        instance().file_logger = spdlog::basic_logger_mt("file_logger", file_name);
        instance().file_logger->set_level(log_level);
        instance().file_logger->set_pattern("%Y-%m-%d %H:%M:%S.%e %l: %v");
        spdlog::flush_on(log_level);  // Flush logs immediately based on log level
    }

    static std::shared_ptr<spdlog::logger> get_logger()
    {
        return instance().file_logger;
    }

    static void info(const std::string &message)
    {
        instance().file_logger->info(message);
    }

    static void error(const std::string &message)
    {
        instance().file_logger->error(message);
    }

private:
    Logger() = default;

    static Logger &instance()
    {
        static Logger logger_instance;
        return logger_instance;
    }

    ~Logger()
    {
        if (file_logger)
        {
            file_logger->flush();  // Ensure all logs are flushed on destruction
        }
    }

    std::shared_ptr<spdlog::logger> file_logger;
};

#endif  // LOGGER_H
