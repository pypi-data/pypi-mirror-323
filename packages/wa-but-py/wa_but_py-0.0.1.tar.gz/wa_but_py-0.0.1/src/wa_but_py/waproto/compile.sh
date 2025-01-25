#!/bin/bash

OUTPUT_DIR="./generated"

mkdir -p $OUTPUT_DIR

PROTO_FILE="WAProto.proto"

if ! command -v protoc &> /dev/null; then
  echo "Error: protoc is not installed. Please install Protocol Buffers compiler."
  exit 1
fi

echo "Compiling $PROTO_FILE to Python with type hints..."
protoc --python_out=$OUTPUT_DIR --mypy_out=$OUTPUT_DIR $PROTO_FILE

if [ $? -eq 0 ]; then
  echo "✅ Compilation successful! Files saved to $OUTPUT_DIR"
else
  echo "❌ Compilation failed. Please check for errors."
  exit 1
fi
