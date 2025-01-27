# Writing data 

Writing UNSIO data from python language is pretty simple and is done in 3 steps:

* UNSIO object instantiation 
* Setting data to save
* Saving data

## Create/instantiate CUNS_OUT object

Unsio python wrapper is based on C++ API with slight modifications to works with numpy arrays. Module **unsio.output** provides an easy way to save  snapshot data, in different format, from a set of methods implemented in **CUNS_OUT** object. The first step is to instantiate a **CUNS_OUT** object.

```python
import unsio.input as uns_in
import unsio.output as uns_out

simname="/home/jcl/gtr119_1600"
components="disk,gas,stars"
times="all"
float32=True

# input
uns = uns_in.CUNS_IN(simname,components,times,float32)

# output
outfile="mysnap.g2"     # output filename
type="gadget2"             # we choose to save file in gadget2 format
unsout=uns_out.CUNS_OUT(outfile,type,float32)  # instantiate output object
```

CUNS_OUT constructor accepts 3 parameters :

* **outfile**,  is a string, which contain the output file name
* **type**,   is a string which contain the [format type](../Guide/supported_input_file_format.md#list-of-files) in which you want to save.
* **float32**, is a boolean to activate (True -default) for saving data in single precision / deactivate (False ) for saving data in double precision

## Setting data

CUNS_OUT class provides one universal function to setData to be stored in a file : **CUNS_OUT.setData( data_array, comp, tag)**

!!! tips 
    To get some python docstring help
    ```shell
    python -m pydoc unsio.output
    ```

### Setting numpy arrays

```python

CUNS_OUT.setData(data_array, comp, tag=None)

Args:
   data_array (array|float) : 1D numpy_array or single value

   comp (str) : component gas,stars,disk,halo,bndry or bulge

   tag    (str) : array to set
                  example :
                      tag="pos"
                      tag="acc"
                      pos,vel,mass,rho...

IMPORTANT : if 'tag' is None, then 'comp' is treated as 'tag' (see below, setting single value)

Return :
    status : 1 if success, 0 otherwise

```

From argument **comp** , we specify the [component](../Guide/components_table.md) to be treated.


From argument *tag* , we specify which data we want to set. 

|tag string   | descripton | numpy data_array passed as parameter  |
| --- | --- | --- |
| pos              | particles positions | numpy 1D array of particles position (size=n*3) |
| vel              | particles  velocities | numpy 1D array of particles velocitie  (size=n*3)|
| mass            | particles masses | numpy 1D array of particles velocitie  (size=n)|
| acc              | particles accelerations | numpy 1D array of particles acceleration  (size=n*3)|
| pot               | particles potential | numpy 1D array of particles potential  (size=n)|
| rho               | particles densities | numpy 1D array of particles density  (size=n)|
| hsml            | particles hsml | numpy 1D array of particles hydro smooth length   (size=n)|
| temp           |  particles temperatures | numpy 1D array of particles temperature   (size=n)|
| age              | particles ages | numpy 1D array of particles age   (size=n)|
| metal           | particles metallicity | numpy 1D array of particles metallicity   (size=n)|
| u                 |  particles internal energy |numpy 1D array of particles internal energy  (size=n)|
| aux             | particles auxilliary (NEMO) |  numpy 1D auxiliary array  (size=n)|
| keys            |  particles keys (NEMO) |numpy 1D keys array  (size=n)|
| id             |  particles indexes (NEMO) |numpy 1D keys array  (size=n)|

### Setting single value


* `setData`(data_value,tag)

**tag** specify which  data value we want to set

Known **tag** values are :

| tag string   | descripton | float or integer value passed as parameter  |
| --- | --- | --- |
| time              | snapshot time | float value |

## Saving data

Once you have **set** all your data, you must call *save()* method to write file on disk
```python
...
unsout.save()
..
```

## A complete example

See a complete example [here](../Examples/py_example_complete.md).
