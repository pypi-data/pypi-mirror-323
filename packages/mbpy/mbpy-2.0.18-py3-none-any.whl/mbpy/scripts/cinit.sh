#!/bin/sh

set -e
#!/bin/sh

# Function to display help message
show_help() {
    cat << EOF
Usage: $0 [options] <project_name>

Options:
    -h, --help              Show this help message
    --std <standard>        Specify C++ standard (11/14/17/20), default: auto-detect
    --cmake-ver <version>   Specify minimum CMake version, default: 3.10
    --compiler <name>       Specify preferred compiler (gcc/clang), default: auto-detect
    
Examples:
    $0 myproject
    $0 --std 17 myproject
    $0 --std 20 --compiler clang myproject
EOF
    exit 0
}

# Default values
MIN_CMAKE_VERSION="3.10"
PREFERRED_COMPILER=""
FORCED_CPP_STD=""

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            ;;
        --std)
            shift
            FORCED_CPP_STD="$1"
            if ! echo "$FORCED_CPP_STD" | grep -qE '^(11|14|17|20)$'; then
                echo "Error: Invalid C++ standard. Use 11, 14, 17, or 20"
                exit 1
            fi
            ;;
        --cmake-ver)
            shift
            MIN_CMAKE_VERSION="$1"
            ;;
        --compiler)
            shift
            PREFERRED_COMPILER="$1"
            if ! echo "$PREFERRED_COMPILER" | grep -qE '^(gcc|clang)$'; then
                echo "Error: Invalid compiler. Use gcc or clang"
                exit 1
            fi
            ;;
        -*)
            echo "Error: Unknown option $1"
            show_help
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$1"
            else
                echo "Error: Multiple project names specified"
                show_help
            fi
            ;;
    esac
    shift
done

# Check for project name
if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    show_help
fi


# Function to convert string to uppercase
to_upper() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Function to compare version numbers
version_ge() {
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Check if script is run with bash or zsh
if [[ -z "$BASH_VERSION" && -z "$ZSH_VERSION" ]]; then
    echo "Please run this script with bash or zsh."
    exit 1
fi

# Check for project name argument
if [ -z "$1" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

PROJECT_NAME="$1"
UPPER_PROJECT_NAME=$(to_upper "$PROJECT_NAME")

# Detect operating system
OS="$(uname)"
case "$OS" in
    Darwin)
        PLATFORM="macOS"
        ;;
    Linux)
        PLATFORM="Linux"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        PLATFORM="Windows"
        ;;
    *)
        PLATFORM="Unknown"
        ;;
esac

# Interactive CMake installation
if ! command -v cmake >/dev/null 2>&1; then
    echo "CMake is not installed. Would you like to install it? (y/n)"
    read -r install_cmake
    if [ "$install_cmake" = "y" ]; then
        if command -v brew >/dev/null 2>&1; then
            brew install cmake
        else
            echo "Homebrew not found. Please install CMake manually."
            exit 1
        fi
    else
        echo "CMake is required. Please install it manually."
        exit 1
    fi
fi

CMAKE_VERSION=$(cmake --version | head -n1 | awk '{print $3}')
MIN_CMAKE_VERSION="3.10"

if ! version_ge "$CMAKE_VERSION" "$MIN_CMAKE_VERSION"; then
    echo "CMake version must be at least $MIN_CMAKE_VERSION. Current version: $CMAKE_VERSION"
    exit 1
fi

# Interactive C++ compiler installation
if ! command -v clang++ >/dev/null 2>&1 && ! command -v g++ >/dev/null 2>&1; then
    echo "No C++ compiler found. Would you like to install one? (y/n)"
    read -r install_compiler
    if [ "$install_compiler" = "y" ]; then
        if command -v brew >/dev/null 2>&1; then
            brew install llvm
        else
            echo "Homebrew not found. Please install a C++ compiler manually."
            exit 1
        fi
    else
        echo "A C++ compiler is required. Please install one manually."
        exit 1
    fi
fi

# Detect C++ Compiler
if command -v clang++ >/dev/null 2>&1; then
    COMPILER="clang++"
    COMPILER_VERSION=$("$COMPILER" --version | head -n1 | awk '{print $4}')
