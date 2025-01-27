#!/usr/bin/env python
#
# In the example below, we load a RAMSES simulation that
# we save in gadget3 file format
#

import unsio.input as uns_in  # unsio reading module

#myfile="/home/jcl/output_00004" # input RAMSES simulation
myfile="/home/jcl/Documents/EAGLE_SIMULATION/snapshot_028_z000p000/snap_028_z000p000.0.hdf5" # input RAMSES simulation
# we instantiate object
my_in=uns_in.CUNS_IN(myfile,"gas,stars") # We select components GAS and STARS
#
# Reading
#
if my_in.nextFrame(): # load snapshot
  # read stars positions
  status,poss=my_in.getData("stars","pos")
  print("stars",status,poss,poss.size/3)

  # read gas positions
  print("gas")
  status,posg=my_in.getData("gas","pos")
  print("stars",status,posg)
  # read gas densities
  status,rho=my_in.getData("gas","rho")
  print("rho",status,rho)
  # read time simulation
  status,timex=my_in.getData("time")
#
# Writing
#
import unsio.output as uns_out # unsio writing module

myoutfile="snapshot.g3" # output file name
# we instantiate object
my_out=uns_out.CUNS_OUT(myoutfile,"gadget3") # select gadget3 output format

# prepare data to be saved
# set time
status=my_out.setData(timex,"time")
# set positions for stars
status=my_out.setData(poss,"stars","pos")
# set positions for gas
status=my_out.setData(posg,"gas","pos")
# set density for gas
status=my_out.setData(rho,"gas","rho")

# write on file system
my_out.save()
# close
my_out.close()
