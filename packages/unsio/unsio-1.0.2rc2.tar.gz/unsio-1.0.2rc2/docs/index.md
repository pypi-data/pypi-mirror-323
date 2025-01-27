# ABOUT
**UNSIO** (**U**niversal **N**body **S**napshot **I**nput **O**utput) is an API which perform input/output operations in a generic way,
and on different kind of nbody files format (nemo, Gadget binaries 1 and 2, Gadget hdf5, Ramses). By using this API,
a user could write only one analysis program which will work on all known files format supported by UNSIO.
It's not necessary anymore to know how is implemented a file format, UNSIO will do transparently and automatically
all the hard work for you ! With UNSIO, you will spend less time to develop your analysis program.
UNSIO comes with an integrated sqlite3 database which can be used to retrieve automatically all your data
among terabytes of hard disks.

![](imgs/unsio_frontpage.png)

## Features

UNSIO can be used from different languages (C,C++,Fortran and Python)

## Supported files format :
* [**NEMO** (read and write)](https://teuben.github.io/nemo/)
* [**GADGET 1** (read)](http://www.mpa-garching.mpg.de/gadget/)
* **GADGET 2** (read an write)
* **GADGET 3/hdf5** (read and write)
* [**RAMSES** (read)](https://bitbucket.org/rteyssie/ramses)
* **List of files** stored in a file
* Simulations stored in **SQLITE3** database

## License
UNSIO is open source and released under the terms of the [CeCILL2 Licence](http://www.cecill.info/licences/Licence_CeCILL_V2-en.html)

## Webpage

Unsio source code hosted on [gitlab repository](https://gitlab.lam.fr/simutools/unsio)
