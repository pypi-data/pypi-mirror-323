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

#include <cstdlib>
#include "snapshotgadgeth5.h"
#include "ctools.h"
#define DEBUG 0
#include "unsdebug.h"
#include "uns.h"
#include <sstream>
#include <limits>

namespace  uns {

#if ((H5_VERS_MINOR==8 && H5_VERS_RELEASE>=13)||(H5_VERS_MINOR>8))
#define PRINT_ERROR  error.printErrorStack();
#else
#define PRINT_ERROR  error.printError();
#endif

// ----------------------------------------------------------------------------
// READING constructor
template <class T>
CSnapshotGadgetH5In<T>::CSnapshotGadgetH5In(const std::string _name,
                                                        const std::string _comp,
                                                        const std::string _time,
                                                        const bool verb)
  :CSnapshotInterfaceIn<T>(_name, _comp, _time, verb)
{
  this->valid=0;
  first_loc=true;
  myH5 = NULL;
  try {
    /*
     * Turn off the auto-printing when failure occurs so that we can
     * handle the errors appropriately
     */
    Exception::dontPrint();
    myH5 = new GH5<T>(this->filename,H5F_ACC_RDONLY,verb);
    this->valid=1;
    this->interface_type = "Gadget3";
    this->interface_index=3;
    this->file_structure = "component";

    storeComponents(); // fill up crv structure with particles number

    // clear vectors
    pos.clear();
    mass.clear();
    vel.clear();
    rho.clear();
    hsml.clear();
    temp.clear();
    nh.clear();
    sfr.clear();
    age.clear();
    id.clear();
    uenerg.clear();
    s_metal.clear();
    g_metal.clear();
  }
  catch (...) {
    this->valid=0;
    if (this->verbose) {
      std::cerr << "WARNING: not a Gadget3 (HDF5) file...\n";
    }
  }
}
// ----------------------------------------------------------------------------
// destructor
template <class T>
CSnapshotGadgetH5In<T>::~CSnapshotGadgetH5In()
{
  if (myH5) {
    delete myH5;
  }
}

// ============================================================================
// storeComponents
template <class T>
void CSnapshotGadgetH5In<T>::storeComponents()
{
  uns::ComponentRange cr;
  // all
  cr.setData(0,myH5->getNpartTotal()-1);
  cr.setType("all");
  this->crv.clear();
  this->crv.push_back(cr);
  // components
  const char * comp [] = { "gas", "halo", "disk", "bulge", "stars", "bndry"};
  for(int k=0,start=0; k<6; k++)  {
    if (myH5->getHeader().NumPart_Total[k]) {
      cr.setData(start,start+myH5->getHeader().NumPart_Total[k]-1,comp[k]);
      this->crv.push_back(cr);
      start+=myH5->getHeader().NumPart_Total[k];
    }
  }
}

// ============================================================================
// nextFrame
template <class T>
int CSnapshotGadgetH5In<T>::nextFrame(uns::UserSelection &user_select)
{
  int status=0;
  assert(this->valid==true);
  if (first_loc) {
    first_loc = false;
    if (this->checkRangeTime(getTime())) {

      // ** very important **
      // update user_select object according to which particles are
      // present in the file (this->crv populated via storeComponents)
      // then getRangeSelect() will return later, in getData, indexes
      // first,last of the component in memory
      user_select.setSelection(this->getSelectPart(),&this->crv);
      if (this->select_part=="all") {    // if "all" selected
        user_select.setCrv(this->crv);   // CRVselect must be components presents in file
      }
      // ** very important **

      // compute nbody selected (nsel)
      this->nsel=user_select.getNSel();
      comp_bits=user_select.compBits();
      //read(user_select);
      status = 1;
    }
  }
  return status;
}
// ============================================================================
// close
template <class T>
int CSnapshotGadgetH5In<T>::close()
{
//  if (is_open) in.close();
//  is_open = false;

  return 1;
}
// ============================================================================
// getSnapshotRange
template <class T>
ComponentRangeVector * CSnapshotGadgetH5In<T>::getSnapshotRange()
{
  return &this->crv;
}
// ============================================================================
// read file and put data on cache
template <class T>
void CSnapshotGadgetH5In<T>::read(uns::UserSelection user_select)
{


}
// ============================================================================
// getData methods
// ============================================================================
template <class T>
//template <class U> std::vector<U> CSnapshotGadgetH5In<T>::getData(const std::string comp,const std::string name)
template <class U> void CSnapshotGadgetH5In<T>::getData(const std::string comp,const std::string name)
{

  //std::vector<U> v =  myH5->getDataset(name);
  //return v;

}
// ============================================================================
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string name,int *n,T ** data)
{
  bool ok=getData("all",name,n,data);
  return ok;
}
// ============================================================================
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string name , T * data )
{
  bool ok=true;
  *data=0.0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Time   :
    *data = getTime();
    break;
  case uns::Redshift   :
    *data = myH5->getHeader().Redshift;
    break;
  default: ok=false;
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
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string name,int *n,int   ** data)
{
  bool ok=getData("all",name,n,data);
  return ok;
}
// ============================================================================
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string name, int   * data )
{
  bool ok=true;
  *data=0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Nsel   :
    *data = this->getNSel();
    break;
  case uns::Ngas   :
    *data = myH5->getHeader().NumPart_Total[0];
    break;
  case uns::Nhalo   :
    *data = myH5->getHeader().NumPart_Total[1];
    break;
  case uns::Ndisk   :
    *data = myH5->getHeader().NumPart_Total[2];
    break;
  case uns::Nbulge   :
    *data = myH5->getHeader().NumPart_Total[3];
    break;
  case uns::Nstars   :
    *data = myH5->getHeader().NumPart_Total[4];
    break;
  case uns::Nbndry   :
    *data = myH5->getHeader().NumPart_Total[5];
    break;
  default: ok=false;
  }
  if (ok && !*data) ok = false; // not ok because array is NULL
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetH5In::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetH5In::getData Value ["<<name<<"] does not exist or empty\n";
    }
  }
  return ok;
}
// ============================================================================
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string comp, const std::string name,int * n,T ** data)
{

  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=false;

  if (comp!="STREAM") {
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
    if (status && this->req_bits&POS_BIT && loadCommonDataset("Coordinates",pos,3)) {
      *data = &pos[first*3];// &getPos()[first*3];
      *n    = nbody;
    } else {
      ok=false;
    }
    break;
  case uns::Vel   :
    if (status && this->req_bits&VEL_BIT && loadCommonDataset("Velocities",vel,3)) {
      *data = &vel[first*3];// &getPos()[first*3];
      *n    = nbody;
    } else {
      ok=false;
    }
    break;
  case uns::Mass   :
    if (status && this->req_bits&MASS_BIT && loadCommonDataset("Masses",mass,1)) {
      *data = &mass[first];// &getPos()[first*3];
      *n    = nbody;
    } else {
        if (status && this->req_bits&MASS_BIT && loadCommonDataset("Mass",mass,1)) {
          *data = &mass[first];// &getPos()[first*3];
          *n    = nbody;
        } else {  
            ok=false;
          }
    }
    break;
  case uns::Acc :
      if (status && this->req_bits&ACC_BIT && loadCommonDataset("Acceleration",acc,3)) {
        *data = &acc[first*3];// &getPos()[first*3];
        *n    = nbody;
      } else {
        ok=false;
      }
      break;
  case uns::Pot   :
    if (status && this->req_bits&POT_BIT && loadCommonDataset("Potential",pot,1)) {
      *data = &pot[first];// &getPos()[first*3];
      *n    = nbody;
    } else {
      ok=false;
    }
    break;
  case uns::Rho :
    if (status && this->req_bits&RHO_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/Density",rho)) {
      *data = &rho[0];
      *n = rho.size();
    } else {
      ok=false;
    }
    break;
  case uns::U :
    if (status && this->req_bits&U_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/InternalEnergy",uenerg)) {
      *data = &uenerg[0];
      *n = uenerg.size();
    } else {
      ok=false;
    }
    break;
  case uns::Ne:
    {}
  case uns::Temp :
    if (status && this->req_bits&TEMP_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/ElectronAbundance",temp)) {
      *data = &temp[0];
      *n = temp.size();
    } else {
      ok=false;
    }
    break;
  case uns::Nh :
    if (status && this->req_bits&NH_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/NeutralHydrogenAbundance",nh)) {
      *data = &nh[0];
      *n = nh.size();
    } else {
      ok=false;
    }
    break;
  case uns::Sfr :
    if (status && this->req_bits&SFR_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/StarFormationRate",sfr)) {
      *data = &sfr[0];
      *n = sfr.size();
    } else {
      ok=false;
    }
    break;
  case uns::Hsml :
    if (status && this->req_bits&HSML_BIT && (comp=="gas" || comp=="all") && loadDataset("/PartType0/SmoothingLength",hsml)) {
      *data = &hsml[0];
      *n = hsml.size();
    } else {
      ok=false;
    }
    break;
  case uns::Metal :
    if (status && this->req_bits&METAL_BIT && comp=="gas" && loadDataset("/PartType0/Metallicity",g_metal)) {
      *data = &g_metal[0];
      *n = g_metal.size();
    } else {
      if (status && this->req_bits&METAL_BIT && comp=="stars" && loadDataset("/PartType4/Metallicity",s_metal)) {
        *data = &s_metal[0];
        *n = s_metal.size();
      }
      else {
        ok=false;
      }
    }
    break;
  case uns::Age :
    if (status && this->req_bits&AGE_BIT && (comp=="stars"  || comp=="all") && loadDataset("/PartType4/StellarFormationTime",age)) {
      *data = &age[0];
      *n = age.size();
    }
    else {
      ok=false;
    }
    break;
  default: // unkown name
      if (comp=="STREAM") { // data stream reading
      } else {
        ok=false;
      }
  }
  if (ok && !*data &&
      (CunsOut2<T>::s_mapStringValues[name]!=uns::Nbody &&
       CunsOut2<T>::s_mapStringValues[name]!=uns::Nsel)) ok = false; // not ok because array is NULL
  if (this->verbose) {
    if (ok) {
      std::cerr << "CSnapshotGadgetH5In::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetH5In::getData Value ["<<name<<"] for component <"<<comp<<"> does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
//
template <class T>
bool CSnapshotGadgetH5In<T>::getData(const std::string comp, const std::string name,
                                     int *n ,int ** data)
{
  bool ok=true;
  *data=NULL;
  *n = 0;

  int nbody,first,last;
  bool status=false;

  if (comp!="STREAM") {
    status=this->getRangeSelect(comp.c_str(),&nbody,&first,&last,false); // find components ranges
    if (!status && comp=="all") { // retreive all particles selected by the user
      status=1;
      first=0;
      nbody=this->getNSel();
    }
  }
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Id :
    if (status && loadCommonDataset("ParticleIDs",id,1)) {
      *data = &id[first];
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
      std::cerr << "CSnapshotGadgetH5In::getData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "**WARNING** CSnapshotGadgetH5In::getData Value ["<<name<<"] for component <"<<comp<<"> does not exist...\n";
    }
  }
  return ok;
}
// ============================================================================
// loadDataset
// this method load TAG dataset
template <class T>
template <class U>
bool CSnapshotGadgetH5In<T>::loadDataset(std::string dataset, std::vector<U> &data) {
    bool ok = false;
    const int dim=1;

    if (data.size() == 0) {  // not loaded yest
        try {            
            
            U dummy = (U)1;  // use dummy variable to help compiler to guess return type
            GH5<T> *dataH5 = NULL;
            unsigned int offset = 0;
            unsigned int total_alloc = 0;
            for (int ifile = 0; ifile < myH5->getHeader().NumFilesPerSnapshot; ifile++) {
                if (myH5->getHeader().NumFilesPerSnapshot > 1) {
                    // create file name
                    std::size_t f1 = this->filename.find(".hdf5");              // search ".hdf5"
                    std::size_t f2 = this->filename.find_last_of(".", f1 - 1);  // search last "."
                    std::ostringstream stm;
                    stm << "." << ifile << ".hdf5";
                    std::string myfile = this->filename.substr(0, f2);
                    myfile = myfile + stm.str();
                    if (this->verbose) {
                      std::cerr << "myfile = " << myfile << "\n";
                    }
                    try {
                        Exception::dontPrint();
                        dataH5 = new GH5<T>(myfile, H5F_ACC_RDONLY, false);
                    } catch (...) {
                        std::cerr << "ERROR !! [" << myfile << "] not a Gadget3 (HDF5) file...\n";
                    }
                } else {
                    dataH5 = myH5;
                }

                // load dataset in a local vector
                std::vector<U> vec = dataH5->getDataset(dataset, dummy);
                ok = true;
                total_alloc += vec.size();
                data.resize(total_alloc);  // re-allocate dataset for next data
                memcpy(&data[offset * dim], &vec[0], vec.size() * sizeof(U));
                offset += vec.size() / dim;
            }
            //assert(offset == myH5->getHeader().NumPart_Total[comp_id]);
            if (dataH5 != myH5) {  // it's a split file
                delete dataH5;
            }
        } catch (...) {
            if (this->verbose) {
                std::cerr << "CSnapshotGadgetH5In<T>::loadDataset [" << dataset << "] fails......\n";
            }
            ok = false;
        }
    } else {
        ok = true;
    }
    return ok;
}
// ============================================================================
// loadCommonDataset
// common dataset are pos,vel,mass,id
// this method load TAG dataset for all components selected by user
template <class T>
template <class U>
bool CSnapshotGadgetH5In<T>::loadCommonDataset(std::string tag, std::vector<U> &data, const int dim)
{
    std::map<std::string, int> compo_indx;
    compo_indx["gas"] = 0;
    compo_indx["halo"] = 1;
    compo_indx["disk"] = 2;
    compo_indx["bulge"] = 3;
    compo_indx["stars"] = 4;
    compo_indx["bndry"] = 5;

    bool ok = false;
    if (data.size() == 0) {  // not loaded yest
        try {
            data.resize(this->getNSel() * dim);  // total selected
            //unsigned long int cpt_copied = 0;    // track #elements copied into datat vector
            ComponentRangeVector *crv = this->user_select.getCrvFromSelection();

            int npartOffset[6];
            unsigned int npart_loaded[6];
            // compute offset in case of multiple gadget file
            int nextoffset = 0;
            for (int i = 0; i < 6; i++) {
                npart_loaded[i] = 0;
                //std::map<std::string, int>::iterator it;
                //it = compo_indx.find((*crv)[i].type);
                //if (this->select_part == "all" || it != compo_indx.end()) {
                    bool ok = false;
                    for (unsigned int j = 0; j < crv->size(); j++) {
                        std::map<std::string, int>::iterator it;
                        it = compo_indx.find((*crv)[j].type);
                        //if (this->select_part == "all" || it != compo_indx.end()) {
                        if (this->select_part == "all" || (it != compo_indx.end() && it->second==i)) {  
                            ok = true;
                            break;
                        }
                    }
                    if (ok) {
                        //npartOffset[i] = npartOffset[i-1]+myH5->getHeader().NumPart_Total[i-1];
                        npartOffset[i] = nextoffset;
                        nextoffset += myH5->getHeader().NumPart_Total[i];
                        //      std::cerr
                        //          << "npartOffset["<<i<<"]="<<npartOffset[i]<<" npartOffset["<<i-1<<"]="
                        //          <<npartOffset[i-1]<<" header.npartTotal["<<i-1<<"]="<<myH5->getHeader().NumPart_Total[i-1]<<"\n";
                    } else {
                        npartOffset[i] = 0;
                    }
                //} else {
                //    npartOffset[i] = 0;
                //}
            }

            GH5<T> *dataH5 = NULL;
            std::map<std::string, bool> same_mass_done; // if same mass and multiple files must be done only for the first file
            same_mass_done["gas"]   = false;
            same_mass_done["halo"]  = false;
            same_mass_done["disk"]  = false;
            same_mass_done["bulge"] = false;
            same_mass_done["stars"] = false;
            same_mass_done["bndry"] = false;
            for (int ifile = 0; ifile < myH5->getHeader().NumFilesPerSnapshot; ifile++) {
                if (myH5->getHeader().NumFilesPerSnapshot > 1) {
                    // create file name
                    std::size_t f1 = this->filename.find(".hdf5");              // search ".hdf5"
                    std::size_t f2 = this->filename.find_last_of(".", f1 - 1);  // search last "."
                    std::ostringstream stm;
                    stm << "." << ifile << ".hdf5";
                    std::string myfile = this->filename.substr(0, f2);
                    myfile = myfile + stm.str();
                    if (this->verbose) {
                      std::cerr << "myfile = " << myfile << "\n";
                    }
                    try {
                        Exception::dontPrint();
                        dataH5 = new GH5<T>(myfile, H5F_ACC_RDONLY, false);
                    } catch (...) {
                        std::cerr << "ERROR !! [" << myfile << "] not a Gadget3 (HDF5) file...\n";
                    }
                } else {
                    dataH5 = myH5;
                }
                for (unsigned int i = 0; i < crv->size(); i++) {
                    std::map<std::string, int>::iterator it;
                    it = compo_indx.find((*crv)[i].type);
                    if (it != compo_indx.end()) {  // key exist
                        std::stringstream myid("");
                        myid << (*it).second;
                        std::string dataset = "/PartType" + myid.str() + "/" + tag;
                        if (this->verbose) std::cerr << dataset << "\n";

                        U dummy = (U)1;  // use dummy variable to help compiler to guess return type
                        // load dataset in a local vector
                        std::vector<U> vec;
                        if ((tag == "Masses" || tag == "Mass") && myH5->getHeader().MassTable[(*it).second] != 0.0 && !same_mass_done[(*it).first]) {
                            same_mass_done[(*it).first]=true; // proceed same mass only once
                            vec.resize(myH5->getHeader().NumPart_Total[(*it).second]);
                            U same_mass = myH5->getHeader().MassTable[(*it).second];
                            std::fill(vec.begin(), vec.end(), same_mass);
                            npart_loaded[(*it).second] += vec.size() / dim;
                            assert(npart_loaded[(*it).second] <= myH5->getHeader().NumPart_Total[(*it).second]);
                            memcpy(&data[npartOffset[(*it).second] * dim], &vec[0], vec.size() * sizeof(U));
                            npartOffset[(*it).second] += (vec.size() / dim);
                            ok = true;
                        } else {
                            try {
                                vec = dataH5->getDataset(dataset, dummy);
                                npart_loaded[(*it).second] += vec.size() / dim;
                                //std::cerr << "vec size/dim ="<< vec.size() / dim << " npart_loaded[(*it).second]" << npart_loaded[(*it).second] << "\n";
                                assert(npart_loaded[(*it).second] <= myH5->getHeader().NumPart_Total[(*it).second]);
                                memcpy(&data[npartOffset[(*it).second] * dim], &vec[0], vec.size() * sizeof(U));
                                npartOffset[(*it).second] += (vec.size() / dim);
                                ok = true;
                            } catch (...) {
                                if (this->verbose) {
                                    std::cerr << "WARNING !!! : error while reading Dataset["
                                              << dataset << "]\n";
                                }
                                if (dataH5 != myH5) {  // it's a split file
                                    delete dataH5;
                                }
                                throw -1;
                            }
                        }

                        // if (this->verbose) std::cerr << " size=" << vec.size() << " size/dim=" << vec.size() / dim << "\n";
                        // if (vec.size() > 0) ok = true;
                        // int nbody, first, last;
                        // assert((*crv)[i].type != "all");
                        // bool status = this->getRangeSelect((*crv)[i].type.c_str(), &nbody, &first, &last, false);
                        // assert(status == true);
                        // // copy back local vector to main memory vector
                        // memcpy(&data[first * dim], &vec[0], vec.size() * sizeof(U));
                        // cpt_copied += vec.size();
                    }
                }
                if (dataH5 != myH5) {  // it's a split file
                    delete dataH5;
                }
                // assert(cpt_copied <= data.size());  // must matched
                ok = true;
            }
        } catch (int e) {
            if (this->verbose) {
                std::cerr << "WARNING !!! : error while loadCommonDataset....\n";
            }
            data.clear();
        }
    } else {
        ok = true;
    }

    return ok;
}
// ----------------------------------------------------------------------------
//
//                     CSnapshotGadgetH5Out CLASS implementation
//
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// WRITING constructor
template <class T>
CSnapshotGadgetH5Out<T>::CSnapshotGadgetH5Out(const std::string _n, const std::string _t, const bool _v):CSnapshotInterfaceOut<T>(_n, _t, _v)
{
  myH5 = NULL;
  try {
    /*
     * Turn off the auto-printing when failure occurs so that we can
     * handle the errors appropriately
     */
    Exception::dontPrint();
    myH5 = new GH5<T>(this->simname,H5F_ACC_TRUNC,this->verbose);
    this->interface_type = "Gadget3";
    this->file_structure = "component"; // "component" like file
    if (this->verbose)
      std::cerr << "CSnapshotGadgetH5Out::CSnapshotGadgetH5Out simname = " << this->simname <<"\n";
    bzero(&header,sizeof(t_h5_header));

    // setup header
    header.MassTable.resize(6);
    header.NumFilesPerSnapshot=1;
    header.NumPart_ThisFile.resize(6);
    header.NumPart_Total.resize(6);
    header.NumPart_Total_HighWord.resize(6);

   // detect precision
   if ((std::numeric_limits<T>::max()) == (std::numeric_limits<double>::max())) {
      header.Flag_DoublePrecision=1;
    };

  } catch (...) {
    if (this->verbose) {
      std::cerr << "WARNING: impossible to create Gadget3 (HDF5) output file...\n";
    }
    throw(-1);
    std::exit(1);
  }
}
// ----------------------------------------------------------------------------
// destructor
template <class T>
CSnapshotGadgetH5Out<T>::~CSnapshotGadgetH5Out()
{
  if (myH5) {
    delete myH5;
  }
}
// ----------------------------------------------------------------------------
// putHeader
template <class T>
int CSnapshotGadgetH5Out<T>::setHeader(void * _header)
{
  memcpy(&header,_header,sizeof(t_h5_header));
  return 1;
}
// ============================================================================
// setNbody:
template <class T>
int CSnapshotGadgetH5Out<T>::setNbody(const int _nbody)
{
  return 1;
}
// ----------------------------------------------------------------------------
// setData
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name,T  data)
{
  int status=0;

  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Time :
    status = 1;
    header.Time = data;
    //status=myH5->setAttribute("Time",&header.Time,1);
    break;
  default: status=0;
  }

  if (this->verbose) {
    if (status) {
      std::cerr << "CSnapshotGadgetH5Out::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** SnapshotGadgetH5Out::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
// setData("gas","pos",n,gas_array,true)
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name,std::string array,  const int n ,T * data,const bool _addr)
{
  int status=0;
  try {
    switch(CunsOut2<T>::s_mapStringValues[array]) {
    case uns::Pos  :
      status = saveCommonDataset(name,"Coordinates",n,data,3);
      break;
    case uns::Vel  :
      status = saveCommonDataset(name,"Velocities",n,data,3);
      break;
    case uns::Mass :
      status = saveCommonDataset(name,"Masses",n,data,1);
      break;
    case uns::Pot  :
      status = saveCommonDataset(name,"Potential",n,data,1);
      break;
    case uns::Acc  :
      status = saveCommonDataset(name,"Acceleration",n,data,3);
      break;
    case uns::Hsml :
      status = saveCommonDataset(name,"SmoothingLength",n,data,1);
      break;
    case uns::Rho  :
      status = saveCommonDataset(name,"Density",n,data,1);
      break;
    case uns::U  :
      if (name=="gas") {
        status = saveCommonDataset(name,"InternalEnergy",n,data,1);
      }
      break;
    case uns::Ne:
    case uns::Temp  :
      if (name=="gas") {
        status = saveCommonDataset(name,"ElectronAbundance",n,data,1);
      }
      break;
    case uns::Nh  :
      if (name=="gas") {
        status = saveCommonDataset(name,"NeutralHydrogenAbundance",n,data,1);
      }
      break;
    case uns::Sfr  :
      if (name=="gas") {
        status = saveCommonDataset(name,"StarFormationRate",n,data,1);
      }
      break;
    case uns::Age  :
      if (name=="stars") {
        status = saveCommonDataset(name,"StellarFormationTime",n,data,1);
      }
      break;
    case uns::GasMetal  :
      if (name=="gas")
        status = saveCommonDataset(name,"Metallicity",n,data,1);
      break;
    case uns::StarsMetal  :
      if (name=="stars")
      status = saveCommonDataset(name,"Metallicity",n,data,1);
      break;
    case uns::Metal  :
      if (name=="gas" || name=="stars") {
        status = saveCommonDataset(name,"Metallicity",n,data,1);
      }
      break;
    default: status=0;
    }
  } catch (...) {
    std::cerr << "Error during CSnapshotGadgetH5Out<T>::setData(..)\n";
  }
  if (this->verbose) {
    if (status) {
      std::cerr << "CSnapshotGadgetH5Out::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      if (name != "EXTRA") {
        std::cerr << "** WARNING ** CSnapshotGadgetH5Out::setData  Value ["<<name<<"]=<"<< array<<"] does not exist.....\n";
      } else {
        std::cerr << "CSnapshotGadgetH5Out::setData EXTRA tags["<<array<<"]\n";
      }
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name, const int n ,T * data,const bool _addr)
{
  int status=0;
  switch(CunsOut2<T>::s_mapStringValues[name]) {
  case uns::Rho :
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::Hsml:
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::U:
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::Ne    :
  case uns::Temp  :
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::Nh  :
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::Sfr  :
    status = setData("gas",name,n,data,_addr);
    break;
  case uns::Age  :
    status = setData("stars",name,n,data,_addr);
    break;
  case uns::GasMetal  :
    status = setData("gas","metal",n,data,_addr);
    break;
  case uns::StarsMetal  :
    status = setData("stars","metal",n,data,_addr);
    break;
  default: status=0;
  }
  if (this->verbose) {
    if (status) { std::cerr << "CSnapshotGadgetH5Out::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[name] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetH5Out::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
// setData("all","id",n,gas_array,true)
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name,std::string array,  const int n ,int * data,const bool _addr)
{
  int status=0;
  switch(CunsOut2<T>::s_mapStringValues[array]) {
  case uns::Id   :
    status = saveCommonDataset(name,"ParticleIDs",n,data,1);
    break;
  default: status=false;
  }

  if (this->verbose) {
    if (status) {
      std::cerr << "CSnapshotGadgetH5Out::setData name["<<name<<"]=" << CunsOut2<T>::s_mapStringValues[array] << "\n";
    } else {
      std::cerr << "** WARNING ** CSnapshotGadgetH5Out::setData Value ["<<name<<"] does not exist.....\n";
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
// setData
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name, const int n ,int * data,const bool _addr)
{
  int status=0;
  return status;
}
// ----------------------------------------------------------------------------
// setData
// setData("gas",n,pos,vel,mass,true)
template <class T>
int CSnapshotGadgetH5Out<T>::setData(std::string name, const int n ,T * data, T * data1, T * data2, const bool _addr)
{
  int status=0;
  return status;
}
// ============================================================================
// save:
template <class T>
int CSnapshotGadgetH5Out<T>::save()
{
  int fail=0;
  // write headers
  myH5->setAttribute("MassTable",&header.MassTable[0], header.MassTable.size());
  myH5->setAttribute("Time",&header.Time,1);
  myH5->setAttribute("Redshift",&header.Redshift,1);
  myH5->setAttribute("BoxSize",&header.BoxSize,1);
  myH5->setAttribute("Omega0",&header.Omega0,1);
  myH5->setAttribute("OmegaLambda",&header.OmegaLambda,1);
  myH5->setAttribute("HubbleParam",&header.HubbleParam,1);
  myH5->setAttribute("Flag_Cooling",&header.Flag_Cooling,1);
  myH5->setAttribute("Flag_DoublePrecision",&header.Flag_DoublePrecision,1);
  myH5->setAttribute("Flag_IC_Info",&header.Flag_IC_Info,1);
  myH5->setAttribute("Flag_Metals",&header.Flag_Metals,1);
  myH5->setAttribute("Flag_Sfr",&header.Flag_Sfr,1);
  myH5->setAttribute("Flag_StellarAge",&header.Flag_StellarAge,1);
  myH5->setAttribute("NumFilesPerSnapshot",&header.NumFilesPerSnapshot,1);
  myH5->setAttribute("NumPart_ThisFile",&header.NumPart_ThisFile[0],header.NumPart_ThisFile.size());
  myH5->setAttribute("NumPart_Total",&header.NumPart_Total[0],header.NumPart_Total.size());
  myH5->setAttribute("NumPart_Total_HighWord",&header.NumPart_Total_HighWord[0],header.NumPart_Total_HighWord.size());

  myH5->close();
  return fail;
}
// ----------------------------------------------------------------------------
// checkMasses
// check out if masses are differents. If not save mass value in attribute MassTable
// return ok if NOT same masses
template <class T>
template <class U>
bool CSnapshotGadgetH5Out<T>::checkMasses(const int n, U *data, const int comp_id)
{
  bool same_mass=true;
  U massref=data[0];
  // check if same masses
  for ( int i=1; i<n;i++) {
    if (massref != data[i]) { // not same mass
      same_mass=false;
      break;
    }
  }
  if (same_mass ) { // we must same unique mass value in Attribute
    header.MassTable[comp_id]=massref;
  } else {
    header.MassTable[comp_id]=0.0;
  }
  // save attribute MassTable
  //myH5->setAttribute("MassTable",&header.MassTable[0], header.MassTable.size());
  return !same_mass;
}

// ----------------------------------------------------------------------------
// saveCommonDataset
template <class T>
template <class U>
bool CSnapshotGadgetH5Out<T>::saveCommonDataset(std::string comp,std::string tag,
                                                const int n ,U * data, const unsigned int second_dim)
{
  bool ok=false;

  std::map<std::string,int> compo_indx;
  compo_indx["gas"  ]=0;
  compo_indx["halo" ]=1;
  compo_indx["dm"   ]=1;
  compo_indx["disk" ]=2;
  compo_indx["bulge"]=3;
  compo_indx["stars"]=4;
  compo_indx["bndry"]=5;

  try {

    std::map<std::string,int>::iterator it;
    it = compo_indx.find(comp);
    if (it != compo_indx.end()) { // key exist
      bool save=true;
      if (tag=="Masses") { // special process for masses
        save=checkMasses(n,data,(*it).second);
      }
      if (save) {
        std::stringstream myid("");
        myid << (*it).second;
        std::string dataset="/PartType"+myid.str()+"/"+tag;
        if (this->verbose)  std::cerr << dataset << "\n";
        try {
          Exception::dontPrint();
          ok = myH5->setDataset(dataset,data,n,second_dim);
          header.NumPart_ThisFile[(*it).second]=n;
          header.NumPart_Total[(*it).second]=n;
          header.NumPart_Total_HighWord[(*it).second]=n;
//          bool ok2 = myH5->setAttribute("NumPart_ThisFile",
//                                        &header.NumPart_ThisFile[0],header.NumPart_ThisFile.size());
//          bool ok3 = myH5->setAttribute("NumPart_Total",
//                                        &header.NumPart_Total[0],header.NumPart_Total.size());
//          bool ok4 = myH5->setAttribute("NumPart_Total_HighWord",
//                                        &header.NumPart_Total_HighWord[0],header.NumPart_Total_HighWord.size());

        }
        // catch failure caused by the H5File operations
        catch( FileIException error )
        {
          PRINT_ERROR;
          throw -1;
        }
        // catch failure caused by the DataSet operations
        catch( DataSetIException error )
        {
          PRINT_ERROR;
          throw -1;
        }
        // catch failure caused by the DataSpace operations
        catch( DataSpaceIException error )
        {
          PRINT_ERROR;
          throw -1;
        }
        // catch failure caused by the DataSpace operations
        catch( DataTypeIException error )
        {
          PRINT_ERROR;
          throw -1;
        }
        catch( GroupIException error )
        {
          PRINT_ERROR;
          return -1;
        }
        catch (...) {
          if (this->verbose) {
            std::cerr << "WARNING !!! : error while saving Dataset["
                      << dataset << "]\n";
          }
          throw -1;
        }
      }
    }
  }
  catch (int e) {
    std::cerr << "WARNING !!! : enable to saveCommonDataset....\n";
  }
  return ok;
}

// ============================================================================
// Implementation of class GH5
// ============================================================================

// ============================================================================
// Constructor
template <class T>
GH5<T>::GH5(const std::string _f_name,unsigned int mode, const bool verb)
{
  verbose = verb;
  f_name=_f_name;
  myfile = NULL;
  myfile = new H5File(f_name,mode);

  if (mode==H5F_ACC_RDONLY) { // reading mode only
    readHeaderAttributes();
  } else
    if (mode==H5F_ACC_TRUNC) { // read and write mode
      // we create header group
      header_group=myfile->createGroup("/Header");
    }
}
// ============================================================================
// Destructor
template <class T>
GH5<T>::~GH5()
{
  if (myfile) {
    delete myfile;
  }
}


// ============================================================================
// readHeaderAttributes
template <class T>
void GH5<T>::readHeaderAttributes()
{
  header.MassTable = getAttribute<double>("MassTable");
  assert(header.MassTable.size()==6);
  header.Time      = (double ) getAttribute<double>("Time")[0];
  header.Redshift  = (double ) getAttribute<double>("Redshift")[0];
  header.BoxSize   = (double ) getAttribute<double>("BoxSize")[0];
  header.Omega0    = (double ) getAttribute<double>("Omega0")[0];
  header.OmegaLambda = (double ) getAttribute<double>("OmegaLambda")[0];
  header.HubbleParam = (double ) getAttribute<double>("HubbleParam")[0];

  header.Flag_Cooling = (int) getAttribute<int>("Flag_Cooling")[0];
  header.Flag_DoublePrecision = (int) getAttribute<int>("Flag_DoublePrecision")[0];
  try {
    header.Flag_IC_Info = (int) getAttribute<int>("Flag_IC_Info")[0];
  } 
  catch (...) {
    std::cerr << "might be an arepo...";
  }
  header.Flag_Metals = (int) getAttribute<int>("Flag_Metals")[0];
  header.Flag_Sfr = (int) getAttribute<int>("Flag_Sfr")[0];
  header.Flag_StellarAge = (int) getAttribute<int>("Flag_StellarAge")[0];
  header.NumFilesPerSnapshot = (int) getAttribute<int>("NumFilesPerSnapshot")[0];

  header.NumPart_ThisFile = getAttribute<int>("NumPart_ThisFile");
  header.NumPart_Total = getAttribute<int>("NumPart_Total");
  header.NumPart_Total_HighWord = getAttribute<int>("NumPart_Total_HighWord");

  // compute npart_total
  npart_total=0;
  for(int k=0; k<6; k++)  {
    npart_total+=header.NumPart_Total[k];
  }

}
// ============================================================================
// getAttribute
// Read an attribute from desired group Header
// return a vector of data
template <class T>
template <class U> std::vector<U> GH5<T>::getAttribute(std::string attr_name)
{
  if (verbose) {
    std::cerr << "= = = = = = = = = = = = = = = = = =\n";
    std::cerr << "Read Attribute ["<<attr_name<< "]\n";
  }
  Group     grp  = myfile->openGroup("Header"  );
  Attribute attr = grp.openAttribute(attr_name);
  DataType  atype = attr.getDataType();
  DataSpace aspace= attr.getSpace();

  if (verbose) {
    std::cerr << "size          = "<< atype.getSize() << "\n";
    std::cerr << "storage space =" << attr.getStorageSize() << "\n";
    std::cerr << "mem data size =" << attr.getInMemDataSize() << "\n";
  }

  int arank = aspace.getSimpleExtentNdims();
  hsize_t adims_out[arank];
  aspace.getSimpleExtentDims( adims_out, NULL);
  if (verbose) {
    std::cerr << "rank " << arank << ", dimensions " ;
  }
  int nbelements=0;
  for (int i=0; i<arank; i++) {
    if (verbose) {
      std::cerr << (unsigned long)(adims_out[i]);
      if (i<arank-1) std::cerr << " x " ;
      else  std::cerr << "\n";
    }
    nbelements += adims_out[i];
  }
  std::vector<U>  vret(nbelements==0?1:nbelements);
  if (verbose)
    std::cerr << "nb elements = " << nbelements << "\n";
  attr.read(atype,&vret[0]);
  aspace.close();
  //atype.close();
  attr.close();
  grp.close();
  return vret;
}
// ============================================================================
// getDataset
// Read the corresponding dataset
// return a vector of data
// U dummy variable used to detect return type
template <class T>
template <class U> std::vector<U> GH5<T>::getDataset(std::string dset_name, U dummy)
{
  if (verbose) {
    std::cerr << "= = = = = = = = = = = = = = = = = =\n";
    std::cerr << "Dataset ["<<dset_name<< "]\n";
  }
  if (dummy) ; // remove compiler warning
  // open dataset
  DataSet dataset = myfile->openDataSet(dset_name);
  // Get dataspace of the dataset
  DataSpace dataspace = dataset.getSpace();
  // Get the number of dimensions in the dataspace
  int rank = dataspace.getSimpleExtentNdims();
  hsize_t dims_out[rank];
  dataspace.getSimpleExtentDims( dims_out, NULL);
  if (verbose) {
    std::cerr << "rank " << rank << ", dimensions " ;
  }
  int nbelements=0;
  for (int i=0; i<rank; i++) {
    if (verbose) {
      std::cerr << (unsigned long)(dims_out[i]);
      if (i<rank-1) std::cerr << " x " ;
      else  std::cerr << "\n";
    }
    if (i==0) {
      nbelements = dims_out[i];
    } else {
      nbelements *= dims_out[i];
    }

  }
  std::vector<U>  vret(nbelements==0?1:nbelements);
  if (verbose)
    std::cerr << "nb elements = " << nbelements << "\n";

  //
  //H5T_class_t data_type = dataset.getTypeClass();
  DataType  data_type = dataset.getDataType();
  DataType mem_type;
  switch (data_type.getClass()) {
  case H5T_INTEGER :
    mem_type = PredType::NATIVE_INT;//H5T_NATIVE_INT;
    break;
  case H5T_FLOAT   :
    if (sizeof(U)==sizeof(double)) {
      mem_type = PredType::NATIVE_DOUBLE;//H5T_NATIVE_DOUBLE;
    } else {
      mem_type = PredType::NATIVE_FLOAT ;//H5T_NATIVE_FLOAT;
    }
    break;
   default :
    std::cerr << "We should not be here.....\n";
    assert(0);
  }

  // read vector of data
  dataset.read(&vret[0],mem_type,H5S_ALL,H5S_ALL);//,H5P_DEFAULT);
  mem_type.close();
  data_type.close();
  dataspace.close();
  dataset.close();
  return vret;

}
// ============================================================================
// setDataset
// Write the corresponding dataset
//
template <class T>
template <class U>
bool GH5<T>::setDataset(std::string dset_name, U * data, const unsigned int n,
                        const unsigned int second_dim)
{
  bool ok=true;
  assert(second_dim==1 || second_dim==3);
  if (verbose) {
    std::cerr << "= = = = = = = = = = = = = = = = = =\n";
    std::cerr << "Set Dataset ["<<dset_name<< "]\n";
  }

  // first create group
  std::size_t o1=dset_name.find("/");
  std::size_t o2=dset_name.find("/",1);
  if (o1==std::string::npos || o1==std::string::npos ) {
    std::cerr << "GH5<T>::setDataset no '/' in datasetname....\n";
    throw -1;
  }
  std::string groupname=dset_name.substr(o1,o2-o1); // find groupname

  if (histo_group[groupname]==false) { // check if not created yet
    Group  group=myfile->createGroup(groupname);
    histo_group[groupname]=true;
  }
  // set the number of dimensions in the dataspace
  int rank=1;

  hsize_t dims_out[2];
  dims_out[0] = n;
  if (second_dim>1) {
    rank=2;
    dims_out[1]=second_dim;
  }
  if (verbose) {
    std::cerr << "rank " << rank << "\n";
  }
  // set dataspace of the dataset
  DataSpace dataspace(rank,dims_out);
  // guess U type
  DataType mem_type=guessType(U (1));
  // Create dataset
  DataSet dataset = myfile->createDataSet(dset_name,mem_type,dataspace);
  // write datasey
  dataset.write(data,mem_type);

  if (verbose) {
    std::cerr << "rank " << rank << ", dimensions " ;
  }
  return ok;
}
// ============================================================================
// setAttribute
// Write the corresponding attribute
//
template <class T>
template <class U>
bool GH5<T>::setAttribute(std::string attr_name, U * attr_value, const int n)
{
  if (verbose) {
    std::cerr << "= = = = = = = = = = = = = = = = = =\n";
    std::cerr << "set Attribute ["<<attr_name<< "]\n";
  }
  // guess type
  DataType mem_type=guessType(U (1));
  // set dataspace for the attribute
  hsize_t dims_out[1];
  dims_out[0] = n;
  DataSpace dataspace(1,dims_out);
  // create attribute
  Attribute attr=header_group.createAttribute(attr_name,mem_type,dataspace);
  // write attribute
  attr.write(mem_type,attr_value);

  return true;
}
// ============================================================================
// return HDF5 native type corresponding to U parameter
//
template <class T>
template <class U>
DataType GH5<T>::guessType(U value)
{
  DataType ret;
  if ((std::numeric_limits<U>::max()) == (std::numeric_limits<int>::max())) {
    if (verbose) std::cerr << "U is an INT\n";
    ret = PredType::NATIVE_INT;
  } else
  if ((std::numeric_limits<U>::max()) == (std::numeric_limits<float>::max())) {
    if (verbose) std::cerr << "U is an FLOAT\n";
    ret = PredType::NATIVE_FLOAT;
  } else
  if ((std::numeric_limits<U>::max()) == (std::numeric_limits<double>::max())) {
    if (verbose) std::cerr << "U is an double\n";
    ret = PredType::NATIVE_DOUBLE;
  } else
  if ((std::numeric_limits<U>::max()) == (std::numeric_limits<long int>::max())) {
    if (verbose) std::cerr << "U is an LONG INT\n";
    ret = PredType::NATIVE_LONG;
  } else
  if ((std::numeric_limits<U>::max()) == (std::numeric_limits<long long int>::max())) {
    if (verbose) std::cerr << "U is an LONG LONG INT\n";
    ret = PredType::NATIVE_LLONG;
  } else
    if ((std::numeric_limits<U>::max()) == (std::numeric_limits<long double>::max())) {
      if (verbose) std::cerr << "U is an LONG LONG INT\n";
      ret = PredType::NATIVE_LDOUBLE;
    } else {
      std::cerr << "GH5<T>::guessType, unknown type !!!!\n";
      throw(-1);
      std::exit(1);
    }
  return ret;
}

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CSnapshotGadgetH5In<float>;
template class CSnapshotGadgetH5In<float>;

//extern template class CSnapshotGadgetH5In<double>;
template class CSnapshotGadgetH5In<double>;

//extern template class CSnapshotGadgetH5Out<float>;
template class CSnapshotGadgetH5Out<float>;

//extern template class CSnapshotGadgetH5Out<double>;
template class CSnapshotGadgetH5Out<double>;

//extern template class GH5<float>;
template class GH5<float>;

//extern template class GH5<double>;
template class GH5<double>;
} // end of namespace
