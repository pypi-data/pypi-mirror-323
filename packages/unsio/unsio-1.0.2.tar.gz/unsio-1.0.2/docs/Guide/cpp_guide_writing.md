
# C++ user guide, writing data

## Create/instantiate CunsOut object

Unsio provides an easy way to write  snapshot data from a set of methods implemented in *uns::CunsOut* class. The first step is to instantiate a CunsOut object.

```c++
uns::CunsOut * uns = new uns::CunsOut(simname,snap_type,verbose);
```

CunsIn constructor accept 3 parameters (3rd is optional):

- **simname**,  is a c++ string or a char *, which contain to the input file you want to save
- **snap_type**,   is a c++ string or a char, which indicate the snapshot output file format ( *nemo* and *gadget2* are currently supported )
- **verbose**, is a boolean to activate (true) / deactivate (false - default) some debugging information

## Set data

Unsio provides a unique method, uns->snapshot->setData(),  to store data in a snapshot. This method return true in case of success, false otherwise.


example:
```c++
float * pos;
bool ok;
int nstars;

// put stars positions in pos array
....
....
ok = uns->snapshot->setData("stars","pos" ,nstars,pos, false );       // store positions for component stars
```
In the above example, we store stars positions from "pos" array. The latest argument "false" means that we want to copy positions array into a working array belonging to the class CunsOut.

The method setData() is overloaded and can accept different numbers of parameters.
To have a complete description of setData() method, follow this [link](./set_data_cpp.md)

## Saving data

Once all arrays have been passed to seData() method, call method uns->snapshot->save() to write data on file system.

```c++
uns->snapshot->save();
```
## A complete example

To see a complete example, follow this [link](../Examples/cpp_example.md).
