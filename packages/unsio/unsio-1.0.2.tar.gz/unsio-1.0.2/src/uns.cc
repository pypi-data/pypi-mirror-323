// ============================================================================
// Copyright Jean-Charles LAMBERT - 2008-2025
//           Centre de donneeS Astrophysiques de Marseille (CeSAM)
// e-mail:   Jean-Charles.Lambert@lam.fr
// address:  Aix Marseille Universite, CNRS, LAM
//           Laboratoire d'Astrophysique de Marseille
//           Pole de l'Etoile, site de Chateau-Gombert
//           38, rue Frederic Joliot-Curie
//           13388 Marseille cedex 13 France
//           CNRS UMR 7326
// ============================================================================

#include "uns.h"
#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <assert.h>
#include "snapshotinterface.h"
#include "snapshotgadget.h"
#include "snapshotgadgeth5.h"
#include "snapshotramses.h"
#include "snapshotnemo.h"
#include "snapshotsim.h"
#include "snapshotlist.h"
#include "userselection.h"
#include "ctools.h"

#define DEBUG 0
#include "unsdebug.h"

namespace uns {
// static variable to store DATA string
template <class T> std::map<std::string, StringData> CunsOut2<T>::s_mapStringValues;
template <class T> std::map<std::string, int> CunsIn2<T>::s_mapCompInt;

// ----------------------------------------------------------------------------
// READING OPERATIONS
template <class T>  CunsIn2<T>::CunsIn2(const std::string _name ,const std::string _comp ,const std::string _time, const bool verb)
{
  init(_name,_comp,_time,verb);
}
// ----------------------------------------------------------------------------
// constructor for READING operations
template <class T>  CunsIn2<T>::CunsIn2(const char * _name ,const char * _comp, const char * _time,
               const bool verb)
{
  init(_name,_comp,_time,verb);
}
// ----------------------------------------------------------------------------
//
template <class T>  void CunsIn2<T>::init(const std::string _name ,const std::string _comp ,const std::string _time, const bool verb )
{
  if (verb) {
    std::cerr << "CunsIn2::CunsIn2 -- UNSIO version = "<<uns::getVersion()<< "\n";
  }

  valid = false;
  simname  = tools::Ctools::fixFortran(_name.c_str(),false);
  sel_comp = tools::Ctools::fixFortran(_comp.c_str(),false);
  sel_time = tools::Ctools::fixFortran(_time.c_str(),false);

  initMap();

  // to lower
  //simname  = tools::Ctools::tolower(simname);
  //sel_comp = tools::Ctools::tolower(sel_comp);
  //sel_time = tools::Ctools::tolower(sel_time);

  verbose=verb;
  snapshot = NULL;
  PRINT("name    ["<< simname  <<"]\n");
  PRINT("sel_comp["<< sel_comp <<"]\n");
  PRINT("sel_time["<< sel_time <<"]\n");
  CunsOut2<T>::initializeStringMap(verbose);
  if (simname == "-") { // we assume here that "-"
    tryNemo();          // is standard input and a NEMO stream...
  } else {
    if (tools::Ctools::isFileExist(simname)) { // file exist
      if ( tools::Ctools::isDirectory(simname)) {
        PRINT("try RAMSES 1st\n");
        tryRamses();             // try ramses
        if (!valid) {
          trySimDB();              // try DataBase
        }
      } else {
        // ! ) { // not a directory
        PRINT("try GADGET\n");
        tryGadget();               // try gadget
        if (!valid) {
          PRINT("try RAMSES\n");
          tryRamses();             // try ramses
        }
        if (!valid) {              // gadget failed
          PRINT("try NEMO\n");
          tryNemo();               // try nemo
        }
        if (!valid) {
          PRINT("try HDF5\n");
          tryGadgetH5();           // try gadgetHDF5
        }
        if (!valid) {              // nemo
          PRINT("try LIST\n");
          trySnapList();           // try snapshotlist
        }
        if (!valid) {
          PRINT("try DATABASE\n");
          trySimDB();              // try DataBase
        }
      }
    }
    else {                       // file does not exist
      PRINT("try GADGET 2nd\n");
      tryGadget();               // try gadget parallel output
      if (!valid) {
        PRINT("try DATABASE2\n");
        trySimDB();              // try DataBase
      }
    }
  }
  if (valid && verb) {
    std::cerr << "File      : " << snapshot->getFileName() << "\n";
    std::cerr << "Interface : " << snapshot->getInterfaceType() << "\n";
  }
  if (!valid){
    std::cerr << "\nFile ["<< snapshot->getFileName() <<"], unknown UNS file format, aborting.....\n\n";
  }
}
// ----------------------------------------------------------------------------
// destructor for READING operations
template <class T>  CunsIn2<T>::~CunsIn2()
{
  if (snapshot) delete snapshot;
}
// ----------------------------------------------------------------------------
// tryGadget binary 1 and 2
template <class T> void CunsIn2<T>::tryGadget()
{
  PRINT("tryGadget("<<simname<<")\n");
  snapshot = new CSnapshotGadgetIn<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
}
// ----------------------------------------------------------------------------
// tryGadget HDF5
template <class T> void CunsIn2<T>::tryGadgetH5()
{
  PRINT("tryGadgetH5("<<simname<<")\n");
  snapshot = new CSnapshotGadgetH5In<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
}
// ----------------------------------------------------------------------------
// tryRamses
template <class T> void CunsIn2<T>::tryRamses()
{
  PRINT("tryRamses("<<simname<<")\n");
  snapshot = new CSnapshotRamsesIn<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
}
// ----------------------------------------------------------------------------
// tryNemo
template <class T> void CunsIn2<T>::tryNemo()
{
  PRINT("tryNemo("<<simname<<")\n");
  snapshot = new CSnapshotNemoIn<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
}
// ----------------------------------------------------------------------------
// trySim
template <class T> void CunsIn2<T>::trySimDB()
{
#ifndef NOSQLITE3
  snapshot = new CSnapshotSimIn<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
  if (valid && verbose) {
    std::cerr << "CunsIn2::trySimDB() It's recorded to sqlite3 database...\n";
  }
#else
  valid = false;
#endif

}
// ----------------------------------------------------------------------------
// trySnapList
template <class T> void CunsIn2<T>::trySnapList()
{
  snapshot = new CSnapshotList<T>(simname, sel_comp, sel_time, verbose);
  valid = snapshot->isValidData();
}
// ----------------------------------------------------------------------------
// nextFrame
template <class T> int CunsIn2<T>::nextFrame(const char *  _bits) {
  std::string bits(_bits);
  int ok=snapshot->nextFrame(bits);
  return ok;
}
// ----------------------------------------------------------------------------
// getData
template <class T> bool CunsIn2<T>::getData(const std::string  comp,const std::string  prop,
                     unsigned int * size,T ** farray) {
  T * data=NULL;
  int nbody=0;
  *size=0;
  bool ok=snapshot->getData(comp,prop,&nbody,&data);
  if (ok) {
    int dim=1;
    if (prop=="pos" || prop == "vel" || prop == "acc") dim=3;
    *farray = data;
    *size=nbody*dim;
  }
  return ok;
}
// ----------------------------------------------------------------------------
// getData
template <class T> bool CunsIn2<T>::getData(const std::string  prop,
                     unsigned int * size,T ** farray) {
  T * data=NULL;
  int nbody=0;
  *size=0;
  bool ok=snapshot->getData(prop,&nbody,&data);
  if (ok) {
    int dim=1;
    if (prop=="pos" || prop == "vel" || prop == "acc") dim=3;
    *farray = data;
    *size=nbody*dim;
  }
  return ok;
}
// ----------------------------------------------------------------------------
// getData
template <class T> bool CunsIn2<T>::getData(const std::string  prop,T * fvalue) {
  bool ok=snapshot->getData(prop,fvalue);
  return ok;
}
// ----------------------------------------------------------------------------
// getData
// int
template <class T> bool CunsIn2<T>::getData(const std::string  comp,const std::string  prop,
                     unsigned int * size,int ** iarray) {
  int * data=NULL;
  int nbody=0;
  *size=0;
  bool ok=snapshot->getData(comp,prop,&nbody,&data);
  if (ok) {
    int dim=1;
    *iarray = data;
    *size=nbody*dim;
  }
  return ok;
}
// ----------------------------------------------------------------------------
// getData
// int
template <class T> bool CunsIn2<T>::getData(const std::string  prop,
                     unsigned int * size,int ** iarray) {
  int * data=NULL;
  int nbody=0;
  *size=0;
  bool ok=snapshot->getData(prop,&nbody,&data);
  if (ok) {
    int dim=1;
    *iarray = data;
    *size=nbody*dim;
  }
  return ok;
}
// ----------------------------------------------------------------------------
// getData
// int
template <class T> bool CunsIn2<T>::getData(const std::string  prop,int * ivalue) {
  bool ok=snapshot->getData(prop,ivalue);
  return ok;
}



// ----------------------------------------------------------------------------
// WRITING OPERATIONS
//  ---------------------------------------------------------------------------

//  ---------------------------------------------------------------------------
// constructor
template <class T> CunsOut2<T>::CunsOut2(const std::string _name, const std::string _type, const bool _verb )
{
  simname  = tools::Ctools::fixFortran(_name.c_str(),false);
  simtype  = tools::Ctools::fixFortran(_type.c_str(),false);
  verbose = _verb;
  snapshot= NULL;
  if (verbose) {
    std::cerr << "CunsOut2<T>::CunsOut2 -- UNSIO version = "<<uns::getVersion()<< "\n";
  }
  initializeStringMap(verbose);
  simtype = tools::Ctools::tolower(simtype);
  if (simtype == "gadget2" || simtype == "gadget1") {
    snapshot = new CSnapshotGadgetOut<T>(simname,simtype,verbose);
  } else {
    if (simtype == "nemo") {
      snapshot = new CSnapshotNemoOut<T>(simname,simtype,verbose);
    }
    else {
      if (simtype == "gadget3") {
        snapshot = new CSnapshotGadgetH5Out<T>(simname,simtype,verbose);
      }
      else {
        std::cerr << "Unkonwn UNS output file format => ["<<simtype<<"]"
                << " aborting program...... \n\n";
        std::exit(1);
      }
    }
  }
}
// ----------------------------------------------------------------------------
// destructor for READING operations
template <class T> CunsOut2<T>::~CunsOut2()
{
  if (snapshot) delete snapshot;
}
// ----------------------------------------------------------------------------
// setData comp prop farray
template <class T> int CunsOut2<T>::setData(const std::string  comp,const std::string  prop,
            unsigned int  size,T * farray, const bool _addr) {
  int status = snapshot->setData(comp,prop,size,farray,_addr);
  return status;
}
// ----------------------------------------------------------------------------
// setData prop farray
template <class T> int CunsOut2<T>::setData(const std::string  prop,
            unsigned int  size,T * farray, const bool _addr) {
  int status = snapshot->setData(prop,size,farray,_addr);
  return status;
}
// ----------------------------------------------------------------------------
// setData prop fvalue
template <class T> int CunsOut2<T>::setData(const std::string  prop,T fvalue) {
  int status = snapshot->setData(prop,fvalue);
  return status;
}
// ----------------------------------------------------------------------------
// setData comp prop iarray
template <class T> int CunsOut2<T>::setData(const std::string  comp,const std::string  prop,
                   unsigned int  size,int * iarray, const bool _addr) {
  int status = snapshot->setData(comp,prop,size,iarray,_addr);
  return status;
}
// ----------------------------------------------------------------------------
// setData prop iarray
template <class T> int CunsOut2<T>::setData(const std::string  prop,
                     unsigned int  size,int * iarray, const bool _addr) {
  int status = snapshot->setData(prop,size,iarray,_addr);
  return status;
}
// ----------------------------------------------------------------------------
// setData prop ivalue
template <class T> int CunsOut2<T>::setData(const std::string  prop,int ivalue) {
  int status = snapshot->setData(prop,ivalue);
  return status;
}
// ----------------------------------------------------------------------------
// setData
template <class T> int CunsOut2<T>::save()
{
  return snapshot->save();
}
// ----------------------------------------------------------------------------
// initializeStringMap
template <class T> void  CunsOut2<T>::initializeStringMap(const bool verbose)
{

  CunsOut2<T>::s_mapStringValues["time"       ] = uns::Time;
  CunsOut2<T>::s_mapStringValues["redshift"   ] = uns::Redshift;
  CunsOut2<T>::s_mapStringValues["pos"        ] = uns::Pos;
  CunsOut2<T>::s_mapStringValues["vel"        ] = uns::Vel;
  CunsOut2<T>::s_mapStringValues["mass"       ] = uns::Mass;
  CunsOut2<T>::s_mapStringValues["id"         ] = uns::Id;
  CunsOut2<T>::s_mapStringValues["rho"        ] = uns::Rho;
  CunsOut2<T>::s_mapStringValues["hsml"       ] = uns::Hsml;
  CunsOut2<T>::s_mapStringValues["u"          ] = uns::U;
  CunsOut2<T>::s_mapStringValues["aux"        ] = uns::Aux;
  CunsOut2<T>::s_mapStringValues["acc"        ] = uns::Acc;
  CunsOut2<T>::s_mapStringValues["pot"        ] = uns::Pot;
  CunsOut2<T>::s_mapStringValues["eps"        ] = uns::Eps;
  CunsOut2<T>::s_mapStringValues["keys"       ] = uns::Keys;
  CunsOut2<T>::s_mapStringValues["age"        ] = uns::Age;
  CunsOut2<T>::s_mapStringValues["temp"       ] = uns::Temp;
  CunsOut2<T>::s_mapStringValues["ne"         ] = uns::Temp;
  CunsOut2<T>::s_mapStringValues["nh"         ] = uns::Nh;
  CunsOut2<T>::s_mapStringValues["sfr"        ] = uns::Sfr;
  CunsOut2<T>::s_mapStringValues["metal"      ] = uns::Metal;
  CunsOut2<T>::s_mapStringValues["gas_metal"  ] = uns::GasMetal;
  CunsOut2<T>::s_mapStringValues["stars_metal"] = uns::StarsMetal;
  CunsOut2<T>::s_mapStringValues["nsel"       ] = uns::Nsel;
  CunsOut2<T>::s_mapStringValues["nbody"      ] = uns::Nbody;
  CunsOut2<T>::s_mapStringValues["ngas"       ] = uns::Ngas;
  CunsOut2<T>::s_mapStringValues["nhalo"      ] = uns::Nhalo;
  CunsOut2<T>::s_mapStringValues["ndisk"      ] = uns::Ndisk;
  CunsOut2<T>::s_mapStringValues["nbulge"     ] = uns::Nbulge;
  CunsOut2<T>::s_mapStringValues["nstars"     ] = uns::Nstars;
  CunsOut2<T>::s_mapStringValues["nbndry"     ] = uns::Nbndry;
  CunsOut2<T>::s_mapStringValues["gas"        ] = uns::Gas;
  CunsOut2<T>::s_mapStringValues["halo"       ] = uns::Halo;
  CunsOut2<T>::s_mapStringValues["dm"         ] = uns::Halo;
  CunsOut2<T>::s_mapStringValues["ndm"        ] = uns::Halo;
  CunsOut2<T>::s_mapStringValues["bulge"      ] = uns::Bulge;
  CunsOut2<T>::s_mapStringValues["disk"       ] = uns::Disk;
  CunsOut2<T>::s_mapStringValues["stars"      ] = uns::Stars;
  CunsOut2<T>::s_mapStringValues["bndry"      ] = uns::Bndry;
  CunsOut2<T>::s_mapStringValues["all"        ] = uns::All;
  CunsOut2<T>::s_mapStringValues["gas_mpv"    ] = uns::GasMPV;
  CunsOut2<T>::s_mapStringValues["halo_mpv"   ] = uns::HaloMPV;
  CunsOut2<T>::s_mapStringValues["bulge_mpv"  ] = uns::BulgeMPV;
  CunsOut2<T>::s_mapStringValues["disk_mpv"   ] = uns::DiskMPV;
  CunsOut2<T>::s_mapStringValues["stars_mpv"  ] = uns::StarsMPV;
  CunsOut2<T>::s_mapStringValues["bndry_mpv"  ] = uns::BndryMPV;
  CunsOut2<T>::s_mapStringValues["zs"         ] = uns::Zs;
  CunsOut2<T>::s_mapStringValues["zsmt"       ] = uns::ZSMT;
  CunsOut2<T>::s_mapStringValues["im"         ] = uns::Im;
  CunsOut2<T>::s_mapStringValues["ssl"        ] = uns::Ssl;
  CunsOut2<T>::s_mapStringValues["cm"         ] = uns::Cm;
  CunsOut2<T>::s_mapStringValues["czs"        ] = uns::Czs;
  CunsOut2<T>::s_mapStringValues["czsmt"      ] = uns::Czsmt;
  //
  CunsOut2<T>::s_mapStringValues["header"     ] = uns::Header;
  // EXTRA
  CunsOut2<T>::s_mapStringValues["EXTRA"      ] = uns::Extra;
  // HYDRO
  CunsOut2<T>::s_mapStringValues["hydro"      ] = uns::Hydro;
  CunsOut2<T>::s_mapStringValues["nvarh"      ] = uns::Nvarh;

  if (verbose) {
    std::cout << "CunsOut2<T>::initializeStringMap s_mapStringValues contains "
              << CunsOut2<T>::s_mapStringValues.size() << " entries." << std::endl;
  }
}

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CunsIn2<float>;
template class CunsIn2<float>;

//extern template class CunsIn2<double>;
template class CunsIn2<double>;

// C++11
//extern template class CunsOut2<float>;
template class CunsOut2<float>;

//extern template class CunsOut2<double>;
template class CunsOut2<double>;

}
// ----------------------------------------------------------------------------
// End of file
// ----------------------------------------------------------------------------
