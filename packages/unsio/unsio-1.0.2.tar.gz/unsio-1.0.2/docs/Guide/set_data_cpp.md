# Method setData()

Here is a complete description of setData() method used to stored data.

setData()  method belong to uns::CunsOut class.

## Return value

All `setData()` method, return a boolean "true" in case of success, "false" otherwise.

## An overloaded method

Method setData is overloaded and can have different number of arguments

- `setData(comp, tag, n, array,map=false)` see arguments description below
- `setData( tag, n, array,map=false)` see arguments description below
- `setData( tag, value)` see arguments description below

## Arguments description

| argument    | type  | description |
| --- | --- | --- |
| **comp** | input c++ string or char * | specify requested component (see table below) |
| **tag** | input c++ string or char * | specify requested data type (see table below) |
| **n** | int  |set number of particles for the requested data |
| **array** | float* or int* | array fulfilled with the requested data to be saved |
| **value** | float* or int* | value fulfilled with the requested data to be saved |
| **map** | boolean | specify if address of stored data must be mapped or copy (default is copy [false]) |

### Components (comp)

From argument *comp* , we select the component to be treated.

{%
    include-markdown "./components_table.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}

### Data (tag)

From argument *tag* , we specify which data we want to store. If comp is specified in setData() method, then data  which  belong to the component "comp" will be treated only. If comp is not specified, then data which  belong to all the components selected during the object instantiation will be treated.

| tag value  | n | array  | description |
| --- | --- | --- | --- |
| pos              | #particles | float * |  array of particles position (size=n*3) |
| vel              | #particles | float * |  array of particles velocitie  (size=n*3)|
| mass              | #particles | float * | array of particles velocitie  (size=n)|
| acc              | #particles | float * | array of particles acceleration  (size=n*3)|
| pot              | #particles | float * | array of particles potential  (size=n)|
| rho              | #particles | float * | array of particles density  (size=n)|
| hsml              | #particles | float * | array of particles hydro smooth length   (size=n)|
| temp              | #particles | float * | array of particles temperature   (size=n)|
| age              | #particles | float * | array of particles age   (size=n)|
| metal              | #particles | float * | array of particles metallicity   (size=n)|
| u              | #particles | float * | array of particles internal energy  (size=n)|
| id              | #particles | int * | array of particles index  (size=n)|
| aux              | #particles | float * | auxiliary array  (size=n)|
| keys              | #particles | float * | return keys array  (size=n)|

| tag value  | value  | description |
| --- | --- | --- |
| time           | float *        | snapshot time |