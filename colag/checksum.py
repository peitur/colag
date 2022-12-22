#!/usr/bin/env python3

import pathlib
import sys,re,os,re
import hashlib, random, string

import colag.util

SUPPORTED_CHECKSUM=("md5", "sha1", "sha224", "sha256", "sha384","sha512")
CHECKSUM_MAP={
    32:"md5",
    40:"sha1",
    56:"sha224",
    64:"sha256",
    96:"sha384",
    128:"sha512",    
}


from pprint import pprint


################################################################################
## Hashing large files
################################################################################
def get_hasher( chksum="sha256" ):
    hasher = None
    if chksum in SUPPORTED_CHECKSUM:
        if chksum == "md5":
            hasher = hashlib.sha1()
        elif chksum == "sha1":
            hasher = hashlib.sha1()
        elif chksum == "sha224":
            hasher = hashlib.sha224()
        elif chksum == "sha256":
            hasher = hashlib.sha256()
        elif chksum == "sha384":
            hasher = hashlib.sha384()
        elif chksum == "sha512":
            hasher = hashlib.sha512()
    else:
        raise AttributeError("Hash algorithm not supported: %s" % ( chksum  ) )

    return hasher    

def file_list_hash( filelist, chksum="sha256", filter=".*" ):
    BLOCKSIZE = 65536

    hasher =  get_hasher( chksum )
    
    for f in filelist:
        with open( f, 'rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def file_hash( filename, chksum="sha256", **opt ):
    BLOCKSIZE = 65536

    hasher =  get_hasher( chksum )

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def data_hash( buffer, **opt ):

    chksum = opt.get('checksum', "sha1" )

    try:
        hasher =  get_hasher( chksum )
        hasher.update( buffer.encode('utf-8', "ignore") )
        return hasher.hexdigest()
    except Exception as e:
        print_exception(e)

    raise RuntimeError( "Unknown hash function %s" % ( chksum ) )

def detect_algorithm( s ):
    if len( s ) in CHECKSUM_MAP:
        return CHECKSUM_MAP[ len(s) ]
    raise AttributeError("Malformed checksum size")


if __name__ ==  "__main__":
    pprint( file_list_hash( colag.util.dirtree( "." ) ))

