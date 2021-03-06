#!/bin/sh
echo "Building the CDMS library."
msg="Usage: ./install_script targetdir"
U=`uname`
if (test "${U}" = "Linux") then
    if (test -z "${PGI-}") then
        FC=${FC-f77}
    else
        FC="${FC-pgf77}"
    fi
else
    FC="${FC-f77}"
fi
export FC
if (test "${U}" = "Darwin") then
  CDMSARCH=`uname -m`
  if (test "${CDMSARCH}" = "i386") then
     export CPPFLAGS="-Df2cFortran -DBYTESWAP"
  else
     export CPPFLAGS="-Df2cFortran"
  fi 
fi
if (test "${U}" = "FreeBSD") then
  export CPPFLAGS="-Df2cFortran"
fi
if (test "${U}" = "HP-UX") then
  export CPPFLAGS="+z"
fi
# Define compilation flags for itanium based NEC TX-7 (and gcc)
CDMSARCH=`uname -m`
if (test "${CDMSARCH}" = "ia64") then
  export CFLAGS="$CFLAGS -Bshareable -fPIC -D__ia64"
  #export CFLAGS="$CFLAGS -fpic -D__alpha"
fi
if (test "${CDMSARCH}" = "x86_64") then
  export CC="gcc -fPIC -D__x86_64__"
fi
target="cddrs cdunif db_util cduniftest"
if (test $# -eq 0) then 
    echo ${msg};
    exit 1
fi
D=''
if (test "$1" = "--debug") then
    D="--debug"; shift
fi
if (test $# -eq 0) then 
    echo ${msg};
    exit 1
fi
if (test ! -d $1) then
    echo -n "$1 is not a directory; create it? (y/[n])";
    y='n'
    read y;
    if (test ${y} = 'y') then
        mkdir $1;
        if (test ! -d $1) then
            echo "Could not create $1, installation aborted.";
            exit 1
        fi
    else
        echo 'Installation aborted.';
        exit 1
    fi
fi
if (test ! -d $1/man) then
    mkdir --parents $1/man; \
    mkdir --parents $1/man/man1; \
    mkdir --parents $1/man/man3
fi
PREFIX=$1;
if (test "$2" = "" ) then
  PYPREFIX=${PREFIX}
else
  PYPREFIX=`(cd $2;pwd)`
fi
echo "prefix" ${PREFIX}
echo "pyprefix" ${PYPREFIX}
/bin/rm -fr ${PREFIX}/lib/libcdms.a ${PREFIX}/include/cdms
CDMS_INCLUDE_DRS=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_INCLUDE_DRS,"`
CDMS_INCLUDE_HDF=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_INCLUDE_HDF,"`
#CDMS_LIBRARY_HDF5=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_LIBRARY_HDF5,"`
CDMS_INCLUDE_PP=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_INCLUDE_PP,"`
CDMS_INCLUDE_QL=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_INCLUDE_QL,"`
drs_file=`${PYPREFIX}/bin/python -c "import cdat_info;print cdat_info.drs_file,"`
#CDMS_INCLUDE_DAP=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_INCLUDE_DAP,"`
#CDMS_DAP_DIR=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_DAP_DIR,"`
CDMS_HDF_DIR=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_HDF_DIR,"`
CDMS_GRIB2LIB_DIR=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.CDMS_GRIB2LIB_DIR,"`
netcdf_directory=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.netcdf_directory,"`
netcdf_include_directory=`${PYPREFIX}/bin/python -c "import sys, os;sys.path.insert(0,os.path.join('${PREFIX}','lib','python%i.%i' % sys.version_info[:2],'site-packages')) ; import cdat_info;print cdat_info.netcdf_include_directory,"`
netcdf_library_directory=${netcdf_directory}/lib
echo "./configure  --enable-dap=${CDMS_INCLUDE_DAP} --enable-drs=${CDMS_INCLUDE_DRS} --enable-hdf=${CDMS_INCLUDE_HDF} --enable-pp=${CDMS_INCLUDE_PP} --enable-ql=${CDMS_INCLUDE_QL} --cache-file=/dev/null --prefix=${PREFIX} --with-nclib=${netcdf_library_directory} --with-ncinc=${netcdf_include_directory} --with-daplib=${CDMS_DAP_DIR}/lib --with-dapinc=${CDMS_DAP_DIR}/include --with-hdfinc=${CDMS_HDF_DIR}/include --with-hdflib=${CDMS_HDF_DIR}/lib --with-hdf5lib=${CDMS_LIBRARY_HDF5} --with-grib2lib=${CDMS_GRIB2LIB_DIR}/lib --with-jasperlib=${CDMS_GRIB2LIB_DIR}/lib --with-grib2inc=${CDMS_GRIB2LIB_DIR}/include --enable-grib2 " 
#./configure  --enable-dap=${CDMS_INCLUDE_DAP} --enable-drs=${CDMS_INCLUDE_DRS} --enable-hdf=${CDMS_INCLUDE_HDF} --enable-pp=${CDMS_INCLUDE_PP} --enable-ql=${CDMS_INCLUDE_QL} --cache-file=/dev/null --prefix=${PREFIX} --with-nclib=${netcdf_library_directory} --with-ncinc=${netcdf_include_directory} --with-daplib=${CDMS_DAP_DIR}/lib --with-dapinc=${CDMS_DAP_DIR}/include --with-hdfinc=${CDMS_HDF_DIR}/include --with-hdflib=${CDMS_HDF_DIR}/lib --with-hdf5lib=${CDMS_LIBRARY_HDF5} --with-grib2lib=${CDMS_GRIB2LIB_DIR}/lib --with-jasperlib=${CDMS_GRIB2LIB_DIR}/lib --with-grib2inc=${CDMS_GRIB2LIB_DIR}/include --enable-grib2 || exit 1
./configure  --enable-dap --with-ncinc=${netcdf_include_directory} --enable-drs=${CDMS_INCLUDE_DRS} --enable-hdf=${CDMS_INCLUDE_HDF} --enable-pp=${CDMS_INCLUDE_PP} --enable-ql=${CDMS_INCLUDE_QL} --cache-file=/dev/null --prefix=${PREFIX} --with-nclib=${netcdf_library_directory} --with-hdfinc=${CDMS_HDF_DIR}/include --with-hdflib=${CDMS_HDF_DIR}/lib --with-grib2lib=${CDMS_GRIB2LIB_DIR}/lib --with-jasperlib=${CDMS_GRIB2LIB_DIR}/lib --with-grib2inc=${CDMS_GRIB2LIB_DIR}/include --enable-grib2 || exit 1
echo "make cdms"
make cdms || exit 1
echo "make cddrs"
make cddrs || exit 1
echo "make cdunif"
make cdunif || exit 1
echo "make ${target}"
make ${target} || exit 1
echo "make bininstall"
make bininstall || exit 1
echo /bin/cp lib/libcdms.a ${PREFIX}/lib/libcdms.a
/bin/cp lib/libcdms.a ${PREFIX}/lib/libcdms.a
echo /bin/cp -R include ${PREFIX}/include/cdms
/bin/cp -R include ${PREFIX}/include/cdms
echo "Done building the CDMS library."
