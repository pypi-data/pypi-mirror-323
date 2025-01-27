# Fortran user guide, reading data
 
Reading UNSIO data from fortran language is pretty simple and is done in 3 steps:

- UNSIO initialization 
- data loading
- data extracting

## Unsio intialization

You must first initialize UNSIO engine by calling uns_init() function.

```fortran
ident=uns_init(filename,select_component,select_time)
```

uns_init() accepts 3 parameters :

* **filename**,  is a string which contain to the input file you want to read  (see the [list of supported input/output files](../Guide/supported_input_file_format.md))
* **select_component**,   is a string  which contain the list of the component you want to load (see the [list of the component](../Guide/components_table.md))
* **select_time**,  is a string  which specify on which range of time data must be loaded

### return value

`uns_init()` returns a unique identifier *ident* (positive integer) which will be used later to load data. A negative returned value means that the simulation does not exist or an unknown file format.

## Loading data

The next step consist to load a snapshot according to user requests (components and time range) by calling function  `uns_load_opt()`:

```fortran
status=uns_load_opt(ident, bits)
```

This function accepts two parameters. 

*  **ident** corresponds to the return value of the function uns_init() during [unsio initialization](#unsio-intialization).
*  **bits** is a string variable which specify  data (positions, masses,velocities etc..)  that the user want to load (see  [how to select data at loading](../Guide/howto_select_data.md#how-to-select-data-at-loading))) . This variable is used to speed up reading process in case the user does not want to load all the data but just only few of them. It can be really interesting when snapshot files are really big. If blank string  is used for this parameter, then all data will be loaded.

### Return values

This function return *1* in case of success, *0* if end of snapshot reached and *-1* if failed.

## Getting data

Unsio fortran interface provides several functions to get data stored in a snapshot.

### Getting arrays

example:
```fortran
real * 4 pos(3,MAXBODIES)
integer nstars
character * 80 component, tag

component = "stars"
tag =  "pos"

nstars = uns_get_array_f(ident,component,tag ,pos, MAXBODIES )       ! read positions for component stars

```
In the above example, we explicitly ask to `uns_get_array_f()` method, to return positions for **"stars"** component. Here is a description of all parameters:

* **ident** corresponds to the return value of the function uns_init() during [[FortranReadData#Unsio-intialization|unsio initialization]].
* **component** specify on which component we want to select, here it's "stars" component.
* **tag** specify which array data we want to get. Here it's positions.
* **pos**  is the array itself where we want positions to be stored ( Three dimensional arrays must be declared always in that way array(3,MAXBODIES) )
* **MAXBODIES** specify the second dimension of the array.

To have a complete description of `uns_get_array_f()` function, follow this [link](./fortran_get_array.md#uns_get_array_f)

### Getting values

example:
```fortran
integer nbody_select, status
real * 4 time

status = uns_get_value_i(ident, "nsel", nbody_select)       !  return #bodies in nbody_select variable
status = uns_get_value_f(ident, "time", time)                     !  return time step in time variable
```

There are two functions which return values:

* **uns_get_value_i()** returns integer value  
* **uns_get_value_f()** returns float value

To  have a complete description of `uns_get_value_X`() function, follow this [link](./fortran_get_array.md#uns_get_value_f).

## Closing file

Use `uns_close(ident)` to close an unsio file opened with [unsio initialization](#unsio-intialization), example :

```fortran
integer ok

ok = uns_close(ident)  ! Ident is the file descriptor return by uns_init
```

This function accepts one parameter. 

*  **ident** corresponds to the return value of the function uns_init() during [unsio initialization](#unsio-intialization).

### Return value

`uns_close()` returns a positive number (>=0). A negative returned value means that the simulation does not exist or an unexpected error occurred.

## Useful functions

In every examples below,  first parameter **ident** , corresponds to the return value of the function uns_init() during [unsio initialization](#unsio-intialization).

### Input interface type

Subroutine `uns_get_interface_type(ident, interface)` return into variable **interface** the type of the snapshot (nemo, gadget1, gadget2, ramses, etc..)

```fortran
uns_get_interface_type(ident, interface)
integer ident
character *(*) interface
```

### Input snapshot file structure

There are two kinds of input snapshot file structure:

* **range** type, like NEMO snapshots. The user may know in which range are spread data into the file.
* **component** type, lile Gagdet, Ramses snapshots. In such snapshots, data are structured by components.

Subroutine `uns_get_file_structure(ident, fstructure)` return in variable **fstructure** the file structure of the snapshot, *range*, or *component*

```fortran
uns_get_file_structure(ident, fstructure)
integer ident
character *(*) fstructure
```

### Input filename

Subroutine `uns_get_file_name(ident, fname)` return in variable **fname** the snapshot filename.
This subroutine can be useful when you work on a list of snapshots or a snapshot stored in sqlite3 database. It will return then, for every time steps, the filename corresponding.

```fortran
uns_get_file_name(ident, fname)
integer ident
character *(*) fname
```

### Components range

A user may want to load several components at the same time, "gas,disk" for example. 

Subroutine `uns_get_range(ident,component,size,first,last)`  retrieve in which indexes ranges are stored requested components in the different arrays (positions, velocities, masses) 

```fortran
status=uns_get_range(ident, "gas",ngas,first,last)
```

In the above example, `uns_get_range()` function, return in **ngas** variable the number of gas particles, in **first** the index of the first gas particle, in **last** the index of the last particle.

* *return 1*
The function return 1 if there are gas particles in the snapshot and the user has requested them during  [unsio initialization](#unsio-intialization).

* *return 0*
If there no gas particles in the snaphot OR the user did not request gas particles during [unsio initialization](#unsio-intialization), then the function return 0.

## A complete example

To see a complete example, follow this [link](../Examples/fortran_example.md).