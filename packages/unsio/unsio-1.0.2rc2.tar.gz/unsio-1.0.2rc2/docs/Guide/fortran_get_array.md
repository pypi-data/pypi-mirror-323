# Fortran functions to get data

Here is a complete description of all Fortran functions used for getting data from snapshot.


## uns_get_array_f

`uns_get_array_f()` get floating data array.

*  integer `uns_get_array_f(ident,comp, tag, array, size_array)` see arguments description below

## uns_get_array_i

`uns_get_array_i()` get integer data array.

*  integer `uns_get_array_i(ident,comp, tag, array, size_array)` see arguments description below

## uns_get_value_f

`uns_get_value_f`() get floating data value.

*  integer `uns_get_value_f(ident, tag, value)` see arguments description below

## uns_get_value_i

`uns_get_value_i()` get integer data value.

*  integer `uns_get_value_i(ident, tag, value)` see arguments description below

## return value

All `uns_get_array_Y()`  methods, return a integer which is the size of array in case of success (requests exist), "0" otherwise.

All `uns_get_value_Y()`  methods, return a integer "1" in case of success, "0" otherwise.

## Arguments description

| argument  | type |description |
| --- | --- | --- |
| **ident** | integer | specify identifier return by uns_init() function |
| **comp** | character string | specify requested component (see table below) |
| **tag** | character string | specify requested data type (see table below) |
| **array** | real*4 or integer | return an array fulfilled with the requested data |
| **size_array** | integer |size of array. For 2D arrays like array(3,MAX), use MAX |
| **value** | real*4 or integer | return one value fulfilled with the requested data |

h3. Components (comp)

From argument *comp* , we select the component to be treated.

{%
    include-markdown "./components_table.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}
h3. Data (tag)

From argument **tag** , we specify which data we want to get.

| tag value  | array |size_array | description |
| --- | --- | --- | --- |
| pos              | real*4 | MAXSIZE | return array of particles positions, pos(3,MAXSIZE)) |
| vel              | real*4 |  MAXSIZE | return array of particles velocities, vel(3,MAXSIZE)) |
| mass            | real*4 | MAXSIZE |  return array of particles masses,  mass(MAXSIZE)|
| acc              | real*4 |  MAXSIZE | return array of particles accelerations, acc(3,MAXSIZE)) |
| pot               |real*4 |  MAXSIZE |  return array of particles potential,  pot(MAXSIZE)|
| rho               | real*4 |   MAXSIZE | return array of particles density,  rho(MAXSIZE)|
| hsml           |real*4 |  MAXSIZE | return array of particles hydro smooth length,  hsml(MAXSIZE)|
| temp             | real*4 | MAXSIZE |  return array of particles temperature,  temp(MAXSIZE)|
| age              | real*4 |MAXSIZE |   return array of particles age,  age(MAXSIZE)|
| metal             |real*4 | MAXSIZE |   return array of particles metallicity ,  metal(MAXSIZE)|
| u               |real*4 |  MAXSIZE | return array of particles internal energy ,  u(MAXSIZE)|
| id             |integer | MAXSIZE |  return array of particles index  ,  id(MAXSIZE)|
| aux              | real*4 |  MAXSIZE | return auxiliary array ,  aux(MAXSIZE)|
| keys             |real*4 |MAXSIZE |  return keys array,  keys(MAXSIZE)|

h3. Value

| tag value  | value  | description |
| --- | --- | --- |
| ngas           | integer        | #gas particles |
| nhalo           | integer       | #dark matter particles |
| ndisk           | integer       | #old stars particles |
| nstars          | integer       | #stars particles |
| nbulge           | integer        | #bulge particles |
| nbndry           | integer        | #bndry particles |
| nsel           | integer        | #selected particles |
| time           | real*4        | snapshot time |
| nvarh         | integer    | #hydro arrays (RAMSES) |