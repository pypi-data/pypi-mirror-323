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

/*
    @author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */


#include <sstream>
#include <cstdlib>
#include "snapshotgadget.h"
#include "uns.h"
#include "ctools.h"
#define DEBUG 0
#include "unsdebug.h"


namespace uns {

// ----------------------------------------------------------------------------
// READING constructor
template <class T>
CSnapshotGadgetIn<T>::CSnapshotGadgetIn(const std::string _name,
                                  const std::string _comp,
                                  const std::string _time,
                  const bool verb)
   :CSnapshotInterfaceIn<T>(_name, _comp, _time, verb)
{
  filename = _name;
  //this->valid=false;
  first_loc = true;
  status=false;
  is_open=false;
  is_read=false;
  swap   = false;

  mass   = NULL;
  pos    = NULL;
  vel    = NULL;
  acc    = NULL;
  pot    = NULL;
  id     = NULL;
  age    = NULL;
  metal  = NULL;
  intenerg=NULL;
  temp   = NULL;
  nh     = NULL;
  sfr    = NULL;
  rho    = NULL;
  hsml   = NULL;
  zs     = NULL;
  zsmt   = NULL;
  im     = NULL;
  ssl    = NULL;
  cm     = NULL;
  bits   = 0;
  this->load_bits = 0;
  tframe = 0.;
  redshift=0.;
  frecord_offset = 4;
  czs = 0;
  czsmt= 0;
  bytes_counter = 0;
  multiplefiles = 0;
  lonely_file   = true;
  ntotmasses = 0;
  this->verbose = verb;

  int fail = open(filename);
  if (!fail) {
    this->valid=true;
    std::stringstream stm("");
    stm << getVersion();
    this->interface_type = "Gadget" + stm.str();
    this->interface_index=1;
    this->file_structure = "component";
  }

}
// ----------------------------------------------------------------------------
// destructor
template <class T>
CSnapshotGadgetIn<T>::~CSnapshotGadgetIn()
{
  if (this->valid) {
    if (mass)     delete [] mass;
    if (pos)      delete [] pos;
    if (vel)      delete [] vel;
    if (acc)      delete [] acc;
    if (pot)      delete [] pot;
    if (id)       delete [] id;
    if (age)      delete [] age;
    if (metal)    delete [] metal;
    if (intenerg) delete [] intenerg;
    if (temp)     delete [] temp;
    if (nh)       delete [] nh;
    if (sfr)      delete [] sfr;
    if (rho)      delete [] rho;
    if (hsml)     delete [] hsml;
    if (zs)       delete [] zs;
    if (zsmt)     delete [] zsmt;
    if (im)       delete [] im;
    if (ssl)      delete [] ssl;
    if (cm)       delete [] cm;

    typename std::map<std::string,std::vector<T>  >::const_iterator it;
    for (it =  data_vector.begin(); it != data_vector.end(); it++) {
        if (this->verbose) {
            std::cerr << "~CSnapshotGadgetIn(): Delete key = " <<  it->first
                      << "  size=" << it->second.size() << "\n";
        }
        data_vector[it->first].clear();
      }
  }
  crv.clear();
}
// ============================================================================
// getSnapshotRange
template <class T>
ComponentRangeVector * CSnapshotGadgetIn<T>::getSnapshotRange()
{
  //crv.clear();
  if (this->valid && crv.size()) {
    //crv = getCRV();
    //ComponentRange::list(&crv);
    if (this->first) {
      this->first       = false;
      this->crv_first   = crv;
      this->nbody_first = getNtotal();
      //std::cerr << "CSnapshotGadgetIn::getSnapshotRange() = " << nbody_first << "\n";
      this->time_first  = getTime();
    }
  }
  return &crv;
}
//// ============================================================================
//// nextFrame
//int CSnapshotGadgetIn::nextFrame()
//{
//  user_select.setSelection(getSelectPart(),getSnapshotRange());
//  return nextFrame(user_select.getIndexesTab(),user_select.this->getNSel());
//}

// ============================================================================
// nextFrame
template <class T>
int CSnapshotGadgetIn<T>::nextFrame(uns::UserSelection &user_select)
{
  int status=0;
  assert(this->valid==true);
  if (first_loc) {
    first_loc = false;
    if (this->checkRangeTime(getTime())) {
      read(user_select); // read Gadget
      status = 1;
    }
  }
  return status;
}

// ============================================================================
// open() :
// open file and return :
// 0 : success
// 1 : unable to open
// 2 : not a GADGET file
template <class T>
int CSnapshotGadgetIn<T>::open(const std::string myfile)
{
  int fail=0;
  in.clear();
  in.open(myfile.c_str(),std::ios::in | std::ios::binary);
  if ( ! in.is_open()) {
   in.close();
   in.clear(); // mandatory under win32 !
   // try to open a multiple gadget file
   file0 = myfile+".0";
   PRINT("GadgetIn::open In gadget open file0 : " << file0 << "\n";)
   in.open(file0.c_str(),std::ios::in | std::ios::binary);
   if (in.is_open()) {
//     assert(in.good());
     lonely_file=false;
     PRINT("It's a multiple gadget file.\n";)
   }
  }
  if ( ! in.is_open()) {
    fail = 1;               // unable to open
    PRINT("In gadget, failed to open...\n";)
  }
  else {
    is_open=true;
    if (guessVersion()) {
      fail = readHeader(0);    // try to read header
      if (!fail) status=true; // valid header
      else close();           // not valid header
    }
    else {
      fail=1;
      close();             // not a valid gadgetfile
    }
  }
  return fail;
}
// ============================================================================
template <class T>
int CSnapshotGadgetIn<T>::close()
{
  if (is_open) in.close();
  is_open = false;
  return 1;
}
// ============================================================================
template <class T>
template <class U> int CSnapshotGadgetIn<T>::readCompData(U ** data, const int * index2,
                                                          const int * npartOffset,const int dim, const int nsel)
{
  bytes_counter=0;
  int len1 = readFRecord();
  //std::cerr << " SizeofT="<<sizeof(T) << " sizeofU="<<sizeof(U)<<"\n";
  checkFileVsArray(len1,sizeof(U),npart_total_local*dim);
  // allocate memory for the array
  if (*data==NULL) { // the first time
    *data = new U[dim*nsel];
  }
  U * ptr = *data;
  int fskip; // file skip factor
  if (array_vs_file_size<=1) {
    // 0 keep
    // 1 X 2
    fskip = sizeof(U) << array_vs_file_size;
  } else {
    // 2 divide by 2
    fskip= sizeof(U) >> 1;
  }
  for(int k=0;k<6;k++) {
    if (header.npart[k]>0) { // there are particles for the component
      int idx=index2[npartOffset[k]];
      if (idx != -1) {
        readData((char *) &ptr[dim*idx], sizeof(U), dim*header.npart[k]);
      } else {
        skipData(fskip*dim*header.npart[k]);
      }
    }
  }
  int len2 = readFRecord();
  if (len2==len1) ; // remove warning....
  assert(len2==len1 && in.good() && len1==bytes_counter);
  return 1;
}
// ============================================================================
template <class T>
template <class U>
int CSnapshotGadgetIn<T>::readGasStarsUnknownArray(U ** data, int * nguess,const int * compOffset)
{
  bytes_counter=0;
  int len1 = readFRecord();
  *nguess = len1/sizeof(U)/(header.npart[0]+header.npart[4]); // geuss #records
  //std::cerr << "NGuess constant = " << *nguess << "\n";
  checkFileVsArray(len1,sizeof(U),(*nguess)*(header.npart[0]+header.npart[4]));
  // allocate memory for the array
  if (*data==NULL) { // the first time
    *data = new U[(*nguess)*(header.npartTotal[0]+header.npartTotal[4])];
  }
  U * ptr = *data;
  // read gas DATA
  int idx=compOffset[0]*(*nguess); // set index to the correct offset
  assert((idx+(*nguess)*header.npart[0])<=(*nguess)*(header.npartTotal[0]+header.npartTotal[4]));
  readData((char *) &ptr[idx], sizeof(U),(*nguess)*header.npart[0]);
  // read stars DATA
  idx=header.npartTotal[0]*(*nguess)+compOffset[4]*(*nguess);
  assert((idx+(*nguess)*header.npart[4])<=(*nguess)*(header.npartTotal[0]+header.npartTotal[4]));
  readData((char *) &ptr[idx], sizeof(U),(*nguess)*header.npart[4]);
  int len2 = readFRecord();
  if (len2==len1) ; // remove warning....
  assert(in.good() && len2==len1 && len1==bytes_counter);
  return 1;
}
// ============================================================================
template <class T>
template <class U>
int CSnapshotGadgetIn<T>::readOneArray(U ** data, const int compid,const int * compOffset)
{
  bytes_counter=0;
  int len1 = readFRecord();
  checkFileVsArray(len1,sizeof(U),header.npart[compid]);
  // allocate memory for the array
  if (*data==NULL) { // the first time
    *data = new U[header.npartTotal[compid]];
  }
  U * ptr = *data;
  int idx=compOffset[0]; // set index to the correct offset
  assert((idx+header.npart[compid])<=header.npartTotal[compid]);
  readData((char *) &ptr[idx], sizeof(U),header.npart[compid] );
  int len2 = readFRecord();
  if (len2==len1) ; // remove warning....
  assert(in.good() && len1==len2 && len1==bytes_counter);
  return 1;
}
// ============================================================================
template <class T>
template <class U>
int CSnapshotGadgetIn<T>::readStreamBlock(const std::string req_blockname, std::vector<U> & data)
{
  if (is_read) { // file has already been read
    close();
  }
  int fail = open(filename);
  if (fail) assert(0);     // fail is true abort

  //assert(sizeof(U)==sizeof(float)); // works only for float NOW

  int last_len=0;
  // loop on all the files
  for (int i=0; i<header.num_files || (i==0 && header.num_files==0);i++) {
    std::string infile;
    if (header.num_files > 0 ) { // more than one file
      std::stringstream stm("");
      stm << "." << i;               // add ".XX" extension
      infile = filename + stm.str(); // new filename
      if (i>0) {
        close();                 // close previous file
        int fail=open(infile);   // open new file,read header
        if (fail) assert(0);     // fail is true abort
      }
    }
    else infile=filename;        // lonely file

    bool stop=false;
    bool ok=false;

    while(readBlockName() && !stop) {
      if (req_blockname == block_name) { // found requested block name
        bytes_counter=0;
        int len1 = readFRecord();

        if (data.size()==0) { //  first time
          data.resize(len1/sizeof(U)); // !! TO CHECK
        }
        else {
          if (i>0) { // more than one file
            data.resize((last_len+len1)/sizeof(U));
          } else {
            std::cerr << "WARNING, pointer not allocated...\n";
          }
        }

        U * ptr = &data[0];
        readData((char *) &ptr[last_len], sizeof(U), len1/sizeof(U) );
        int len2 = readFRecord();
        if (len2==len1) ; // remove warning....
        assert(in.good() && len1==len2 && len1==bytes_counter);
        last_len += len1;
        stop=true; // we must stop
        ok=true;
      } else {
        if (!ok) {
          if (in.eof()) { // it's end of file, must stop loop
            stop=true;
          }
          else {
            skipBlock();
          }
        }

      }
    }
  }

//  if (last_len>0) { // found something
//    *nbody=last_len/sizeof(T);
//  }
  return 1;
}

// ============================================================================
template <class T>
int CSnapshotGadgetIn<T>::read(uns::UserSelection &user_select)
{
  const uns::t_indexes_tab * index=user_select.getIndexesTab();
  const int nsel=user_select.getNSel();

  int npartOffset[6], // store absolute component offset (between components)
      compOffset[6];  // store relative component offset
  if (! is_read ) {
    //checkCompBits(index,nsel);

    // check component bits`
    this->comp_bits=user_select.compBits();

    //ComponentRange::list(&crv);
    //ComponentRange::list(user_select.getCrvFromSelection());

    is_read=true;
    assert(nsel<=npartTotal);
    // compute offset in case of multiple gadget file
    npartOffset[0] = 0;
    compOffset[0]  = 0;
    for (int i=1;i<=5;i++) {
      npartOffset[i] = npartOffset[i-1]+header.npartTotal[i-1];
      compOffset[i] = 0;
      if (this->verbose) std::cerr
          << "npartOffset["<<i<<"]="<<npartOffset[i]<<" npartOffset["<<i-1<<"]="
          <<npartOffset[i-1]<<" header.npartTotal["<<i-1<<"]="<<header.npartTotal[i-1]<<"\n";
    }
    //for (int i=0;i<6;i++)   std::cerr << "npartOffset["<<i<<"]="<<npartOffset[i] <<"\n";

    // allocate array to store indexes
    int * index2  = new int[npartTotal];
    for (int i=0; i<npartTotal; i++)
      index2[i] = -1; // index2 init

    for (int i=0, cpt=0; i<npartTotal; i++) {
      int idx=index[i].i;
      assert(idx<npartTotal);
      //std::cerr << i<< " " << index[i].i << " "<< index[i].idx << " " << nsel << " " <<npartTotal << "\n";
      if (idx != -1 ) {
        index2[idx] = cpt++;
      }
    }

    int z_offset  =0; // metalicity offset
    int age_offset=0; // age offset
    int im_offset=0; // age offset
    // loop on all the files
    for (int i=0; i<header.num_files || (i==0 && header.num_files==0);i++) {
      std::string infile;
      if (header.num_files > 0 ) { // more than one file
        std::stringstream stm("");
        stm << "." << i;               // add ".XX" extension
        infile = filename + stm.str(); // new filename
        if (i>0) {
          close();                 // close previous file
          int fail=open(infile);   // open new file,read header
          if (fail) assert(0);     // fail is true abort
        }
      }
      else infile=filename;        // lonely file
      int len1=0,len2=0;
      bool stop=false;
      std::string next_block_name;
      if (version==1) next_block_name="POS";

      // Read the whole file till a valid block exist
      // or stop = true in case of Gadget1 file
      while (this->req_bits!=0 && readBlockName() && !stop) {
        if (version==1) block_name=next_block_name;
        bool ok=false;
        // --> Postions block
        if (block_name=="POS" && this->req_bits&POS_BIT) {
          this->load_bits |= POS_BIT;
          ok=true;
          readCompData(&pos,index2,npartOffset,3, nsel);
          if (version==1) next_block_name="VEL";
        }
        // --> Velocities block
        if (block_name=="VEL" && this->req_bits&VEL_BIT) {
          this->load_bits |= VEL_BIT;
          ok=true;
          readCompData(&vel,index2,npartOffset,3,nsel);
          if (version==1) next_block_name="ID";
        }
        // --> IDs block
        if (block_name=="ID" && this->req_bits&ID_BIT) {
          this->load_bits |= ID_BIT;
          ok=true;
          readCompData(&id,index2,npartOffset,1,nsel);
          if (version==1) next_block_name="MASS";
        }
        // --> MASS block
        if (block_name=="MASS" && this->req_bits&MASS_BIT ) {
          this->load_bits |= MASS_BIT;
          ok=true;
          bytes_counter=0;
          if (ntotmasses>0) {    // different masses
            len1 = readFRecord(); // we must read from disk
            checkFileVsArray(len1,sizeof(T),ntotmasses);
          }
          // allocate memory if NULL pointer
          if (! mass )  mass = new T[nsel  ];
          for(int k=0;k<6;k++) {
            for(int n=0;n<header.npart[k];n++){
              int idx=index2[npartOffset[k]+n];
              assert(idx<nsel);
              if (idx != -1 && (header.mass[k] == 0)) {          // variable mass selected
                readData((char *) &mass[idx], sizeof(T), 1); // read from disk
              } else {
                if (idx == -1 && (header.mass[k] == 0)) {        // variable mass **not** selected
                  T tmp;
                  readData((char *) &tmp, sizeof(T), 1);     // read from disk (skip it)
                } else {
                  if (idx != -1 && (header.mass[k] != 0)) {      // constant mass selected
                    mass[idx] = header.mass[k];                  // read from header
                  }
                }
              }
            } // for n
          } // for k
          if (ntotmasses > 0) {  // different masses
            len2 = readFRecord(); // we must read from disk
            if (len2==len1) ; // remove warning....
            assert(in.good() && len2==len1 && len1==bytes_counter);
          }
          if (version==1) stop=true; // we stop reading for gadget1
        }
        // --> POT block
        if (block_name=="POT" && this->req_bits&POT_BIT) {
          this->load_bits |= POT_BIT;
          ok=true;
          readCompData(&pot,index2,npartOffset,1,nsel);
        }
        // --> Acceleration block
        if (block_name=="ACCE" && this->req_bits&ACC_BIT) {
          this->load_bits |= ACC_BIT;
          ok=true;
          readCompData(&acc,index2,npartOffset,3,nsel);
        }
        // --> U block (Internal energy)
        if (block_name=="U" && this->req_bits&U_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= U_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&intenerg,0,compOffset);
        }
        // --> Temperature block (= Electron Abundance)
        if (block_name=="NE" && this->req_bits&TEMP_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= TEMP_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&temp,0,compOffset);
        }
        // --> NH block (= Neutral Hydrogen Abundance)
        if (block_name=="NH" && this->req_bits&NH_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= NH_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&nh,0,compOffset);
        }
        // --> SFR block (= Star Formation Rate)
        if (block_name=="SFR" && this->req_bits&SFR_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= SFR_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&sfr,0,compOffset);
        }
        // --> RHO block (density)
        if (block_name=="RHO" && this->req_bits&RHO_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= RHO_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&rho,0,compOffset);
        }
        // --> HSML block (neighbours size)
        if (block_name=="HSML" && this->req_bits&HSML_BIT && this->comp_bits&GAS_BIT) {
          this->load_bits |= HSML_BIT;
          assert(header.npart[0]>0); // (gas only)
          ok=true;
          readOneArray(&hsml,0,compOffset);
        }
        // --> Z block (Metalicity)
        if (block_name=="Z" && this->req_bits&METAL_BIT && (this->comp_bits&GAS_BIT || this->comp_bits&STARS_BIT)) {
          this->load_bits |= METAL_BIT;
          assert((header.npart[0]+header.npart[4])>0); // gas+stars
          ok=true;
          bytes_counter=0;
          len1 = readFRecord();
          checkFileVsArray(len1,sizeof(T),header.npart[0]+header.npart[4]);
          // allocate memory for array only if NULL pointer
          if (!metal) {
            metal = new T[header.npartTotal[0]+header.npartTotal[4]];
          }
          // read gas metal
          int idx=compOffset[0];
          assert((idx+header.npart[0])<=(header.npartTotal[0]+header.npartTotal[4]));
          readData((char *) &metal[idx], sizeof(T),header.npart[0]);
          // read stars metal
          idx=header.npartTotal[0]+compOffset[4];
          assert((idx+header.npart[4])<=(header.npartTotal[0]+header.npartTotal[4]));
          readData((char *) &metal[idx], sizeof(T),header.npart[4]);
          len2 = readFRecord();
          assert(in.good() && len1==len2 && len1==bytes_counter);
        }
        // --> AGE block
        if (block_name=="AGE" && this->req_bits&AGE_BIT && this->comp_bits&STARS_BIT) {
          this->load_bits |= AGE_BIT;
          ok=true;
          bytes_counter=0;
          len1 = readFRecord();
          checkFileVsArray(len1,sizeof(T),header.npart[4]);
          // allocate memory for array only if NULL pointer
          if (!age) {
            age = new T[header.npartTotal[4]];
          }
          if ((int)(len1/sizeRealOnFile()) != header.npart[4]) {
            std::cerr << "\nWARNING: Wang's AGE bug detected.......skipping age\n";
            in.seekg(len1,std::ios::cur);
          } else {
            assert(header.npart[4]>0); // stars only
            int idx=age_offset;
            assert((idx+header.npart[4])<=(header.npartTotal[4]));
            readData((char *) &age[idx], sizeof(T),header.npart[4]);
          }
          len2 = readFRecord();
          assert(in.good() && len1==len2);// && len1==bytes_counter);
        }
        // --> IM block
        if (block_name=="iM" && this->req_bits&IM_BIT && this->comp_bits&STARS_BIT) {
          this->load_bits |= IM_BIT;
          assert((header.npart[4])>0); // stars
          ok=true;
          readOneArray(&im,4,compOffset);
        }
        // --> SSL block
        if ((block_name=="SSL" || block_name=="ssl") && this->req_bits&SSL_BIT && this->comp_bits&STARS_BIT) {
          this->load_bits |= SSL_BIT;
          assert((header.npart[4])>0); // stars
          ok=true;
          readOneArray(&ssl,4,compOffset);
        }
        // --> CM block
        if (block_name=="cM" && this->req_bits&CM_BIT && (this->comp_bits&GAS_BIT || this->comp_bits&STARS_BIT)) {
          assert((this->load_bits&CM_BIT)==0); // if failed means that multiple file not supported for this block
          this->load_bits |= CM_BIT;
          assert((header.npart[0]+header.npart[4])>0); // gas+stars
          ok=true;
          int ccm;
          readGasStarsUnknownArray(&cm,&ccm,compOffset);
          assert(ccm==1); // there is only one value per particle
        }
        // --> Zs block
        if (block_name=="Zs" && this->req_bits&ZS_BIT && (this->comp_bits&GAS_BIT || this->comp_bits&STARS_BIT)) {
          assert((this->load_bits&ZS_BIT)==0); // if failed means that multiple file not supported for this block
          this->load_bits |= ZS_BIT;
          assert((header.npart[0]+header.npart[4])>0); // gas+stars
          ok=true;
          readGasStarsUnknownArray(&zs,&czs,compOffset);
        }
        // --> ZSMT block
        if (block_name=="ZSMT" && this->req_bits&ZSMT_BIT && (this->comp_bits&GAS_BIT || this->comp_bits&STARS_BIT)) {
          assert((this->load_bits&ZSMT_BIT)==0); // if failed means that multiple file not supported for this block
          this->load_bits |= ZSMT_BIT;
          assert((header.npart[0]+header.npart[4])>0); // gas+stars
          ok=true;
          readGasStarsUnknownArray(&zsmt,&czsmt,compOffset);
        }
        if (!ok) {
          if (in.eof()) {
            stop=true;
          }
          else {
            skipBlock();
            if (version==1) { // we set the nextblockname
              if (block_name=="POS") next_block_name="VEL";
              if (block_name=="VEL") next_block_name="ID";
              if (block_name=="ID" ) next_block_name="MASS";
            }
          }
        }
      } // end of while readBlock

      // add masses if no BLOCK_MASS present (mass inside the header)
      if (ntotmasses == 0 && this->req_bits&MASS_BIT) { // no BLOCK_MASS present (mass inside the header)
        this->load_bits |= MASS_BIT;
        // allocate memory if NULL pointer
        if (! mass )  mass = new T[nsel  ];
        for(int k=0;k<6;k++) {
          for(int n=0;n<header.npart[k];n++){
            int idx=index2[npartOffset[k]+n];
            assert(idx<nsel);
            if (idx != -1 && (header.mass[k] != 0)) {      // constant mass selected
              mass[idx] = header.mass[k];                  // read from header
            }
          } // for n
        } // for k
      } // if

      // correct the offset of the particles which have been read
      for (int i=0;i<6;i++) {
        npartOffset[i] = npartOffset[i]+header.npart[i];
        compOffset[i] = compOffset[i]+header.npart[i];
      }
      // correction for metalicity and age
      z_offset   += (header.npart[0]+header.npart[4]);
      age_offset += header.npart[4];
      im_offset  += header.npart[4];
    } // end of loop on numfiles

    // garbage collecting
    delete [] index2;

    // convert to temperature units
    if (header.npartTotal[0] > 0) {
      //unitConversion();
    }
    // check bits
    this->freeNotLoadedData(&mass     ,MASS_BIT);
    this->freeNotLoadedData(&pos      ,POS_BIT);
    this->freeNotLoadedData(&vel      ,VEL_BIT);
    this->freeNotLoadedData(&acc      ,ACC_BIT);
    this->freeNotLoadedData(&pot      ,POT_BIT);
    this->freeNotLoadedData(&age      ,AGE_BIT);
    this->freeNotLoadedData(&metal    ,METAL_BIT);
    this->freeNotLoadedData(&temp     ,TEMP_BIT);
    this->freeNotLoadedData(&nh       ,NH_BIT);
    this->freeNotLoadedData(&sfr      ,SFR_BIT);
    this->freeNotLoadedData(&intenerg ,U_BIT);
    this->freeNotLoadedData(&rho      ,RHO_BIT);
    this->freeNotLoadedData(&hsml     ,HSML_BIT);
    this->freeNotLoadedData(&zs       ,ZS_BIT);
    this->freeNotLoadedData(&zsmt     ,ZSMT_BIT);
    this->freeNotLoadedData(&im       ,IM_BIT);
    this->freeNotLoadedData(&ssl      ,SSL_BIT);
    this->freeNotLoadedData(&cm       ,CM_BIT);
  }
  return 1;
}
// ============================================================================
// unitConversion()
template <class T>
void CSnapshotGadgetIn<T>::unitConversion()
{
  double BOLTZMANN, PROTONMASS;
  double UnitLength_in_cm, UnitMass_in_g, UnitVelocity_in_cm_per_s;
  double UnitTime_in_s, UnitDensity_in_cgs, UnitEnergy_in_cgs;
  double Xh;

#if 0
  double UnitPressure_in_cgs, HubbleParam=0.65m G;
  double GRAVITY;
#endif
  double MeanWeight, u, gamma;
  double RhoUniverse_omegabar;
  /* physical constants in cgs units */
  //GRAVITY   = 6.672e-8;
  BOLTZMANN = 1.3806e-16;
  PROTONMASS = 1.6726e-24;

  /* internal unit system of the code */
  UnitLength_in_cm= 3.085678e21;   /*  code length unit in cm/h */
  UnitMass_in_g= 1.989e43;         /*  code mass unit in g/h */
#ifdef GRAPE_UNIT
  UnitVelocity_in_cm_per_s= 207.9*1.0e5;
#else
  UnitVelocity_in_cm_per_s= 1.0e5;
#endif

  UnitTime_in_s= UnitLength_in_cm / UnitVelocity_in_cm_per_s;
  UnitDensity_in_cgs= UnitMass_in_g/ pow(UnitLength_in_cm,3);
  //UnitPressure_in_cgs= UnitMass_in_g/ UnitLength_in_cm/ pow(UnitTime_in_s,2);
  UnitEnergy_in_cgs= UnitMass_in_g * pow(UnitLength_in_cm,2) / pow(UnitTime_in_s,2);

  //G=GRAVITY/ pow(UnitLength_in_cm,3) * UnitMass_in_g * pow(UnitTime_in_s,2);

  Xh= 0.76;  /* mass fraction of hydrogen */

  RhoUniverse_omegabar=1.9e-29*0.04;

  assert(intenerg != NULL);

  for(int i=0;i<header.npart[0];i++) {

    MeanWeight= 4.0/(3*Xh+1+4*Xh*temp[i]) * PROTONMASS;

    /* convert internal energy to cgs units */

    u  = intenerg[i] * UnitEnergy_in_cgs/ UnitMass_in_g;

    gamma= 5.0/3;

    /* get temperature in Kelvin */

    temp[i] = MeanWeight/BOLTZMANN * (gamma-1) * u;
    if (rho) {
      rho[i] *= UnitDensity_in_cgs/RhoUniverse_omegabar;
    }

#if 0
#ifndef NOAGE
    if(P[i].Type==4)
      {
    if(P[i].Age!=0)
      P[i].Age=1.0/P[i].Age-1;
    else
      {
        //cout<<"Error Age"<<endl;
        //cout<<"N="<<i<<P[i].Age<< endl;
        //exit(0);
      }

      }
#endif
#endif
  }

}
// ============================================================================
// readHeader():
// read gadget header structure
// return values : 0 success, >0 not a Gadget header data
template <class T>
int CSnapshotGadgetIn<T>::readHeader(const int id)
{
  int len1,len2;

  // Header block
  readBlockName();
  bytes_counter=0;
  len1 = readFRecord();
  readData((char *)  header.npart         , sizeof(int   ),  6);
  readData((char *)  header.mass          , sizeof(double),  6);
  readData((char *) &header.time          , sizeof(double),  1);
  readData((char *) &header.redshift      , sizeof(double),  1);
  readData((char *) &header.flag_sfr      , sizeof(int   ),  1);
  readData((char *) &header.flag_feedback , sizeof(int   ),  1);
  readData((char *)  header.npartTotal    , sizeof(int   ),  6);
  readData((char *) &header.flag_cooling  , sizeof(int   ),  1);
  readData((char *) &header.num_files     , sizeof(int   ),  1);
  readData((char *) &header.BoxSize       , sizeof(double),  1);
  readData((char *) &header.Omega0        , sizeof(double),  1);
  readData((char *) &header.OmegaLambda   , sizeof(double),  1);
  readData((char *) &header.HubbleParam   , sizeof(double),  1);
  readData((char *)  header.fill          , sizeof(char  ), 96);
  len2 = readFRecord();
  if (this->verbose) {
    std::cerr << "header.flag_cooling = " << header.flag_cooling << "\n";
  }
  t_header.BoxSize = (T) header.BoxSize;
  t_header.redshift = (T) header.redshift;
  t_header.Omega0  = (T) header.Omega0;
  t_header.OmegaLambda  = (T) header.OmegaLambda;
  t_header.HubbleParam  = (T) header.HubbleParam;
  //std::cerr << "len1="<<len1<< " len2="<<len2<< " bytes_counter="<<bytes_counter<<"\n";
  if (in.bad() || len1!=len2 || len1!=bytes_counter)
    return 2;
  if (id==0) {                         // first time
    tframe = header.time;
    redshift = header.redshift;
    npartTotal = 0;
    npart_total_local = 0;
    ntotmasses  = 0 ; // !!!!!!!!!!! NEW
    for(int k=0; k<6; k++)  {
      npartTotal += header.npartTotal[k];    // count global total  particles
      npart_total_local += header.npart[k];  // count local total particles
    }
    for(int k=0; k<6; k++) {
      if (header.mass[k] == 0 ) {
        //ntotmasses += header.npartTotal[k];
        ntotmasses += header.npart[k];
      }
      if (this->verbose) {
        std::cerr << "mass["<<k<<"]="<<header.mass[k]<<"\n";
      }
    }
    storeComponents();
  }
  in_start_block = in.tellg(); // save poistion of input file

  return 0;
}
// ============================================================================
// readBlockName : read Gadget2 file format block
template <class T>
bool CSnapshotGadgetIn<T>::readBlockName()
{
  bool status=true;
  if (version == 2 ) { // gadget2 file format
    int dummy,nextblock;
    char name[5];
    array_vs_file_size = 0;
    readData((char *) &dummy    , sizeof(int) , 1); // read
    readData((char *) name      , sizeof(char), 4); // read label
    readData((char *) &nextblock, sizeof(int) , 1); // read nextblock
    readData((char *) &dummy    , sizeof(int) , 1); // read
#if 0
    int i=0; while (isupper(name[i])&& i<4) i++;
    name[i]='\0';
#else
    int i=0; while (name[i]!=' ' && i<4) i++;
    name[i]='\0';
#endif

    block_name=name;
    status = in.good();
    if (status && block_name!= "HEAD" && this->verbose)
      std::cerr << "Reading Block Name : <" << block_name << ">\n";
  }
  return status;
}
// ============================================================================
// guessVersion()
// detect Gadget  file format version ( 1 or 2 )
// return true if successfully detected otherwise false
template <class T>
bool CSnapshotGadgetIn<T>::guessVersion()
{
  bool status=true;
  // try to read 32bits length fortran record
  int dummy;
  swap = false; // no swapping
  array_vs_file_size = 0;
  readData((char *) &dummy, sizeof(int), 1); // read
  //std::cerr << "GadgetIn::guessVersion dummy = "<<dummy<<"\n";
  if( dummy != 256  && dummy != 8  ) {           // unknow number
    swap = true;                                 // need bytes swapping
    swapBytes((int *) &dummy, sizeof(int));      // swap
    //std::cerr << "GadgetIn::guessVersion dummy swapped= "<<dummy<<"\n";
    if( dummy != 256  && dummy != 8  )           // unknow swapped number
     status = false;                             // not a gadget file
  }
  if (status) {
    if (dummy==256) version=1; // gadget1
    else            version=2; // gadget2
    in.seekg(0,std::ios::beg); // rewind
    //std::cerr << "gadget Version : " <<version << "\n";
  }

  return status;
}
// ============================================================================
// readData:
// perform IO (Read,Write) operation on Data
template <class T>
int CSnapshotGadgetIn<T>::readData(char * ptr,const size_t size_bytes,const int items)
{
  if (array_vs_file_size==0) { // no conversion, same floating format
    bytes_counter += (size_bytes*items);

    // get data from file
    in.read(ptr,size_bytes*items);
    //assert(in.good());
    if (! in.good()) return 0;

    // We SWAP data
    if (swap && (size_bytes != CHAR)) { // swapping requested
      for (int i=0; i<items; i++) {
        swapBytes(ptr,size_bytes);
        ptr += size_bytes;
      }
    }
  } else if (array_vs_file_size==1) {
    bytes_counter += (size_bytes*2*items);
    // data bigger on file (double) than array(float)
    // we must use a temporary variable
    double tmp;
    for (int i=0; i<items; i++) {
      in.read((char *) &tmp,sizeof(double)); // read one double from file
      if (swap && (size_bytes != CHAR)) { // swapping requested
        swapBytes((char *) &tmp,sizeof(double));
      }
      float tofloat=(float) tmp; // cast to float
      memcpy(ptr+sizeof(float)*i,(char*)&tofloat,sizeof(float)); // copy back to array

    }
  }else {
    assert(array_vs_file_size==2);
    long int size_bytes_file = (size_bytes>>1);
    // data bigger on array (double) than file (float)
    // we use the destination array to store all read data
    bytes_counter += (size_bytes_file*items);

    // get data from file
    in.read(ptr+(size_bytes_file*items),size_bytes_file*items);
    //assert(in.good());
    if (! in.good()) return 0;

    // convert float read to double array

    for (int i=0; i<items; i++) {
      float  * value = (float * ) (ptr+(size_bytes_file*items)+i*sizeof(float));
      if (swap && (size_bytes != CHAR)) { // swapping requested
        swapBytes((char *) value,sizeof(float));
      }
      double tmp=(double) *value;
      char * p=(char *) &tmp;
      for (unsigned int j=0; j<size_bytes; j++) {
        ptr[size_bytes*i+j]=p[j];
      }
    }

  }
  return 1;
}
// ============================================================================
// getData
// return requested array according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string comp, std::string name, int *n,T **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=false;

  if (comp!="STREAM" && comp!="HEADER") {
    status=this->getRangeSelect(comp.c_str(),&nbody,&first,&last,false); // find components ranges
    if (!status && comp=="all") { // retreive all particles selected by the user
      status=1;
      first=0;
      nbody=this->getNSel();
    }
  }

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Nbody :
    if (status) {
      *data = NULL;
      *n = nbody;
    } else {
      ok = false;
    }
    break;
  case uns::Nsel   :
    if (status) {
      *n    = nbody;
    } else {
      ok=false;
    }
  case uns::Pos   :
    if (status && getPos()) {
      *data = &getPos()[first*3];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Vel  :
    if (status && getVel()) {
      *data = &getVel()[first*3];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Acc  :
    if (status && getAcc()) {
      *data = &getAcc()[first*3];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Pot  :
    if (status && getPot()) {
      *data = &getPot()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Mass  :
    if (status && getMass()) {
      *data = &getMass()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Rho :
    if (status && comp=="gas" && getRho(*n)) {
      *data = getRho(*n);
    } else {
      ok=false;
    }
    break;
  case uns::U :
    if (status && comp=="gas" && getU(*n)) {
      *data = getU(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Hsml :
    if (status && comp=="gas" && getHsml(*n)) {
      *data = getHsml(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Temp :
    if (status && comp=="gas" && getTemp(*n)) {
      *data = getTemp(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Nh :
    if (status && comp=="gas" && getNh(*n)) {
      *data = getNh(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Sfr :
    if (status && comp=="gas" && getSfr(*n)) {
      *data = getSfr(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Age :
    if (status && comp=="stars" && getAge(*n)) {
      *data = getAge(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Metal :
    if (status && comp=="gas" && this->ckloadBit(METAL_BIT)) {
      *data = getMetalGas(*n);
    } else
      if (status && comp=="stars" && this->ckloadBit(METAL_BIT)) {
      *data = getMetalStars(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Cm :
    if (status && comp=="gas") {
      *data = getCmGas(*n);
    } else
      if (status && comp=="stars") {
        *data = getCmStars(*n);
      } else
        if (status && comp=="all") {
          *data = getCm(*n);
        } else {
          ok=false;
        }
    break;
  case uns::Zs :
    if (status && comp=="gas") {
      *data = getZsGas(*n);
    } else
      if (status && comp=="stars") {
        *data = getZsStars(*n);
      } else
        if (status && comp=="all") {
          *data = getZs(*n);
        } else {
          ok=false;
        }
    break;
  case uns::ZSMT :
    if (status && comp=="gas") {
      *data = getZsmtGas(*n);
    } else
      if (status && comp=="stars") {
        *data = getZsmtStars(*n);
      } else
        if (status && comp=="all") {
          *data = getZsmt(*n);
        } else {
          ok=false;
        }
    break;
  case uns::Im :
    if (status && comp=="stars" && getIm(*n)) {
      *data = getIm(*n);
    } else {
      ok=false;
    }
    break;
  case uns::Ssl :
    if (status && comp=="stars" && getSsl(*n)) {
      *data = getSsl(*n);
    } else {
      ok=false;
    }
    break;
  default: // unkown name
      if (comp=="STREAM") { // data stream reading
        if (data_vector[name].size()==0) { // map key does not exist
          std::vector<T> * p = &(data_vector[name]);
          int status=readStreamBlock(name,*p);
          if (status>0) {
            ok=true;
          }
        } else {
          ok = true;
        }
        if (ok) {
          *n = data_vector[name].size();
          *data = &data_vector[name][0];
        }
      }

  }
  if (comp != "HEADER" && ok && !*data &&
      (CunsOut2<T>::s_mapStringValues[name]!=uns::Nbody &&
       CunsOut2<T>::s_mapStringValues[name]!=uns::Nsel)) ok = false; // not ok because array is NULL
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] for component <"<<comp<<"> does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData
// return requested array according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string name,int *n,T **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Pos   :
    *data = getPos();
    *n    = this->getNSel();
    break;
  case uns::Vel  :
    *data = getVel();
    *n    = this->getNSel();
    break;
  case uns::Mass  :
    *data = getMass();
    *n    = this->getNSel();
    break;
  case uns::Rho :
    *data = getRho(*n);
    break;
  case uns::U :
    *data = getU(*n);
    break;
  case uns::Hsml :
    *data = getHsml(*n);
    break;
  case uns::Temp :
    *data = getTemp(*n);
    break;
  case uns::Nh :
    *data = getNh(*n);
    break;
  case uns::Sfr :
    *data = getSfr(*n);
    break;
  case uns::Age :
    *data = getAge(*n);
    break;
  case uns::Acc :
    *data = getAcc();
    *n    = this->getNSel();
    break;
  case uns::Metal :
    if (this->comp_bits&STARS_BIT && this->comp_bits&GAS_BIT)      // gas and stars requested
      *data = getMetal(*n);
    else
      if (this->comp_bits&STARS_BIT)                         // only stars requested
        *data = getMetalStars(*n);
      else
        if (this->comp_bits&GAS_BIT)                         // only gas requested
          *data = getMetalGas(*n);
    break;
  case uns::GasMetal :
    if (this->ckloadBit(METAL_BIT))
      *data = getMetalGas(*n);
    break;
  case uns::StarsMetal :
    if (this->ckloadBit(METAL_BIT))
      *data = getMetalStars(*n);
    break;
  case uns::Zs :
    if (this->comp_bits&STARS_BIT && this->comp_bits&GAS_BIT)      // gas and stars requested
      *data = getZs(*n);
    else
      if (this->comp_bits&STARS_BIT)                         // only stars requested
        *data = getZsStars(*n);
      else
        if (this->comp_bits&GAS_BIT)                         // only gas requested
          *data = getZsGas(*n);
    break;
  case uns::Cm :
    if (this->comp_bits&STARS_BIT && this->comp_bits&GAS_BIT)      // gas and stars requested
      *data = getCm(*n);
    else
      if (this->comp_bits&STARS_BIT)                         // only stars requested
        *data = getCmStars(*n);
      else
        if (this->comp_bits&GAS_BIT)                         // only gas requested
          *data = getCmGas(*n);
    break;
  case uns::ZSMT :
    if (this->comp_bits&STARS_BIT && this->comp_bits&GAS_BIT)      // gas and stars requested
      *data = getZsmt(*n);
    else
      if (this->comp_bits&STARS_BIT)                         // only stars requested
        *data = getZsmtStars(*n);
      else
        if (this->comp_bits&GAS_BIT)                         // only gas requested
          *data = getZsmtGas(*n);
    break;
  case uns::Im :
    *data = getIm(*n);
    break;
  case uns::Ssl :
    *data = getSsl(*n);
    break;
  default: ok=false;
  }

  if (ok && !*data) ok = false; // not ok because array is NULL
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData
// return requested T according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string name,T *data)
{
  bool ok=true;
  *data=0.0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Time   :
    *data = getTime();
    break;
  case uns::Redshift   :
    *data = getRedshift();
    break;
  default: ok=false;
    if (getHeader(name,data)) {
      ok = true;
    }
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    }  else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData
// return requested array according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string comp,const std::string name,int *n, int **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=this->getRangeSelect(comp.c_str(),&nbody,&first,&last,false); // find components ranges
  if (!status && comp=="all") { // retreive all particles selected by the user
    status=1;
    first=0;
    nbody=this->getNSel();
  }
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Id :
    if (status && this->ckloadBit(ID_BIT)) {
      *data = id+first;
      *n = nbody;
    } else {
      ok = false;
    }
    break;
  case uns::Nbody :
    if (status) {
      *data = NULL;
      *n = nbody;
    } else {
      ok = false;
    }
    break;
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] for component <"<<comp<<"> does not exist...\n";
    }
  }
  return ok;
}

// ============================================================================
// getData
// return requested array according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string name,int *n, int **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Id :
    if (this->ckloadBit(ID_BIT)) {
      *data = id;
      *n    = this->getNSel();
    } else {
      ok = false;
    }
    break;
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getHeader
// return requested header data according 'name' selection
template <class T> bool CSnapshotGadgetIn<T>::getHeader(const std::string name, T * data)
{

  std::string nameupper = tools::Ctools::toupper(name);
  bool status = false;

  if (nameupper=="BOXLEN" || nameupper=="BOXSIZE") {
    *data= (T) t_header.BoxSize;
    status = true;
  }
  if (nameupper=="OMEGA_M" || nameupper=="OMEGA0") {
    *data= (T) t_header.Omega0;
    status = true;
  }
  if (nameupper=="OMEGA_L" || nameupper=="OMEGALAMBDA") {
    *data= (T) t_header.OmegaLambda;
    status = true;
  }
  if (nameupper=="HUBBLEPARAM" || nameupper=="H0") {
    *data= (T) t_header.HubbleParam;
    status = true;
  }
  return status;
}
// ============================================================================
// getData
// return requested int according 'name' selection
template <class T>
bool CSnapshotGadgetIn<T>::getData(const std::string name,int *data)
{
  bool ok=true;
  *data=0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Nsel   :
    *data = this->getNSel();
    break;
  case uns::Ngas   :
    *data = header.npartTotal[0];
    break;
  case uns::Nhalo   :
    *data = header.npartTotal[1];
    break;
  case uns::Ndisk   :
    *data = header.npartTotal[2];
    break;
  case uns::Nbulge   :
    *data = header.npartTotal[3];
    break;
  case uns::Nstars   :
    *data = header.npartTotal[4];
    break;
  case uns::Nbndry   :
    *data = header.npartTotal[5];
    break;
  case uns::Czs   :
    *data = czs;
    break;
  case uns::Czsmt   :
    *data = czsmt;
    break;
  default: ok=false;
  }
  if (ok && !*data) ok = false; // not ok because array is NULL
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetIn::getData Value ["<<name<<"] does not exist or empty\n";
    }
  }
  return ok;
}
// ============================================================================
// isLittleEndian()
// Test endianess: return true if little endian architecture, false if big endian
template <class T>
bool CSnapshotGadgetIn<T>::isLittleEndian()
{
  bool status=false;
  int one=1;
  char * p = (char *)&one;
  if (p[0]==1 ) status=true;
  return status;
}
// ============================================================================
// storeComponents:
template <class T>
void CSnapshotGadgetIn<T>::storeComponents()
{
  uns::ComponentRange cr;
  // all
  cr.setData(0,npartTotal-1);
  cr.setType("all");
  crv.clear();
  crv.push_back(cr);
  // components
  const char * comp [] = { "gas", "halo", "disk", "bulge", "stars", "bndry"};
  for(int k=0,start=0; k<6; k++)  {
    if (header.npartTotal[k]) {
      cr.setData(start,start+header.npartTotal[k]-1,comp[k]);
      crv.push_back(cr);
      start+=header.npartTotal[k];
    }
  }
}


// ----------------------------------------------------------------------------
//
//                     CSnapshotGadgetOut CLASS implementation
//
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// WRITING constructor
template <class T>
CSnapshotGadgetOut<T>::CSnapshotGadgetOut(const std::string _n, const std::string _t, const bool _v):CSnapshotInterfaceOut<T>(_n, _t, _v)
{
  if (this->simtype=="gadget1") version=1;
  else
    if (this->simtype=="gadget2") version=2;
  else {
    std::cerr << "Unkwown Gadget file type : ["<<this->simtype<<"]\n"
        << "aborting .....\n";
    std::exit(1);
  }
  std::stringstream stm("");
  stm << version;
  this->interface_type = "Gadget" + stm.str();
  this->file_structure = "component"; // "component" like file
  if (this->verbose) std::cerr << "CSnapshotGadgetOut::CSnapshotGadgetOut simname = " << this->simname <<"\n";
  for (int i=0;i<6; i++) {
    mass[i]   = NULL;
    pos [i]   = NULL;
    vel [i]   = NULL;
    pot [i]   = NULL;
    acc [i]   = NULL;
    id  [i]   = NULL;
    metal[i]  = NULL;
    ptrIsAlloc[i]["mass" ]=false;
    ptrIsAlloc[i]["pos"  ]=false;
    ptrIsAlloc[i]["vel"  ]=false;
    ptrIsAlloc[i]["id"   ]=false;
    ptrIsAlloc[i]["pot"  ]=false;
    ptrIsAlloc[i]["acc"  ]=false;
    ptrIsAlloc[i]["metal"]=false;
  }
  //id     = NULL;
  age    = NULL;
  //metal  = NULL;
  intenerg=NULL;
  temp   = NULL;
  nh     = NULL;
  sfr    = NULL;
  rho    = NULL;
  hsml   = NULL;
  ntot_withmasses=0;

  // gas only
  ptrIsAlloc[0]["temp" ]=false;
  ptrIsAlloc[0]["rho"  ]=false;
  ptrIsAlloc[0]["hsml" ]=false;
  ptrIsAlloc[0]["metal"]=false;
  ptrIsAlloc[0]["u"    ]=false;
  ptrIsAlloc[0]["nh"   ]=false;
  ptrIsAlloc[0]["sfr"  ]=false;
  // stars only
  ptrIsAlloc[4]["age"  ]=false;
  ptrIsAlloc[4]["metal"]=false;

  bits   = 0;
  bzero(&header,sizeof(header));
}
// ----------------------------------------------------------------------------
// destructor
template <class T>
CSnapshotGadgetOut<T>::~CSnapshotGadgetOut()
{
  for (int i=0; i<6; i++) {
    if (mass[i]&& ptrIsAlloc[i]["mass" ]) delete [] mass[i];
    if (pos [i]&& ptrIsAlloc[i]["pos"  ]) delete [] pos[i];
    if (vel [i]&& ptrIsAlloc[i]["vel"  ]) delete [] vel[i];
    if (id  [i]&& ptrIsAlloc[i]["id"   ]) delete [] id[i];
    if (pot [i]&& ptrIsAlloc[i]["pot"  ]) delete [] pot[i];
    if (acc [i]&& ptrIsAlloc[i]["acc"  ]) delete [] acc[i];
    if (metal[i]&& ptrIsAlloc[i]["metal"]) delete [] metal[i];
  }
  // gas only
  if (rho      && ptrIsAlloc[0]["rho"  ]) delete [] rho;
  if (hsml     && ptrIsAlloc[0]["hsml" ]) delete [] hsml;
//  if (metal    && ptrIsAlloc[0]["metal"]) {
//    delete [] metal;
//    metal=NULL;
//  }
  if (temp     && ptrIsAlloc[0]["temp" ]) delete [] temp;
  if (nh       && ptrIsAlloc[0]["nh"   ]) delete [] nh;
  if (sfr      && ptrIsAlloc[0]["sfr"  ]) delete [] sfr;
  if (intenerg && ptrIsAlloc[0]["u"    ]) delete [] intenerg;
  // stars only
//  if (metal    && ptrIsAlloc[4]["metal"]) {
//    delete [] metal;
//    metal=NULL;
//  }
  if (age      && ptrIsAlloc[4]["age"  ]) delete [] age;
}
// ----------------------------------------------------------------------------
// putHeader
template <class T>
int CSnapshotGadgetOut<T>::setHeader(void * _header)
{
  setHeader((t_io_header_1 *) (_header));
  return 1;
}
  // ----------------------------------------------------------------------------
  // setData
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name,T  data)
  {
    bool ok=true;
    int status=0;
    
    switch(CunsOut2<T>::s_mapStringValues[name]) {
    case uns::Time :
      status = 1;
      header.time = data;
      break;
    default: ok=false;
      if (setHeader(name,data)) {
        status=1;
        ok=1;
      }
    }

    if (this->verbose) {
      if (ok) {
        std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
      } else {
        std::cerr << "** WARNING ** SnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
      }
    }
    return status;
  }

// ----------------------------------------------------------------------------
// setData
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name, const int n ,int * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
#if 0
  case uns::Id :
    assert(n==npartTotal);
    if (_addr) { // map address
      id = data;
    }
    else {
      //ptrIsAlloc["mass"]=true;
      if (! id)
    id = new int[npartTotal];
      memcpy(id,data,sizeof(int)*n);
    }
    bits |= ID_BIT;
    break;
#endif
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) { std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name, const int n ,T * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Rho :
    status = setRho(n, data, _addr);
    break;
  case uns::Hsml:
    status = setHsml(n, data, _addr);
    break;
  case uns::U:
    status = setU(n, data, _addr);
    break;
  case uns::Temp  :
    status = setTemp(n, data, _addr);
    break;
  case uns::Nh  :
    status = setNh(n, data, _addr);
    break;
  case uns::Sfr  :
    status = setSfr(n, data, _addr);
    break;
  case uns::Age  :
    status = setAge(n, data, _addr);
    break;
  case uns::GasMetal  :
    status = setMetalGas(n, data, _addr);
    break;
  case uns::StarsMetal  :
    status = setMetalStars(n, data, _addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) { std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
// setData("gas","pos",n,gas_pos_array,true)
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name,std::string array,  const int n ,T * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  // Special EXTRA treatment
  // setData("EXTRA","TX",n,tx_array,true)
  if (CunsOut2<T>::s_mapStringValues[name]==uns::Extra) {
    status = setExtra(array,n, data, _addr);
  } else { 
    // Test all array/tag possibilities
    switch(CunsOut2<T>::s_mapStringValues[array]) {
    // case uns::Extra :
    //   status = setExtra(name,n, data, _addr);
    //   break;
    case uns::Header :
      //status = setHeader(array,n, data, _addr);
      break;
    case uns::Pos  :
      status = setPos(name, n, data, _addr);
      break;
    case uns::Vel  :
      status = setVel(name, n, data, _addr);
      break;
    case uns::Mass :
      status = setMass(name, n, data, _addr);
      break;
    case uns::Pot  :
      status = setPot(name, n, data, _addr);
      break;
    case uns::Acc  :
      status = setAcc(name, n, data, _addr);
      break;
    case uns::Hsml :
      status = setHsml(n, data, _addr);
      break;
    case uns::Rho  :
      status = setRho(n, data, _addr);
      break;
    case uns::U  :
      status = setU(n, data, _addr);
      break;
    case uns::Temp  :
      status = setTemp(n, data, _addr);
      break;
    case uns::Nh  :
      status = setNh(n, data, _addr);
      break;
    case uns::Sfr  :
      status = setSfr(n, data, _addr);
      break;
    case uns::Age  :
      status = setAge(n, data, _addr);
      break;
    case uns::GasMetal  :
      status = setMetalGas(n, data, _addr);
      break;
    case uns::StarsMetal  :
      status = setMetalStars(n, data, _addr);
      break;
    case uns::Metal  :
      if (name=="gas") {
        status = setMetalGas(n, data, _addr);
      } else {
        if (name=="stars") {
          status = setMetalStars(n, data, _addr);
        }
      }
      break;
    default: ok=false;
    }
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      if (name != "EXTRA") {
        std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
      } else {
        std::cerr << "CSnapshotGadgetOut::setData EXTRA tags["<<array<<"]\n";
      }
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
// setData("all","id",n,gas_array,true)
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name,std::string array,  const int n ,int * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[array]) {
  case uns::Id   :
    status = setId(name, n, data, _addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
#if 0
  switch(CunsOut2<T>::s_mapStringValues[array]) {
  case uns::Id  :
    status = setData(array, n, data, _addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
#endif

}

// ----------------------------------------------------------------------------
// setData
// setData("gas",n,pos,vel,mass,true)
template <class T>
int CSnapshotGadgetOut<T>::setData(std::string name, const int n ,T * data, T * data1, T * data2, const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Gas   :
  case uns::Halo  :
  case uns::Disk  :
  case uns::Bulge :
  case uns::Stars :
  case uns::Bndry :
    status = setMass(name, n, data , _addr);
    status = setPos (name, n, data1, _addr);
    status = setVel (name, n, data2, _addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetOut::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}

// ============================================================================
// setHeader:
template <class T>
int CSnapshotGadgetOut<T>::setHeader(t_io_header_1 * _header)
{
  memcpy(&header,_header,sizeof(t_io_header_1));
  bits &= HEADER_BIT;
  return 1;
}
// ============================================================================
// setNbody:
template <class T>
int CSnapshotGadgetOut<T>::setNbody(const int _nbody)
{
  npartTotal = _nbody;
  return 1;
}
// ============================================================================
// setId:
template <class T>
int CSnapshotGadgetOut<T>::setId(std::string name, const int _n, int * _id, const bool addr)
{
  int index=-1;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Gas    : index=0; break;
  case uns::Halo   : index=1; break;
  case uns::Disk   : index=2; break;
  case uns::Bulge  : index=3; break;
  case uns::Stars  : index=4; break;
  case uns::Bndry  : index=5; break;
  default:
    break;
  }
  assert(index!=-1);
  if (addr) { // map address
    id[index] = _id;
  }
  else {
    ptrIsAlloc[index]["id"]=true;
    if (id[index])  delete [] id[index];
    id[index] = new int[_n];
    memcpy(id[index],_id,sizeof(int)*_n);
  }
  header.npart[index] = _n;
  bits |= ID_BIT;
  return 1;
}
// ============================================================================
// setMass:
template <class T>
int CSnapshotGadgetOut<T>::setMass(std::string name, const int _n, T * _mass, const bool addr)
  {
    int index=-1;
    switch(CunsOut2<T>::s_mapStringValues[name]) {
    case uns::Gas    : index=0; break;
    case uns::Halo   : index=1; break;
    case uns::Disk   : index=2; break;
    case uns::Bulge  : index=3; break;
    case uns::Stars  : index=4; break;
    case uns::Bndry  : index=5; break;
    default:
      break;
    }
    assert(index!=-1);
  if (addr) { // map address
    mass[index] = _mass;
  }
  else {
    ptrIsAlloc[index]["mass"]=true;
    if (mass[index])  delete [] mass[index];
    mass[index] = new T[_n];
    memcpy(mass[index],_mass,sizeof(T)*_n);
  }
  header.npart[index] = _n;
  bits |= MASS_BIT;
  return 1;
}
// ============================================================================
// setPos:
template <class T>
int CSnapshotGadgetOut<T>::setPos(std::string name, const int _n, T * _pos, const bool addr)
{
  int index=-1;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Gas    : index=0; break;
  case uns::Halo   : index=1; break;
  case uns::Disk   : index=2; break;
  case uns::Bulge  : index=3; break;
  case uns::Stars  : index=4; break;
  case uns::Bndry  : index=5; break;
  default:
    break;
  }
  if (addr) { // map address
    pos[index]= _pos;
  }
  else{
    ptrIsAlloc[index]["pos"]=true;
    if (pos[index]) delete [] pos[index];
    pos[index] = new T[_n*3];
    memcpy(pos[index],_pos,sizeof(T)*_n*3);
  }
  header.npart[index] = _n;
  bits |= POS_BIT;
  return 1;
}
// ============================================================================
// setVel:
template <class T>
int CSnapshotGadgetOut<T>::setVel(std::string name, const int _n, T * _vel, const bool addr)
{
  int index=-1;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Gas    : index=0; break;
  case uns::Halo   : index=1; break;
  case uns::Disk   : index=2; break;
  case uns::Bulge  : index=3; break;
  case uns::Stars  : index=4; break;
  case uns::Bndry  : index=5; break;
  default:
    break;
  }
  if (addr) { // map address
    vel[index] = _vel;
  }
  else {
    ptrIsAlloc[index]["vel"]=true;
    if (vel[index]) delete [] vel[index];
    vel[index] = new T[_n*3];
    memcpy(vel[index],_vel,sizeof(T)*_n*3);
  }
  header.npart[index] = _n;
  bits |= VEL_BIT;
  return 1;
}
 // ============================================================================
 // setPot:
template <class T>
int CSnapshotGadgetOut<T>::setPot(std::string name, const int _n, T * _pot, const bool addr)
 {
   int index=-1;
   switch(CunsOut2<T>::s_mapStringValues[name]) {
   case uns::Gas    : index=0; break;
   case uns::Halo   : index=1; break;
   case uns::Disk   : index=2; break;
   case uns::Bulge  : index=3; break;
   case uns::Stars  : index=4; break;
   case uns::Bndry  : index=5; break;
   default:
     break;
   }
   if (addr) { // map address
     pot[index]= _pot;
   }
   else{
     ptrIsAlloc[index]["pot"]=true;
     if (pot[index]) delete [] pot[index];
     pot[index] = new T[_n];
     memcpy(pot[index],_pot,sizeof(T)*_n);
   }
   header.npart[index] = _n;
   bits |= POT_BIT;
   return 1;
 }
 // ============================================================================
 // setAcc:
template <class T>
int CSnapshotGadgetOut<T>::setAcc(std::string name, const int _n, T * _acc, const bool addr)
 {
   int index=-1;
   switch(CunsOut2<T>::s_mapStringValues[name]) {
   case uns::Gas    : index=0; break;
   case uns::Halo   : index=1; break;
   case uns::Disk   : index=2; break;
   case uns::Bulge  : index=3; break;
   case uns::Stars  : index=4; break;
   case uns::Bndry  : index=5; break;
   default:
     break;
   }
   if (addr) { // map address
     acc[index] = _acc;
   }
   else {
     ptrIsAlloc[index]["acc"]=true;
     if (acc[index]) delete [] acc[index];
     acc[index] = new T[_n*3];
     memcpy(acc[index],_acc,sizeof(T)*_n*3);
   }
   header.npart[index] = _n;
   bits |= ACC_BIT;
   return 1;
 }
// ============================================================================
// setRho:
template <class T>
int CSnapshotGadgetOut<T>::setRho(const int _n, T * _rho, const bool addr)
 {
  if (header.npart[0]>0) assert(_n==header.npart[0]);; // #rho particles = #gas particles
  header.npart[0]=_n;

  if (addr) { // map address
    rho = _rho;
  }
  else {
    ptrIsAlloc[0]["rho"]=true;
    if (! rho)
      rho = new T[_n];
    memcpy(rho,_rho,sizeof(T)*_n);
  }
  bits |= RHO_BIT;
  return 1;
}
// ============================================================================
// setHsml:
template <class T>
int CSnapshotGadgetOut<T>::setHsml(const int _n, T * _hsml, const bool addr)
{
  if (header.npart[0]>0) assert(_n==header.npart[0]);; // #hsml particles = #gas particles
  header.npart[0]=_n;
  if (addr) { // map address
    hsml = _hsml;
  }
  else {
    ptrIsAlloc[0]["hsml"]=true;
    if (! hsml)
      hsml = new T[_n];
    memcpy(hsml,_hsml,sizeof(T)*_n);
  }
  bits |= HSML_BIT;
  return 1;
}
 // ============================================================================
 // setU:
template <class T>
int CSnapshotGadgetOut<T>::setU(const int _n, T * _U, const bool addr)
 {
   if (header.npart[0]>0) assert(_n==header.npart[0]);; // #U particles = #gas particles
   header.npart[0]=_n;
   if (addr) { // map address
     intenerg = _U;
   }
   else {
     ptrIsAlloc[0]["u"]=true;
     if (! intenerg)
       intenerg = new T[_n];
     memcpy(intenerg,_U,sizeof(T)*_n);
   }
   bits |= U_BIT;
   return 1;
 }
 // ============================================================================
 // setTemp:
template <class T>
int CSnapshotGadgetOut<T>::setTemp(const int _n, T * _temp, const bool addr)
 {

   if (header.npart[0]>0) assert(_n==header.npart[0]);; // #U particles = #gas particles
   header.npart[0]=_n;
   if (addr) { // map address
     temp = _temp;
   }
   else {
     ptrIsAlloc[0]["temp"]=true;
     if (! temp)
       temp = new T[_n];
     memcpy(temp,_temp,sizeof(T)*_n);
   }
   bits |= TEMP_BIT;
   return 1;
 }
// ============================================================================
// setNh:
template <class T>
int CSnapshotGadgetOut<T>::setNh(const int _n, T * _nh, const bool addr)
{

  if (header.npart[0]>0) assert(_n==header.npart[0]);; // #U particles = #gas particles
  header.npart[0]=_n;
  if (addr) { // map address
    nh = _nh;
  }
  else {
    ptrIsAlloc[0]["nh"]=true;
    if (! nh)
      nh = new T[_n];
    memcpy(nh,_nh,sizeof(T)*_n);
  }
  bits |= NH_BIT;
  return 1;
}
// ============================================================================
// setSfr:
template <class T>
int CSnapshotGadgetOut<T>::setSfr(const int _n, T * _sfr, const bool addr)
{

  if (header.npart[0]>0) assert(_n==header.npart[0]);; // #U particles = #gas particles
  header.npart[0]=_n;
  if (addr) { // map address
    sfr = _sfr;
  }
  else {
    ptrIsAlloc[0]["sfr"]=true;
    if (! sfr)
      sfr = new T[_n];
    memcpy(sfr,_sfr,sizeof(T)*_n);
  }
  bits |= SFR_BIT;
  return 1;
}
 // ============================================================================
 // setMetalGas:
template <class T>
int CSnapshotGadgetOut<T>::setMetalGas(const int _n, T * _mg, const bool addr)
 {

   if (header.npart[0]>0) assert(_n==header.npart[0]);; // #U particles = #gas particles
   header.npart[0]=_n;
   if (addr) { // map address
     metal[0] = _mg;
   }
   else {
     ptrIsAlloc[0]["metal"]=true;
     if (metal[0]) delete [] metal[0];
     metal[0] = new T[header.npart[0]];
     memcpy(metal[0],_mg,sizeof(T)*_n);
   }
   bits |= METAL_BIT;
   return 1;
 }
 // ============================================================================
 // setMetalStars:
template <class T>
int CSnapshotGadgetOut<T>::setMetalStars(const int _n, T * _ms, const bool addr)
 {

   if (header.npart[4]>0) assert(_n==header.npart[4]);; // #metal stars particles
   header.npart[4]=_n;
   if (addr) { // map address
     metal[4] = _ms;
   }
   else {
     ptrIsAlloc[4]["metal"]=true;
     if (metal[4]) delete [] metal[4];
     metal[4] = new T[header.npart[4]];
     memcpy(metal[4],_ms,sizeof(T)*_n);
   }
   bits |= METAL_BIT;
   return 1;
 }
 // ============================================================================
 // setAge:
template <class T>
int CSnapshotGadgetOut<T>::setAge(const int _n, T * _age, const bool addr)
 {

   if (header.npart[4]>0) assert(_n==header.npart[4]);; // #age stars particles
   header.npart[4]=_n;
   if (addr) { // map address
     age = _age;
   }
   else {
     ptrIsAlloc[4]["age"]=true;
     if (! age)
       age = new T[header.npart[4]];
     memcpy(age,_age,sizeof(T)*_n);
   }
   bits |= AGE_BIT;
   return 1;
 }
 // ============================================================================
 // setExtra:
template <class T>
int CSnapshotGadgetOut<T>::setExtra(std::string tag, const int _n, T * _data, const bool addr)
 {
   s_mapStringVector[tag].clear();
   s_mapStringVector[tag].resize(_n);
   memcpy((T *) &s_mapStringVector[tag][0],_data,sizeof(T)*_n);
   return 1;
 }
 // ============================================================================
 // setHeader:
template <class T>
int CSnapshotGadgetOut<T>::setHeader(std::string tag, T data)
 {
  std::string nameupper=tools::Ctools::toupper(tag);
  int ok=0;

  if (nameupper=="REDSHIFT") {
      header.redshift=data;
      ok=1;
  }
  if (nameupper=="FLAGSFR") {
      header.flag_sfr=(int) data;
      ok=1;
  }

  if (nameupper=="BOXLEN" || nameupper=="BOXSIZE") {
     header.BoxSize=data;
     ok=1;
  }
  if (nameupper=="OMEGA_M" || nameupper=="OMEGA0") {
    header.Omega0=data;
    ok=1;
  }
  if (nameupper=="OMEGA_L" || nameupper=="OMEGALAMBDA") {
    header.OmegaLambda=data;
    ok=1;
  }
  if (nameupper=="HUBBLEPARAM" || nameupper=="H0") {
    header.HubbleParam=data;
    ok=1;
  }
  return ok;
 }
 //// ============================================================================
//// saveDataMPV:
// int CSnapshotGadgetOut::saveDataMPV(const int _n, const float * _m, const float * _p, const float * _v)
//{
//  npartTotal = _n;
//  return 1;
//}
// ============================================================================
// save:
template <class T>
int CSnapshotGadgetOut<T>::save()
{
  int fail=0;
#if 0
  if (!(bits & HEADER_BIT)) {
    std::cerr << "No Header Bit !!\n";
    fail = 1;
  }
#endif
  if (!(bits & MASS_BIT)) {
    std::cerr << "No Mass Bit !!\n";
    //fail = 1;
  }
  if (!(bits & POS_BIT)) {
    std::cerr << "No Pos Bit !!\n";
    //fail = 1;
  }
  if (!(bits & VEL_BIT)) {
    std::cerr << "No Vel Bit !!\n";
    //fail = 1;
  }

  if (!fail) {
    npartTotal = 0;
    for (int k=0; k<6;  k++) {
      header.npartTotal[k]= header.npart[k];
      npartTotal += header.npartTotal[k];
    }
    if (this->verbose) std::cerr << "CSnapshotGadgetOut::save npartTotal = " << npartTotal << "\n";
    setupHeader();
    saveFile();
  }
  return 1;
}
// ============================================================================
// writeData:
// perform Write operation on Data
template <class T>
int CSnapshotGadgetOut<T>::writeData(char * ptr,const size_t size_bytes,const int items)
{
  bytes_counter += (size_bytes*items);

  // Save Data to file
  out.write(ptr,size_bytes*items);
  assert(out.good());

  return 1;
}
// ============================================================================
// writeDataZero:
// perform Write operation on Data with value
template <class T>
int CSnapshotGadgetOut<T>::writeDataValue(T value,const size_t size_bytes,const int items)
{
  bytes_counter += (size_bytes*items);

  char * buffer=new char[size_bytes*items];

  for (unsigned int i=0;i<(size_bytes*items);i+=sizeof(T)) {
    char * p = (char *) &value;
    for (unsigned int j=0;j<sizeof(T);j++) {
      buffer[i]=*p; // init to value
      p++;
    }
  }
  // Save Data to file
  out.write(buffer,size_bytes*items);
  assert(out.good());

  delete [] buffer;
  return 1;
}
// ============================================================================
// setupHeader:
template <class T>
void CSnapshotGadgetOut<T>::setupHeader(bool check)
{
  bool ok=true;
  if (check) {

  }
  if (ok) {
    // we assumed that there is only ONE file
    header.num_files=1;

    // here we figure out if masses are different
    // for all the particles of a component. Accordingly
    // we fill header.mass[] array

    ntot_withmasses=0;
    for(int k=0;k<6;k++) { // loop on components
      if (header.npart[k] ) {
        //assert(mass[k]!=NULL);
        T mass0=0.0;
        if (mass[k]!=NULL)
          mass0=mass[k][0]; // mass 0
        bool equal=true;
        // loop on all masses of the currentcomponent
        for(int n=0;(n<header.npart[k])&&equal;n++) {
          int pindex=n;
          assert(pindex<npartTotal);
//          if (pindex>npartTotal) {
//            std::cerr << "pindex :"<<pindex<<" "<< npartTotal <<"\n";
//          }

          if (mass[k]!=NULL && mass0 != mass[k][pindex]) { // mass differ !
            equal=false;
          }
        }
        if (mass[k]) {
          if (equal) { // same masses for the component
            if (this->verbose) std::cerr <<"CSnapshotGadgetOut::setupHeader => same Mass["<<k<<"]="<<mass0<<"\n";
            header.mass[k] = mass0;
          } else {
            header.mass[k] = 0.0;
            ntot_withmasses+=header.npart[k];
          }
        } else { // mass has not been specify for 'k' component
                 // we assume it's volontary, and we set mass = -666
          header.mass[k] = -666.;
        }
        //std::cerr << "index before ="<< index << "\n";
        //index += header.npart[k]; // next index in mass array
        //std::cerr << "index after  ="<< index << "\n";
      }
    }
  }
}
// ============================================================================
// saveFile():
template <class T>
void CSnapshotGadgetOut<T>::saveFile()
{
  out.clear();
  out.open(this->simname.c_str(),std::ios::out | std::ios::binary);
  if (! out.is_open()) {
    std::cerr << "Unable to open file ["<<this->simname<<"]for writing\n"
          << "aborting....\n";
    std::exit(1);
  }
  writeHeader();
  write();
  out.close();
}
// ============================================================================
// writeHeader():
// write gadget header structure
// return values : 0 success, >0 not a Gadget header data
template <class T>
int CSnapshotGadgetOut<T>::writeHeader()
{
  int status=0;
//  for (int i=0;i<6;i++) {
//    std::cerr << "header.npart["<<i<<"]="<<header.npart[i]<<"\n";
//    std::cerr << "header.mass ["<<i<<"]="<<header.mass [i]<<"\n";
//  }
    // Header block
  writeBlockName("HEAD",sizeof(t_io_header_1));
  bytes_counter=0;
  writeFRecord(sizeof(t_io_header_1));
  writeData((char *)  header.npart         , sizeof(int   ),  6);
  writeData((char *)  header.mass          , sizeof(double),  6);
  writeData((char *) &header.time          , sizeof(double),  1);
  writeData((char *) &header.redshift      , sizeof(double),  1);
  writeData((char *) &header.flag_sfr      , sizeof(int   ),  1);
  writeData((char *) &header.flag_feedback , sizeof(int   ),  1);
  writeData((char *)  header.npartTotal    , sizeof(int   ),  6);
  writeData((char *) &header.flag_cooling  , sizeof(int   ),  1);
  writeData((char *) &header.num_files     , sizeof(int   ),  1);
  writeData((char *) &header.BoxSize       , sizeof(double),  1);
  writeData((char *) &header.Omega0        , sizeof(double),  1);
  writeData((char *) &header.OmegaLambda   , sizeof(double),  1);
  writeData((char *) &header.HubbleParam   , sizeof(double),  1);
  writeData((char *)  header.fill          , sizeof(char  ), 96);
  writeFRecord(sizeof(t_io_header_1));

  //std::cerr << "len1="<<len1<< " len2="<<len2<< " bytes_counter="<<bytes_counter<<"\n";
  if (out.bad() )
    status = 2;
  return status;
}
// ============================================================================
// write():
// write gadget data
template <class T>
int CSnapshotGadgetOut<T>::write()
{
  int blk;
  // POS
  if (bits & POS_BIT) {
    blk=sizeof(T)*3*npartTotal;
    writeBlockName("POS ",blk);
    writeFRecord(blk);
    for(int k=0;k<6;k++) {
      if (header.npart[k]) { // pos exist for the component
        //assert(pos[k]!=NULL);
        if (pos[k])
          writeData((char *) pos[k], sizeof(T)*3, header.npart[k]);
        else
          writeDataValue(0.0,sizeof(T)*3, header.npart[k]);
      }
    }
    writeFRecord(blk);
  }
  // VEL
  if (bits & VEL_BIT) {
    blk=sizeof(T)*3*npartTotal;
    writeBlockName("VEL ",blk);
    writeFRecord(blk);
    for(int k=0;k<6;k++)
      if (header.npart[k]) { // vel exist for the component
        if (vel[k])
          writeData((char *) vel[k], sizeof(T)*3, header.npart[k]);
        else
          writeDataValue(0.0,sizeof(T)*3, header.npart[k]);
      }
    writeFRecord(blk);
  }
  // ID
  blk=sizeof(int)*npartTotal;
  writeBlockName("ID  ",blk);
  writeFRecord(blk);

  if (!(bits & ID_BIT)) {
    std::cerr << "No Ids Bit set, I am going to create them for you....\n";
    int * iid;
    iid = new int[npartTotal];

    for (int i=0; i<npartTotal; i++) iid[i]=i;
    writeData((char *) iid, sizeof(int), npartTotal);
    delete [] iid;
  } else { // There are IDs
    for(int k=0;k<6;k++)
      if (header.npart[k]) {// id exist for the component
        if (id[k])
          writeData((char *) id[k], sizeof(int), header.npart[k]);
        else
          writeDataValue(0,sizeof(int), header.npart[k]);
      }
  }
  writeFRecord(blk);

  // MASS
  if (ntot_withmasses >0 ) {
    blk=sizeof(T)*ntot_withmasses;
    writeBlockName("MASS",blk);
    if (this->verbose) std::cerr << "CSnapshotGadgetOut::write => ntotwithmass="<<ntot_withmasses<<"\n";
    writeFRecord(blk);
    for(int k=0;k<6;k++)
      if (header.npart[k] && header.mass[k]==0) // mass exist for the component
        writeData((char *) mass[k], sizeof(T), header.npart[k]);
    writeFRecord(blk);
  }
  // U
  if (bits & U_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("U   ",blk);
    writeFRecord(blk);
    writeData((char *) intenerg, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // RHO
  if (bits & RHO_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("RHO ",blk);
    writeFRecord(blk);
    writeData((char *) rho, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // HSML
  if (bits & HSML_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("HSML",blk);
    writeFRecord(blk);
    writeData((char *) hsml, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // Pot
  if (bits & POT_BIT) {
    blk=sizeof(T)*npartTotal;
    writeBlockName("POT ",blk);
    writeFRecord(blk);
    for(int k=0;k<6;k++) {
      if (header.npart[k]) { // pos exist for the component
        if (pot[k])
          writeData((char *) pot[k], sizeof(T), header.npart[k]);
        else
          writeDataValue(0.0,sizeof(T), header.npart[k]);
      }
    }
    writeFRecord(blk);
  }
  // ACC
  if (bits & ACC_BIT) {
    blk=sizeof(T)*3*npartTotal;
    writeBlockName("ACCE",blk);
    writeFRecord(blk);
    for(int k=0;k<6;k++)
      if (header.npart[k]) { // acc exist for the component
        if (acc[k])
          writeData((char *) acc[k], sizeof(T)*3, header.npart[k]);
        else
          writeDataValue(0.0,sizeof(T)*3, header.npart[k]);
      }
    writeFRecord(blk);
  }
  // Temp
  if (bits & TEMP_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("NE  ",blk);
    writeFRecord(blk);
    writeData((char *) temp, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // Nh
  if (bits & NH_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("NH  ",blk);
    writeFRecord(blk);
    writeData((char *) nh, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // Sfr
  if (bits & SFR_BIT) {
    assert(header.npart[0]>0);
    blk=sizeof(T)*header.npart[0];
    writeBlockName("SFR  ",blk);
    writeFRecord(blk);
    writeData((char *) sfr, sizeof(T), header.npart[0]);
    writeFRecord(blk);
  }
  // Metal
  if (bits & METAL_BIT) {
    int nb=(header.npart[0]+header.npart[4]);
    assert(nb>0);
    blk=sizeof(T)*nb;
    writeBlockName("Z   ",blk);
    writeFRecord(blk);
    // write metal gas
    if (ptrIsAlloc[0]["metal"]) {
      writeData((char *) metal[0], sizeof(T), header.npart[0]);
    } else {
      writeDataValue(0.0,sizeof(T), header.npart[0]);
    }
    // write metal stars
    if (ptrIsAlloc[4]["metal"]) {
      writeData((char *) metal[4], sizeof(T), header.npart[4]);
    } else {
      writeDataValue(0.0,sizeof(T), header.npart[4]);
    }
    writeFRecord(blk);
  }
  // Age
  if (bits & AGE_BIT) {
    assert(header.npart[4]>0);
    blk=sizeof(T)*header.npart[4];
    writeBlockName("AGE ",blk);
    writeFRecord(blk);
    writeData((char *) age, sizeof(T), header.npart[4]);
    writeFRecord(blk);
  }
  // Write EXTRA
  typename std::map<std::string,std::vector <T>  >::const_iterator it;
  for (it =  s_mapStringVector.begin(); it != s_mapStringVector.end(); it++) {
    if (this->verbose) {
      std::cerr << "Saving EXTRA Tag=["<< it->first << "] of size="<<it->second.size()<<"\n";
    }
    blk=sizeof(T)*it->second.size();
    writeBlockName(it->first,blk);
    writeFRecord(blk);
    writeData((char *) &s_mapStringVector[it->first][0] , sizeof(T), it->second.size());
    writeFRecord(blk);
  }
  return 1;
}
// ============================================================================
// writeBlockName : write Gadget2 file format block
template <class T>
bool CSnapshotGadgetOut<T>::writeBlockName(std::string block_name, int nextblock)
{
  bool status=true;
  if (version == 2 ) { // gadget2 file format
    int dummy=8;
    nextblock += (2*sizeof(int));
    char block[4];
    std::string str ("    ");
    str.copy(block,4,0);
    block_name.copy(block,block_name.length()<=4?block_name.length():4,0);
    writeData((char *) &dummy , sizeof(int),  1); // write
    //writeData((char *) block_name.c_str()   , sizeof(char), 4); // write label
    writeData((char *) block   , sizeof(char), 4); // write label
    writeData((char *) &nextblock           , sizeof(int),  1); // write nextblock
    writeData((char *) &dummy , sizeof(int),  1); // write
    status = out.good();
    if (status && block_name!= "HEAD" && this->verbose)
      std::cerr << "Writing Block Name : <" << block_name << ">\n";
  }
  return status;
}
// ============================================================================
// moveToCom()
template <class T>
std::vector<double> CSnapshotGadgetOut<T>::moveToCom()
{
  std::vector<double> com(6,0.);
  double masstot=0.0;
  // loop on all components to compute COM
  for (int i=0;i<6;i++) {
    if (header.npart[i]) { // component exist
      for (int j=0;j<header.npart[i];j++) {
        T massi=1.0;
        if (mass[i]) {
          massi = mass[i][j];
        }
        masstot += massi;
        if (pos[i]) {
          com[0] += (pos[i][j*3+0]*massi);
          com[1] += (pos[i][j*3+1]*massi);
          com[2] += (pos[i][j*3+2]*massi);
        }
        if (vel[i]) {
          com[3] += (vel[i][j*3+0]*massi);
          com[4] += (vel[i][j*3+1]*massi);
          com[5] += (vel[i][j*3+2]*massi);
        }
      }
    } // header.npart
  } // for i

  // loop on all components to shift to COM
  for (int i=0;i<6;i++) {
    if (header.npart[i]) { // component exist
      for (int j=0;j<header.npart[i];j++) {
        if (pos[i]) {
          pos[i][j*3+0] -= (com[0]/masstot);
          pos[i][j*3+1] -= (com[1]/masstot);
          pos[i][j*3+2] -= (com[2]/masstot);
        }
        if (vel[i]) {
          vel[i][j*3+0] -= (com[3]/masstot);
          vel[i][j*3+1] -= (com[4]/masstot);
          vel[i][j*3+2] -= (com[5]/masstot);
        }
      }
    }
  }
  return com;
}

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CSnapshotGadgetIn<float>;
template class CSnapshotGadgetIn<float>;

//extern template class CSnapshotGadgetIn<double>;
template class CSnapshotGadgetIn<double>;

// C++11
//extern template class CSnapshotGadgetOut<float>;
template class CSnapshotGadgetOut<float>;

//extern template class CSnapshotGadgetOut<double>;
template class CSnapshotGadgetOut<double>;
} // end of namespace
