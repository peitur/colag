#!/usr/bin/env python3

import sys, os, re
import hashlib
import traceback
from pprint import pprint
from pathlib import Path

SUPPORTED_CHECKSUM=("md5", "sha1", "sha224", "sha256", "sha384","sha512")

################################################################################
## Hashing large files
################################################################################
def file_hash( filename, chksum="sha256" ):
    BLOCKSIZE = 65536

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
        hasher = hashlib.sha256()

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def data_hash( buffer, **opt ):

    chksum = "md5"
    if 'checksum' in opt:
        chksum = opt['checksum']

    if chksum in SUPPORTED_CHECKSUM:
        if chksum == "md5":
            hasher = hashlib.md5()
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

#        print( type(buffer ) )
        try:
            hasher.update( buffer.encode('utf-8', "ignore") )
            return hasher.hexdigest()
        except Exception as e:
            print_exception(e)

    raise RuntimeError( "Unknown hash function %s" % ( chksum ) )

################################################################################
## Local file operaitons
################################################################################

def load_file( lmbda, **opt ):
    result = 0
    filename = opt['filename']
    try:
        fd = open( filename, "r", encoding="latin-1" )
        for line in fd.readlines():
            line = line.rstrip().lstrip()
            result += 1
            if len( line ) > 0:
                yield (line, lmbda( line, **opt ) )
#            result.append( line.lstrip().rstrip() )
    except Exception as e:
        print("ERROR Reading %s: %s" % ( filename, e ))
        print_exception( e )

    return result

def dirtree( path, filter=".*" ):
    res = list()
    for f in [ Path("%s/%s" %( path, f.name )) for f in Path( path ).iterdir() if re.match( filter, f.name ) and f.name not in (".","..", ".git") ]:
       if f.is_dir():
           res += dirtree( str( f ), filter )     
       elif f.is_file():
           res.append( f )
    return res

def print_exception( e ):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("*** print_tb:")
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print("*** print_exception:")
    # exc_type below is ignored on 3.5 and later
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                                limit=2, file=sys.stdout)
    print("*** print_exc:")
    traceback.print_exc(limit=2, file=sys.stdout)
    print("*** format_exc, first and last line:")
    formatted_lines = traceback.format_exc().splitlines()
    print(formatted_lines[0])
    print(formatted_lines[-1])
    print("*** format_exception:")
    # exc_type below is ignored on 3.5 and later
    print(repr(traceback.format_exception(exc_type, exc_value,
                                            exc_traceback)))
    print("*** extract_tb:")
    print(repr(traceback.extract_tb(exc_traceback)))
    print("*** format_tb:")
    print(repr(traceback.format_tb(exc_traceback)))
    print("*** tb_lineno:", exc_traceback.tb_lineno)

################################################################################


if __name__ == "__main__":
    opt = dict()
    opt['script'] = sys.argv.pop(0)
    opt['path'] = "."
    opt['checksum'] = "sha1"

    if len( sys.argv ) > 0:
        opt["path"] = sys.argv.pop(0)

    if len( sys.argv ) > 0:
        opt["checksum"] = sys.argv.pop(0)

    for f in dirtree( opt["path"] ):
        print( "%s : %s" % (f, file_hash( str(f), opt["checksum"] )))
