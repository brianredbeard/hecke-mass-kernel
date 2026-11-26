cmake_minimum_required(VERSION 3.16)
project(HeckeMass VERSION 0.1.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

option(HECKE_MASS_ENABLE_RVV "Build the vector kernels for RV64 with V" OFF)
option(HECKE_MASS_BUILD_FINITE_KERNEL "Build the GMP-backed finite kernel" ON)

add_library(hecke_mass)
add_library(HeckeMass::hecke_mass ALIAS hecke_mass)
target_compile_features(hecke_mass PUBLIC c_std_99)
target_include_directories(hecke_mass PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
set_target_properties(hecke_mass PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

if(HECKE_MASS_ENABLE_RVV)
    set(rvv_sources src/rvv/scaffold.c src/rvv/brandt.c)
    target_sources(hecke_mass PRIVATE ${rvv_sources})
    set_property(SOURCE ${rvv_sources} APPEND PROPERTY COMPILE_OPTIONS -march=rv64gcv)
else()
    target_sources(hecke_mass PRIVATE src/scaffold.c src/brandt.c)
endif()

set(package_dir "${CMAKE_INSTALL_LIBDIR}/cmake/HeckeMass")
set(pkgconfig_requires "")
if(HECKE_MASS_BUILD_FINITE_KERNEL)
    include(cmake/HeckeMassGMP.cmake)
    if(NOT TARGET HeckeMassGMP::GMP)
        message(FATAL_ERROR "The HeckeMass finite kernel requires GMP headers and library.")
    endif()
    target_sources(hecke_mass PRIVATE src/kernel.c)
    target_link_libraries(hecke_mass PUBLIC HeckeMassGMP::GMP)
    set(pkgconfig_requires "gmp")
    install(FILES include/hecke_mass/kernel.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/hecke_mass")
    install(FILES cmake/HeckeMassGMP.cmake DESTINATION "${package_dir}")
endif()

set(pkgconfig_dir "${CMAKE_INSTALL_LIBDIR}/pkgconfig")
file(RELATIVE_PATH pkgconfig_prefix "${CMAKE_INSTALL_FULL_LIBDIR}/pkgconfig" "${CMAKE_INSTALL_PREFIX}")
set(pkgconfig_libdir "${CMAKE_INSTALL_LIBDIR}")
set(pkgconfig_includedir "${CMAKE_INSTALL_INCLUDEDIR}")
if(NOT IS_ABSOLUTE "${pkgconfig_libdir}")
    set(pkgconfig_libdir "\${prefix}/${pkgconfig_libdir}")
endif()
if(NOT IS_ABSOLUTE "${pkgconfig_includedir}")
    set(pkgconfig_includedir "\${prefix}/${pkgconfig_includedir}")
endif()
configure_file(cmake/hecke_mass.pc.in "${CMAKE_CURRENT_BINARY_DIR}/hecke_mass.pc" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/hecke_mass.pc" DESTINATION "${pkgconfig_dir}")

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
install(FILES include/hecke_mass/scaffold.h include/hecke_mass/brandt.h
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/hecke_mass"
)
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
        add_executable(hecke_mass_brandt_counts tests/brandt_counts.c)
        target_link_libraries(hecke_mass_brandt_counts PRIVATE HeckeMass::hecke_mass)
        add_test(NAME brandt_counts COMMAND hecke_mass_brandt_counts)
        if(HECKE_MASS_BUILD_FINITE_KERNEL)
            add_executable(hecke_mass_kernel_vectors tests/kernel_vectors.c)
            target_link_libraries(hecke_mass_kernel_vectors PRIVATE HeckeMass::hecke_mass)
            add_test(NAME kernel_vectors COMMAND hecke_mass_kernel_vectors
                "${CMAKE_CURRENT_SOURCE_DIR}/../tests/vectors/kernel.tsv"
                "${CMAKE_CURRENT_SOURCE_DIR}/../tests/vectors/orbit.tsv")
        endif()
    endif()
endif()