elif command -v g++ >/dev/null 2>&1; then
    COMPILER="g++"
    COMPILER_VERSION=$("$COMPILER" -dumpversion)
fi

# Detect C++ standard supported
detect_cpp_standard() {
    for std in 20 17 14 11; do
        echo "int main() { return 0; }" > test.cpp
        if "$COMPILER" -std=c++"$std" -o test test.cpp >/dev/null 2>&1; then
            CPP_STANDARD="$std"
            rm test.cpp test
            return
        fi
        rm -f test.cpp test
    done
    CPP_STANDARD="17"
}

detect_cpp_standard

# Check for pybind11
if command -v python3 >/dev/null 2>&1; then
    PYBIND11_AVAILABLE=true
else
    PYBIND11_AVAILABLE=false
fi

# Set CMake generator
if command -v ninja >/dev/null 2>&1; then
    CMAKE_GENERATOR="Ninja"
elif [[ "$PLATFORM" == "Windows" ]]; then
    CMAKE_GENERATOR="NMake Makefiles"
else
    CMAKE_GENERATOR="Unix Makefiles"
fi

# Create project structure
mkdir -p "$PROJECT_NAME"/{src,include,test,build,docs,examples,scripts}
cd "$PROJECT_NAME" || exit

# Create CMakeLists.txt with modern features
cat <<EOL > CMakeLists.txt
cmake_minimum_required(VERSION ${MIN_CMAKE_VERSION})
project(${PROJECT_NAME})

set(CMAKE_CXX_STANDARD ${CPP_STANDARD})
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Compiler settings
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(STATUS "Using Clang compiler")
    set(CMAKE_CXX_FLAGS "\${CMAKE_CXX_FLAGS} -Wall -Wextra")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    message(STATUS "Using GCC compiler")
    set(CMAKE_CXX_FLAGS "\${CMAKE_CXX_FLAGS} -Wall -Wextra")
endif()

include_directories(include)

# Main executable
add_executable(\${PROJECT_NAME} src/main.cpp)

# Testing
enable_testing()
add_subdirectory(test)

# Optional pybind11 support
if(EXISTS "\${CMAKE_CURRENT_SOURCE_DIR}/pybind11")
    add_subdirectory(pybind11)
    pybind11_add_module(\${PROJECT_NAME}_py src/bindings.cpp)
endif()
EOL

# Create main.cpp
cat <<EOL > src/main.cpp
#include <iostream>
#include "${PROJECT_NAME}.h"

int main() {
    std::cout << "Hello, ${PROJECT_NAME}!" << std::endl;
    return 0;
}
EOL

# Create header file
cat <<EOL > "include/${PROJECT_NAME}.h"
#ifndef ${UPPER_PROJECT_NAME}_H
#define ${UPPER_PROJECT_NAME}_H

// Header file for ${PROJECT_NAME}

#endif // ${UPPER_PROJECT_NAME}_H
EOL

# Create test files
cat <<EOL > test/CMakeLists.txt
add_executable(${PROJECT_NAME}_test ${PROJECT_NAME}_test.cpp)
add_test(NAME ${PROJECT_NAME}_test COMMAND ${PROJECT_NAME}_test)
EOL

cat <<EOL > test/${PROJECT_NAME}_test.cpp
#include "../include/${PROJECT_NAME}.h"
#include <cassert>

int main() {
    // Add your tests here
    return 0;
}
EOL

# Create additional files
cat <<EOL > .gitignore
build/
*.log
.DS_Store
compile_commands.json
EOL

echo "# ${PROJECT_NAME}" > README.md

# Print summary
echo "C++ project '${PROJECT_NAME}' has been created successfully on ${PLATFORM}."
echo "CMake version: ${CMAKE_VERSION}"
echo "C++ Compiler: ${COMPILER} (${COMPILER_VERSION})"
echo "C++ Standard: C++${CPP_STANDARD}"
echo "CMake generator: ${CMAKE_GENERATOR}"
if [ "$PYBIND11_AVAILABLE" = true ]; then
    echo "Python bindings support is available"
fi
