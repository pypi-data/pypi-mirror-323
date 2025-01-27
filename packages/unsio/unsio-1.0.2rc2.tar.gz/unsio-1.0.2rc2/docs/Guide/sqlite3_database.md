

# Sqlite3 database

## Introduction
 
Unsio introduce a very useful feature using a sqlite3 database. The idea is to store, in a sqlite3  database, some important information regarding to a simulation, like its name, its file format (Nemo, Gadget, Ramses), its location on the file system, its path etc... 

Thereby, a user will be able to load a snapshot located anywhere in the storage area by simply giving the simulation name as input parameter of any UNSIO programs. Hundreds of simulations can be stored in this file. It's not necessary to know anymore location of the simulation in the storage file system. It makes the analysis of all these simulations even simpler for the user.

## Database name

We must specify to UNSIO library, where is located its sqlite3 database filename. A user must create a file called *$HOME/.unsio*, with the entry *dbname=*, the absolute path of the database. Example of .unsio file:

```
#
dbname = /home/jcl/WD/mydb.sql3
#
```

In the above file example, unsio sqlite3 database file name _dbname_ is " */home/jcl/WD/mydb.sql3*". Unsio engine will try to load information from this file.

## Database scripts

We provide a set of scripts to create and to manage operations to unsio sqlite3 database. These scripts are located in *bin* folder in the installation directory. Note that you must have *DBI perl module installed* to run these scripts.

Each script accept 2 extra parameters :
* --help
give information how to use the script
* --db=_unsio_sqlite3_file_name_
this parameter specify an explicit unsio sqlite3 database name to choose instead of the one specified in [[Sqlite3Db#Unsio-sqlite3-database-name|$HOME/.unsio file]]

Note that you need to install on your system sqlite3-tools package.

## How to create a new unsio sqlite3 database

To create a new unsio sqlite3 database, called "mydb.sql3", use the following script *scripts/perl/mains/unsio_sql3_create_db.pl*

```
unsio_sql3_create_db.pl --help

  ========================================================
  Create an empty unsio sqlite3 database
  ========================================================

 Usage   : unsio_sql3_create_db.pl databasename
 Example : unsio_sql3_create_db.pl --db=mydb.sql3

```

There are 2 _tables_ in an unsio sqlite3 database :
* *info*
 In this table we store information regarding to simulation path location and file format
* *nemorange*
This table is useful for NEMO (gyrfalcON) simulations which don't have explicit components like disk, halo etc... but only one array for all particles. This table is designed to store components name with their corresponding range.

## How to add information to an unsio sqlite3 database

To fill *info* table, use the following script *scripts/perl/mains/unsio_sql3_update_info.pl*

```
unsio_sql3_update_info.pl --help
==========================================================
Update Info table from an UNSIO SQLite3 database
==========================================================

usage   : unsio_sql3_update_info.pl   sim_name         sim_type      sim_dir                     sim_basename       [unsio sqlite3 db]
example : unsio_sql3_update_info.pl --simname=sgs007 --type=Gadget --dir=/rbdata/sergas/sgs007 --base=SNAPS/sgs007

```

### Example

Let suppose that we have the following Gadget simulation :
* name given to the simulation:
**sgs007**
* location directory:
**/rbdata/sergas/sgs007**
* snapshots name:
**/rbdata/sergas/sgs007/SNAPS/sgs007_XXXX**  (where XXXX is an integer incremented at each output)

To add this information to the database *mydb.sql3* proceed as following:

```
unsio_sql3_update_info.pl --simname=sgs007 --type=Gadget --dir=/rbdata/sergas/sgs007 --base=SNAPS/sgs007 --db=mydb.sql3
```

Any programs based on UNSIO library will retrieve information automatically from unsio sqlite3 database about sgs007 simulation.


## How to add particles ranges to an unsio sqlite3 database

NEMO based simulations, like gyrfalcON don't have range in the file format to identify components. We can use *nemorange* table from unsio sqlite3 database to store this information.

To fill *nemorange* table, use the following script *scripts/perl/mains/unsio_sql3_update_nemorange.pl*.

```
unsio_sql3_update_nemorange.pl --help

==========================================================
Update NEMORANGE table of an UNSIO SQLite3 database
==========================================================

usage     : unsio_sql3_update_nemorange.pl simname    [total] [disk] [bulge] [halo] [halo2] [gas] [bndry] [stars] [database]
example : unsio_sql3_update_nemorange.pl --simname=nde145 --total=0:1932766 --disk=0:99999 --halo=100000:599772 --halo2=599773:1932766
```

### Example

Let suppose we have a NEMO simulation snapshot with an halo of dark matter particles stored in the first 800000 indexes, and a disk of old stars particles stored in the last 200000 indexes. To store this information in the unsio slite3 database, proceed as following :

```
unsio_sql3_update_nemorange.pl --simname=nde064 --disk=800000:999999 --halo=0:799999
```

Any programs based on UNSIO library will retrieve information automatically from unsio sqlite3 database about nde064 simulation.

example : to display information about disk component of the simulation nde064

```

ouzo:/home/jcl% uns_info nde064 disk times=200

**************************************************
File name : /r9data/ndisc_evol/nde064/nde064.snap_sp
File type : Nemo
Nbody selected = 200000
Time=200
==================================================
disk    :   200000
mass[1] =  5.000000e-06 5.000000e-06 5.000000e-06 
           5.000000e-06 5.000000e-06 5.000000e-06 
           . . .
pos [3] =  2.390437e-01 -8.551193e-02 -7.266443e-02 
           -1.874399e-01 -1.039366e+00 -1.467193e-01 
           . . .
vel [3] =  8.641896e-01 2.728877e-01 -2.908319e-01 
           9.486520e-01 -2.209999e-01 -3.645913e-02 
           . . .

```


## How to  retrieve information regarding to a simulation name

We provide  a script to display information stored in an unsio sqlite3 database, *scripts/perl/mains/unsio_sql3_get_info.pl* :

```
unsio_sql3_get_info.pl --help

========================================================
Return from an unsio sqlite3 database simulation file:
[/pil/programs/DB/simulation.dbl]
all the informations belonging to the simulation's name
given in parameter.
========================================================

Usage   : unsio_sql3_get_info.pl simname [db]
Example : unsio_sql3_get_info.pl --simname=sgs019

```

### Example

* gadget simulation (simulation name sgs007)

unsio_sql3_get_info.pl sgs007

simname=[sgs007] db=[/pil/programs/DB/simulation.dbl]
dir = /rbdata/sergas/sgs007
 base = SNAPS/sgs007
 name = sgs007
 type = Gadget
 dir = /rbdata/sergas/sgs007

* nemo simulation (simulation name nde145)

unsio_sql3_get_info.pl nde145

simname=[nde145] db=[/pil/programs/DB/simulation.dbl]
dir = /r9data/ndisc_evol/nde145
 base = nde145.snap_sp
 name = nde145
 type = Nemo
 dir = /r9data/ndisc_evol/nde145
 stars = 
 disk = 0:99999
 gas = 
 name = nde145
 halo2 = 599773:1932766
 total = 0:1932766
 halo = 100000:599772
 bndry = 
 bulge =