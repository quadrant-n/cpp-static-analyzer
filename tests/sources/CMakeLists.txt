cmake_minimum_required(VERSION 3.12)
project(tests)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(${PROJECT_NAME}_main main.cpp)
add_executable(${PROJECT_NAME}_link_list link_list.cpp)
add_executable(${PROJECT_NAME}_binary_tree binary_tree.cpp)
