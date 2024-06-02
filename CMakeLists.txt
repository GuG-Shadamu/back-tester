cmake_minimum_required(VERSION 3.10)

# Set the project name
project(Back-Tester)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Set the build type to Debug by default
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/protos) # Include the correct protos directory

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

# Find Protobuf package
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})

# Generate the protobuf sources
file(GLOB PROTO_FILES "${PROJECT_SOURCE_DIR}/protos/*.proto")
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})

# Add the executable
file(GLOB SOURCES "src/*.cpp") # Source files in src directory
add_executable(Back-Tester ${SOURCES} ${PROTO_SRCS} ${PROTO_HDRS}) # Include generated protobuf sources

# Link libraries
target_link_libraries(Back-Tester ${ZMQ_LIBRARIES} spdlog::spdlog ${PROTOBUF_LIBRARIES})

# Add additional debug flags if necessary (optional)
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
endif()
