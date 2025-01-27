# Method getData

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

## Return value

`getData()` method, return two variables. First a boolean ( "true" in case of success, or "false" otherwise) and a 1D numpy array filled with float or int values, it depends what have been requested.

## An overloaded method

Method getData is overloaded and can have different number of arguments

* `ok,data=myobj.getData(comp, tag)` see arguments description below
* `ok,data=myobj.getData( tag)` see arguments description below

### Return variables

| variable    | type  | description |
| --- | --- | --- |
| *ok* | boolean | return true if array exist, false otherwise |
| *data* | float or int | return a numpy 1D array fulfilled with the requested float or integer data |

### Arguments description

| argument    | type  | description |
| --- | --- | --- |
| *comp* | string | specify requested component (see table below) |
| *tag* | string | specify requested data type (see table below) |

#### Components (comp)

From argument **comp** , we select the component to be treated.

{{include(Components)}}

#### Data tag (in combination with comp)

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

#### Data tag (no comp specified)

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