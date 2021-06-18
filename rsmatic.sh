#!/bin/bash


COL_ERR="\033[0;31m"
COL_OK="\033[0;32m"
COL_INFO="\033[0;97m"
COL_WARN="\033[0;33m"

ENDCOLOR="\033[0;0m"

if [[ -z $1 ]]; then
  echo -e "${COL_ERR}[!]${ENDCOLOR}ERROR: Missing input file"
  exit 1
fi

BWLIMIT=""
TARGET="mirror"
LISTONLY="--list-only"

if [[ $2 ]]; then
  BWLIMIT="--bwlimit $2"
fi

if [[ ! -d ${TARGET} ]]; then
  mkdir -p ${TARGET}
fi

for SITE in $( cat $1 ); do
  echo -en "${COL_INFO}[+]${ENDCOLOR}INFO: Processing ${SITE}"
  rsync -r -q ${LISTONLY} ${BWLIMIT} ${SITE} ${TARGET}/. >> ${TARGET}/list 2>&1
  if [[ $? == 0 ]]; then
    echo -e "... ${COL_OK}OK${ENDCOLOR}"
  else
    echo -e "... ${COL_ERR}FAIL${ENDCOLOR}"
  fi
done
