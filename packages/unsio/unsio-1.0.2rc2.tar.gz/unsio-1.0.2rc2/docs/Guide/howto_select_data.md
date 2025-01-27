# Selecting data

## How to select list of components

When you instantiate CunsIn(simname, *select_c* ,select_t,verbose) object, you can specify one or many components separated by "," from the list below:

 gas, disk, halo, dm, stars, bulge, bndry, all

| component value   | description |
| --- | --- |
| **gas** | Gas particles |
| **halo** | Dark matter particles |
| **dm**   | Dark matter particles |
| **disk** | Old stars particles |
| **stars** | Stars particles |
| **bulge** | Bulge particles |
| **bndry** | bndry particles |

examples:
* to select gas only
 `select_c="gas"`
* to select halo and gas and stars
 `select_c="halo,gas,stars"`
* to select all components
 `select_c="all"`

## How to select list of ranges of particles

When you instantiate uns::UnsIn(simname, *select_c* ,select_t,verbose) object, you can specify one or many range of particles  separated by "," . This is useful for nbody simulations file format which don't have components like NEMO format.

examples:
* to select particle in one range 0:99999
  `select_c="0:99999"`
* to select particles from 2 ranges 0:99999 and 300000:399999
<pre> select_c="0:99999,300000:399999" </pre>
* to select all particles
<pre> select_c="all"</pre>

## How to specify range of time at loading

When you instantiate uns::UnsIn(simname, select_c, *select_t* ,verbose) object, you can specify only a sequence of time step to load. Range of time is controlled by a string variable with the following syntax:

  "time1:time2,time3:time4"

examples:
* select_t="5.0"
will load time step 5.0
* select_t="0.0:3.0"
will load all time steps between time from 0.0 to 3.0
* select_t="0.0:3.0,5.0:7.0"
will load all time steps between time from 0.0 to 3.0 and from 5.0 to 7.0


## How to select data at loading

When you load a snapshot by calling method snapshot->nextFrame(bits), you can give a parameter  'bits', to specify which data you want to load. A user may not want to load all the possible data stored in a snapshot but just few of them. This feature can dramatically speed up file reading in case of big input files.

Variable bits is a c++ string, or a char * composed of letters which represent data that user may want to load. Here is the list of all available data.

| character    |  description |
| --- | --- |
|  x                    |  position         |
|  v                    |  velocity         |
|  m                    |  mass         |
| p                    | potential |
| a                    | acceleration |
| R                   | density          |
| H                   | hsml |
| I                     | particles id  |
| e                   | softening |
| U                  | internal energy |
| M                  | metallicity |
| A                   | stars  age |
| T                   | temperature |
| k                    | keys (nemo) |
| X                   | auxiliary (nemo) |
| z                   | extra 1         |
| Z                  | extra 2 |
| i                   | extra 3 |

examples:
* bits="xvm"
load positions, velocities and masses
* bits="xRH"
load positions, densities and hsml
* bit="" 
load all data (default)




