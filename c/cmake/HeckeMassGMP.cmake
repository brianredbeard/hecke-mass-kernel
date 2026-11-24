if(NOT TARGET HeckeMassGMP::GMP)
    find_path(HeckeMassGMP_INCLUDE_DIR NAMES gmp.h)
    find_library(HeckeMassGMP_LIBRARY NAMES gmp)
    mark_as_advanced(HeckeMassGMP_INCLUDE_DIR HeckeMassGMP_LIBRARY)

    if(HeckeMassGMP_INCLUDE_DIR AND HeckeMassGMP_LIBRARY)
        add_library(HeckeMassGMP::GMP UNKNOWN IMPORTED)
        set_target_properties(HeckeMassGMP::GMP PROPERTIES
            IMPORTED_LOCATION "${HeckeMassGMP_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${HeckeMassGMP_INCLUDE_DIR}"
        )
    endif()
endif()
