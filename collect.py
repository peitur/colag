#!/usr/bin/env python3

import sys,re,os,re, datetime
import requests
import json
import hashlib
import getopt

from pprint import pprint
from pathlib import Path

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
    else:
        hasher = hashlib.sha256()

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()

################################################################################
## HTTP operations, download large files
################################################################################

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
                    print("# [ %s ] [ %s / %s ] --> %s -> %s" % ( proj, x_size, r_size, url_filename, local_filename ), end="\r" )
        print("")
    else:
        print("# [ %s ] [ skip ] --> %s -> %s " % ( proj, url_filename, local_filename ) )

    r.close()

    return local_filename

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

################################################################################

def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )

################################################################################
def _apply_version( string, version ):
    return re.sub( r"<%\s*version\s*%>", version, string )

def _apply_project( string, version ):
    return re.sub( r"<%\s*project\s*%>", version, string )

################################################################################


if __name__ == "__main__":
    opt = dict()

    opt['config'] = "collect.json"
    opt['config_d'] = "collect.d"

    opt['load'] = None
    opt['script'] = sys.argv.pop(0)
    if len( sys.argv ):
        opt['load'] = sys.argv.pop(0)

    config = load_file( "collect.json" )[0]
    conf_dir = Path( opt['config_d'] )

    for conf_file in conf_dir.iterdir():

        for xo in load_file( str( conf_file ) ):
            hdata = dict()

            x_dir = re.split("\.", str( conf_file.name ) )[0]
            if opt['load'] and opt['load'] != x_dir:
                continue

            if 'skip' in xo and xo['skip']:
                continue

            if not Path( "%s/%s" % ( config['target'], x_dir )).exists():
                Path( "%s/%s" % ( config['target'], x_dir )).mkdir()

            bsize = 8192
            chksum = "sha256"
            if 'checksum' in config: chksum = config['checksum']
            if 'bsize' in config: bsize = int( config['bsize'] )
            if 'bsize' in xo: bsize = int( xo['bsize'] )
            if 'version' not in xo: xo['version'] = ""

            x_url =  _apply_version( xo['url'], xo['version'] )
            x_path = "%s/%s/%s" % ( config['target'], x_dir, re.split( r"\/", x_url )[-1] )

            if 'filename' in xo:
                x_path = "%s/%s/%s" % ( config['target'], x_dir, xo['filename'] )

            try:
                download_file( x_dir, x_url, x_path, bsize=bsize )
            except Exception as e:
                print( "# EXCEPTION: Failed to download %s to %s" % ( x_url, x_path ) )
                pprint( e )

            if not Path( x_path).exists():
                print( "# ERROR: Failed to download %s to %s" % ( x_url, x_path ) )
                continue

            chkfile = "%s.%s.json" % (x_path, chksum)

            fst = os.stat( x_path )
            hdata['01.filename'] = x_path
            hdata['02.source'] = x_url
            hdata['03.atime'] = datetime.datetime.fromtimestamp( fst.st_atime ).isoformat()
            hdata['04.ctime'] = datetime.datetime.fromtimestamp( fst.st_ctime ).isoformat()
            hdata['05.mtime'] = datetime.datetime.fromtimestamp( fst.st_mtime ).isoformat()
            hdata['06.size'] = fst.st_size
            hdata['07.checksum'] = "%s:%s" % ( chksum, file_hash( x_path, chksum ) )

            if 'signature' in xo:
                x_sign = _apply_version( xo['signature'], xo['version'] )
                x_lsign = _apply_version( "%s/%s/%s" % ( config['target'], x_dir, re.split( r"\/", xo['signature'] )[-1] ), xo['version'] )

                try:
                    download_file( x_dir, x_sign, x_lsign, bsize=1024 )
                except Exception as e:
                    print( "# EXCEPTION: Failed to download %s to %s" % ( x_sign, x_lsign ) )
                    pprint( e )

                hdata['10.signature'] = x_lsign
                hdata['11.signature_checksum'] = "%s:%s" % ( chksum, file_hash( x_lsign, chksum ) )

            if not Path( chkfile ).exists():
                write_file( chkfile, [ hdata ] )
