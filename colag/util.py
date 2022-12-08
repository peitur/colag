#!/usr/bin/env python3

import pathlib
import sys,re,os,re
import datetime
import requests
import json
import hashlib, random, string
import tarfile, zipfile
from pathlib import Path
from pprint import pprint

from colag.checksum import file_hash
from colag.checksum import data_hash


BOOLIFY_TRUE=( True, "True", "Yes", "yes" )
BOOLIFY_FALSE=(False, "False", "No", "no")

def boolify( s ):
    if s in BOOLIFY_TRUE:
        return True
    elif s in BOOLIFY_FALSE:
        return False
    else:
        raise AttributeError("Bad boolish value" )
        
    
def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )


def download_file( proj, url_filename, local_filename, **opt ):
    x_size = 0
    l_size = 0
    r_size = 0
    bsize=1024
    overwrite = False
    timeout = 10

    if 'bsize' in opt: bsize = opt['bsize']
    if 'timeout' in opt: timeout = opt['timeout']

    if 'overwrite' in opt and opt['overwrite'] in (True,False):
        overwrite = opt['overwrite']

    if Path( local_filename ).exists():
        l_size = Path( local_filename ).stat().st_size

    r = requests.get( url_filename, timeout=timeout, stream=True)
    if 'content-length' in r.headers:
        r_size = r.headers['content-length']

    if r.status_code != 200:
        print("# ERROR: Could not find %s,  %s : " % ( url_filename, r.status_code ) )
        return None

    if int( l_size ) != int( r_size ) or overwrite:
        with open( local_filename, 'wb') as f:
            for chunk in r.iter_content( chunk_size=bsize ):
                if chunk: # filter out keep-alive new chunks
                    x_size += len( chunk )
                    f.write(chunk)
                    print("# [ %s ] [ %s / %s ] --> %s" % ( proj, x_size, r_size, local_filename ), end="\r" )
        print("")
    else:
        print("# [ %s ] [ skip ] --> %s -> %s " % ( proj, url_filename, local_filename ) )

    r.close()

    return local_filename


def get_request( proj, url , **opt ):
    x_size = 0
    l_size = 0
    r_size = 0
    bsize=1024
    overwrite = False
    timeout = 10

    if 'bsize' in opt: bsize = opt['bsize']
    if 'timeout' in opt: timeout = opt['timeout']

    r = requests.get( url, timeout=timeout )
    if 'content-length' in r.headers:
        r_size = r.headers['content-length']

    if r.status_code != 200:
        print("# ERROR: Could not find %s,  %s : " % ( url, r.status_code ) )
        return None

    return r.json()

################################################################################
## Local file operaitons
################################################################################

def _read_text( filename ):
    result = list()
    try:
        fd = open( filename, "r" )
        for line in fd.readlines():
            result.append( line.lstrip().rstrip() )
        return result
    except Exception as e:
        print("ERROR Reading %s: %s" % ( filename, e ))

    return result

def _read_json( filename ):
    return json.loads( "\n".join( _read_text( filename ) ) )

def load_file( filename ):
    filesplit = re.split( r"\.", filename )
    if filesplit[-1] in ( "json" ):
        return _read_json( filename )
    else:
        return _read_text( filename )


def _write_json( filename, data ):
    return _write_text( filename, json.dumps( data, indent=2, sort_keys=True ) )

def _write_text( filename, data ):
    fd = open( filename, "w" )
    fd.write( str( data ) )
    fd.close()

def write_file( filename, data ):
    filesplit = re.split( "\.", filename )
    if filesplit[-1] in ( "json" ):
        return _write_json( filename, data )
    else:
        return _write_text( filename, data )

def semi_crunch( string ):
    return re.split( r"[;]", string )

def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )

def rmdir_tree( path ):
    pth = Path( path )
    for sub in pth.iterdir() :
        if sub.is_dir() :
            rmdir_tree(sub)
        else:
            sub.unlink()
    pth.rmdir()

def mk_temp_dir( root="/tmp" ):
    return "%s/crate_%s" % ( root, random_string( 6 ) )


def time_now_raw():
    return datetime.datetime.now()

def time_now_isoformat():
    return time_now_raw().isoformat()

def time_now_string():
    return time_now_raw().strftime( "%Y%m%d_%H%M%S.%f" )

def date_now_string():
    return time_now_raw().strftime( "%Y%m%d" )

def random_string( length=10):
    return ''.join(random.SystemRandom().choice( string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range( length ))

def random_tempdir( rootdir="/tmp", rlen=5, create=False ):
    random_dir = pathlib.Path( "%s/%s" % ( rootdir, random_string( rlen ) ) )
    if create and not random_dir.exists():
        random_dir.mkdir( exist_ok=False, parents=True )
    return random_dir

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

if __name__ == "__main__":
    pass