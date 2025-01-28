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

#ifndef SNAPSHOTGADGET_H
#define SNAPSHOTGADGET_H

#include <string>
#include <assert.h>
#include <fstream>
#include <map>
#include <iostream>
#include <sstream>
#include "snapshotinterface.h"

namespace uns {

typedef struct io_header_1
{
  int      npart[6];
  double   mass[6];
  double   time;
  double   redshift;
  int      flag_sfr;
  int      flag_feedback;
  int      npartTotal[6];
  int      flag_cooling;
  int      num_files;
  double   BoxSize;
  double   Omega0;
  double   OmegaLambda;
  double   HubbleParam;
  char     fill[256- 6*4- 6*8- 2*8- 2*4- 6*4- 2*4 - 4*8];  /* fills to 256 Bytes */
} t_io_header_1;

template <class T> class CG2_T_Header {
public:
  T   time;
  T   redshift;
  T   BoxSize;
  T   Omega0;
  T   OmegaLambda;
  T   HubbleParam;
};

typedef struct s_data_type_header {
  int size_bytes;
  int items;
} t_data_type_header;

enum DATA_TYPE {
  INT   =4,
  FLOAT =4,
  DOUBLE=8,
  CHAR  =1
};

const int NB_DATA_HEADER = 14;
const t_data_type_header dth[NB_DATA_HEADER] = {
  {INT      ,6}, // int      npart[6];
  {DOUBLE   ,6}, // double   mass[6];
  {DOUBLE   ,1}, // double   time;
  {DOUBLE   ,1}, // double   redshift;
  {INT      ,1}, // int      flag_sfr;
  {INT      ,1}, // int      flag_feedback;
  {INT      ,6}, // int      npartTotal[6];
  {INT      ,1}, // int      flag_cooling;
  {INT      ,1}, // int      num_files;
  {DOUBLE   ,1}, // double   BoxSize;
  {DOUBLE   ,1}, // double   Omega0;
  {DOUBLE   ,1}, // double   OmegaLambda;
  {DOUBLE   ,1}, // double   HubbleParam;
  {CHAR     ,96} // char     fill[256- 6*4- 6*8- 2*8- 2*4- 6*4- 2*4 - 4*8];
};


  // ---------------------------------------------------
  // CSnapshotGadgetIn
  // READING class
  // ---------------------------------------------------

