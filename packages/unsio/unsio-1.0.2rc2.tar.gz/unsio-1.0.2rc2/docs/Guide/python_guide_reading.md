# Reading data

Reading UNSIO data from python language is pretty simple and is done in 3 steps:

* UNSIO object instantiation 
* Loading data
* Extracting data

## Create/instantiate CUNS_IN object

Unsio python wrapper is based on C++ API with slight modifications to works with numpy arrays. Module **unsio.input** provides an easy way to access  snapshot data from a set of methods implemented in **CUNS_IN** object. The first step is to instantiate a CUNS_IN object.

```python
import unsio.input as uns_in

simname="/home/jcl/gtr119_1600"
components="disk,gas,stars"
times="all"
float32=True
uns = uns_in.CUNS_IN(simname,components,times,float32)
```

CUNS_IN constructor accepts 4 parameters (4th is optional):

* **simname**,  is a string, which contain the input file you want to read from a [list of supported input files](../Guide/supported_input_file_format.md)
* **components**,   is a string, which contain the [list of the component](../Guide/components_table.md) you want to load (see also [how to select data](../Guide/howto_select_data.md))
* **times**,  is a string, which specify on which range of time data must be loaded
* **float32**, is a boolean to activate (True -default) for loading data in single precision / deactivate (False ) for loading data in double precision

According to simname, unsio will detect automatically the simulation file format.

## Loading data

The next step consist to load a snapshot according to user requests (components and time range). To do that use the following method **nextFrame()**:

```python
bits=""         # select properties, "" means all
ok=uns.nextFrame(bits)   # load data from disk
```

This function return **True** if a new snapshot has been successfully loaded, **False** otherwise
This function accepts an optional parameter, "bits", which is a string. Variable "bits" contains a list of all the data (positions, masses,velocities etc..)  that the user want to load (see [how to select data at loading](../Guide/howto_select_data.md#how-to-select-data-at-loading))
This variable is used to speed up reading process in case the user does not want to load all the data but just only few of them. It can be really interesting when snapshot files are really big. If no parameter is passed to this function, then all data will be loaded.

## Extracting data

CUNS_IN class provides one universal function to [getData](#method-getdata) stored in a snapshot : **CUNS_IN.getData(comp, tag)**


```python

CUNS_IN.getData(comp,tag)

Args:
    comp (str) : component or list of components separeted with a coma
                   example :
                      select="gas"
                      select="gas,stars"
    tag    (str) : array to get
                   example :
                      tag="pos"
                      tag="acc"
                      pos,vel,mass,rho...

    IMPORTANT : if 'tag' is None, then 'comp' is treated as 'tag' (see below)

Return :
    status,numpy_array       (if tag is not None)
    status,value             (if tag is None)
    in both case, status=1 if success, 0 otherwise

```

Arrays are treated as one dimensional numpy arrays. 
This function returns a boolean first, then a numpy 1D array. Boolean is set to True if the requested array exist, otherwise False.

* example : getting positions from disk component
 
```python
comp="disk"
prop="pos"
# read positions for component disk
ok,pos = uns.getData(comp,prop)  # pos is a 1D numpy array, it returns pos for disk component                                        
```

In the previous example, first argument 'comp' specify the component selected among gas, disk, halo, dm, stars, bulge, bndry and  all. Second argument specify which properties of the component we want to get. Return array *is a one dimensional numpy array*.

* example : getting id arrays

```python
comp="disk"
prop="id"
# read IDs for component disk
ok,id = uns.getData(comp,prop)  # id is a 1D numpy array, it returns particles indexes                                       
```


* example : getting time simulation value 

```python
# get timestep of the current snapshot
ok,timex = uns.getData("time")  #  
```
!!! tips 
    To get some python docstring help
    ```shell
    python -m pydoc unsio.input
    ```
## Method getData 

 **getData()** python method is used to get data from snapshot.

It comes from CUNS_IN class of **unsio.input** module, and is a method which belong to CUNS_IN class.

In the example below, we assume that we have instantiate `myobj`, a CUNS_IN object like the following piece of code :

```python
import unsio.input as uns_in
...
...
myobj=uns_in.CUNS_IN(simname,comp,time)
...
```

### Return value

`getData()` method, return two variables. First a boolean ( "true" in case of success, or "false" otherwise) and a 1D numpy array filled with float or int values, it depends what have been requested.

### An overloaded method

Method getData is overloaded and can have different number of arguments

* `ok,data=myobj.getData(comp, tag)` see arguments description below
* `ok,data=myobj.getData( tag)` see arguments description below

#### Return variables

| variable    | type  | description |
| --- | --- | --- |
| *ok* | boolean | return true if array exist, false otherwise |
| *data* | float or int | return a numpy 1D array fulfilled with the requested float or integer data |

#### Arguments description

| argument    | type  | description |
| --- | --- | --- |
| *comp* | string | specify requested component (see table below) |
| *tag* | string | specify requested data type (see table below) |

##### Components (comp)

From argument **comp** , we select the [component](../Guide/components_table.md) to be treated.


##### Data tag (in combination with comp)

From argument **tag** , we specify which data we want to get. If comp is specified in getdata() method, then retrieved data  will belong to the component "comp".  All return variables are numpy 1D array in floating format or integer format.

| tag value   | return variable |
| --- | --- |
| pos              | return numpy 1D array of particles position (size=n*3) |
| vel              | return numpy 1D array of particles velocitie  (size=n*3)|
| mass            | return numpy 1D array of particles velocitie  (size=n)|
| acc              | return numpy 1D array of particles acceleration  (size=n*3)|
| pot               | return numpy 1D array of particles potential  (size=n)|
| rho               | return numpy 1D array of particles density  (size=n)|
| hsml            | return numpy 1D array of particles hydro smooth length   (size=n)|
| temp           | return numpy 1D array of particles temperature   (size=n)|
| age              | return numpy 1D array of particles age   (size=n)|
| metal           | return numpy 1D array of particles metallicity   (size=n)|
| u                 | return numpy 1D array of particles internal energy  (size=n)|
| aux             | return numpy 1D auxiliary array  (size=n)|
| id                 | return numpy 1D int array of particles id (size=n)|
| keys            | return numpy 1D int keys array  (size=n)|

##### Data tag (no comp specified)

If **comp** is not specified, then retrieved data will be a single value specified by **tag**.

| tag   | return variable |
| --- | --- |
| time              | return snapshot time (float) |
| nbody              | return snapshot nbody (int)|
| nsel              | return #bodies selected during instantiation (int)|
| ngas              | return #gas bodies if selected during instantiation (int)|
| nstars              | return #stars bodies if selected during instantiation (int)|
| nhalo              | return #halo bodies if selected during instantiation (int)|
| ndisk              | return #disk bodies if selected during instantiation (int)|
| nbulge              | return #bulge bodies if selected during instantiation (int)|
| nbndry              | return #bndry bodies if selected during instantiation (int)|
| nvarh              | return #physical quantities for RAMSES snapshot (int)|


## Useful methods

**CUNS_IN** reading class, from unsio.input module, has a set of useful methods which give information about the snapshot.

* **uns.getInterfaceType()**, returns a string which contains the interface type of the loaded snapshot. It can be **Nemo**, **Gadget1/2/3** or **Ramses**.

* **uns.getFileStructure()**, returns a string which give information of the file structure of the snapshot. It can be **range** (for nemo snapshot), or **component** (for others snapshots)

* **uns.getFileName()**, returns snapshot file name.

## A complete example

See a complete example [here](../Examples/py_example_complete.md).