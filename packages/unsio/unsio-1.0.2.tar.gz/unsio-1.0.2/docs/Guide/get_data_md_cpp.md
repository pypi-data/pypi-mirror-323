# getData method()

Here is a complete description of getData() method used to get data from snapshot.

getData()  method belong to uns::Cunsin class.

## Return value

All `getData()` method, return a boolean "true" in case of success, "false" otherwise.

## getData, an overloaded method

Method getData is overloaded and can have different number of arguments

- `getData(comp, tag, n, array)` see arguments description below
- `getData( tag, n, array)` see arguments description below
- `getData( tag, value)` see arguments description below

## Arguments description

| argument    | type  | description |
| --- | --- | ---|
| **comp** | input c++ string or char * | specify requested component (see table below) |
| **tag** | input c++ string or char * | specify requested data type (see table below) |
| **n** | int * |return number of particles for the requested data |
| **array** | float** or int** | return an array fulfilled with the requested data |
| **value** | float* or int* | return one value fulfilled with the requested data |

### Components (comp)

From argument **comp** , we select the component to be treated.

{%
    include-markdown "./components_table.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}

### Data (tag)

From argument *tag* , we specify which data we want to get. If comp is specified in getData() method, then retrieved data  will belong to the component "comp". If comp is not specified, then retrieved data will  belong to all the components selected during the object instantiation. 

{%
    include-markdown "./data_description.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}