#!/usr/bin/env python3

import sys
import hashlib
import traceback
from pprint import pprint
from pathlib import Path

SUPPORTED_CHECKSUM=("md5", "sha1", "sha224", "sha256", "sha384","sha512")

################################################################################
## Hashing large files
################################################################################
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
    opt['filename'] = sys.argv.pop(0)
    opt['checksum'] = "sha256"

    if len( sys.argv ) > 0:
        opt['checksum'] = sys.argv.pop(0)

    if opt['checksum'] not in SUPPORTED_CHECKSUM:
        raise AttributeError("Unsupported checksum %s, must be one of [%s]" % ( opt['checksum'], ",".join(SUPPORTED_CHECKSUM) ) )

    for x in load_file( data_hash, **opt ):
        print("%s %s" % ( x[0], x[1] ) )
