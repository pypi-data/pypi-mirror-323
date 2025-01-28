# ----------------------------------------
#  # MAKEFILE to use UNS
# ----------------------------------------
#  # find libg2c.a library
LIB_G77 := $(shell g77 -print-libgcc-file-name  2> /dev/null)
LIB_G77 := $(shell dirname $(LIB_G77)           2> /dev/null)

# path for NEMO Library, UNS library and G2C
UNS_LIB_PATH := /r5data/home/jcl/works/CVS_WORKS/uns/lib 
LIBS         := -L$(NEMOLIB) -L$(UNS_LIB_PATH) -L$(LIB_G77)
#
# # - - - - - - - - - - - - - - - - - - - -
# # compilation with gfortran compiler
# # - - - - - - - - - - - - - - - - - - - -
GFORTFLAGS = -Wall -O2 -ggdb -Wl,-rpath,$(UNS_LIB_PATH)
#
testlib : testlib.F
	gfortran $(GFORTFLAGS)  -o $@ testlib.F $(LIBS) \
		                -luns -lnemomaing77 -lnemo -lg2c -lstdc++ -lm
# ----------------------------------------
