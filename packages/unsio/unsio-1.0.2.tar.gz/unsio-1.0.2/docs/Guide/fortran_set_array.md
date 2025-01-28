# Fortran functions to set data

Here is a complete description of all Fortran functions used for setting data to a  snapshot.

## uns_set_array_f

`uns_set_array_f`() set floating data array.

- `integer uns_set_array_f(ident,comp, tag, array, number_elements)` see arguments description [below.](#arguments-description)

## uns_set_array_f

`uns_set_array_i()` set integer data array.

- `integer uns_set_array_i(ident,comp, tag, array, number_elements)` see arguments description [below.](#arguments-description)

## uns_set_value_f

`uns_set_value_f()` set floating data value.

- `integer uns_set_value_f(ident,comp, tag, value)` see arguments description [below.](#arguments-description)

## uns_set_value_i

`uns_set_value_i()` set integer data value.

- `integer uns_set_value_i(ident,comp, tag, value)` see arguments description [below.](#arguments-description)

### Return value

All functions, return an integer "1" in case of success, "0" otherwise.

### Arguments description

|argument |type  | description |
| --- | --- | --- |
| **ident** | integer | specify identifier return by [[FortranWriteData#Unsio-intialization-for-saving| unsio save initialization]] function |
| **comp** | character string | specify requested component (see table below) |
| **tag** | character string | specify requested data type (see table below) |
| **array** | real*4 or integer | array fulfilled with the data to be saved |
| **size_element** | integer |number of elements in  array. For 2D arrays like array(3,nelements), use nelements |
| **value** | real*4 or integer | value to be saved |

### Components (comp)

From argument **comp** , we select the component to be treated.

{%
    include-markdown "./components_table.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}

### Data (tag)

From argument **tag** , we specify which data we want to set.

| tag value  | array | number_elements | description |
| --- | --- | --- | --- |
| pos              | real*4 | nbody | array of particles positions, pos(3,nbody)) |
| vel              | real*4 |  nbody | array of particles velocities, vel(3,nbody)) |
| mass            | real*4 | nbody |  array of particles masses,  mass(nbody)|
| acc              | real*4 |  nbody | array of particles accelerations, acc(3,nbody)) |
| pot               |real*4 |  nbody |  array of particles potential,  pot(nbody)|
| rho               | real*4 |   nbody | array of particles density,  rho(nbody)|
| hsml           |real*4 |  nbody | array of particles hydro smooth length,  hsml(nbody)|
| temp             | real*4 | nbody |  array of particles temperature,  temp(nbody)|
| age              | real*4 |nbody |   array of particles age,  age(nbody)|
| metal             |real*4 | nbody | array of particles metallicity ,  metal(nbody)|
| u               |real*4 |  nbody | array of particles internal energy ,  u(nbody)|
| id             |integer | nbody |  array of particles index  ,  id(nbody)|
| aux              | real*4 |  nbody | auxiliary array ,  aux(nbody)|
| keys             |real*4 |nbody |  keys array,  keys(nbody)|


| tag value  | value  | description |
| --- | --- | --- |
| time           | real*4        | snapshot time |
