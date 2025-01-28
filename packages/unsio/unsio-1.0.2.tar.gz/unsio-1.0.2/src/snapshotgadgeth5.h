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

/**
        @author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */

#ifndef SNAPSHOTGADGETH5_H
#define SNAPSHOTGADGETH5_H

#include <string>
#include <assert.h>
#include <map>
#include <iostream>
#include <sstream>
#include "snapshotinterface.h"
#include <H5Cpp.h>
#ifndef H5_NO_NAMESPACE
using namespace H5;
#endif
namespace uns {
// HDF5 gadget header
typedef struct h5_header {
  std::vector<double> MassTable; //[6]; "
  double   Time;
  double   Redshift;
  int      Flag_DoublePrecision;
  int      Flag_IC_Info;
  int      Flag_Metals;
  int      Flag_Cooling;
  int      Flag_Sfr;
  int      Flag_StellarAge;
  int      flag_feedback;
  std::vector<int> NumPart_Total;//[6];
  std::vector<int> NumPart_Total_HighWord;//[6];
  std::vector<int> NumPart_ThisFile;//[6];
  int      NumFilesPerSnapshot;
  double   BoxSize;
  double   Omega0;
  double   OmegaLambda;
  double   HubbleParam;
} t_h5_header;

//
// class GH5
//
template <class T> class GH5 {
public:
  GH5(const std::string _f_name,unsigned int mode, const bool verb=false);
 ~GH5();
  t_h5_header getHeader() { return header; }
  int close() {
    int status=0;
    if (myfile) {
      header_group.close(); // ! necessary to close this opened group
      myfile->close();
      //delete myfile;
      //myfile=NULL;
      status=1;
    }
    return status;
  }

  // reading
  template <class U> std::vector<U> getDataset(std::string dset_name, U );
  template <class U> std::vector<U> getAttribute(std::string attr_name);
  int getNpartTotal() { return npart_total; }
  // writing
  template <class U>
  bool setDataset(std::string dset_name, U * data, const unsigned int n, const unsigned int second_dim);
  template <class U> bool setAttribute(std::string attr_name, U *, const int );
private:
  std::map<std::string, bool> histo_group;

  bool verbose;
  void readHeaderAttributes();
  int npart_total;
  template <class U>
  DataType guessType(U);
  std::string f_name;
  H5File * myfile;
  Group header_group;
  t_h5_header header;

};

// ---------------------------------------------------
// class CSnapshotGadgetH5In
// READING class
// ---------------------------------------------------
template <class T> class CSnapshotGadgetH5In : public CSnapshotInterfaceIn<T> {

public:
  CSnapshotGadgetH5In(const std::string, const std::string, const std::string, const bool verb=false);
  ~CSnapshotGadgetH5In();

  int nextFrame(uns::UserSelection &);
  ComponentRangeVector * getSnapshotRange();

  // virtual function implemented
  //template <class U> std::vector<U> getData(const std::string, const std::string);
  template <class U> void getData(const std::string, const std::string);
  bool getData(const std::string,int *n,T **);
  bool getData(const std::string,       T * );
  bool getData(const std::string,int *n,int   **);
  bool getData(const std::string,       int   * );
  bool getData(const std::string, const std::string ,int *,T **);
  bool getData(const std::string, const std::string ,int *,int   **);

  bool isNewFrame() { return first_loc;}
 int close();

private:
 bool first_loc;

 unsigned int comp_bits;
 std::vector <T> pos,vel,mass, acc,pot, hsml,rho,temp,nh,sfr,
                 age,s_metal, g_metal,uenerg;
 std::vector <int> indexes,id;

 // HDF5 gadget object
 GH5<T> * myH5;
 void read(uns::UserSelection user_select);
 // methods
 T   getTime()   { return myH5->getHeader().Time;}
 template <class U>
 bool loadCommonDataset(std::string tag, std::vector<U> &data, const int dim);
 template <class U>
 bool loadDataset(std::string tag, std::vector<U> &data);
 void storeComponents();

}; // End of class snapshotgadgetH5In

// ---------------------------------------------------
// class CSnapshotGadgetH5Out
// WRITING class
// ---------------------------------------------------
template <class T> class CSnapshotGadgetH5Out : public CSnapshotInterfaceOut<T> {

public:
  CSnapshotGadgetH5Out(const std::string, const std::string, const bool);
  ~CSnapshotGadgetH5Out();
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

private:
  // methods
  template <class U>
  bool saveCommonDataset(std::string name,std::string dataset,  const int n ,U * data, const unsigned int);
  template <class U>
  bool checkMasses(const int n ,U * data, const int comp_id);
  // HDF5 gadget object
  GH5<T> * myH5;
  t_h5_header header;

}; // End of class snapshotgadgetH5Out

} // namespace
#endif // SNAPSHOTGADGETH5_H
