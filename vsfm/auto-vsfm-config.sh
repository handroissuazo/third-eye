#!/bin/sh

# Must be root to run script
if [ "$(id -u)" != "0" ]; then
   echo "ERROR: Must be root to run script!" 1>&2
   exit 1
fi

# Get current directory
CURRENT_VSFM_DIR=$PWD

echo "${CURRENT_VSFM_DIR}/vsfm/bin" > /etc/ld.so.conf.d/vsfm.conf

sudo ldconfig
