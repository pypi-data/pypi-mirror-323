# Reading data

Unsio provide an easy way to access  snapshot data from a set of methods implemented in *uns::CunsIn* class. The first step is to instantiate a CunsIn object.

## Create/instantiate CunsIn object

```c++
uns::CunsIn * uns = new uns::CunsIn(simname,select_c,select_t,verbose);
```

CunsIn constructor accept 4 parameters (4th is optional):

- **simname**,  is a c++ string or a char *, which contain to the input file you want to read  (see the [list of supported input/output files](../Guide/supported_input_file_format.md))
- **select_c**,   is a c++ string or a char *, which contain the list of the component you want to load (see the [list of the component](../Guide/components_table.md) )
- **select_t**,  is a c++ string or a char *, specify on which range of time data must be loaded
- **verbose**, is a boolean to activate (true) / deactivate (false - default) some debugging information

## Check valid file format

According to simname, unsio will detect automatically the simulation file format. Once object is instantiated, you have to check that requested input file is supported by unsio. To do that use the following method:

```c++
 bool uns->isValid() 
```

This method return true if the snapshot file format (simname) is supported by unsio, and return false otherwise.

## Loading data

The next step consist to load a snapshot according to user requests (components and time range). To do that use the following method:

```c++
 bool uns->snapshot->nextFrame(bits)
```

This function return **true** if a new snapshot has been successfully loaded, **false** otherwise
This function accept an optional parameter, "bits", which is a c++ string. Variable "bits" contains a list of all the data (positions, masses,velocities etc..)  that the user want to load (see [how to select data at loading](../Guide/howto_select_data.md#how-to-select-data-at-loading))
This variable is used to speed up reading process in case the user does not want to load all the data but just only few of them. It can be really interesting when snapshot files are really big. If no parameter is passed to this function, then all data will be loaded.

## Getting data

Unsio provides a unique method, uns->snapshot->getData(),  to get data stored in a snapshot. This method return true in case of success, false otherwise.
The method getData() is overloaded and can accept different numbers of parameters.

example:
```c++
float * pos;
bool ok;
int nbody;
ok = uns->snapshot->getData("stars","pos" ,&nbody,&pos );       // read positions for component stars
```
In the above example, we explicity ask to getData method, to return positions for **"stars"** component. This is why we give string **"stars"** as first argument. Second argument specify which data we want to return, in that case positions with **"pos"** string. Third argument, **nbody** , will return number of particles in the array of positions. Last and fourth argument, **pos** , is the array of positions itself. This array is automatically memory allocated by unsio.
As we assume data on disk have 3 dimensions, nbody will return the number of particles for the requested component, but the array itself will have three time more values.

example:
```c++
float * pos;
bool ok;
int nbody;
ok = uns->snapshot->getData("pos" ,&nbody,&pos );       // read positions for all components selected by user
```
In the above example, you can notice that getData() method as only three arguments. Here we get positions data for all components requested by the user. This request occur during unsio instantiation object.

To have a complete description of getData() method, follow this [link](./get_data_md_cpp.md).

## Useful methods

Unsio reading class,  **uns::CunsIn**, has a set of useful methods which give information about the snapshot.

```c++
 std::string uns->snapshot->getInterfaceType()
```
Return a string which contains the interface type of the loaded snapshot. It can be **Nemo**, **Gadget1**, **Gadget2** or **Ramses**.

```c++
 std::string uns->snapshot->getFileStructure()
```
Return a string which give information of the file structure of the snapshot. It can be *range* (for nemo snapshot), or *component* (for others snapshots)

```c++
 std::string uns->snapshot->getFileName()
```
Return snapshot file name.

## A complete example

To see a complete example, follow this [link](../Examples/cpp_example.md).
