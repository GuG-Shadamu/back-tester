#!/bin/bash
# @Author: Tairan Gao
# @Date:   2024-06-01 10:07:49
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2024-06-01 19:19:46

PROTO_DIR="protos"

# Loop through all .proto files in the specified directory
for proto_file in $PROTO_DIR/*.proto; do
    echo "Compiling Python $proto_file"
    protoc --python_out=. $proto_file
done

rm -rf build
mkdir build
cd build




cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