  template <class T> class CSnapshotGadgetIn : public CSnapshotInterfaceIn<T> {

  public:
    // READING constrcuctor
    CSnapshotGadgetIn(const std::string, const std::string, const std::string, const bool verb=false);
    ~CSnapshotGadgetIn();
    int nextFrame(uns::UserSelection &);
//    int nextFrame();
    ComponentRangeVector * getSnapshotRange();
    int getNbody() { return getNtotal();}
    // virtual function implemented
    bool getData(const std::string,int *n,T **);
    bool getData(const std::string,       T * );
    bool getData(const std::string,int *n,int   **);
    bool getData(const std::string,       int   * );
    bool getData(const std::string, const std::string ,int *,T **);
    bool getData(const std::string, const std::string ,int *,int   **);
    bool isNewFrame() { return first_loc;}
   int close();

  private:

   std::map<std::string, std::vector<T> > data_vector; // map container to track vector storage


   bool first_loc;
   int open(const std::string);

   int read (uns::UserSelection &);
   int getVersion() const { return version;}
   const uns::ComponentRangeVector getCRV() const { return crv;}
   int   getNtotal() const { return npartTotal;}
     std::string filename,file0;
  std::ifstream in; // input descriptor
  std::ios::pos_type in_start_block;

  int multiplefiles;
  bool lonely_file;

  //data
  T * mass, * pos, * vel, * acc, *pot, * rho,
    * hsml, * age, * metal, * intenerg, * temp, * nh, *sfr;
  int * id;
  // new data for Sergey
  T * zs, * zsmt, * im, * cm, * ssl;
  int czs, czsmt; // constant for zs and zsmt
  int bits; // to store the bits components
  T tframe,redshift;
  int ntotmasses;
  t_io_header_1 header;
  CG2_T_Header<T> t_header;
  int npartTotal, npart, npart_total_local;
  int array_vs_file_size; // array vs file 0:same  1:smaler(half) 2:bigger(double)
  inline void checkFileVsArray(const int bytes_to_read, const int size_data, const int npart) {
    int bytes_array = size_data * npart;
    if (bytes_array == bytes_to_read) {
      array_vs_file_size = 0; // same size
    } else
      if (bytes_array < bytes_to_read) {
        array_vs_file_size = 1; // file data type bigger than array data size
        //assert(2*bytes_array == bytes_to_read);
      } else {
        array_vs_file_size = 2; // file data type smaller than array data size
        //assert(bytes_to_read*2 == bytes_array);
      }
    if (this->verbose) {
      std::cerr << "file_vs_array_size ="<<array_vs_file_size<<" bytes_to_read="<<bytes_to_read<<" bytes_array ="<<bytes_array<<"\n";
    }
  }
  int sizeRealOnFile() {
    int ret;
    switch (array_vs_file_size) {
    case 0 : ret=sizeof(T); break;
    case 1 : ret=sizeof(double); break;
    case 2 : ret=sizeof(float); break;
    default: std::cerr << "Wrong array_vs_file_size ["<<array_vs_file_size<<"]\nabort...";
      std::exit(1);
      break;
    }
    return ret;
  }

  bool isLittleEndian();
  bool swap;
  uns::ComponentRangeVector  crv;
  void storeComponents();

  // member data
  T * getMass()   { return mass; }
  T   getTime()   { return tframe;}
  T   getRedshift() { return redshift;}
  T * getPos()    { return pos; }
  T * getVel()    { return vel; }
  T * getAcc()    { return acc; }
  T * getPot()    { return pot; }
  T * getAge(int & n)   { n=header.npartTotal[4]; return age;}
  T * getMetal(int & n) { n=header.npartTotal[0]+header.npartTotal[4]; return metal;}
  T * getMetalGas(int & n) { n=header.npartTotal[0]; return metal;}
  T * getMetalStars(int & n) { n=header.npartTotal[4]; return metal+header.npartTotal[0];}
  T * getTemp(int & n) { n=header.npartTotal[0]; return temp;}
  T * getNh(int & n) { n=header.npartTotal[0]; return nh;}
  T * getSfr(int & n) { n=header.npartTotal[0]; return sfr;}
  T * getU(int & n) { n=header.npartTotal[0]; return intenerg;}
  T * getRho(int & n) { n=header.npartTotal[0]; return rho;}
  T * getHsml(int & n) { n=header.npartTotal[0]; return hsml;}
  T * getZs(int & n) { n=czs*(header.npartTotal[0]+header.npartTotal[4]); return zs;}
  T * getZsGas(int & n) { n=czs*(header.npartTotal[0]); return zs;}
  T * getZsStars(int & n) { n=czs*(header.npartTotal[4]); return zs+header.npartTotal[0]*czs;}
  T * getZsmt(int & n) { n=czsmt*(header.npartTotal[0]+header.npartTotal[4]); return zsmt;}
  T * getZsmtGas(int & n) { n=czsmt*(header.npartTotal[0]); return zsmt;}
  T * getZsmtStars(int & n) { n=czsmt*(header.npartTotal[4]); return zsmt+header.npartTotal[0]*czsmt;}
  T * getIm(int & n) { n=header.npartTotal[4]; return im;}
  T * getSsl(int & n) { n=header.npartTotal[4]; return ssl;}
  T * getCm(int & n) { n=1*(header.npartTotal[0]+header.npartTotal[4]); return cm;}
  T * getCmGas(int & n) { n=1*(header.npartTotal[0]); return cm;}
  T * getCmStars(int & n) { n=1*(header.npartTotal[4]); return ((cm==NULL)?cm:cm+header.npartTotal[0]*1);}
  bool getHeader(std::string name, T * data);
  //fortran offset record length
  int frecord_offset;
  //control
  bool is_open, is_read;
  bool status;
  int bytes_counter;
  // method
  template <class U> int readCompData(U ** data, const int * index2, const int * npartOffset,
                                      const int dim, const int nsel);
  template <class U> int readGasStarsUnknownArray(U ** data, int * n,const int * compOffset);
  template <class U> int readOneArray(U ** data, const int compid,const int * compOffset);

  template <class U> int readStreamBlock(const std::string blockname, std::vector<U> &data);
  bool readBlockName();
  std::string block_name;
  int readHeader(const int);

  int readData(char * ptr,const size_t size_bytes,const  int items);
  bool guessVersion();
  int version;
  void unitConversion();
  // skip Block
  inline void skipBlock() {
    int len1 = readFRecord();
    in.seekg(len1,std::ios::cur);
    int len2 = readFRecord();
    if (this->verbose) std::cerr << "skipping block name ["<<block_name<<"]\n";
    if (len2==len1) ; // remove warning....
    assert(len1==len2 && in.good());
    if (block_name == "AGE" || block_name == "Z" ) {
      //std::cerr << "len1 = " << len1 << "\nlen2 = " << len2 << "\n";
    }
  }
  inline void skipData(int len) {
    bytes_counter += (len);
    in.seekg(len,std::ios::cur);
    assert(in.good());
  }
  // swap bytes
  inline void swapBytes(void * x,const int size) {
    char * p=(char *) x;
    for (int i=0;i<size/2;i++) {
     int t=*(p+i); *(p+i)=*(p+size-i-1); *(p+size-i-1)=t;
    }
  }
  // read fortran record
  inline int readFRecord() {
    int len; in.read((char *) &len,sizeof(int));
    // We SWAP data
    if (swap) { // swapping requested
      swapBytes(&len,sizeof(int));
    }
    assert(in.good());
    return len;
  }

  }; // end of class CSnapshotGadgetIn

