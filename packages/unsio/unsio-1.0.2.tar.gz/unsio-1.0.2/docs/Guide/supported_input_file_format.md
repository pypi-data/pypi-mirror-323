
# Supported input/output file format

| File format    | read(input) | write(output) |
| --- |--- | --- | 
| [Gadget 1](http://www.mpa-garching.mpg.de/gadget)    |   x    |         |               |
| [Gadget 2](http://www.mpa-garching.mpg.de/gadget/)      |   x    |     x   |
| [Gadget 3/hdf5](http://www.mpa-garching.mpg.de/gadget/) |   x    |     x   |
| [Nemo](http://carma.astro.umd.edu/nemo)  |   x    |     x    | 
| [Ramses](http://www.itp.uzh.ch/~teyssier/Site/RAMSES.html)  |   x    |         | 
| [List of files](./supported_input_file_format.md#list-of-files) |   x    |         | 
| [Sqlite3 db](./supported_input_file_format.md#sqlite3-database) |   x    |         |


# list of files

List of files is made of an ascii file with one file file per line. Every file in the list must be a know file format supported by unsio. 
Example of list of file :

```shell
cat list.input
snap_00001
snap_00002
snap_00003
snap_00004
snap_00005
```

# sqlite3 database

A [sqlite3 database](./sqlite3_database.md) is embedded to unsio which allows direct access to simulations stored in your storage area. Instead of giving full path name of a simulation, a user can give a simulation's name stored in sqlite3 database.