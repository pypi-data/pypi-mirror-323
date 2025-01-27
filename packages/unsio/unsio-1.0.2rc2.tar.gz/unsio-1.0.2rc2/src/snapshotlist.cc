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
#include "uns.h"
#include "snapshotlist.h"
#include "ctools.h"
#include <sstream>
#include <iomanip>
#include <iostream>

namespace uns {

// ----------------------------------------------------------------------------
// constructor
template <class T> CSnapshotList<T>::CSnapshotList(const std::string _name,
                                                   const std::string _comp,
                                                   const std::string _time,
                                                   const bool        verb)
  :CSnapshotInterfaceIn<T>(_name, _comp, _time, verb)
{
  snapshot = NULL;
  unsin    = NULL;
  nframe   = 0;   // # frames read
  nemosim  = "";
  this->valid=openFileList();
}
// ----------------------------------------------------------------------------
// constructor
template <class T> CSnapshotList<T>::~CSnapshotList()
{
  if (unsin) delete unsin;
}
// ============================================================================
// getSnapshotRange
template <class T> int CSnapshotList<T>::nextFrame(uns::UserSelection &user_select)
{
  assert(snapshot != NULL);
  assert(snapshot->isValidData()==true);
  snapshot->setNsel(this->nsel);
  return (snapshot->nextFrame(user_select));
}
// ============================================================================
// nextFrame
template <class T> int CSnapshotList<T>::nextFrameSelect(ComponentRangeVector * crvs)
{
  snapshot->user_select.setSelection(this->getSelectPart(),crvs);
  this->setNsel(snapshot->user_select.getNSel());
  snapshot->setReqBits(this->req_bits);
  snapshot->setNsel(snapshot->user_select.getNSel());
  return(snapshot->nextFrame(snapshot->user_select));
}
// ============================================================================
// isNewFrame()
template <class T> bool CSnapshotList<T>::isNewFrame()
{
  bool stop=false;
  while (!stop && getLine()) {
    if (unsin) {
      delete unsin;
    }
    unsin = new uns::CunsIn2<T>(snapname.c_str(),this->select_part.c_str(),this->select_time.c_str(),this->verbose);
    T t;
    bool ok=unsin->snapshot->getData("time",&t);
    if (unsin->isValid() && ok && this->checkRangeTime(t)) {
      snapshot = unsin->snapshot;
      stop=true;
      this->interface_type = snapshot->getInterfaceType();
    }
  }
  if (!stop) this->end_of_data = true; // EOF reached
  return stop;

}
// ============================================================================
template <class T> ComponentRangeVector * CSnapshotList<T>::getSnapshotRange()
{
  assert(snapshot != NULL);
  assert(snapshot->isValidData());
  if ((tools::Ctools::tolower(simtype) == "nemo") && nemosim != "" && crv.size()>0) {
    return &crv;
  }
  else {
    return snapshot->getSnapshotRange();
  }
}
// ----------------------------------------------------------------------------
// openFileList
template <class T> bool CSnapshotList<T>::openFileList()
{
  bool status=false;
  if (this->filename == "-" )
    ;
  else
    fi.open(this->filename.c_str(),std::ios::in);
  if (! fi.is_open()) {
    std::cerr << "Unable to open file ["<<this->filename<<"] for reading, aborting...\n";
    status = false;
  }
  else {
    // read magic numberé
    std::string line;
    if (getLine(true)) { // read the first file
      // -----------------------------------------------
      // instantiate a new UNS input object (for reading)
      uns::CunsIn2<T> * test_data = new uns::CunsIn2<T>(snapname.c_str(),this->select_part.c_str(),this->select_time.c_str(),this->verbose);

      if (test_data->isValid()) { // it's a valid snaphot
        delete test_data;
        status = true;
        fi.seekg(0, std::ios::beg); // go back to the beginning
      }
    }
    else {
      status=false;
      fi.close();
    }
  }
  return status;
}
// ----------------------------------------------------------------------------
//
template <class T> bool CSnapshotList<T>::getLine(const bool force)
{
  bool status=false,stop=false;
  if (this->valid || force) {
    while (!stop && ! fi.eof()) {           // while ! eof
      std::string line;
      getline(fi,line);
      if ( ! fi.eof()) {
        std::istringstream str(line);  // stream line
        std::string parse;
        // following loop parse each lines previously read
        //
        int cpt=0;
        while (  str >> parse   &&              // something to read
                 parse[0] != '#' &&             // not commented out
                 parse[0] != '!' &&             // not commented out
                 parse[0] != '\n'               // not a blank line
                 ) {
          cpt++;
          if (cpt==1) snapname=parse;
        }
        if (cpt > 0 ) {
          unsigned int i=0;
          while(i<snapname.length() && snapname[i]==' ') i++; // search first non blank
          if (i<snapname.length() && snapname[i]!='/')        // first char not a '/'
          {;}//snapname = dirpath.toStdString() + snapname;      // append to dirpath
          stop   = true; // we have a snapname
          status = true; // so we can stop reading
        }
      }
      else { // end of file
        stop   = true;
        status = false;
      }
    }
  }
  else status=false;
  return status;
}
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// Templates instantiation MUST be declared **AFTER** templates declaration
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// C++11
//extern template class CSnapshotList<float>;
template class CSnapshotList<float>;

//extern template class CSnapshotList<double>;
template class CSnapshotList<double>;
} // end of namespace


//
