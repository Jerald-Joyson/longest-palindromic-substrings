#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 programName"
    exit 1
fi

PROGRAM_NAME=$1
SOURCE_FILE="${PROGRAM_NAME}.cpp"
EXECUTABLE="./${PROGRAM_NAME}"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '${SOURCE_FILE}' not found."
    exit 1
fi

g++ "$SOURCE_FILE" -o "$EXECUTABLE"

if [ $? -ne 0 ]; then
    echo "Error: Compilation failed."
    exit 1
fi

$EXECUTABLE

if [ $? -eq 0 ]; then
    rm "$EXECUTABLE"
else
    echo "Error: Program execution failed."
    exit 1
fi
