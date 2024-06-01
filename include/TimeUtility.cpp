/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 23:09:22
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 23:10:35
 */

#include "TimeUtility.h"

#include <iomanip>
#include <sstream>

std::time_t parse_timestamp(const std::string &datetime)
{
    std::tm tm = {};
    std::stringstream ss(datetime);
    ss >> std::get_time(&tm, "%Y%m%d %H%M%S");
    return std::mktime(&tm);
}
