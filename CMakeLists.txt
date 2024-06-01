cmake_minimum_required(VERSION 3.10)

# Set the project name
project(Back-Tester)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/protos) # Include protos directory

# Find ZeroMQ package
find_package(PkgConfig REQUIRED)
pkg_check_modules(PC_ZMQ QUIET zmq)

find_path(ZMQ_INCLUDE_DIR
  NAMES zmq.hpp
  PATHS ${PC_ZMQ_INCLUDE_DIRS})

find_library(ZMQ_LIBRARIES
  NAMES zmq
  PATHS ${PC_ZMQ_LIBRARY_DIRS})

include_directories(${ZMQ_INCLUDE_DIR})

# Find spdlog package
find_package(spdlog REQUIRED)

# Add the executable
file(GLOB SOURCES "src/*.cpp" "protos/*.cc") # Include protos source files
add_executable(Back-Tester ${SOURCES})

# Link libraries
target_link_libraries(Back-Tester ${ZMQ_LIBRARIES} spdlog::spdlog)

# Link Protobuf library
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})
target_link_libraries(Back-Tester ${PROTOBUF_LIBRARIES})