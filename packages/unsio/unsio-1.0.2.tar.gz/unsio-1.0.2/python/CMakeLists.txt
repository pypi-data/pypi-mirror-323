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

project(PYTHON_UNSIO)

# package required to build python wrapper
FIND_PACKAGE(SWIG REQUIRED)
FIND_PACKAGE(Python REQUIRED Interpreter Development.Module)

MESSAGE(STATUS "==== python wrapper ====")
MESSAGE(STATUS "SWIG_EXECUTABLE =" ${SWIG_EXECUTABLE})
MESSAGE(STATUS "Python_EXECUTABLE =" ${Python_EXECUTABLE})
MESSAGE(STATUS "CMAKE_CURRENT_SOURCE_DIR =" ${CMAKE_CURRENT_SOURCE_DIR})
MESSAGE(STATUS "CMAKE_CURRENT_BINARY_DIR =" ${CMAKE_CURRENT_BINARY_DIR})
MESSAGE(STATUS "SKBUILD_PROJECT_NAME =" ${SKBUILD_PROJECT_NAME})

MESSAGE(STATUS "CMAKE_INSTALL_RPATH=" ${CMAKE_INSTALL_RPATH})
# Grab the variables from a local Python installation F2PY headers
execute_process(
  COMMAND "${Python_EXECUTABLE}" -c
          "import numpy; print(numpy.get_include())"
  OUTPUT_VARIABLE NUMPY_INCLUDE_DIR
  OUTPUT_STRIP_TRAILING_WHITESPACE)
MESSAGE(STATUS "NUMPY_INCLUDE_DIR =" ${NUMPY_INCLUDE_DIR})

# Generate the wrapper files
add_custom_command(
  OUTPUT py_unsio.py py_unsio_wrap.cxx
  COMMAND ${SWIG_EXECUTABLE} -c++ -python -I${CMAKE_CURRENT_SOURCE_DIR}/../src
           -outdir ${CMAKE_CURRENT_BINARY_DIR}
           -o ${CMAKE_CURRENT_BINARY_DIR}/py_unsio_wrap.cxx
          ${CMAKE_CURRENT_SOURCE_DIR}/py_unsio.i 
  VERBATIM
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/py_unsio.i
)
#add_definitions(-DNPY_TARGET_VERSION=NPY_1_17_API_VERSION)
python_add_library(
  _py_unsio
  MODULE
  WITH_SOABI
  ${CMAKE_CURRENT_BINARY_DIR}/py_unsio_wrap.cxx
)

target_include_directories(_py_unsio PUBLIC  ${NUMPY_INCLUDE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/../src)

# 
if (APPLE)
    set_target_properties(_py_unsio PROPERTIES INSTALL_RPATH "@loader_path")
else()
    set_target_properties(_py_unsio PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()
target_link_libraries(_py_unsio PUBLIC unsio)

install(TARGETS _py_unsio DESTINATION unsio)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/py_unsio.py DESTINATION unsio)
install(FILES ${UNSIO2_BINARY_DIR}/lib/libunsio.${LIBEXT} DESTINATION unsio)
