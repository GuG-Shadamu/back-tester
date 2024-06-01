/*
 * @Author: Tairan Gao
 * @Date:   2024-05-31 21:06:02
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2024-05-31 23:02:10
 */
#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H
#include <stdexcept>
#include <string>

class NotImplemented : public std::logic_error
{
public:
    NotImplemented() : std::logic_error("Function not yet implemented"){};
};
#endif  // EXCEPTIONS_H