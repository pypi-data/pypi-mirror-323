// ============================================================================
// Copyright Jean-Charles LAMBERT - 2008-2025
//           Centre de donneeS Astrophysiques de Marseille (CeSAM)
// e-mail:   Jean-Charles.Lambert@lam.fr
// address:  Dynamique des galaxies
//           Laboratoire d'Astrophysique de Marseille
//           Pole de l'Etoile, site de Chateau-Gombert
//           38, rue Frederic Joliot-Curie
//           13388 Marseille cedex 13 France
//           CNRS U.M.R 6110
// ============================================================================

/**
  @author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */
#ifndef SNAPSHOTRAMSES_H
#define SNAPSHOTRAMSES_H

#include "snapshotinterface.h"
//#include "camr.h"
//#include "cpart.h"

namespace ramses {
class CAmr;
class CPart;
class CGrav;
template <class T> class T_Header;
}
namespace uns {

template <class T> class CParticles {
public:
  CParticles() {    
    ntot  =0; // SWIG forbid multiple variable affectation
    ngas  =0; // like ntot=ngas=ndm=0 !!!!!!!!!
    ndm   =0; // it was a bug in py_unsio wrapper for ramses files,
    nstars=0; // really really damn crazy !!!!!
    nvarh =0; // #hydro variables

    load_bits=0;
  }
  static const unsigned int MAX_HYDRO=20;
  std::vector <T> pos,vel,mass,hsml,rho,acc,u,phi,temp,age,metal;
  std::vector <T> hydro[MAX_HYDRO]; // extra hydro from var[nvarh] array
  std::vector <int> indexes,id;
  int ntot, ngas, ndm, nstars, nvarh;
  unsigned int load_bits;
};



template <class T> class CSnapshotRamsesIn: public CSnapshotInterfaceIn<T> {

public:
  CSnapshotRamsesIn(const std::string, const std::string, const std::string, const bool verb=false);

  ~CSnapshotRamsesIn();
  // pure virtual function implemented
  ComponentRangeVector * getSnapshotRange();
  int nextFrame(uns::UserSelection &);
  bool getData(const std::string,int *n,T **);
  bool getData(const std::string,       T * );
  bool getData(const std::string,int *n,int   **);
  bool getData(const std::string,       int   * );
  bool getData(const std::string, const std::string ,int *,T **);
  bool getData(const std::string, const std::string ,int *,int   **);
 int close();

private:
 ramses::CAmr * amr;
 ramses::CPart * part;
 ramses::CGrav * grav;
 CParticles<T> * particles;
 bool first_loc;
 ramses::T_Header<T> * t_header;

 int reorderParticles(uns::UserSelection & );
 bool getHeader(std::string name, T * data);
};
}
#endif // SNAPSHOTRAMSES_H

