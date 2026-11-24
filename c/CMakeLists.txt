cmake_minimum_required(VERSION 3.16)
project(HeckeMass VERSION 0.1.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

option(HECKE_MASS_ENABLE_RVV "Build the scaffold probe for RV64 with V" OFF)

add_library(hecke_mass)
add_library(HeckeMass::hecke_mass ALIAS hecke_mass)
target_compile_features(hecke_mass PUBLIC c_std_99)
target_include_directories(hecke_mass PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
set_target_properties(hecke_mass PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

if(HECKE_MASS_ENABLE_RVV)
    target_sources(hecke_mass PRIVATE src/rvv/scaffold.c)
    target_compile_options(hecke_mass PRIVATE -march=rv64gcv)
else()
    target_sources(hecke_mass PRIVATE src/scaffold.c)
endif()

set(package_dir "${CMAKE_INSTALL_LIBDIR}/cmake/HeckeMass")
configure_package_config_file(cmake/HeckeMassConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/HeckeMassConfig.cmake"
    INSTALL_DESTINATION "${package_dir}"
)
write_basic_package_version_file("${CMAKE_CURRENT_BINARY_DIR}/HeckeMassConfigVersion.cmake"
    COMPATIBILITY SameMinorVersion
)
install(TARGETS hecke_mass EXPORT HeckeMassTargets
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
install(DIRECTORY include/ DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
install(EXPORT HeckeMassTargets NAMESPACE HeckeMass:: DESTINATION "${package_dir}")
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/HeckeMassConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/HeckeMassConfigVersion.cmake"
    DESTINATION "${package_dir}"
)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    include(CTest)
    if(BUILD_TESTING)
        add_executable(hecke_mass_scaffold_vectors tests/scaffold_vectors.c)
        target_link_libraries(hecke_mass_scaffold_vectors PRIVATE HeckeMass::hecke_mass)
        add_test(NAME scaffold_vectors COMMAND hecke_mass_scaffold_vectors
            "${CMAKE_CURRENT_SOURCE_DIR}/../tests/vectors/scaffold.csv")
    endif()
endif()
