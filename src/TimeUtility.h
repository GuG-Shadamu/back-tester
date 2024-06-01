/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 19:19:03
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 23:10:32
 */
#ifndef TIME_UTILS_H
#define TIME_UTILS_H

#include <ctime>
#include <string>

// Function to parse timestamp from string to time_t (seconds since epoch)
std::time_t parse_timestamp(const std::string &datetime);
#endif  // TIME_UTILS_H