  //
  //
  //

  // ---------------------------------------------------
  // CSnapshotGadgetout
  // WRITING class
  // ---------------------------------------------------

  template <class T> class CSnapshotGadgetOut : public CSnapshotInterfaceOut<T> {

  public:
    // WRITING constructor
    CSnapshotGadgetOut(const std::string, const std::string, const bool);
    ~CSnapshotGadgetOut();
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

  private:
    //data
    T * mass[6], * pos[6], *acc[6], * vel[6], * pot[6], * rho, * hsml,
       * age, * metal[6], * intenerg, * temp, * nh, * sfr;
    int * id[6];
    int ntot_withmasses;
    std::ofstream out;
    // Map to associate EXTRA tags with vectors
    std::map<std::string, std::vector <T>  > s_mapStringVector;
    // Map to associate the strings with the bool values
    std::map<std::string, bool> ptrIsAlloc[6];
    t_io_header_1 header;
    int bits, npartTotal;
    int bytes_counter;
    int version;
    int setHeader(t_io_header_1 *);
    int writeData(char * ptr,const size_t size_bytes,const int items);
    int writeDataValue(T value, const size_t size_bytes,const int items);
    void saveFile();
    void setupHeader(bool check=false);
    int writeHeader();
    int write();
    bool writeBlockName(std::string, int);
    inline void writeFRecord(const int len) {
      out.write((char *) &len,sizeof(int));
      assert(out.good());
    }
    // array by keys
    int setMass(std::string, const int _n, T * _mass, const bool addr);
    int setPos (std::string, const int _n, T * _pos , const bool addr);
    int setVel (std::string, const int _n, T * _vel , const bool addr);
    int setId  (std::string, const int _n, int   * _id  , const bool addr);
    int setPot (std::string, const int _n, T * _pot , const bool addr);
    int setAcc (std::string, const int _n, T * _acc , const bool addr);

    int setRho (const int _n, T * _rho , const bool addr);
    int setHsml(const int _n, T * _hsml, const bool addr);
    int setU   (const int _n, T * _U   , const bool addr);
    int setAge (const int _n, T * _age   , const bool addr);
    int setTemp(const int _n, T * _temp, const bool addr);
    int setNh  (const int _n, T * _nh, const bool addr);
    int setSfr (const int _n, T * _sfr, const bool addr);
    int setMetalGas(const int _n, T * _mg   , const bool addr);
    int setMetalStars(const int _n, T * _ms   , const bool addr);
    // extra TAGS
    int setExtra(std::string tag, const int _n, T * _data, const bool addr);
    int setHeader(std::string tag,  T  _data);

  }; // end of class CSnapshotGadgetOut
} // namespace

#endif
