# ============================================================================
# Copyright Jean-Charles LAMBERT - 2008-2025
#           Centre de donneeS Astrophysiques de Marseille (CeSAM)       
# e-mail:   Jean-Charles.Lambert@lam.fr                                      
# address:  Aix Marseille Universite, CNRS, LAM 
#           Laboratoire d'Astrophysique de Marseille                          
#           Pole de l'Etoile, site de Chateau-Gombert                         
#           38, rue Frederic Joliot-Curie                                     
#           13388 Marseille cedex 13 France                                   
#           CNRS UMR 7326    
# ============================================================================
# CMakeListst.txt file to compile UNSIO library
# ============================================================================

cmake_minimum_required(VERSION 3.15)

# project name
project (UNSIO2)


SET(CMAKE_VERBOSE_MAKEFILE OFF)
# extra cmake path
SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake)

# load setup flags
include(SetupFlags)

# Check fortran compiler
include(CheckFortranCompiler)

# Cpack Generator detection
include(DetectCpackGenerator)

# compilation options
add_definitions(${OPT} -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE ${DNOSQLITE3})
SET(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} ${WARNCPP})
SET(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} ${WARNC})
SET(CMAKE_Fortran_FLAGS ${CMAKE_Fortran_FLAGS} ${WARNF})


# contains the full path to the top level directory of your build tree
MESSAGE( STATUS "PROJECT_BINARY_DIR: " ${PROJECT_BINARY_DIR} )

# contains the full path to the root of your project source directory,
# i.e. to the nearest directory where CMakeLists.txt contains the PROJECT() command
MESSAGE( STATUS "PROJECT_SOURCE_DIR: " ${PROJECT_SOURCE_DIR} )

MESSAGE( STATUS "CMAKE_BUILD_TYPE =" ${CMAKE_BUILD_TYPE} )
MESSAGE( STATUS "CMAKE_CXX_FLAGS  =" ${CMAKE_CXX_FLAGS} )
MESSAGE( STATUS "LIBRARY TYPE     =" ${LIBTYPE} )

MESSAGE( STATUS "core OPT  =" ${OPT} )
MESSAGE( STATUS "OSX detected =" ${OSX} )
MESSAGE( STATUS "BUILD_TYPE =" ${RELEASE} )

find_program(CCACHE_PROGRAM ccache)
if (CCACHE_PROGRAM)
    message(NOTICE "Selected CCache: ${CCACHE_PROGRAM}")
    MESSAGE (STATUS "CCACHE_BASEDIR=${PROJECT_SOURCE_DIR}")
    MESSAGE (STATUS "CCACHE_DIR=$ENV{CCACHE_DIR}")
    set(ccacheEnv
            CCACHE_BASEDIR=${PROJECT_SOURCE_DIR}
            CCACHE_SLOPPINESS="pch_defines,file_macro,include_file_ctime"
            CCACHE_NOHASHDIR=true
    )
    set(CMAKE_C_COMPILER_LAUNCHER ${CMAKE_COMMAND} -E env ${ccacheEnv} ${CCACHE_PROGRAM})
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CMAKE_COMMAND} -E env ${ccacheEnv} ${CCACHE_PROGRAM})
endif ()

# Detect NEMO
FIND_PACKAGE(NEMO)

FIND_PACKAGE(SQLITE3)
if (APPLE)
#set (HDF5_USE_STATIC_LIBRARIES TRUE)
endif(APPLE)

FIND_PACKAGE(HDF5 COMPONENTS CXX REQUIRED)
#MESSAGE( STATUS "1) HDF5_CXX_LIBRARIES=" ${HDF5_CXX_LIBRARIES})

MESSAGE(STATUS "NEMO LIGHT will be build")
#add_subdirectory(${PROJECT_SOURCE_DIR}/3rdparty/nemolight  ${PROJECT_SOURCE_DIR}/3rdparty/nemolight/build-${CMAKE_BUILD_TYPE} )
add_subdirectory(${PROJECT_SOURCE_DIR}/3rdparty/nemolight)
set(NEMOLIGHT ${PROJECT_SOURCE_DIR}/3rdparty/nemolight)
set(NEMOLIB ${PROJECT_BINARY_DIR}/3rdparty/nemolight/lib)
set(NEMOINC ${NEMOLIGHT}/src/inc)

# ----------------------------------------------------------
# Install SETUP
# ----------------------------------------------------------
mark_as_advanced(CMAKE_INSTALL_PREFIX)

