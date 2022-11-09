#!/usr/bin/env python3

import sys,re,os,re, datetime
import requests
import json
import hashlib, random, string
import getopt
import tarfile, zipfile

import colag.util

from pprint import pprint
from pathlib import Path

module_seen = list()

def get_crates_url( module = "" ):
    return "https://crates.io/api/v1/crates/%s" % ( module )

def get_crates_dl_url( module, version ):
    return "https://crates.io/api/v1/crates/%s/%s/download" % ( module, version )

def random_string( length ):
    return ''.join(random.SystemRandom().choice( string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range( length ))

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

################################################################################

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

def get_versions_index( module, **opt ):
    res = dict()
    module = module.lstrip().rstrip()
    q = get_request( module, get_crates_url( module ))

    if not q:
        pprint( q )
        return None

    if 'versions' in q:
        for x in q['versions']:
            res[ q['versions']['num'] ] = x

    return res

def version_regex( vstring ):

    m = re.match( r"([\^=]*)(.+)", vstring )
    h = m.group(1)
    v = m.group(2)
    
    p = re.split( r"\.", v )
    
    
    ## Any version, so lets take newest, i.e. first matching
    if len(p) == 0:
        return r".+"

    if len(p) <= 1 and p[-1] in ("*"):
        return r".+"

    if len( p ) > 1:
        if h in ("^") or p[-1] in ("*"):
            return r"^%s\." % ( ".".join( p[:len(p)-1]) )    

        if h in ("","="):
            return r"^%s$" % ( ".".join( p[:len(p)]) )    
    
    return r".+"
        
    
def collect_pkg_full( module, **opt ):
    module = module.lstrip().rstrip()

    if len( module ) == 0:
        return None

    if module in module_seen:
        return None
    else:
        module_seen.append( module )

    q = get_request( module, get_crates_url( module ))
    if not q:
        pprint( q )
        return None

    latest = dict()
    links = dict()

    if 'versions' in q:

        i = 0  
        if not opt['prerelease']:
            while re.match( r"^[.0-9]+-(rc|beta|alpha|alfa|test).*$", q['versions'][i]['num'] ) and i < len( q['versions'] ):
                i += 1
                if i >= len( q['versions'] ):
                    break
            if i < len( q['versions'] ):
                latest =  q['versions'][i].copy()

        if 'version' in opt and opt['version']:
            i = 0
            rx = version_regex( opt['version'] )
            while not re.match( rx, q['versions'][i]['num'] ):
                i += 1
                if i >= len( q['versions'] ):
                    break
                
            if i < len( q['versions'] ):
                latest =  q['versions'][i].copy()
        
        if not latest:
            latest = q['versions'][0]
        
        links = latest['links']
        version = latest['num']
        url = get_crates_dl_url( module, version )
        print( "# [ %s ] [ checking ] Version: %s  => %s" % ( module, version, url ) )
        filename = "%s-%s.crate" % (module, version)
        fullfilename = "%s/%s" %( opt['target'] , filename )
        chkfile = "%s.%s.json" % ( fullfilename, opt['checksum'] )

        if not Path( fullfilename ).exists() or not Path( chkfile ).exists():

            if not download_file( module, url, fullfilename ):
                return None

            hd = dict()

            fst = Path( fullfilename ).stat()
            hd['01.filename'] = filename
            hd['02.source'] = url
            hd['03.size'] = int( fst.st_size )
            hd['04.ctime'] = datetime.datetime.fromtimestamp( fst.st_ctime ).isoformat()
            hd['05.mtime'] = datetime.datetime.fromtimestamp( fst.st_mtime ).isoformat()
            hd['06.atime'] = datetime.datetime.fromtimestamp( fst.st_atime ).isoformat()
            hd['07.checksum'] = "%s:%s" % ( opt['checksum'], colag.util.file_hash( fullfilename, opt['checksum'] ) )
            hd['10.release'] = latest

            if not Path( chkfile ).exists():
                print( "# [ %s ] [ checksum ] %s -> %s  " % ( module, fullfilename, chkfile ) )
                write_file( chkfile, [ hd ] )

        reqlist_raw = get_request( module, "https://crates.io%s" %( links['dependencies']))
        if len( reqlist_raw['dependencies']  ) > 0:
            for r in reqlist_raw['dependencies'] :
                req = r['crate_id']
                ver = r['req']
                
                if len( req ) == 0: continue
                if req == module: continue
                if re.match( r"[\[\]]+", req ): continue

#                    print("## [%s] %s => %s" % ( len(module_seen), module, req ) )
                opt['version'] = ver
                collect_pkg_full( req, **opt )

    return None


if __name__ == "__main__":
    opt = dict()

    opt['script'] = sys.argv.pop(0)
    opt['filename'] = "trailer.txt"
    opt['target'] = "trailer"
    opt['config'] = None
    opt['checksum'] = "sha256"
    opt['prerelease'] = False
    
    if len( sys.argv ) > 0:
        opt['filename'] = sys.argv.pop(0)

    print( "reading crate list from %s" % ( opt['filename'] ) )
    if Path( "trailer.json" ).exists():
        cfg = load_file( "trailer.json" )[0]
        opt['target'] = cfg['target']
        if 'prerelease' in cfg:
            opt['prerelease'] = cfg['prerelease']

    target = Path( opt['target'] )
    if not target.exists():
        target.mkdir()

    ##
    ## 1. If module exists, create temp dir
    ## 2. download json
    ## 3. download file specified in json
    ## 4. unpack file to temp dir
    ## 5. Check requirements
    ## -- for each requirement, redo from step 1

    modules = load_file( opt['filename'] )
    for module in modules:
        version = None
        m =re.match(r"^(\S+)\s*=\s*\"(\S+)\"", module )
        if m:
            module = m.group(1).lstrip().rstrip()
            version = m.group(2).lstrip().rstrip()
            
        opt['version'] = version
        collect_pkg_full( module, **opt )
