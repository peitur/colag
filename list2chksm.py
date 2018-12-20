#!/usr/bin/env python3

import sys
import hashlib

from pprint import pprint
from pathlib import Path

################################################################################
## Hashing large files
################################################################################
def data_hash( buffer, **opt ):

    chksum = "md5"
    if 'checksum' in opt:
        chksum = opt['checksum']

    if chksum in ("md5", "sha1", "sha256", "sha512"):
        if chksum == "md5":
            hasher = hashlib.md5()
        elif chksum == "sha1":
            hasher = hashlib.sha1()
        elif chksum == "sha256":
            hasher = hashlib.sha256()
        elif chksum == "sha512":
            hasher = hashlib.sha512()

        hasher.update( buffer.encode('utf-8') )
        return hasher.hexdigest()

    raise RuntimeError( "Unknown hash function %s" % ( chksum ) )

################################################################################
## Local file operaitons
################################################################################

def load_file( lmbda, **opt ):
    result = 0
    filename = opt['filename']
    try:
        fd = open( filename, "r" )
        for line in fd.readlines():
            line = line.rstrip().lstrip()
            result += 1
            if len( line ) > 0:
                yield (line, lmbda( line, **opt ) )
#            result.append( line.lstrip().rstrip() )
    except Exception as e:
        print("ERROR Reading %s: %s" % ( filename, e ))

    return result




################################################################################



if __name__ == "__main__":
    opt = dict()
    opt['script'] = sys.argv.pop(0)
    opt['filename'] = sys.argv.pop(0)
    opt['checksum'] = "sha256"

    if len( sys.argv ) > 0:
        opt['checksum'] = sys.argv.pop(0)

    for x in load_file( data_hash, **opt ):
        print("%s %s" % ( x[0], x[1] ) )
