// ============================================================================
// Copyright Jean-Charles LAMBERT - 2008-2025
//           Centre de donneeS Astrophysiques de Marseille (CeSAM)         
// e-mail:   Jean-Charles.Lambert@lam.fr                                      
// address:  Aix Marseille Universite, CNRS, LAM 
//           Laboratoire d'Astrophysique de Marseille                          
//           Pôle de l'Etoile, site de Château-Gombert                         
//           38, rue Frédéric Joliot-Curie                                     
//           13388 Marseille cedex 13 France                                   
//           CNRS UMR 7326                                       
// ============================================================================

/**
	@author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */
#ifndef UNSSNAPSHOTNEMO_H
#define UNSSNAPSHOTNEMO_H
#include "snapshotinterface.h"
#include <map>

extern "C" {
  int io_nemo(const char * , const char *, ...);
#include <stdinc.h>
#include <filestruct.h>
#include <nemo.h>
#include <snapshot/snapshot.h>
}

namespace uns {

  template <class T> class CSnapshotNemoIn : public CSnapshotInterfaceIn<T> {
  
  public:
    CSnapshotNemoIn(const std::string, const std::string, const std::string,
		  const bool verb=false);
    ~CSnapshotNemoIn();
    int nextFrame(uns::UserSelection &);
    int close();
    ComponentRangeVector * getSnapshotRange();
    // virtual function implemented
    bool getData(const std::string,int *n,T **);
    bool getData(const std::string,       T * );
    bool getData(const std::string,int *n,int   **);
    bool getData(const std::string,       int   * );
    bool getData(const std::string, const std::string ,int *,T **);
    bool getData(const std::string, const std::string ,int *,int   **);
   
private:
    int full_nbody;
    int * nemobits , * ionbody, *iokeys;
    int * keys;
    T * iotime, *iopos, *iovel, *iomass, *iorho, *ioaux, *ioacc, *iopot, *ioeps;
    T * pos, *vel, *mass, * rho, *acc, *aux, *pot, *eps;
    bool first_stream;
    int status_ionemo;
    int last_nbody,last_nemobits;
    void checkBits(std::string,const int);
    bool isValidNemo();
    T *  getPos()  { //checkBits("pos",PosBit);
                         return pos ;}
    T *  getVel()  { //checkBits("vel",VelBit);
                         return vel ;}
    T *  getMass() { //checkBits("mass",MassBit);
                         return mass;}
    T *  getEps()  { return eps;}
    T *  getRho()  { return rho ;}
    T *  getAux()  { return aux ;}
    T *  getAcc()  { return acc ;}
    T *  getPot()  { return pot ;}
    int   *  getKeys() { return keys;}
    T    getTime() { return *iotime; }
    int      getNbody(){ return *ionbody;}

    std::string realString() { // return a string with the real format
      std::string io_nemo_select;
      if (sizeof(T)==sizeof(double)) {
        io_nemo_select="double";
      } else {
        if (sizeof(T)==sizeof(float)) {
          io_nemo_select="float";
        } else {
          assert(0);
        }
      }
      return io_nemo_select;
    }
};
  
  template <class T> class CSnapshotNemoOut : public CSnapshotInterfaceOut<T> {

  public:
    // WRITING constructor
    CSnapshotNemoOut(const std::string, const std::string, const bool);
    ~CSnapshotNemoOut();
    int setHeader(void * );
    int setNbody(const int _n);
    int setData(std::string, T);
    int setData(std::string, const int , T *,const bool _addr=false);
    // array by double keys
    int setData(std::string, std::string, const int , T *,const bool _addr=false);
    int setData(std::string, std::string, const int , int   *,const bool _addr=false);
    
    int setData(std::string, const int , int *,const bool _addr=false);
    int setData(std::string, const int , 
        T *, T *, T *, const bool _addr=false);
    int save();
    std::vector<double> moveToCom();
    int close();
  private:
    // Map to associate the strings with the bool values
    std::map<std::string, bool> ptrIsAlloc;
    T * mass, * pos, * vel, * aux, * acc, * pot, * rho, * eps;
    T time;
    int * keys;
    int nbody;
    int bits;
    bool is_saved, is_closed;

    std::string realString() { // return a string with the real format
      std::string io_nemo_select;
      if (sizeof(T)==sizeof(double)) {
        io_nemo_select="double";
      } else {
        if (sizeof(T)==sizeof(float)) {
          io_nemo_select="float";
        } else {
          assert(0);
        }
      }
      return io_nemo_select;
    }
    // array
    int setArray(const int _n, const int _d, T * src, T ** dest, const char * name, const int tbits, const bool addr);
    int setArray(const int _n, const int _d, int   * src, int   ** dest, const char * name, const int tbits, const bool addr);
};
}
#endif
