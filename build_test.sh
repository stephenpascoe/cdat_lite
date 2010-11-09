#!/bin/sh
#
# Build and test cdat_lite
#
# This script assumes the presence of NetCDF3/4 and virtualenv
# 
#!NOTE: This script won't work as expected if you have numpy installed
#       in your system python


########################################################################
# Customisation section.
#
# Select your NetCDF installation and numpy version here.  The script
# will attempt to install numpy and cdat_lite in a clean virtualenv.
#

NETCDF_HOME=/opt/netcdf-4.1.1-classic
#HDF5_HOME=/opt/hdf5
NUMPY_VERSION=1.5

DIST_DIR=$PWD/dist
VIRTUALENV=$PWD/test_venv
PIP_CACHE=$HOME/.pip/cache

########################################################################

export NETCDF_HOME HDF5_HOME NUMPY_VERSION DIST_DIR VIRTUALENV PIP_CACHE

(
    virtualenv --no-site-packages $VIRTUALENV
    cd $VIRTUALENV

    ./bin/pip install --download-cache=$PIP_CACHE  nose
    if [ $? != 0 ]
    then
	echo "nose install failed"
	exit 1
    fi

    ./bin/pip install --download-cache=$PIP_CACHE  numpy==${NUMPY_VERSION}
    if [ $? != 0 ]
    then
	echo "Numpy install failed"
	exit 1
    fi

    ./bin/pip install -f file://${DIST_DIR} --no-index --download-cache=$PIP_CACHE cdat_lite
    if [ $? != 0 ]
    then
	echo "cdat_lite install failed"
	exit 1
    fi

    ./bin/nosetests cdat_lite
)