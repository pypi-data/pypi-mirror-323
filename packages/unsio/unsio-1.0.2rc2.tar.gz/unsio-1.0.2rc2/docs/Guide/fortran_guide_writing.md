# Fortran user guide, writing data

Writing UNSIO data from fortran language is pretty simple and is done in 3 steps:

- UNSIO initialization for saving
- setting data
- saving

## Unsio intialization for saving

You must first initialize UNSIO engine by calling `uns_save_init()` function.

```fortran
snapshot_type="gadget2"
ident=uns_save_init(filename,snaphot_type)
```
`uns_save_init()` accepts 2 parameters :

* **filename**,  is a string which contain the input file you want to save.

* **snaphot_type** is a string which contain the format type in which you want to save (see the [list of supported input/output files](../Guide/supported_input_file_format.md))

### return value

`uns_save_init()` returns a unique identifier **ident** (positive integer) which will be used later in all unsio functions. A negative returned value means that something bad happen.

## Setting data

Unsio fortran interface provides several functions to set data into an output snapshot

### Setting arrays

example:

```fortran
integer ngas
real * 4 pos(3,ngas)
character * 80 component, tag

component = "gas"
tag =  "pos"

ok = uns_set_array_f(ident,component,tag ,pos, ngas)       ! write positions for component gas
```

- **ident**  corresponds to the return value of the function uns_save_init() during [unsio save initialization](#unsio-intialization-for-saving).
- **component** specify which component we want to save, here it's "gas" component.
- **tag** specify which array data we want to set. Here it's positions.
- **pos**  is the array itself which contain all "gas" particles to be saved ( Three dimensional arrays must be declared always in that way array(3,MAXBODIES) )
- **ngas** specify the number of gas particles

Function `uns_set_array_f())` return an integer, 1 in case of success 
To have a complete description of `uns_set_array_X()` function, follow this [[SetDataDescriptionFortran|link]].

### Setting values

Functions `uns_set_value_X(f "float" , i "integer')` prepare floating or integer value to be saved.

example:
```fortran
integer  ok
real * 4 time

ok = uns_set_value_f(ident, "time", time)    !  save time
```

To  have a complete description of `uns_set_value_X()` function, follow this [link](./fortran_set_array.md).

## Saving data

Once all data have been set, a snapshot can be write on disk by calling subroutine `uns_save()`

```fortran
call uns_save(ident) 
```

`uns_save(ident)` accept one parameter which is the identifier value return during  [unsio save initialization](#unsio-intialization-for-saving).

## Closing file

Use `uns_close_out(ident)` to close an open unsio file by [unsio save initialization](#unsio-intialization-for-saving) , example :

```fortran
integer ok

ok = uns_close_out(ident)  ! Ident is the file descriptor return by uns_save_init
```

This function accepts one parameter. 

*  **ident** corresponds to the return value of the function uns_save_init() during [unsio save initialization](#unsio-intialization-for-saving)

### Return value

`uns_close_out()` returns a positive number (>=0). A negative returned value means that the simulation has not been opened or an unexpected error occurred.

## A complete example

To see a complete example, follow this [link](../Examples/fortran_example.md).

