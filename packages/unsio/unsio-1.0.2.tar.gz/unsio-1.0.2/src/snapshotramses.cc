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

/*
  @author Jean-Charles Lambert <Jean-Charles.Lambert@lam.fr>
 */

#include "snapshotramses.h"
#include "camr.h"
#include "cpart.h"
#include <limits>
#include "uns.h"
#include "ctools.h"
#include <iostream>
namespace uns {

// ============================================================================
// constructor : CSnapshotRamsesIn
template <class T> CSnapshotRamsesIn<T>::CSnapshotRamsesIn(const std::string _name,
                                     const std::string _comp,
                                     const std::string _time,
                                     const bool verb):
  CSnapshotInterfaceIn<T>(_name, _comp, _time, verb)
{
  first_loc=true;
  particles = new CParticles<T>();
  this->valid=false;
  part = new ramses::CPart(this->filename,this->verbose);
  amr  = new ramses::CAmr(this->filename,this->verbose);

  // convert Header to template format
  t_header = new ramses::T_Header<T>;
  if (amr->isValid()) {
      t_header->omega_m = (T) amr->getHeader()->omega_m;
      t_header->omega_l = (T) amr->getHeader()->omega_l;
      t_header->omega_k = (T) amr->getHeader()->omega_k;
      t_header->omega_b = (T) amr->getHeader()->omega_b;
      t_header->h0 = (T) amr->getHeader()->h0;
      t_header->aexp_ini = (T) amr->getHeader()->aexp_ini;
      t_header->boxlen_ini = (T) amr->getHeader()->boxlen_ini;
      t_header->boxlen = (T) amr->getHeader()->boxlen;
      t_header->aexp = (T) amr->getHeader()->aexp;
      t_header->hexp = (T) amr->getHeader()->hexp;
      t_header->aexp_old = (T) amr->getHeader()->aexp_old;
      t_header->epot_tot_int = (T) amr->getHeader()->epot_tot_int;
      t_header->epot_tot_old = (T) amr->getHeader()->epot_tot_old;
  }

  if (part->isValid() || amr->isValid()) {
    this->valid=true;
    this->interface_type = "Ramses";
    this->file_structure = "component";
    this->interface_index= 2;

    // >> !! NEEDS TO BE FIXED
    // all
    uns::ComponentRange cr;
    cr.setData(0,0);
    cr.setType("all");
    this->crv.clear();
    this->crv.push_back(cr);
    // << !! NEEDS TO BE FIXED

  }
}
// ============================================================================
// desstructor : ~CSnapshotRamsesIn
template <class T> CSnapshotRamsesIn<T>::~CSnapshotRamsesIn()
{
  delete amr;
  delete part;
  delete particles;
}
// ============================================================================
// PURE virtual FUNCTION delared in CSnapshotInterfaceIn
// ============================================================================

// ============================================================================
// getSnapshotRange
template <class T> ComponentRangeVector * CSnapshotRamsesIn<T>::getSnapshotRange()
{

  if (this->valid && this->crv.size()) {
    //this->crv = getCRV();
    //ComponentRange::list(&this->crv);
    if (this->first) {
      this->first       = false;
      this->crv_first   = this->crv;
      //nbody_first = getNtotal();
      //std::cerr << "CSnapshotGadgetIn::getSnapshotRange() = " << nbody_first << "\n";
      //time_first  = getTime();
    }
  }
  return &this->crv;
}
// ============================================================================
// nextFrame
template <class T> int CSnapshotRamsesIn<T>::nextFrame(uns::UserSelection &user_select)
{
  int status=0;
  assert(this->valid==true);
  if (first_loc) {
    first_loc = false;
    if (1 /*checkRangeTime(getTime())*/) {
      // check component bits selected
      user_select.setSelection(this->getSelectPart(),&this->crv,true);
      unsigned int comp_bits=user_select.compBits();

      // set boundaries
      double x[8];

      x[0]=x[2]=x[4]=std::numeric_limits<double>::max() * -1.0; // LOWEST
      x[1]=x[3]=x[5]=std::numeric_limits<double>::max();
      x[6]=0.; // level min
      x[7]=0.; // nlevelmax

      if ((comp_bits&HALO_BIT || comp_bits&STARS_BIT) && part->isValid()) {
        part->setBoundary(x);
        part->loadData(particles,this->req_bits,comp_bits);
      }
      if (comp_bits&GAS_BIT && amr->isValid()) {
        amr->setBoundary(x);
        amr->loadData(particles,this->req_bits);
      }
      if (this->verbose) {
        std::cerr << "ntot   = "<< particles->ntot <<"\n";
        std::cerr << "ngas   = "<< particles->ngas <<"\n";
        std::cerr << "ndm    = "<< particles->ndm <<"\n";
        std::cerr << "nstars = "<< particles->nstars <<"\n";
        std::cerr << "Box len=" << amr->getHeader()->boxlen << "\n";
      }
      //if (this->req_bits) {
      //std::cerr << "Start reordering...\n";
      if (particles->indexes.size()>0) {
        reorderParticles(user_select);
      }
      //std::cerr << "Stop reordering...\n";
      //}
      status = 1;
    }
  }
  return status;
}
// ============================================================================
// close operation
template <class T> int CSnapshotRamsesIn<T>::close()
{
  return 1;
}
// ============================================================================
// reorderParticles
// here we re order particles according to user's component selection
// select_order is a vector containing indexes of components sorted
// according to user request
template <class T> int CSnapshotRamsesIn<T>::reorderParticles(uns::UserSelection &user_select)
{

  if (this->verbose) std::cerr <<"Nbody particles loaded="<<particles->ntot<<"\n";
  std::vector <int> offset_comp(6,-1); // init 6 offsets with value =-1
  std::vector <int> npart_comp(6,0);   // initialise #part per component to ZERO
  char * comp[] = { (char*) "gas",(char*) "halo",(char*) "disk",(char*) "bulge",(char*) "stars",(char*) "bndry",(char*) "all" };
  // get ordering
  std::vector <int> select_order = user_select.selectOrder();

  // component range
  uns::ComponentRange cr;
  this->crv.clear();

  // set #particles per component
  npart_comp[0] = particles->ngas;
  npart_comp[1] = particles->ndm;
  npart_comp[4] = particles->nstars;

  assert(particles->indexes.size()>0);
  assert(select_order.size()<7);
  bool first=true;
  // according to user selection
  // we reformat offset of each components
  for (unsigned int i=0;i<select_order.size(); i++) {
    assert(select_order[i]<7);
    if (first) { // first in the order
      if (npart_comp[select_order[i]] > 0 ) { // part exist for the component
        offset_comp[select_order[i]]=0; // offset 0
        first=false;

      }
    } else { // remaining sorted component
      // current offset of the component
      assert(offset_comp[select_order[i-1]]!=-1);
      offset_comp[select_order[i]]=offset_comp[select_order[i-1]]+ // previous offset
                                   npart_comp[select_order[i-1]];  // size of previous component
    }
    if (!first && npart_comp[select_order[i]]>0) { // if first && #npart > 0
      cr.setData(offset_comp[select_order[i]],     // first part
                 offset_comp[select_order[i]]+     // last part
                 npart_comp[select_order[i]]-1,
                 comp[select_order[i]]);           // component name
      this->crv.push_back(cr);
    }
  }

  if (this->select_part=="all") { // if "all" selected
    uns::ComponentRangeVector crvall;
    uns::ComponentRange cr;
    // all
    cr.setData(0,particles->ntot-1);
    cr.setType("all");
    crvall.push_back(cr);
    user_select.setCrv(crvall);  // we force CRV with "all" only because select_part="all"
  } else {                  // if not "all" selected
    // set the new real user select
    user_select.setCrv(this->crv);  // we rebuild CRV with the user selection
  }
  if (this->verbose)
    uns::ComponentRange::list(&this->crv);

  // all
  cr.setData(0,particles->ntot-1);
  cr.setType("all");
  uns::ComponentRangeVector::iterator it;
  it = this->crv.begin();
  // insert "all" at the beginning of componentRangeVector
  this->crv.insert(it,cr);

  if (this->verbose) {
    for (unsigned int i=0;i<offset_comp.size(); i++) {
      std::cerr << "i="<<i<<"["<<comp[i]<<"] offset="<<offset_comp[i]<<"\n";
    }
  }
  if (this->verbose)
    uns::ComponentRange::list(&this->crv);

  // particles reordering
  if (particles->ntot && this->req_bits) { // exist particles to reorder
    std::vector <int> id;
    std::vector <T> pos,vel,mass,metal;
    if (particles->pos.size()>0)
      pos.resize(particles->pos.size());      // resize new pos   vector
    if (particles->vel.size()>0)
      vel.resize(particles->vel.size());      // resize new pos   vector
    if (particles->mass.size()>0)
      mass.resize(particles->mass.size());    // resize new mass  vector
    if (particles->metal.size()>0)
      metal.resize(particles->metal.size());  // resize new metal vector
    if (particles->id.size()>0)
      id.resize(particles->id.size());     // resize new id vector

    for (long int i=0; i<particles->ntot; i++) {

      bool found=false;

      long int icomp=particles->indexes[i]; // integer component
      if (! (icomp==0 ||icomp==1 || icomp==4)) {
        std::cerr << "ASSERT fails i="<<i<<" icomp="<<icomp<<"\n";
      }
      assert(icomp==0 ||icomp==1 || icomp==4); // gas || halo || stars only
      assert(offset_comp[icomp]>=0);
      unsigned long int istart=offset_comp[icomp]; // index start in the new pos array

      // positions
      if (particles->pos.size()>0) {
        assert((istart*3)+2< particles->pos.size());
        found=true;
        pos[istart*3+0] = particles->pos[i*3+0]; // x
        pos[istart*3+1] = particles->pos[i*3+1]; // y
        pos[istart*3+2] = particles->pos[i*3+2]; // z
      }

      // velocities
      if (particles->vel.size()>0) {
        assert((istart*3)+2<particles->vel.size());
        found=true;
        vel[istart*3+0] = particles->vel[i*3+0]; // x
        vel[istart*3+1] = particles->vel[i*3+1]; // y
        vel[istart*3+2] = particles->vel[i*3+2]; // z
      }

      // masses
      if (particles->mass.size()>0) {
        assert(istart<particles->mass.size());
        found=true;
        mass[istart]    = particles->mass[i];
      }

      // id
      if (particles->id.size()>0) {
        assert(istart<particles->id.size());
        found=true;
        id[istart]    = particles->id[i];
      }
      // metal
      if (particles->metal.size()>0) { // && (icomp==0 || icomp==4)) { // metal for gas or stars
        if (!(istart<particles->metal.size())) {
          std::cerr << " istart ="<<istart<< " metal.size ="<< particles->metal.size() << "\n";
        }
        assert(istart<particles->metal.size());
        found=true;
        metal[istart]    = particles->metal[i];
      }

      if (found) { // found particles
        offset_comp[icomp]++; //  update offset
      }
    }
    // copy back arrays
    particles->pos   = pos;
    particles->vel   = vel;
    particles->mass  = mass;
    particles->metal = metal;
    particles->id    = id;
    //std::cerr << "metal.size() ="<<particles->metal.size() <<"\n";
  }
  return 1;
}
// ============================================================================
// getHeader
template <class T> bool  CSnapshotRamsesIn<T>::getHeader(const std::string name, T * data)
{
  std::string nameupper = tools::Ctools::toupper(name);
  int status = false;
  if (nameupper=="BOXLEN" || nameupper=="BOXSIZE") {
    *data= (T) t_header->boxlen;
    status = true;
  }
  if (nameupper=="OMEGA_M" || nameupper=="OMEGA0") {
    *data= (T) t_header->omega_m;
    status = true;
  }
  if (nameupper=="OMEGA_L" || nameupper=="OMEGALAMBDA") {
    *data= (T) t_header->omega_l;
    status = true;
  }
  if (nameupper=="HUBBLEPARAM" || nameupper=="H0") {
    *data= (T) t_header->h0;
    status = true;
  }
  return status;
}
// ============================================================================
// getData
// return requested array according 'name' selection
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string comp, const std::string name, int *n,T **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=this->getRangeSelect(comp.c_str(),&nbody,&first,&last,false); // find components ranges
  if (!status && comp=="all") { // retreive all particles selected by the user
    status=1;
    first=0;
    nbody=particles->ntot;
  }
  if (!status) { // "comp" is not a known conponent, might be an array

    int a_index=-1;
    bool res;
    switch(CunsOut2<T>::s_mapStringValues[comp]) {
    case uns::Hydro : // hydro array requested
      res=tools::Ctools::isStringANumber(name,a_index);
      if (res) { // string is a number
        if (a_index >= 0 && a_index < particles->nvarh) {
          *data=&particles->hydro[a_index][0];
          *n=particles->hydro[a_index].size();
          if (*n == 0) { // array not processed
            ok = false;
          }
        } else {
          std::cerr << "CSnapshotGadgetIn::getData uns::Hydro index out of range ["
                    <<a_index<<"]\n";
          ok=false;
        }
      } else {
        ok=false;
      }
      break;
    default: ok=false;            
    }

  } else {
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
      if (status && particles->pos.size()>0) {
        *data = &particles->pos[first*3];
        *n    = nbody;//getNSel();
      } else {
        ok=false;
      }
      break;
    case uns::Vel  :
      if (status && particles->vel.size()>0) {
        *data = &particles->vel[first*3];
        *n    = nbody;//getNSel();
      } else {
        ok=false;
      }
      break;
    case uns::Mass  :
      if (status && particles->mass.size()) {
        *data = &particles->mass[first];
        *n    = nbody;//getNSel();
      } else {
        ok=false;
      }
      break;

    case uns::Rho :
      if (status && comp=="gas" && particles->rho.size()>0) {
        *data = &particles->rho[0];
        *n=particles->rho.size();
      } else {
        ok=false;
      }
      break;
    case uns::Pot :
      if (status && comp=="gas" && particles->phi.size()>0) {
        *data = &particles->phi[0];
        *n=particles->phi.size();
      } else {
        ok=false;
      }
      break;
    case uns::Acc :
      if (status && comp=="gas" && particles->acc.size()>0) {
        *data = &particles->acc[0];
        *n=particles->acc.size()/3;
      } else {
        ok=false;
      }
      break;
    case uns::U :
      ok=false;
      break;
    case uns::Hsml :
      if (status && comp=="gas" && particles->hsml.size()>0) {
        *data = &particles->hsml[0];
        *n=particles->hsml.size();
      } else {
        ok=false;
      }
      break;
    case uns::Temp :
      if (status && comp=="gas" && particles->temp.size()>0) {
        *data = &particles->temp[0];
        *n=particles->temp.size();
      } else {
        ok=false;
      }
      break;
    case uns::Age :
      if (status && comp=="stars" && particles->age.size()>0) {
        *data = &particles->age[0];
        *n=particles->age.size();
      } else {
        ok=false;
      }
      break;
    case uns::Metal :
      if (status && particles->metal.size()>0) {
        *data = &particles->metal[first];
        *n    = nbody;
      } else {
        ok=false;
      }
      break;

    default: ok=false;
    }
  }
  if (ok && !*data &&
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
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string name,int *n,T **data)
{
  bool ok=true;
  *data = NULL;
  *n = 0;
  int first=0;
  bool status=true;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Nsel   :
    if (status) {
      *n    = particles->ntot;;
    } else {
      ok=false;
    }
    break;
  case uns::Pos   :
    if (particles->pos.size()>0) {
      *data = &particles->pos[first*3];
      *n    = particles->pos.size()/3;
    } else {
      ok=false;
    }
    break;
  case uns::Vel  :
    if (particles->vel.size()>0) {
      *data = &particles->vel[first*3];
      *n    = particles->vel.size()/3;
    } else {
      ok=false;
    }
    break;
  case uns::Mass  :
    if (particles->mass.size()) {
      *data = &particles->mass[first];
      *n    = particles->mass.size();
    } else {
      ok=false;
    }
    break;
  case uns::Rho :
    if (particles->rho.size()>0) {
      *data = &particles->rho[0];
      *n=particles->rho.size();
    } else {
      ok=false;
    }
    break;
  case uns::Pot :
    if (particles->phi.size()>0) {
      *data = &particles->phi[0];
      *n=particles->phi.size();
    } else {
      ok=false;
    }
    break;
  case uns::Acc :
    if (particles->acc.size()>0) {
      *data = &particles->acc[0];
      *n=particles->acc.size()/3;
    } else {
      ok=false;
    }
    break;
  case uns::U :
      ok=false;
    break;
  case uns::Hsml :
    if (particles->hsml.size()>0) {
      *data = &particles->hsml[0];
      *n=particles->hsml.size();
    } else {
      ok=false;
    }
    break;
  case uns::Temp :
    if (particles->temp.size()>0) {
      *data = &particles->temp[0];
      *n=particles->temp.size();
    } else {
      ok=false;
    }
    break;
  case uns::Age :
    if (particles->age.size()>0) {
      *data = &particles->age[0];
      *n=particles->age.size();
    } else {
      ok=false;
    }
    break;

  default: ok=false;
  }
  if (ok && !*data &&
      (CunsOut2<T>::s_mapStringValues[name]!=uns::Nbody &&
       CunsOut2<T>::s_mapStringValues[name]!=uns::Nsel)) ok = false; // not ok because array is NULL
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
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string name,T *data)
{
  bool ok=true;
  *data=0.0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Time   :
    *data = amr->getHeader()->time; // find time
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
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string comp,const std::string name,int *n, int **data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=this->getRangeSelect(comp.c_str(),&nbody,&first,&last,false); // find components ranges
  if (!status && comp=="all") { // retreive all particles selected by the user
    status=1;
    first=0;
    nbody=particles->ntot;
  }
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Id :
    if (status && particles->id.size()>0) {
      *data = &particles->id[first];
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
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string name,int *n, int **data)
{
  bool ok=false;
  return ok;
}
// ============================================================================
// getData
// return requested int according 'name' selection
template <class T> bool CSnapshotRamsesIn<T>::getData(const std::string name,int *data)
{
  bool ok=true;
  *data=0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Nsel   :
    *data = particles->ntot;
    break;
  case uns::Ngas   :
    *data = particles->ngas;
    break;
  case uns::Nhalo   :
    *data = particles->ndm;
    break;
  case uns::Nstars  :
    *data = particles->nstars;
    break;
  case uns::Nvarh   :
    *data = particles->nvarh;
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

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CSnapshotRamsesIn<float>;
template class CSnapshotRamsesIn<float>;

//extern template class CSnapshotRamsesIn<double>;
template class CSnapshotRamsesIn<double>;
} // end of namespace uns
