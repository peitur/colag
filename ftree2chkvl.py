#!/usr/bin/env python3

import sys, os, re
import hashlib
import traceback
from pprint import pprint
from pathlib import Path

SUPPORTED_CHECKSUM=("md5", "sha1", "sha224", "sha256", "sha384","sha512")
CHECKSUM_MAP={
    32:"md5",
    40:"sha1",
    56:"sha224",
    64:"sha256",
    96:"sha384",
    128:"sha512",    
}

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


def data_hash( buffer, chksum="sha1", **opt ):

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



def filelist_hash( flist, chksum="sha1", **opt ):
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
    for filename in flist:
        with open( filename, 'rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


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

def dirtree( root, path="", filter=".*" ):
    res = list()

    pref = ""
    rpath = root
    if len( path ) > 0:
       rpath = "%s/%s" % ( root, path )
       pref = "%s/" % ( path )

    for f in [ "%s%s" %( pref, f.name ) for f in Path( rpath ).iterdir() if re.match( filter, f.name ) and f.name not in (".","..", ".git") ]:
       i = Path( "%s/%s" % (root, f ))
       if i.is_dir():
           res += dirtree( root, f, filter )     
       elif i.is_file():
           res.append( f )
    return res

def detect_algorithm( s ):
    if len( s ) in CHECKSUM_MAP:
        return CHECKSUM_MAP[ len(s) ]
    raise AttributeError("Malformed checksum size")

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

    opt['path'] = None
    opt['checksum'] = "sha1"
    opt['reference'] = None
    
    
    if len( sys.argv ) > 0:
        opt["path"] = sys.argv.pop(0)

    if len( sys.argv ) > 0:
        opt["reference"] = sys.argv.pop(0)

    if len( sys.argv ) > 0:
        opt["checksum"] = sys.argv.pop(0)

    if not opt['path']:
        raise  AttributeError("Missing path")
    
    if not opt['reference']:
        raise  AttributeError("Missing reference file")
    
    with open( opt['reference'], "r" ) as fp:
        for line in fp:
            line = line.lstrip().rstrip()
            (checksum, size, path ) = [ l.lstrip().rstrip() for l in re.split(r"\s+", line ) ]
            filepath = Path( "%s/%s" % ( opt['path'], path ) )
            if filepath.exists():
                fchecksum = file_hash( str( filepath ), opt['checksum'] )
                fsize = filepath.stat().st_size
                
                if checksum == fchecksum and int( size )  == fsize:
                    print("File %s ... OK" % ( path ) )
                else:
                    print("File %s ... FAIL" % ( path ) )
                    
            else:
                print("Missing %s" % ( filepath ))
            
#    for c in SUPPORTED_CHECKSUM:
#        s =  data_hash( ".", c )
#        print( "%s:\"%s\"" % ( len( s ) , c ) )