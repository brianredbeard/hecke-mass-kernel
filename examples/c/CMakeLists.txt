cmake_minimum_required(VERSION 3.16)
project(hecke_mass_c_example LANGUAGES C)

find_package(HeckeMass CONFIG REQUIRED)

add_executable(hecke_mass_c_example main.c)
target_link_libraries(hecke_mass_c_example PRIVATE HeckeMass::hecke_mass)

enable_testing()
add_test(NAME installed_c_consumer COMMAND hecke_mass_c_example)
