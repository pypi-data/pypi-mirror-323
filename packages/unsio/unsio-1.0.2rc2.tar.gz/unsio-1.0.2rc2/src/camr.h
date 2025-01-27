// ============================================================================
// Copyright Jean-Charles LAMBERT - 2008-2025
//           Centre de donneeS Astrophysiques de Marseille (CeSAM)              
// e-mail:   Jean-Charles.Lambert@lam.fr                                      
// address:  Aix Marseille Universite, CNRS, LAM 
//           Laboratoire d'Astrophysique de Marseille                          
//           Pole de l'Etoile, site de Chateau-Gombert                         
//           38, rue Frederic Joliot-Curie                                     
//           13388 Marseille cedex 13 France                                   
//           CNRS U.M.R 7326                                                   
// ============================================================================

/* 
	@author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */
#ifndef CAMR_H
#define CAMR_H

#include <string>
#include <assert.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <cstdlib>
#include "cfortio.h"
#include "snapshotramses.h"

namespace uns {
template <class T> class CParticles;
}
namespace ramses {

typedef struct  {
  double time;
  double boxlen, omega_m, omega_l, omega_k, omega_b, h0, aexp_ini, boxlen_ini;
  double aexp,hexp,aexp_old,epot_tot_int,epot_tot_old;
} Header;

template <class T> class T_Header {
public:
  T time;
  T boxlen, omega_m, omega_l, omega_k, omega_b, h0, aexp_ini, boxlen_ini;
  T aexp,hexp,aexp_old,epot_tot_int,epot_tot_old;
};

class CAmr  {
public:
    CAmr(const std::string,const bool _v=true);
    
    ~CAmr();
    void setBoundary(double x[8]) {
      xmin=x[0];
      xmax=x[1];
      ymin=x[2];
      ymax=x[3];
      zmin=x[4];
      zmax=x[5];
      
      if (x[7]==0.) {
        lmax= nlevelmax;
      } else {
        lmax = (int) x[7];
      } 

      lmin = std::min((int) x[6],lmax-1);                   
      if (verbose) {
        std::cerr << "min = "<< (int) x[6] << " lmax="<<lmax<<" lmin="<<lmin<<"\n";
      }
    }
    bool isValid();
    template <class T> int loadData(uns::CParticles<T> * particles,
                 const unsigned int req_bits);
    int getNbody()    { return nbody;}
    Header * getHeader() { return &header; }

private:
    // some variables
    
    bool verbose,valid, is_gravity;
    std::string infile,testhydrofile, indir;
    int select,nselect;
    int nbody;
    std::string s_run_index,ordering;
  
    float xmin,xmax,ymin,ymax,zmin,zmax;
    int lmin,lmax;
    CFortIO  amr, hydro, grav;
    int readHeader();

    bool checkGravity(const int ngrida,const int ilevel,const int icpu, int * gridfile);
    // amr header variables
    static const double XH, mH, kB;
    int ncpu, ndim, nx, ny ,nz, nlevelmax, ngridmax, nboundary, ngrid_current;
    int twotondim;
    double xbound[3];
    Header header;

    // hydro
    int nvarh;
    double scale_nH;
    // gravity (phi,acc)
    int nvarg;

};
} // end of namespace
#endif // CAMR_H
