#!/usr/bin/env python
#
# In the example below, we load a RAMSES simulation that
# we save in gadget3 file format
#

import unsio.input as uns_in  # unsio reading module

myfile="/home/jcl/dwarf1.g2" # input RAMSES simulation
# we instantiate object
my_in=uns_in.CUNS_IN(myfile,"all") # We select components GAS and STARS
#
# Reading
#
if my_in.nextFrame("x"): # load snapshot
  # read stars positions
  status,poss=my_in.getData("halo","pos")
  print("get halo pos :",status)
#   # read gas positions
#   status,posg=my_in.getData("gas","pos")
  # read gas densities
  status,z=my_in.getData("STREAM","Z")
  print("get STREAM Z  :",status)
  # read time simulation
  status,timex=my_in.getData("time")
#
# Writing
#
import unsio.output as uns_out # unsio writing module

myoutfile="/home/jcl/snapshot.g2" # output file name
# we instantiate object
my_out=uns_out.CUNS_OUT(myoutfile,"gadget2") # select gadget3 output format

# prepare data to be saved
# set time
status=my_out.setData(timex,"time")
# set positions for stars
status=my_out.setData(poss,"halo","pos")
print("set pos halo :", status)
# # set positions for gas
# status=my_out.setData(posg,"gas","pos")
# set density for gas
status=my_out.setData(z,"EXTRA","Z")
print("set extra zz :", status)

# write on file system
print("yo:")
my_out.save()
# close
my_out.close()
