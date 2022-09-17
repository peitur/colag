#!/usr/bin/env python3

import pathlib
import sys,re,os,re
import datetime
# import requests
import json
import hashlib, random, string
import tarfile, zipfile

from pprint import pprint

BOOLIFY_TRUE=( True, "True", "Yes", "yes" )
BOOLIFY_FALSE=(False, "False", "No", "no")

def boolify( s ):
    if s in BOOLIFY_TRUE:
        return True
    elif s in BOOLIFY_FALSE:
        return False
    else:
        raise AttributeError("Bad boolish value" )
    
    
if __name__ == "__main__":
    pprint( BOOLIFY_TRUE + BOOLIFY_FALSE )
    
    
def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )

################################################################################
## Hashing large files
################################################################################
def file_hash( filename, chksum="sha256" ):
    BLOCKSIZE = 65536

    if chksum == "sha1":
        hasher = hashlib.sha1()
    elif chksum == "sha224":
        hasher = hashlib.sha224()
    elif chksum == "sha256":
        hasher = hashlib.sha256()
    elif chksum == "sha384":
        hasher = hashlib.sha384()
    elif chksum == "sha512":
        hasher = hashlib.sha512()
    elif chksum == "md5":
        hasher = hashlib.md5()
    else:
        hasher = hashlib.sha256()

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()



def time_now_raw():
    return datetime.datetime.now()

def time_now_isoformat():
    return time_now_raw().isoformat()

def time_now_string():
    return time_now_raw().strftime( "%Y%m%d_%H%M%S.%f" )

def date_now_string():
    return time_now_raw().strftime( "%Y%m%d" )

def random_string( length ):
    return ''.join(random.SystemRandom().choice( string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range( length ))

def random_tempdir( rootdir="/tmp", rlen=5, create=False ):
    random_dir = "%s/%s" % ( rootdir, random_string( rlen ) )
    if create and not pathlib.Path( random_dir ).exists():
        os.makedirs( random_dir, exists_ok=False )
    return random_dir


if __name__ == "__main__":
    pass