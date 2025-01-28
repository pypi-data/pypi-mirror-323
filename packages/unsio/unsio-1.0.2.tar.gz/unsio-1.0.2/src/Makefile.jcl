# -*-makefile-*-
# ============================================================================
# Copyright Jean-Charles LAMBERT - 2008                                       
# e-mail:   Jean-Charles.Lambert@oamp.fr                                      
# address:  Dynamique des galaxies                                            
#           Laboratoire d'Astrophysique de Marseille                          
#           Pole de l'Etoile, site de Chateau-Gombert                         
#           38, rue Frederic Joliot-Curie                                     
#           13388 Marseille cedex 13 France                                   
#           CNRS U.M.R 6110                                                   
# ============================================================================


#include $(NEMOLIB)/makedefs

SHELL = /bin/csh -f


# Compilation otions
CPP      = g++
CPPFLAGS = -I$(NEMOINC) -I$(NEMOLIB) -Wall -g
LNEMO    = -L$(NEMOLIB) -lnemo++ -lnemo

OS       = linux
ifeq (${OS},linux) 
	LDL=-ldl
else
	LDL=
endif

# Files OBJ
FOBJ = obj
# Files BIN

# FILES SOURCES
FSRC = ./

# targets
lib    : dirs $(FOBJ)/libuns.a testlib
bin    : dirs info gad
info   : dirs $(FBIN)/g2info
gad    : dirs $(FBIN)/gadget2nemo
nem    : dirs $(FBIN)/nemo2gadget
#install: info gad
#	\cp -p $(FBIN)/gadget2nemo $(FBIN)/g2info ${NEMOBIN}
#	chmod 755  ${NEMOBIN}/gadget2nemo  ${NEMOBIN}/g2info

#nemo_bin: install



clean:
	@/bin/rm $(OBJLIB) $(LIB)  >& /dev/null
#--
# LIBs
#
LIB      := $(FOBJ)/libuns.a
#--
IO       := $(FOBJ)/gadgetio.o
COMP     := $(FOBJ)/componentrange.o
USER     := $(FOBJ)/userselection.o
UNS      := $(FOBJ)/unsengine.o
UNSI     := $(FOBJ)/unsidentifier.o
UNSW     := $(FOBJ)/unsfwrapper.o
INTER    := $(FOBJ)/snapshotinterface.o
SNAPGAD  := $(FOBJ)/snapshotgadget.o

OBJLIB   := $(IO) $(COMP) $(USER) $(UNS) $(UNSI) $(UNSW) $(SNAPGAD)
OBJTOOLS := $(IO) $(COMP)

$(UNS) :  $(FSRC)/unsengine.cc $(FSRC)/unsengine.h $(SNAPGAD)
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/unsengine.cc

$(UNSI):  $(FSRC)/unsidentifier.cc $(FSRC)/unsidentifier.h $(UNS)
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/unsidentifier.cc

$(UNSW):  $(FSRC)/unsfwrapper.cc $(UNSI)
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/unsfwrapper.cc

$(IO) : $(FSRC)/gadgetio.cc $(FSRC)/gadgetio.h $(FSRC)/componentrange.h $(FSRC)/userselection.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/gadgetio.cc

$(COMP) : $(FSRC)/componentrange.cc  $(FSRC)/componentrange.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/componentrange.cc


$(USER) : $(FSRC)/userselection.cc  $(FSRC)/userselection.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/userselection.cc

$(SNAPGAD) : $(FSRC)/snapshotgadget.cc $(FSRC)/snapshotgadget.h $(FSRC)/snapshotinterface.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/snapshotgadget.cc

#$(INTER):  $(FSRC)/snapshotinterface.cc $(FSRC)/snapshotinterface.h  $(COMP) 
#	$(CPP) $(CPPFLAGS)  -o $@ -c $(FSRC)/snapshotinterface.cc

$(FSRC)/snapshotinterface.h : $(FSRC)/componentrange.h

#-- lib

$(FOBJ)/libuns.a : $(OBJLIB)
	ar rcv  $@ $(OBJLIB)


#-- testlib target
OBJF :=  $(FOBJ)/testlib.o

testlib : $(FOBJ)/testlib.o
	$(FC) $(FFLAGS) -o $@ $(FOBJ)/testlib.o $(FOBJ)/libuns.a -lstdc++

$(FOBJ)/testlib.o : $(FSRC)/testlib.F $(FOBJ)/libuns.a 
	$(FC) $(FFLAGS) -o $@ -c $(FSRC)/testlib.F
#--
OBJ1    := $(FOBJ)/gadget2nemo.o
$(FBIN)/gadget2nemo :  $(OBJ1) $(OBJTOOLS) $(USER)
	$(CPP)  -o $@  $(OBJ1) $(OBJTOOLS) $(USER) $(LNEMO) ${LDL} -lstdc++ -lm 

$(OBJ1) : $(FSRC)/gadget2nemo.cc  $(FSRC)/gadgetio.h $(FSRC)/userselection.h $(FSRC)/componentrange.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/gadget2nemo.cc


#--
OBJ2    = $(FOBJ)/nemo2gadget.o 
$(FBIN)/nemo2gadget :  $(OBJ2) $(OBJTOOLS)
	$(CPP)  -o $@ $(OBJ2) $(OBJTOOLS) $(LNEMO) ${LDL} -lstdc++ -lm 

$(OBJ2) : $(FSRC)/nemo2gadget.cc $(FSRC)/gadgetio.h $(FSRC)/userselection.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/nemo2gadget.cc
#--
OBJ3    := $(FOBJ)/g2info.o
$(FBIN)/g2info :  $(OBJ3) $(OBJTOOLS)
	$(CPP)  -o $@  $(OBJ3) $(OBJTOOLS) $(LNEMO) ${LDL} -lstdc++ -lm 

$(OBJ3) : $(FSRC)/g2info.cc  $(FSRC)/gadgetio.h
	$(CPP) 	$(CPPFLAGS)  -o $@ -c  $(FSRC)/g2info.cc




# targets
dirs :
	@mkdir -p ${FOBJ} ${FBIN}

tar:
		(cd ../..; tar czhvf gadget2-tools/gadget2-tools.tar.gz `ls gadget2-tools/src/*.{cc,h,txt}  gadget2-tools/src/Makefile`)
#
