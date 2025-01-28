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

/* 
	@author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */

#include <iostream>
#include <cstdlib>
#include <assert.h>
#include <algorithm>
#include <cctype> // for toupper()
#include "snapshotnemo.h"
#include "ctools.h"
#include "uns.h"

#define DEBUG 0
#include "unsdebug.h"

namespace uns {

// ============================================================================
// Constructor                                                                 
template <class T> CSnapshotNemoIn<T>::CSnapshotNemoIn(const std::string _name,
			     const std::string _comp, 
			     const std::string _time,
			     const bool verb)
  :CSnapshotInterfaceIn<T>(_name, _comp, _time, verb)
{
  const char * defv[] = { "none=none","VERSION=XXX",NULL };
  const char * argv[] = { "CSnapshotNemoIn",NULL };

  this->interface_type="Nemo";
  this->file_structure = "range";
  this->interface_index=0;
  first_stream=false;
  nemobits=NULL;
  ionbody =NULL;
  iotime  =NULL;
  iopos   =NULL;
  iovel   =NULL;
  iomass  =NULL;
  ioacc   =NULL;
  iopot   =NULL;
  ioaux   =NULL;
  iorho   =NULL;
  iokeys  =NULL;
  ioeps   =NULL;
  mass   = NULL;
  pos    = NULL;
  vel    = NULL;
  acc    = NULL;
  pot    = NULL;
  rho    = NULL;
  aux    = NULL;
  keys   = NULL;
  eps    = NULL;
  last_nbody=0;
  last_nemobits=-1;
  reset_history();
  initparam(const_cast<char**>(argv),const_cast<char**>(defv));
  this->valid=isValidNemo();
}

// ============================================================================
// Destructor                                                                  
template <class T> CSnapshotNemoIn<T>::~CSnapshotNemoIn()
{

  if (ionbody) free ((int   *) ionbody);
  if (iotime ) free ((T *) iotime );
  if (iopos  ) free ((T *) iopos  );
  if (iovel  ) free ((T *) iovel  );
  if (iomass ) free ((T *) iomass );
  if (iorho  ) free ((T *) iorho  );
  if (ioaux  ) free ((T *) ioaux  );
  if (ioacc  ) free ((T *) ioacc  );
  if (iopot  ) free ((T *) iopot  );
  if (ioeps  ) free ((T *) ioeps  );
  if (iokeys ) free ((int   *) iokeys );
  
  if (pos    ) delete [] pos;
  if (vel    ) delete [] vel;
  if (mass   ) delete [] mass;
  if (rho    ) delete [] rho;
  if (aux    ) delete [] aux;
  if (acc    ) delete [] acc;
  if (pot    ) delete [] pot;
  if (keys   ) delete [] keys;
  if (eps    ) delete [] eps;
  
  if (this->valid) close();
}
// ============================================================================
// isValidNemo()                                                               
// return true if it's a NEMO snapshot.                                        
template <class T> bool CSnapshotNemoIn<T>::isValidNemo()
{
  bool status;
  this->valid=true;
  
  if (this->filename == "-") { // we assume here that "-"
    status=true;         // is standard input and a NEMO stream...
    first_stream=true;

    std::string io_nemo_select=realString();
    io_nemo_select+=",read,sp,n,pos,vel,mass,dens,aux,acc,pot,key,e,t,st,b";

    //select_time="all";
    std::string force_select = "all"; 
    status_ionemo=io_nemo(this->filename.c_str(),io_nemo_select.c_str(),
            force_select.c_str(),&ionbody,&iopos,&iovel,&iomass,&iorho,&ioaux,&ioacc,&iopot,&iokeys,&ioeps,
            &iotime, this->select_time.c_str(),&nemobits);

    full_nbody = *ionbody;        
  }
  else { // Normal file
    stream str=stropen(this->filename.c_str(),(char *) "r"); // open NEMO file for reading
    if ( ! str )  status = false; // failed to open
    if (qsf(str)) status = true;  // it's a structured binary file (NEMO)
    else          status = false; // it's not                            
    strclose(str);
    if (status)  {                // it's a NEMO snapshot
      int * ptr=NULL;      // get the full nbody
      std::string io_nemo_select=realString();
      io_nemo_select+=",read,n,t,b";
      if (io_nemo(this->filename.c_str(),io_nemo_select.c_str(),&ptr,&iotime,&nemobits) != 0) {
        io_nemo(this->filename.c_str(),"close");
      } else {
      }
      assert(ptr);
      full_nbody=*ptr;
      free((int *) ptr);
    }
  }
  this->valid=status;
  if (this->valid) {
    if ( ! ( *nemobits & TimeBit)) { // no TimeBit
      this->time_first = 0.0;
    }
    else this->time_first = *iotime;
  }
  return status;
}
// ============================================================================
// getSnapshotRange                                                            
template <class T> ComponentRangeVector * CSnapshotNemoIn<T>::getSnapshotRange()
{
  this->crv.clear();
  if (this->valid) {
    ComponentRange * cr = new ComponentRange();
    cr->setData(0,full_nbody-1);
    cr->setType("all");
    this->crv.push_back(*cr);
    //ComponentRange::list(&crv);
    delete cr;
    if (this->first) {
      this->first       = false;
      this->crv_first   = this->crv;
      this->nbody_first = full_nbody;
      //time_first  = 0.0;
    }
  }
  return &(this->crv);
}
// ============================================================================
// nextFrame()                                                                 
template <class T> int CSnapshotNemoIn<T>::nextFrame(uns::UserSelection &user_select)
{


  int status;  // io_nemo status
  std::string force_select = "all";
  if (! first_stream) { // normal file or second reading (stream)
    std::string io_nemo_select=realString();
    io_nemo_select+=",read,sp,n,pos,vel,mass,dens,aux,acc,pot,key,e,t,st,b";
    status=io_nemo(this->filename.c_str(),io_nemo_select.c_str(),
                   force_select.c_str(),&ionbody,&iopos,&iovel,&iomass,&iorho,&ioaux,&ioacc,&iopot,&iokeys,&ioeps,
                   &iotime, this->select_time.c_str(),&nemobits);
    full_nbody = *ionbody;
    this->crvs = getSnapshotRange();
    user_select.setSelection(user_select.getSelection(),this->crvs);

  } else { // "-" first stream, no need to read
    first_stream=false;
    status=status_ionemo; // status read the first time cf : isValid()
  }

  const uns::t_indexes_tab * index_tab=user_select.getIndexesTab();
  const int nsel_loc=user_select.getNSel();
  this->nsel = user_select.getNSel();
  if (status == -1) {  // Bad nemobits
    PRINT("io_nemo status="<<status<<"\n";);
  } else {
    PRINT("io_nemo status="<<status<<" time="<<*iotime<<"\n";);
  }
  if ( status != 0) {
    if (status == -1) {  // Bad nemobits
      if ( ! ( *nemobits & TimeBit)) { // no TimeBit
        if ( ! iotime )
          iotime = (T *) malloc(sizeof(T));
        std::cerr << "CSnapshotNemoIn::nextFrame => Forcing time to [0.0]\n";
        *(iotime) = 0.0;
      }
    }
    if (status != -2) { // NEMO snapshot must have particles TAG
      if (*ionbody > last_nbody || (last_nemobits>0 && last_nemobits!=(*nemobits))) { // we must resize arrays
        if (pos) delete [] pos;
        if ( *nemobits & PosBit && this->req_bits&POS_BIT)  pos = new T[*ionbody*3];
        else pos=NULL;
        if (vel) delete [] vel;
        if ( *nemobits & VelBit && this->req_bits&VEL_BIT)  vel = new T[*ionbody*3];
        else vel=NULL;
        if (mass) delete [] mass;
        if ( *nemobits & MassBit && this->req_bits&MASS_BIT)  mass = new T[*ionbody];
        else mass=NULL;
        if (rho) delete [] rho;
        if ( *nemobits & DensBit && this->req_bits&RHO_BIT)  rho = new T[*ionbody];
        else rho=NULL;
        if (acc) delete [] acc;
        if ( *nemobits & AccelerationBit && this->req_bits&ACC_BIT)  acc = new T[*ionbody*3];
        else acc=NULL;
        if (aux) delete [] aux;
        if ( *nemobits & AuxBit && this->req_bits&AUX_BIT)  aux = new T[*ionbody];
        else aux=NULL;
        if (pot) delete [] pot;
        if ( *nemobits & PotentialBit && this->req_bits&POT_BIT)  pot = new T[*ionbody];
        else pot=NULL;
        if (keys) delete [] keys;
        if ( *nemobits & KeyBit && (this->req_bits&KEYS_BIT || this->req_bits&ID_BIT))  keys = new int[*ionbody];
        else keys=NULL;
        if (eps) delete [] eps;
        if ( *nemobits & EpsBit && this->req_bits&EPS_BIT)  eps = new T[*ionbody];
        else eps=NULL;
      }
      last_nbody    = *ionbody;  // save nbody
      last_nemobits = *nemobits; // save nemobits
      int cpt=0;
      // fill array according to selection
      for (int i=0; i<*ionbody; i++) {
        int idx=index_tab[i].i;
        if (idx!=-1) { // index selected
          for (int j=0; j<3; j++) {
            if ( *nemobits & PosBit && this->req_bits&POS_BIT) pos[cpt*3+j] = iopos[idx*3+j];
            if ( *nemobits & VelBit && this->req_bits&VEL_BIT) vel[cpt*3+j] = iovel[idx*3+j];
            if ( *nemobits & AccelerationBit && this->req_bits&ACC_BIT) acc[cpt*3+j] = ioacc[idx*3+j];
          }
          if ( *nemobits & MassBit && this->req_bits&MASS_BIT) mass[cpt] = iomass[cpt];
          if ( *nemobits & DensBit && this->req_bits&RHO_BIT) rho[cpt]  = iorho[cpt];
          if ( *nemobits & AuxBit  && this->req_bits&AUX_BIT) aux[cpt]  = ioaux[cpt];
          if ( *nemobits & PotentialBit && this->req_bits&POT_BIT ) pot[cpt]  = iopot[cpt];
          if ( *nemobits & KeyBit  && (this->req_bits&KEYS_BIT || this->req_bits&ID_BIT)) keys[cpt]  = iokeys[cpt];
          if ( *nemobits & EpsBit  && this->req_bits&EPS_BIT) eps[cpt]  = ioeps[cpt];
          cpt++;
          assert(i<nsel_loc);
        }
      }
      assert(nsel_loc==cpt);
    }
  }
  if (nsel_loc) ; // remove compiler warning
  if (this->verbose) std::cerr << "CSnapshotNemoIn::nextFrame status = " << status << "\n";
  if (status == -1) status=1;
  return status;

}
// ============================================================================
// close()                                                                     
template <class T> int CSnapshotNemoIn<T>::close()
{
  int status=0;
  if (this->valid) {
    status = io_nemo(this->filename.c_str(),"close");
    this->end_of_data = false;
  }
  return status;
}
// ============================================================================
// checkBits                                                                   
template <class T> void CSnapshotNemoIn<T>::checkBits(std::string comp,const int bits)
{
  if ( ! ( *nemobits & bits)) { // no XXXbits
    std::cerr << "You have requested the component ["<<comp<<"] which is missing\n"
	      << " in the file. Aborting program.....\n\n";
    std::exit(1);
  }
}
// ============================================================================
// getData                                                               
// return requested array according 'name' selection                                               
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string name,int *n,T **data)
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
  case uns::Acc :
    *data = getAcc();
    *n    = this->getNSel();
    break;        
  case uns::Rho :
    *data = getRho();
    *n    = this->getNSel();
    break;
  case uns::Pot :
    *data = getPot();
    *n    = this->getNSel();
    break;    
  case uns::Eps :
    *data = getEps();
    *n    = this->getNSel();
  case uns::Aux :
  case uns::Hsml :
    *data = getAux();
    *n    = this->getNSel();
    break;
    
  default: ok=false;
  }
  if (*data == NULL) {
    ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData                                                               
// return requested array according 'name' selection                                               
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string comp,const std::string name,int *n,T **data)
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
    if (status && getRho()) {
      *data = &getRho()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Eps :
    if (status && getEps()) {
      *data = &getEps()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
  case uns::Aux :
  case uns::Hsml :
    if (status && getAux()) {
      *data = &getAux()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
    
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] for component <"<<comp<<"> does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData                                                               
// return requested T according 'name' selection
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string name,T *data)
{
  bool ok=true;
  *data=0.0;  
  switch(CunsOut2<T>::s_mapStringValues[name]) {
    case uns::Time   :
     *data = getTime();   
     break;
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData                                                               
// return requested array according 'name' selection                                               
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string name,int *n,int **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;
    
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Keys :
  case uns::Id   :
    *data = getKeys();
    *n    = this->getNSel();
    break;
  default: ok=false;
  }
  if (*data == NULL) {
    ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData                                                               
// return requested array according 'name' selection                                               
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string comp,const std::string name,int *n,int **data)
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
  case uns::Id   :
    if (status && getKeys()) {
      *data = &getKeys()[first];
      *n    = nbody;//this->getNSel();
    } else {
      ok=false;
    }
    break;
    
    default: ok=false;
    }

  if (this->verbose) {
    if (ok) {      
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// getData                                                               
// return requested int according 'name' selection                                               
template <class T> bool CSnapshotNemoIn<T>::getData(const std::string name, int *data)
{
  bool ok=true;
  *data=0;  
  switch(CunsOut2<T>::s_mapStringValues[name]) {
    case uns::Nsel   :
    *data = this->getNSel();
     break;
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoIn::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoIn::getData Value ["<<name<<"] does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
//
// CSnapshotNemoOut CLASS implementation
//

// ----------------------------------------------------------------------------
// constructor
template <class T> CSnapshotNemoOut<T>::CSnapshotNemoOut(const std::string _n, const std::string _t, const bool _v):CSnapshotInterfaceOut<T>(_n, _t, _v)
{
  if (this->simtype != "nemo") {
    std::cerr << "CSnapshotNemoOut::CSnapshotNemoOut Unkwown file type : ["<<this->simtype<<"]\n"
              << "aborting .....\n";
    std::exit(1);
  }
  //
  this->interface_type = "Nemo";
  this->file_structure = "range"; // "range" like file
  // RAZ
  mass   = NULL;
  pos    = NULL;
  vel    = NULL;
  aux    = NULL;
  acc    = NULL;
  pot    = NULL;
  rho    = NULL;
  keys   = NULL;
  eps    = NULL;
  
  ptrIsAlloc["mass" ]=false; 
  ptrIsAlloc["pos"  ]=false; 
  ptrIsAlloc["vel"  ]=false; 
  ptrIsAlloc["pot"  ]=false; 
  ptrIsAlloc["acc"  ]=false; 
  ptrIsAlloc["aux"  ]=false; 
  ptrIsAlloc["keys" ]=false; 
  ptrIsAlloc["rho"  ]=false; 
  ptrIsAlloc["eps"  ]=false;
  ptrIsAlloc["id"   ]=false; 
  
  nbody = -1;
  bits = 0;
  is_saved=false;
  is_closed=false;
}
// ----------------------------------------------------------------------------
// desstructor
template <class T> CSnapshotNemoOut<T>::~CSnapshotNemoOut()
{
  if (mass && ptrIsAlloc["mass"]) delete [] mass;
  if (pos  && ptrIsAlloc["pos" ]) delete [] pos;
  if (vel  && ptrIsAlloc["vel" ]) delete [] vel;
  if (pot  && ptrIsAlloc["pot" ]) delete [] pot;
  if (acc  && ptrIsAlloc["acc" ]) delete [] acc;
  if (aux  && ptrIsAlloc["aux" ]) delete [] aux;
  if (eps  && ptrIsAlloc["eps" ]) delete [] eps;
  if ((keys && ptrIsAlloc["keys"]) ||
      (keys && ptrIsAlloc["id"  ])  ) delete [] keys;
  if (rho  && ptrIsAlloc["rho" ]) delete [] rho;
  close();
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setHeader(void * h)
{
  if (h) {;} // remove compiler warning
  return 0;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setNbody(const int _n)
{
  nbody = _n;
  return nbody;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name, T data)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Time : 
    status = 1;
    time = data;
    bits |= TimeBit;
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name, const int n ,int * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Keys :
  case uns::Id:
    //status = setKeys(n, data, _addr);
    status = setArray(n,1,data,&keys,name.c_str(),KeyBit,_addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {      
      std::cerr << "CCSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}

// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name,std::string array,  const int n ,T * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::All  :
    status = setData(array,n,data,_addr);
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name,std::string array,  const int n ,int * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::All  :
    status = setData(array,n,data,_addr);
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name,  const int n ,T * data,const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Pos  :
    status = setArray(n,3,data,&pos,name.c_str(),PosBit,_addr);
    break;
  case uns::Vel  :
    status = setArray(n,3,data,&vel,name.c_str(),VelBit,_addr);
    break;
  case uns::Mass : 
    status = setArray(n,1,data,&mass,name.c_str(),MassBit,_addr);
    break;
  case uns::Acc :
    status = setArray(n,3,data,&acc,name.c_str(),AccelerationBit,_addr);
    break;
  case uns::Pot :
    status = setArray(n,1,data,&pot,name.c_str(),PotentialBit,_addr);
    break;
  case uns::Aux :
  case uns::Hsml:
    status = setArray(n,1,data,&aux,name.c_str(),AuxBit,_addr);
    break;
  case uns::Rho :
    status = setArray(n,1,data,&rho,name.c_str(),DensBit,_addr);
    break;
  case uns::Eps :
    status = setArray(n,1,data,&eps,name.c_str(),EpsBit,_addr);
    break;
  default: ok=false;
  }
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::setData(std::string name, const int n ,T * data, T * data1, T * data2, const bool _addr)
{
  bool ok=true;
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::All :
    status = setArray(n,1,data ,&mass,"mass",MassBit,_addr);
    status = setArray(n,3,data1,&pos ,"pos" ,PosBit ,_addr);
    status = setArray(n,3,data2,&vel ,"vel" ,VelBit ,_addr);
    break;
  default: ok=false;
  }

  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotNemoOut::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotNemoOut::setData Value ["<<name<<"] does not exist....\n";
      //std::exit(1);
    }
  }
  return status;
}
// ============================================================================
// setArray (T)
template <class T> int CSnapshotNemoOut<T>::setArray(const int _n, const int dim, T * src, T ** dest, const char * name, const int tbits, const bool addr)
{
  if (nbody<0) {
    nbody = _n;
  } else {
    assert(nbody==_n);
  }
  
  if (addr) { // map address
    *dest = src;
  }
  else {
    ptrIsAlloc[name]=true;
    if (*dest)  delete [] (*dest);
    *dest = new T[_n*dim];
    memcpy(*dest,src,sizeof(T)*_n*dim);
  }
  bits |= tbits;
  return 1;
}
// ============================================================================
// setArray (int)
template <class T> int CSnapshotNemoOut<T>::setArray(const int _n, const int dim, int * src, int ** dest, const char * name, const int tbits, const bool addr)
{
  if (addr) { // map address
    *dest = src;
  }
  else {
    ptrIsAlloc[name]=true;
    if (*dest)  delete [] (*dest);
    *dest = new int[_n*dim];
    memcpy(*dest,src,sizeof(int)*_n*dim);
  }
  bits |= tbits;
  return 1;
}

// ----------------------------------------------------------------------------
//
template <class T> int CSnapshotNemoOut<T>::save()
{
  int   * n = &nbody;
  T * t = &time;
  int   * b = &bits;
  int status=0;

  std::string io_nemo_select=realString();
  io_nemo_select += ",save,n,t,x,v,m,p,a,aux,k,dens,e,b";

  if (this->simname=="." || this->simname=="-" || (this->simname!="-" && !tools::Ctools::isFileExist(this->simname))) {
    status=io_nemo(this->simname.c_str(),io_nemo_select.c_str(),
                   &n,&t,&pos,&vel,&mass,&pot,&acc,&aux,&keys,&rho,&eps,&b);
  } else {
    std::cerr << "\n\nfile ["<<this->simname<<"] exist, NEMO output cannot overwrite files, please remove it !!!\nAborting...\n\n";
    std::exit(0);
  }
  if (status!=0) {
    is_saved=true;
  }
  return status;
}
// ============================================================================
// close()                                                                     
template <class T> int CSnapshotNemoOut<T>::close()
{
  int status=0;
  if (is_saved && !is_closed) {
    is_closed = true;
    status = io_nemo(this->simname.c_str(),"close");
  }
  return status;
}
// ============================================================================
// moveToCom()                                                                     
template <class T> std::vector<double> CSnapshotNemoOut<T>::moveToCom()
{
  std::vector<double> com(6,0.);
  double masstot=0.0;
  // compute center of mass
  for (int i=0; i<nbody;i++) {
    float massi;
    if (mass) massi = mass[i];
    else      massi = 1.0;
    masstot+=massi;
    if (pos) {
      com[0] +=(pos[i*3  ]*massi);
      com[1] +=(pos[i*3+1]*massi);
      com[2] +=(pos[i*3+2]*massi);
    }
    if (vel) {
      com[3] +=(vel[i*3  ]*massi);
      com[4] +=(vel[i*3+1]*massi);
      com[5] +=(vel[i*3+2]*massi);
    }
  }
  if (!mass) {
    std::cerr << "CSnapshotNemoOut::moveToCom => No mass in the snapshot, we assum mass=1.0 for each particles...\n";
  }
  // shift to center of mass
  for (int i=0; i<nbody;i++) {
    if (pos) {
      pos[i*3+0] -= (com[0]/masstot);
      pos[i*3+1] -= (com[1]/masstot);
      pos[i*3+2] -= (com[2]/masstot);
    }
    if (vel) {
      vel[i*3+0] -= (com[3]/masstot);
      vel[i*3+1] -= (com[4]/masstot);
      vel[i*3+2] -= (com[5]/masstot);
    }
  }  
  return com;
}
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CSnapshotNemoIn<float>;
template class CSnapshotNemoIn<float>;
//extern template class CSnapshotNemoIn<double>;
template class CSnapshotNemoIn<double>;
// C++11
//extern template class CSnapshotNemoOut<float>;
template class CSnapshotNemoOut<float>;
//extern template class CSnapshotNemoOut<double>;
template class CSnapshotNemoOut<double>;

} // end of uns namespace

//
