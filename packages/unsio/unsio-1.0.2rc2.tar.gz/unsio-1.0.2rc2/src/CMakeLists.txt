cmake_minimum_required(VERSION 3.15)

# project name
project(UNSIO2)

MESSAGE(STATUS "==== UNSIO Build lib configuration ====")

# contains the full path to the top level directory of your build tree
MESSAGE(STATUS "PROJECT_BINARY_DIR: " ${PROJECT_BINARY_DIR})
MESSAGE(STATUS "PROJECT_SOURCE_DIR: " ${PROJECT_SOURCE_DIR})
MESSAGE(STATUS "CMAKE_BUILD_TYPE =" ${CMAKE_BUILD_TYPE})
MESSAGE(STATUS "CMAKE_CXX_FLAGS  =" ${CMAKE_CXX_FLAGS})

# For mknemo unsio wworking
IF(NEMO_INSTALLED)
    SET(LIB_SUFFIX "lib")
ENDIF(NEMO_INSTALLED)

MESSAGE(STATUS "NEMOLIB : " ${NEMOLIB})
MESSAGE(STATUS "NEMOINC : " ${NEMOINC})
MESSAGE(STATUS "LIB_SUFFIX : " ${LIB_SUFFIX})

# Find all the sources for the LIB
FILE(GLOB LIBSOURCES ${PROJECT_SOURCE_DIR}/*.cc)

# Destination path for the lib
SET(LIBRARY_OUTPUT_PATH lib)

# remove -DNDEBUG in RElease mode to keep activated assert calls
STRING(REPLACE "-DNDEBUG" "" CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE})

# create library "uns"
add_library(unsio ${LIBTYPE} ${LIBSOURCES})

if(APPLE)
    if(NOT NO_RPATH)
        MESSAGE(STATUS "RPATH activated for UNSIO library")
        SET_TARGET_PROPERTIES(unsio PROPERTIES MACOSX_RPATH TRUE)
    else()
        # to deactivate RPATH compile with -DNO_RPATH=1
        # it's mandatory to build wheel on MacOSX
        MESSAGE(STATUS "RPATH DE-activated for UNSIO library")
    endif()
endif(APPLE)

# special flags for MacOSX
if(OSX)
    set(CMAKE_MACOSX_RPATH ON)
endif()

#
SET(DEP_NEMO_LIB "nemo")

# ENDIF (NOT NEMO_INSTALLED)
target_link_libraries(unsio ${DEP_NEMO_LIB} ${HDF5_CXX_LIBRARIES} sqlite3 z)

if(OSX)
    set_target_properties(unsio PROPERTIES LINK_FLAGS "-undefined suppress -flat_namespace")
endif()

# ----------------------------------------------------------
# Install SETUP
# ----------------------------------------------------------
mark_as_advanced(CMAKE_INSTALL_PREFIX)

SET(PREFIX_LIB ${LIB_SUFFIX})
SET(PREFIX_INC "include")
SET(PREFIX_MAN "share/man")
SET(PREFIX_SCR "share/uns/scripts")

IF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "$ENV{HOME}/local/unsio" CACHE PATH "" FORCE) # if NEMO NOT exist => default install into ${HOME}/local/unsio
ENDIF() # NOT CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)

MESSAGE(STATUS "--------> CMAKE_INSTALL_PREFIX =" ${CMAKE_INSTALL_PREFIX})

# following line is important for building python wheel package later from docker ci
if(NOT OSX)
    set_target_properties(unsio PROPERTIES LINK_FLAGS "-Wl,-rpath=${CMAKE_INSTALL_PREFIX}/${PREFIX_LIB}")
endif()

if(OSX)
    # MESSAGE(STATUS "\nAfter running \"make install\", do not forget to set your environment variable DYLD_LIBRARY_PATH using command:\n\n export DYLD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib\n")
    MESSAGE(STATUS "\nBetter run cmake on macosx using clang compiler with commnand:\nCC=/usr/bin/cc CXX=/usr/bin/c++ cmake ..\n")
endif(OSX)

# use, i.e. don't skip the full RPATH for the build tree
SET(CMAKE_SKIP_BUILD_RPATH FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)

SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${PREFIX_LIB}")

# add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# the RPATH to be used when installing, but only if it's not a system directory
LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${CMAKE_INSTALL_PREFIX}/${PREFIX_LIB}" isSystemDir)

IF("${isSystemDir}" STREQUAL "-1")
    SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${PREFIX_LIB}")
ENDIF("${isSystemDir}" STREQUAL "-1")

# Make sure the compiler can find include files from our Hello library.
include_directories(${PROJECT_SOURCE_DIR} ${NEMOINC} ${NEMOLIB} ${SQLITE3_H_PATH})
include_directories(/usr/include/malloc ${HDF5_INCLUDE_DIRS})

# Make sure the linker can find the Hello library once it is built.
link_directories(${UNSIO2_BINARY_DIR}/lib /usr/X11/lib ${SQLITE3_LIB_PATH})
link_directories(${NEMOLIB} ${FC_GFORT_PATH} ${FC_G77_PATH})

# ----------------------------------------------------------
# Install procedure
# ----------------------------------------------------------

# UNS specific includes
INSTALL(FILES ${PROJECT_SOURCE_DIR}/uns.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/version.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/unsdebug.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/snapshotinterface.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/componentrange.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/ctools.h DESTINATION ${PREFIX_INC}/uns)
INSTALL(FILES ${PROJECT_SOURCE_DIR}/userselection.h DESTINATION ${PREFIX_INC}/uns)

# unsio lib
INSTALL(FILES ${PROJECT_BINARY_DIR}/lib/libunsio.${LIBEXT} DESTINATION ${PREFIX_LIB})

# man
INSTALL(FILES ${UNSIO2_SOURCE_DIR}/../man/man3/unsiof.3 DESTINATION ${PREFIX_MAN}/man3)

#
# NEMO specific lib and includes
#
INSTALL(FILES ${NEMOLIB}/libnemo.a DESTINATION ${PREFIX_LIB}/nemolite)
INSTALL(FILES ${NEMOLIB}/libnemomaing77.a DESTINATION ${PREFIX_LIB})

IF(NOT NEMO_INSTALLED)
    # Find all NEMOLIGHT header files
    FILE(GLOB nlight_files ${NEMOLIGHT}/src/*.h ${NEMOLIGHT}/src/inc/*.h)

    FOREACH(source_header ${nlight_files})
        INSTALL(FILES ${source_header} DESTINATION ${PREFIX_INC}/nemo)
    ENDFOREACH()

    FILE(GLOB nlight_files ${NEMOLIGHT}/src/inc/snapshot/*.c ${NEMOLIGHT}/src/inc/snapshot/*.h)

    FOREACH(source_header ${nlight_files})
        INSTALL(FILES ${source_header} DESTINATION ${PREFIX_INC}/nemo/snapshot)
    ENDFOREACH()
ENDIF(NOT NEMO_INSTALLED)

if(NOT CMAKE_INSTALL_PREFIX STREQUAL "/usr")
    # I man using this hack otherwise the RPM package created fails to install because an unresolve dependency on Tools::Sqlite3
    # module though which comes with this install....

    # install sqlite3 database files
    INSTALL(FILES ${UNSIO2_SOURCE_DIR}/../scripts/perl/lib/Tools/Tools.pm DESTINATION "${PREFIX_SCR}/perl/lib/Tools")
    INSTALL(FILES ${UNSIO2_SOURCE_DIR}/../scripts/perl/lib/Tools/Sqlite3.pm DESTINATION "${PREFIX_SCR}/perl/lib/Tools")
    INSTALL(FILES ${UNSIO2_SOURCE_DIR}/../scripts/sql/create_unsio_db.sql DESTINATION "${PREFIX_SCR}/sql")
    INSTALL(FILES ${UNSIO2_SOURCE_DIR}/../scripts/sql/README DESTINATION "${PREFIX_SCR}/sql")

    # some binaries
    INSTALL(PROGRAMS ${UNSIO2_SOURCE_DIR}/../scripts/perl/mains/unsio_sql3_get_info.pl DESTINATION bin)
    INSTALL(PROGRAMS ${UNSIO2_SOURCE_DIR}/../scripts/perl/mains/unsio_sql3_update_info.pl DESTINATION bin)
    INSTALL(PROGRAMS ${UNSIO2_SOURCE_DIR}/../scripts/perl/mains/unsio_sql3_update_nemorange.pl DESTINATION bin)
    INSTALL(PROGRAMS ${UNSIO2_SOURCE_DIR}/../scripts/perl/mains/unsio_sql3_create_db.pl DESTINATION bin)
endif()

# ----------
# PACKAGING
# ----------
# VERSION
if(EXISTS "${PROJECT_SOURCE_DIR}/src/version.h") # detect version from "version.h" file
    set(CURRENT_VERSION "")
    file(READ "${PROJECT_SOURCE_DIR}/src/version.h" CURRENT_VERSION_H)

    # UNSIO_MAJOR
    string(REGEX MATCH "UNSIO_MAJOR \"([a-zA-Z0-9.-]+)\"" XXXX "${CURRENT_VERSION_H}")
    set(PROJECT_VERSION_MAJOR ${CMAKE_MATCH_1})

    # UNSIO_MINOR
    string(REGEX MATCH "UNSIO_MINOR \"([a-zA-Z0-9.-]+)\"" XXXX "${CURRENT_VERSION_H}")
    set(PROJECT_VERSION_MINOR ${CMAKE_MATCH_1})

    # UNSIO_PATCH
    string(REGEX MATCH "UNSIO_PATCH \"([a-zA-Z0-9.-]+)\"" XXXX "${CURRENT_VERSION_H}")
    set(PROJECT_VERSION_PATCH ${CMAKE_MATCH_1})

    # UNSIO_EXTRA
    string(REGEX MATCH "UNSIO_EXTRA \"([_a-zA-Z0-9.-]+)\"" XXXX "${CURRENT_VERSION_H}")
    set(PROJECT_VERSION_EXTRA ${CMAKE_MATCH_1})

    # PROJECT_VERSION
    set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${PROJECT_VERSION_EXTRA}")

    message(STATUS "Project Version = " ${PROJECT_VERSION})
endif()

# CPACK infos
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_NAME "unsio")
set(CPACK_PACKAGE_RELEASE 1)
set(CPACK_PACKAGE_CONTACT "Jean-Charles LAMBERT")
set(CPACK_PACKAGE_VENDOR "LAM - CeSAM")
set(CPACK_PACKAGING_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX})
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}.${LINUX_NAME}.${CMAKE_SYSTEM_PROCESSOR}")

# set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CPACK_PACKAGE_RELEASE}.${LINUX_NAME}.${CMAKE_SYSTEM_PROCESSOR}")

# CPACK RPM specific
set(CPACK_RPM_CHANGELOG_FILE "${PROJECT_SOURCE_DIR}/ChangeLog")
set(CPACK_RPM_PACKAGE_LICENSE "CeCILL2")
set(CPACK_RPM_PACKAGE_DESCRIPTION "UNSIO - Universal Nbody Snapshot Input Output")
set(CPACK_RPM_PACKAGE_PROVIDES "libunsio.so()(64bit)")

# CPACK debian specific
set(CPACK_DEBIAN_PACKAGE_NAME ${CPACK_PACKAGE_NAME})
set(CPACK_DEBIAN_PACKAGE_VERSION ${CPACK_PACKAGE_VERSION}-${CPACK_PACKAGE_RELEASE}.${LINUX_NAME})
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
set(CPACK_DEBIAN_PACKAGE_GENERATE_SHLIBS ON)

IF(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86_64")
    SET(CPACK_DEBIAN_PACKAGE_ARCHITECTURE amd64)
ELSEIF(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "i686")
    SET(CPACK_DEBIAN_PACKAGE_ARCHITECTURE i386)
ENDIF(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "x86_64")

set(CPACK_DEBIAN_PACKAGE_DESCRIPTION ${CPACK_RPM_PACKAGE_DESCRIPTION})
set(CPACK_DEBIAN_PACKAGE_PROVIDES "unsio, libunsio")

if(APPLE)
    # set(CMAKE_INSTALL_PREFIX "/Applications")
    # set(CMAKE_INSTALL_PREFIX "/")
    # set(CPACK_DMG_DISABLE_APPLICATIONS_SYMLINK ON)
    set(CPACK_GENERATOR "DragNDrop")
    set(CPACK_DMG_FORMAT "UDBZ")
    set(CPACK_DMG_VOLUME_NAME "${PROJECT_NAME}")
    set(CPACK_SYSTEM_NAME "OSX")
    set(CPACK_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}")

    # set(CPACK_PACKAGE_ICON "${ICONS_DIR}/DMG.icns")
    # set(CPACK_DMG_DS_STORE "${ICONS_DIR}/DMGDSStore")
    # set(CPACK_DMG_BACKGROUND_IMAGE "${ICONS_DIR}/DMGBackground.png")
endif()

if(NOT WIN32)
    # SET(CPACK_STRIP_FILES {CMAKE_INSTALL_PREFIX}/bin/glnemo2)
    # SET(CPACK_STRIP_FILES "True")
    # SET(CPACK_SET_DESTDIR On)
    set(CMAKE_INSTALL_DO_STRIP TRUE)

    # SET(CPACK_INSTALL_PREFIX "/usr")
    # SET(CMAKE_INSTALL_PREFIX ${CPACK_INSTALL_PREFIX})
endif()

set(CMAKE_INSTALL_SYSTEM_RUNTIME_DESTINATION "${BIN_INSTALL_DIR}")
include(InstallRequiredSystemLibraries)

# This must always be last!
include(CPack)
