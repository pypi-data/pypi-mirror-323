# Installing the library for C/C++/Fortran

## Clone the repository

The source code for `unsio` can be downloaded from [gitlab](https://gitlab.lam.fr/simutools/unsio)

```
git clone https://gitlab.lam.fr/simutools/unsio
```
## Install the requirements packages
  * hdf5
  * swig
  * cmake
  
## Compile and install
```shell
cd cloned_unsio_library
mkdir build
cd build
cmake ..
make -j 6
make install
```