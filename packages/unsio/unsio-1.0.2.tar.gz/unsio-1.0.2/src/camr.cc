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

#include <cstdlib>
#include <cstring>
#include <sstream>
#include <iomanip>
#include <cmath>
#include "camr.h"
#include "cfortio.h"
#include "snapshotramses.h"

namespace ramses {
const double CAmr::XH = 0.76;
const double CAmr::mH = 1.6600000e-24;
const double CAmr::kB = 1.3806200e-16;

// ============================================================================
//
CAmr::CAmr(const std::string _indir, const bool _v)
{
  nbody=0;
  //pos = mass = vel = NULL;
  verbose=_v;
  indir = _indir;
  infile="";

  // keep filename untill last /
  int found=indir.find_last_of("/");
  if (found != (int) std::string::npos && (int) indir.rfind("output_")<found) {
    indir.erase(found,indir.length()-found);
  }
  if (verbose)
    std::cerr << "indir =[" << indir <<"]\n";
  
  found=(int) indir.rfind("output_"); 
  if (found!=(int) std::string::npos) {
    s_run_index= indir.substr(found+7,indir.length()-1); // output_ = 7 characters
    
    while ((found=s_run_index.find_last_of("/"))>0) { // remove trailing "/"
      s_run_index.erase(found,found);
    }
    infile = indir + "/amr_" + s_run_index + ".out00001";
    testhydrofile = indir + "/hydro_" + s_run_index + ".out00001";
    // check gravity file is present
    std::string gravityfile   = indir + "/grav_" + s_run_index + ".out00001";
    if (grav.open(gravityfile)) {
      is_gravity = true;
      grav.close();
    } else {
      is_gravity = false;
      std::cerr << "GRAVITY files are missing....\n";
    }
    if (verbose)
      std::cerr << "Run index = " << s_run_index <<  "  infile=[" << infile << "]\n";
  }



  // readHeader
  if (amr.open(infile)) {
    readHeader();
    amr.close();
  }

  //computeNbody();
  //loadData();
}
// ============================================================================
//
CAmr::~CAmr()
{
   amr.close();
   hydro.close();
   grav.close();
}
// ----------------------------------------------------------------------------
//
bool CAmr::isValid()
{    
  if (amr.open(infile) && hydro.open(testhydrofile)) {
    valid=true;
    //readHeader();
    amr.close();
    hydro.close();
    if (verbose)
      std::cerr << "ncpu="<<ncpu<<"  ndim="<<ndim<< "\n";// "npart=" << npart << "\n";
    xbound[0] = nx/2;
    xbound[1] = ny/2;
    xbound[2] = nz/2;
    twotondim = pow(2,ndim);  
    ordering = "hilbert";
    scale_nH =  XH/mH * 0.276090728884102e-29;
  }
  else
    valid=false;
  amr.close();
  return valid;
}
// ============================================================================
// readHeader
int CAmr::readHeader()
{
  int len1,len2;
  amr.readDataBlock((char *) &ncpu);

  amr.readDataBlock((char *) &ndim);

  len1=amr.readFRecord();
  amr.readData((char *) &nx,sizeof(int),1);
  amr.readData((char *) &ny,sizeof(int),1);
  amr.readData((char *) &nz,sizeof(int),1);
  len2=amr.readFRecord();
  assert(amr.good() && len1==len2);

  amr.readDataBlock((char *) &nlevelmax);
  if (verbose)
    std::cerr << "AMR Nlevel max="<<nlevelmax<<"\n";
  amr.readDataBlock((char *) &ngridmax);

  amr.readDataBlock((char *) &nboundary);
  
  amr.readDataBlock((char *) &ngrid_current);
  
  amr.readDataBlock((char *) &header.boxlen);
  amr.skipBlock(3); // noutput,iout,ifout
                    // tout
                    // aout
  amr.readDataBlock((char *) &header.time);
  amr.skipBlock(4); // dtold
                    // dtnew
                    // nstep,nstep_coarse
                    // const,mass_tot_0,rho_tot
  len1=amr.readFRecord();
  amr.readData((char *) &header.omega_m   ,sizeof(double),1);
  amr.readData((char *) &header.omega_l   ,sizeof(double),1);
  amr.readData((char *) &header.omega_k   ,sizeof(double),1);
  amr.readData((char *) &header.omega_b   ,sizeof(double),1);
  amr.readData((char *) &header.h0        ,sizeof(double),1);
  amr.readData((char *) &header.aexp_ini  ,sizeof(double),1);
  amr.readData((char *) &header.boxlen_ini,sizeof(double),1);
  len2=amr.readFRecord();
  assert(amr.good() && len1==len2);

  len1=amr.readFRecord();
  amr.readData((char *) &header.aexp,sizeof(double),1);
  amr.readData((char *) &header.hexp,sizeof(double),1);
  amr.readData((char *) &header.aexp_old,sizeof(double),1);
  amr.readData((char *) &header.epot_tot_int,sizeof(double),1);
  amr.readData((char *) &header.epot_tot_old,sizeof(double),1);
  len2=amr.readFRecord();
  assert(amr.good() && len1==len2);

  if (len2==len1) ; // remove warning....
  return 1;
}
// ============================================================================
// loadData
template int CAmr::loadData<float> (uns::CParticles<float> * particles,
                   const unsigned int req_bits);
template int CAmr::loadData<double> (uns::CParticles<double> * particles,
                   const unsigned int req_bits);
template <class T> int CAmr::loadData(uns::CParticles<T> * particles,
                   const unsigned int req_bits)
{
  int ngridfile  [nlevelmax][ncpu+nboundary];
  int ngridlevel [nlevelmax][ncpu          ];
  int ngridbound [nlevelmax][     nboundary];
  double xc[3][8];
  double gamma;
  int ngrida;
  std::string infile;
  
  nbody = 0;
  bool count_only=false;
  //if (index==NULL)  count_only=true;
  int cpt=0;
  bool stop=false;
  int offset_nvarg=0;
  int sdouble=sizeof(double);

  while (!stop) {
    stop=true;
    try {
      // loop on all cpus/files
      for (int icpu=0; icpu<ncpu; icpu++) {
        std::stringstream osf("");
        osf << std::fixed << std::setw(5) << std::setfill('0') <<icpu+1;
        infile = indir + "/amr_" + s_run_index + ".out" + osf.str();
        if (verbose) std::cerr << "CAmr::loadData infile-> ["<<infile << "]\n";
        amr.open(infile);
        amr.skipBlock(21);

        amr.readDataBlock((char *) &ngridlevel);
        memcpy(ngridfile,ngridlevel,sizeof(int)*nlevelmax*ncpu);

        amr.skipBlock();

        if (nboundary>0) {
          amr.skipBlock(2);

          amr.readDataBlock((char *) &ngridbound);
          // must convert the following line
          //ngridfile(ncpu+1:ncpu+nboundary,1:nlevelmax)=ngridbound
          for (int i=0;i<nlevelmax;i++) {
            // copy grid level
            memcpy(&ngridfile [i][0],
                &ngridlevel[i][0],sizeof(int)*ncpu);
            // copy gridbound
            memcpy(&ngridfile [i][ncpu],
                   &ngridbound[i][0],sizeof(int)*nboundary);
          }
        }
        amr.skipBlock();
        // ROM: comment the single following line for old stuff
        amr.skipBlock();
        if (ordering=="bisection")
          amr.skipBlock(5);
        else
          amr.skipBlock();
        amr.skipBlock(3);
        // --------------
        // Open HYDRO file and skip header
        std::string hydrofile = indir + "/hydro_" + s_run_index + ".out" + osf.str();
        //if (verbose) std::cerr << "CAmr::loadData hydrofile-> ["<<hydrofile << "]\n";
        hydro.open(hydrofile,count_only);
        hydro.skipBlock(); // ncpu
        hydro.readDataBlock((char *) &nvarh);
        particles->nvarh = nvarh;
        //std::cerr << "nvarh = " << nvarh << "\n" ;
        hydro.skipBlock(3); // ndim,levelmax,nboundary
        hydro.readDataBlock((char *) &gamma); // gamma

        // --------------
        // Open GRAV file and skip header
        nvarg=0;
        if (is_gravity && (req_bits&POT_BIT || req_bits&ACC_BIT)) {
          std::string gravfile = indir + "/grav_" + s_run_index + ".out" + osf.str();
          //if (verbose) std::cerr << "CAmr::loadData hydrofile-> ["<<hydrofile << "]\n";
          grav.open(gravfile,count_only);
          grav.skipBlock(); // ncpu
          grav.readDataBlock((char *) &nvarg);
          nvarg+=offset_nvarg;  // buggy in old RAMSES version
                          // we had offset in case of old ramses code
          //nvarg=ndim+1; // this is MUST be the real value
          // ndim = 3; nvarg =4, phi,ax,ay,az
          // ndim = 2; nvarg =3, phi,ax,ay
          if (verbose) {
            //std::cerr << "\nWARNING\nWe assume that you are using ramses data files produces with new RAMSES released\n";
          }
          grav.skipBlock(2); //  levelmax,nboundary
        }
        // loop over levels
        for (int ilevel=0; ilevel<lmax; ilevel++) {

          // Geometry
          double dx=pow(0.5,ilevel+1);
          double dx2=0.5*dx;
          for (int ind=0; ind<twotondim; ind++) {
            int iz=ind/4;
            int iy=(ind-4*iz)/2;
            int ix=(ind-2*iy-4*iz);
            xc[0][ind]=(ix-0.5)*dx;
            xc[1][ind]=(iy-0.5)*dx;
            xc[2][ind]=(iz-0.5)*dx;
          }
          // allocate work arrays
          ngrida=ngridfile[ilevel][icpu];
          if (verbose) {
            //std::cerr << "ngrida="<<ngrida<<" nvarg="<<nvarg<<"\n";
          }
          double * xg=NULL, *var=NULL, *varg=NULL;
          int * son=NULL;
          if (ngrida>0) {
            xg = new double[ngrida*ndim];
            son= new int   [ngrida*twotondim];
            if (!count_only) {
              var= new double[ngrida*twotondim*nvarh];
              if (is_gravity && (req_bits&POT_BIT || req_bits&ACC_BIT)) {
                //checkGravity(ngrida,ilevel,icpu,&ngridfile[0][0]);
                //varg= new double[ngrida*twotondim*nvarg];
                varg= new double[ngrida*twotondim*(ndim+1)]; // allocate with ndim+1
                                                             // to prevent crash in case of nvarg=3 and
                                                             // 4 variables (pot,ax,ay,az) due
                                                             // to ramses code prior 2012
              }
            }
          }
          // Loop over domains
          for (int j=0; j<(nboundary+ncpu); j++) {
            if (ngridfile[ilevel][j]>0) {
              amr.skipBlock(); // Skip grid index
              amr.skipBlock(); // Skip next index
              amr.skipBlock(); // Skip prev index
              //
              // Read grid center
              //
              for (int idim=0;idim<ndim;idim++) {
                if (j==icpu && ngrida>0) {
                  amr.readDataBlock((char *) &xg[idim*ngrida]);
                }
                else amr.skipBlock();
              }
              amr.skipBlock();       // Skip father index
              amr.skipBlock(2*ndim); // Skip nbor index
              //
              // Read son index
              //
              for (int ind=0;ind<twotondim;ind++) {
                if (j==icpu&& ngrida>0) {
                  amr.readDataBlock((char *) &son[ind*ngrida]);
                }
                else amr.skipBlock();
              }
              amr.skipBlock(twotondim); // Skip cpu map
              amr.skipBlock(twotondim); // Skip refinement map
            }
            //
            // Read HYDRO data
            //
            hydro.skipBlock(2);
            if (!count_only && ngridfile[ilevel][j]>0) {
              // Read hydro variables
              for (int ind=0;ind<twotondim;ind++) {
                for (int ivar=0; ivar<nvarh; ivar++) {
                  if (j==icpu&& ngrida>0) {
                    hydro.readDataBlock((char *) &var[ivar*ngrida*twotondim+ind*ngrida]);
                  }
                  else hydro.skipBlock();
                }
              }
            }
            //
            // Read GRAV data
            //
            if (is_gravity && (req_bits&POT_BIT || req_bits&ACC_BIT)) {
              grav.skipBlock(2);
              if (!count_only && ngridfile[ilevel][j]>0) {
                // Read grav variables
                for (int ind=0;ind<twotondim;ind++) {
                  for (int ivar=0; ivar<nvarg; ivar++) {
                    if (j==icpu&& ngrida>0) {
                      int n=grav.readDataBlock((char *) &varg[ivar*ngrida*twotondim+ind*ngrida]);
                      if (n!=ngrida*sdouble) { // error !!!
                        // garbage collecting
                        delete [] xg;
                        delete [] son;
                        delete [] var;
                        delete [] varg;
                        throw(-1); // throw error and try with another offset
                      }
                    }
                    else {
                      grav.skipBlock();
                    }
                  }
                }
              }
            }

          }
          if (ngrida>0) {
            //  Loop over cells
            //for (int ind=0;ind<twotondim;ind++) {
              for (int i=0;i<ngrida;i++) {
              // Store data cube
              //for (int i=0;i<ngrida;i++) {
            for (int ind=0;ind<twotondim;ind++) {
                // compute cell center
                double px=xg[0*ngrida+i]+xc[0][ind]-xbound[0]; // x
                double py=xg[1*ngrida+i]+xc[1][ind]-xbound[1]; // y
                double pz=0.0;
                if (ndim > 2) {
                  pz=xg[2*ngrida+i]+xc[2][ind]-xbound[2]; // z
                }
                bool ok_cell =       (
                                       !(son[ind*ngrida+i]>0 && ilevel<lmax) && // cells is NOT refined
                                     (ilevel>=lmin)                        &&
                                     ((px+dx2)>=xmin)                      &&
                                     ((py+dx2)>=ymin)                      &&
                                     ((ndim<3) || ((pz+dx2)>=zmin))        &&
                                     ((px-dx2)<=xmax)                      &&
                                     ((py-dx2)<=ymax)                      &&
                                     ((ndim<3) || ((pz-dx2)<=zmax)));
                if (ok_cell) {
                  if (!count_only) {
                    bool take=false;
                    if (req_bits&POS_BIT) {
                      particles->pos.push_back(px*header.boxlen);  // x
                      particles->pos.push_back(py*header.boxlen);  // y
                      if (ndim>2)
                        particles->pos.push_back(pz*header.boxlen);  // z
                      else
                        particles->pos.push_back(0.0);  // z
                      particles->load_bits |= POS_BIT;
                      take=true;
                    }
                    if (req_bits&VEL_BIT) {
                      particles->vel.push_back(var[1*ngrida*twotondim+ind*ngrida+i]); // vx
                      particles->vel.push_back(var[2*ngrida*twotondim+ind*ngrida+i]); // vy
                      if (ndim>2)
                        particles->vel.push_back(var[3*ngrida*twotondim+ind*ngrida+i]); // vz
                      else
                        particles->vel.push_back(0.0); // vz
                      particles->load_bits |= VEL_BIT;
                      take=true;
                    }
                    // gas density
                    double rho = var[0*ngrida*twotondim+ind*ngrida+i];
                    if (req_bits&MASS_BIT) {
                      particles->mass.push_back(rho*dx*header.boxlen*dx*header.boxlen*dx*header.boxlen);
                      particles->load_bits |= MASS_BIT;
                      take=true;
                    }
                    if (req_bits&HSML_BIT) {
                      particles->hsml.push_back(dx*header.boxlen); // hsml
                      particles->load_bits |= HSML_BIT;
                    }
                    if (req_bits&RHO_BIT) {
                      particles->rho.push_back(rho); // rho var(i,ind,1) * scale_nH
                      particles->load_bits |= RHO_BIT;
                    }
                    //
                    // Get gavitationnal data
                    //
                    if (is_gravity && (req_bits&POT_BIT && (nvarg==ndim+1))) {
                      particles->phi.push_back(varg[0*ngrida*twotondim+ind*ngrida+i]);
                      particles->load_bits |= POT_BIT;
                    }
                    if (is_gravity && (req_bits&ACC_BIT && nvarg>=ndim )) {
                      int offset=0;
                      if (nvarg==ndim+1) { // there is pot/ax/ay/az
                        offset=1;          //  shift to ax
                      }
                      for (int k=offset; k<nvarg; k++) {
                        particles->acc.push_back(varg[k*ngrida*twotondim+ind*ngrida+i]);
                      }
                      if (ndim<3) { // ndim = 2 , set az=0.0
                        particles->acc.push_back(0.0);
                      }
                      particles->load_bits |= ACC_BIT;
                    }
                    //
                    // Get EXTRA hydrodynamic data stored in var[nvarh] array
                    //
                    //     0 : rho
                    //     1 : vx
                    //     2 : vy
                    //     3 : vz
                    //     4 : pressure
                    //     5 : metalicity
                    //   6-? : extra
                    //
                    // with 2D simulations, hydro variables from var[] array are shifted to the left
                    int offset_2d=-1;
                    if (ndim>2) offset_2d=0;

                    if (req_bits&TEMP_BIT && nvarh>(4+offset_2d)) {
                      double temp=0.0;
                      if (rho!=0.0) {
                        temp=std::max(0.0,var[(4+offset_2d)*ngrida*twotondim+ind*ngrida+i]/((gamma-1)*rho));
                      }
                      particles->temp.push_back(temp);
                      particles->load_bits |= TEMP_BIT;
                    }
                    if (req_bits&METAL_BIT && nvarh>(5+offset_2d)) {
                      double metal= var[(5+offset_2d)*ngrida*twotondim+ind*ngrida+i];
                      particles->metal.push_back(metal);
                      particles->load_bits |= METAL_BIT;
                    }
                    if (req_bits&METAL_BIT && nvarh<=5) {
                      double metal= -1.0; // we put -1.0 when no metellicity
                      particles->metal.push_back(metal);
                      particles->load_bits |= METAL_BIT;
                    }
                    // extra hydro data (> 4 )
                    int extra_start=4+offset_2d;
                    if (req_bits&HYDRO_BIT && nvarh>(extra_start)) {
                      for (unsigned int extra=(extra_start); extra<(unsigned int) nvarh;extra++) {
                        assert(extra<particles->MAX_HYDRO);
                        particles->hydro[extra].push_back(var[(extra)*ngrida*twotondim+ind*ngrida+i]);
                        particles->load_bits |= HYDRO_BIT;
                      }
                    }
                    // particles ID
                    if (req_bits&ID_BIT) {
                      //particles->id.push_back(-1.); // no id for gas, use "-1"
                      particles->id.push_back(-1.*(((particles->ngas+1)*(ncpu-1)+icpu+1))); // no id for gas, use "-1"
                      particles->load_bits |= ID_BIT;
                    }
                    if (take|| !req_bits) { // !req_bits for uns_info and display=f
                      particles->indexes.push_back(0); // GAS particles
                      particles->ngas++; // One more gas particles

                    }
                    particles->ntot++; // one more total particles
                    // this variable count all particles
                  }
                  nbody++;
                }
                else {
                  //              if (ilevel>=lmin) {
                  //              std::cerr << "Not ok lmin="<<lmin<<" ilevel="<<ilevel<<" xmin="<<xmin<<" xmax="<<xmax
                  //                           <<" ymin="<<ymin<<" ymax="<<ymax
                  //                          <<" zmin="<<zmin<<" zmax="<<zmax<<"\n";
                  //              }
                }
              }
            }
            // garbage collecting
            if (ngrida>0) {
              delete [] xg;
              //delete [] x;
              delete [] son;
              if (!count_only) {
                delete [] var;
                if (is_gravity && (req_bits&POT_BIT || req_bits&ACC_BIT)) {
                  delete [] varg;
                }
              }
            }
          }
        } // ilevel
        amr.close();
        hydro.close();
        if (is_gravity) {
          grav.close();
        }
      } //for (int icpu=0 ....
    }
    catch (const int e) { // suppose to catch bug on wrong nvarg value
                          // from ramses code prior 2012
      assert(is_gravity && (req_bits&POT_BIT || req_bits&ACC_BIT)); // we must be here if there is gravity
      std::cerr << "\n\nCatch error on gravity files, probably ramses code prior 2012\ntrying next alorithms, please wait....\n\n";
      if (nvarg>ndim) {
        std::cerr << "ALGORITHM ERROR, nvarg>ndim\n";
        assert(0);
        std::exit(1);
      }
      offset_nvarg=1;
      stop=false;
      cpt++;
      assert(cpt<2); // we can loop only twice
      // close files
      amr.close();
      hydro.close();
      grav.close();
    }
  }
  return nbody;
}
//
// checkGravity
//
bool CAmr::checkGravity(const int ngrida, const int ilevel, const int icpu, int *gridfile)
{
  bool status=true;
  // MUST verify this
  assert(nvarg==ndim);
  assert(ngrida>0);

  //double * varg = new double[ngrida*twotondim]; // allocate temporary variable
  int sdouble = sizeof(double); // sizeof double

  // save grav file position
  std::streampos position = grav.getPos();
  try {
    for (int j=0; j<(nboundary+ncpu); j++) {
      grav.skipBlock(2);
      if (gridfile[ilevel*(ncpu+nboundary)+j]>0) {
        // Read grav variables
        for (int ind=0;ind<twotondim;ind++) {
          for (int ivar=0; ivar<nvarg; ivar++) {
            if (j==icpu&& ngrida>0) {
              //int n=grav.readDataBlock((char *) &varg[0]);
              int n=grav.skipBlock();
              //std::cerr << "n="<<n<<"\n";
              if (n!=ngrida*sdouble) {
                // old RAMSES code detected, nvarg=ndim and should be ndim+1
                throw -1;
              }
              assert(n==ngrida*8);
            }
            else {
              grav.skipBlock();
            }
          }
        }
      }
    }
  } catch (const int e) {
    std::cerr << "CAmr::checkGravity, old RAMSES code detected, fixing [nvarg=ndim+1]...\n";
    nvarg++;
    status=false;
    assert(nvarg==ndim+1);
  }

  //delete [] varg;
  // get back to file position
  grav.setPos(position);
  return status;

}
} // end of namespace ramses