SET(PREFIX_LIB ${LIB_SUFFIX})
SET(PREFIX_INC "include")
SET(PREFIX_MAN "share/man")
SET(PREFIX_SCR "share/uns/scripts")

IF (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set   (CMAKE_INSTALL_PREFIX "$ENV{HOME}/local/unsio" CACHE PATH "" FORCE)  #if NEMO NOT exist => default install into ${HOME}/local/unsio
ENDIF ()#NOT CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)

MESSAGE( STATUS "--------> CMAKE_INSTALL_PREFIX =" ${CMAKE_INSTALL_PREFIX})

if (OSX)
  #MESSAGE(STATUS "\nAfter running \"make install\", do not forget to set your environment variable DYLD_LIBRARY_PATH using command:\n\n export DYLD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib\n")
  MESSAGE(STATUS "\nBetter run cmake on macosx using clang compiler with commnand:\nCC=/usr/bin/cc CXX=/usr/bin/c++ cmake ..\n")
endif(OSX)

# LIB source directory
add_subdirectory(${PROJECT_SOURCE_DIR}/src)

IF (SKBUILD_PROJECT_NAME)
  # -----------------------------------
  # triggered by python installation
  # pip install ...
  # python -m build
  # -----------------------------------

  # Python binding
  add_subdirectory(${PROJECT_SOURCE_DIR}/python)


ELSE(SKBUILD_PROJECT_NAME)
# ----------------------------------------------------------
  # proceed below target only if the compilation has not been
  # trigered by python installation ()

  # Executbale output path
  set(EXECUTABLE_OUTPUT_PATH bin)
  MESSAGE( STATUS "EXECUTABLE_OUTPUT_PATH: " ${EXECUTABLE_OUTPUT_PATH} )

  # Find all LIB's sources files
  FILE(GLOB exe_sources test_src/*.F)

  # ----------------------------------------------------------
  # compile CC programs
  # Find all LIB's sources files
  FILE(GLOB execpp_sources test_src/*.cc)

  # build cpp executables according to the source
  FOREACH(exe_cpp ${execpp_sources})

    get_filename_component(exe ${exe_cpp} NAME_WE)
    MESSAGE( STATUS "New executable ==> " ${exe})
    add_executable (${exe} ${exe_cpp})
    if (APPLE)
      set_target_properties(${exe} PROPERTIES MACOSX_RPATH TRUE) 
      set_target_properties(${exe} PROPERTIES INSTALL_RPATH "@loader_path/../${LIB_SUFFIX}") 
    else()
      set_target_properties(${exe} PROPERTIES INSTALL_RPATH "\$ORIGIN/../${LIB_SUFFIX}") 
    endif(APPLE)
    # Link the executable to the Hello library.
    target_link_libraries (${exe} unsio ) # ${FC_GFORT_LIB} ${FC_G77_LIB} stdc++)
    target_include_directories(${exe} PUBLIC src 3rdparty/nemolight/src/inc)
    IF (${exe} STREQUAL "uns_info")
      INSTALL(TARGETS ${exe} RUNTIME  DESTINATION bin)
    ENDIF()

  ENDFOREACH(exe_cpp ${execpp_sources})

  # build Fortran executables according to the source
  # compilation options
  if (CMAKE_Fortran_COMPILER)

  FOREACH(exe_f ${exe_sources})

    get_filename_component(exe ${exe_f} NAME_WE)
    MESSAGE( STATUS "New executable ==> " ${exe})
    add_executable (${exe} ${exe_f})

    # Link the executable to the Hello library.
    #target_link_libraries (${exe} unsio nemomaing77 nemo g2c sqlite3 stdc++)
    target_link_libraries (${exe} unsio nemomaing77 ${FC_LIB} stdc++)
    if (APPLE)
      set_target_properties(${exe} PROPERTIES MACOSX_RPATH TRUE) 
      set_target_properties(${exe} PROPERTIES INSTALL_RPATH "@loader_path/../${LIB_SUFFIX}") 
    else()
      set_target_properties(${exe} PROPERTIES INSTALL_RPATH "\$ORIGIN/../${LIB_SUFFIX}") 
    endif(APPLE)
    SET_TARGET_PROPERTIES(${exe} PROPERTIES LINKER_LANGUAGE Fortran)
    # add "-lstdc++"
    #SET(CMAKE_Fortran_LINK_FLAGS "-L${NEMOLIB} ") #-lstdc++")
  ENDFOREACH(exe_f ${exe_sources})
  endif()

  ENDIF(SKBUILD_PROJECT_NAME)
