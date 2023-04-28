#!/usr/bin/env python3

import sys,re,os,re, datetime
import subprocess, shlex
# import requests
import json
import hashlib

import colag.rsmatic
import colag.util

from datetime import datetime
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
    debug = False

    if 'debug' in opt: debug = opt['debug']
    if 'bsize' in opt: bsize = opt['bsize']
    if 'timeout' in opt: timeout = opt['timeout']

    if 'overwrite' in opt and opt['overwrite'] in (True,False):
        overwrite = opt['overwrite']

    if Path( local_filename ).exists():
        l_size = Path( local_filename ).stat().st_size

    r = requests.get( url_filename, timeout=timeout, stream=True)
    if 'content-length' in r.headers:
        r_size = r.headers['content-length']

    if debug:
        pprint( r.headers )

    if r.status_code != 200:
        print("# ERROR: Could not find %s,  %s : " % ( url_filename, r.status_code ) )
        return None

    if not Path( local_filename ).exists() or overwrite:
        with open( local_filename, 'wb') as f:
            for chunk in r.iter_content( chunk_size=bsize ):
                if chunk: # filter out keep-alive new chunks
                    x_size += len( chunk )
                    f.write(chunk)
                    print("# [ %s ] [ %s / %s ] --> %s" % ( proj, x_size, r_size, local_filename ), end="\r" )
        print("")
    else:
        print("# [ %s ] [ skip ] --> %s " % ( proj, local_filename ) )

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

def extract_protocol( url ):
    m = re.match(r"^(http|https|rsync|ftp|file)://(.+)", url )
    if m:
        return m.group(1)
    return None

def run_command_iter( cmd, **opt ):
    debug = opt.get("debug", False )

    if type( cmd ).__name__ == "str":
        cmd = shlex.split( cmd )

    if debug: print( "Running: '%s'" % ( " ".join( cmd ) ) )
    
    buffer = list()
    errors = list()
    prc = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines=True, shell=False )
    for line in prc.stdout.readlines():
        if debug:
            print("DEBUG: '%s'" % ( line.lstrip().rstrip() ) )
            
        buffer.append( line.rstrip().lstrip() )
                
        while( len( buffer ) >= 10 ):
            buffer.pop(0)
            
        yield line.rstrip().lstrip()
        if prc.poll():
            print("#"*32)
            pprint( buffer )
            print("#"*32)

            break


def rsync_file_list_x( url, target=None, **opt ):
    debug = opt.get("debug", False )
    cmd = list()
    cmd.append("rsync")
    cmd.append("-r")
    cmd.append("--no-motd")
#    if 'list' in opt and boolify( opt['list'] ):
    cmd.append("--list-only")

    if 'logfile' in opt and type( opt['logfile'] ).__name__ in ("str"):
        cmd.append( "--log-file=%s" % (opt["logfile"] ) )
        cmd.append( "--log-file-format=\"%t %o %i %b [%l] %M %n\"" )

    if 'bwlimit' in opt and type( opt['bwlimit'] ).__name__ in ("int", "float"):
        cmd.append( "--bwlimit=%s" % (opt["bwlimit"] ) )

    cmd.append( url )

    if target:
        cmd.append( target )

    ret = list()
    try:
        for f in run_command_iter( cmd, **opt ):
            yield f

    except Exception as e:
        raise e
    return ret



def rsync_file_get_x( url, target, **opt ):
    debug = opt.get("debug", False )
    cmd = list()
    cmd.append("rsync")
    cmd.append("-a")
    cmd.append("-z")
    cmd.append("--safe-links")
    cmd.append("--no-motd")
    cmd.append("--out-format=\"%'i %'b %t %n\"")
#    if 'list' in opt and boolify( opt['list'] ):

    if 'logfile' in opt and type( opt['logfile'] ).__name__ in ("str"):
        cmd.append( "--log-file=%s" % (opt["logfile"] ) )
        cmd.append( "--log-file-format=\"%t %o %i %b [%l] %M %n\"" )

    if 'bwlimit' in opt and type( opt['bwlimit'] ).__name__ in ("int", "float","str"):
        cmd.append( "--bwlimit=%s" % (opt["bwlimit"] ) )

    if 'deltype' in opt and opt['deltype'] in ("before","after","during","delay","excluded"):
        cmd.append("--delete-%s" % (opt['deltype'] ) )

    cmd.append( url )
    cmd.append( target )

    ret = list()
    try:
        for f in run_command_iter( cmd, **opt ):
            yield f

    except Exception as e:
        raise e
    return ret


def rsync_file_list( opt ):
    debug = opt.get("debug", False )

    opt['options']['list-only'] = True
    conf = colag.rsmatic.RsmaticConfig( opt )
    cmd = colag.rsmatic.RsyncCommand( conf ).run()

    try:

        for f in run_command_iter( cmd,debug=True  ):
            yield f

    except Exception as e:
        raise e


def rsync_file_get( opt ):
    debug = opt.get("debug", False )

    conf = colag.rsmatic.RsmaticConfig( opt )
    cmd = colag.rsmatic.RsyncCommand( conf ).run()
    
    try:
        for f in run_command_iter( cmd, debug=debug ):
            yield f

    except Exception as e:
        raise e




def read_env( key ):
    if key not in os.environ:
        return None
    return os.environ.get( key )

def boolify( s ):
    if s in (True, 1, "1", "yes", "Yes", "YES", "True" ):
        return True
    elif s in (False, 0, "0", "no", "No", "NO", "False"):
        return False
    else:
        raise AttributeError("Bool string type not supported %s" % ( s ) )

def byte_unit( s ):
    current = int( s )
    units = ["B","KB","MB","GB", "TB", "PB"]

    for i,x in enumerate( units ):
        if current < 1024:
            return (current, units[i] )

        if i >= len( units ) - 1:
            return (current, units[i] )

        current = current / 1024
    return (0,"none")


################################################################################
def _apply_version( string, version ):
    return re.sub( r"<%\s*version\s*%>", version, string )

def _apply_project( string, version ):
    return re.sub( r"<%\s*project\s*%>", version, string )

def time_now_raw():
    return datetime.now()

def time_now_isoformat():
    return time_now_raw().isoformat()

def time_now_string():
    return time_now_raw().strftime( "%Y%m%d_%H%M%S.%f" )

def date_now_string():
    return time_now_raw().strftime( "%Y%m%d" )


################################################################################


if __name__ == "__main__":
    opt = dict()
    opt['mode'] = None
    opt['config'] = ["rsmatic.list"]

    if len( sys.argv ) > 1:
        opt['mode'] = sys.argv[1]
    else:
        print("ERROR: Missing mode, must be one of [sync,list]")
        sys.exit(1)

    if len( sys.argv ) > 2:
        opt['config'] = sys.argv[2:]

    if opt['mode'] not in ("sync","list"):
        print("ERROR: Unknown mode %s, suported modes are [sync,list] " % ( opt['mode'] ) )
        sys.exit(2)

    tot_stats = dict()

    for config in opt['config']:
        print("Loading sites from file %s" % ( config ) )

        for siteline in load_file( config ):

            target = Path( siteline['target'] )
            site = siteline['source']
            debug = colag.util.boolify( siteline.get("debug", False ) )

            logfile = "%s/%s.%s.log" % ( target, opt['mode'], time_now_string() )
            if 'logfile' in siteline:
                logfile = siteline['logfile']

            stats = dict()
            stats['num_items'] = 0
            stats['num_bytes'] = 0
            stats['num_files'] = 0
            stats['num_dirs'] = 0
            stats['num_links'] = 0
            stats['num_unknownitem'] = 0

            if opt['mode'] in ("sync", "get"):

                if not target.exists():
                    target.mkdir( parents=True, exist_ok=True )

                print("Syncing %s to %s logging to %s" % (site, target, logfile ))
                for f in rsync_file_get( siteline ):
                    stats['num_items'] += 1
                    parts = re.split( r"\s+", f )
                    if len( parts ) == 5:
                        f_pfield = parts[0]
                        f_size = int( re.sub( r",", "", parts[1] ) )
                        f_date = parts[2]
                        f_time = parts[3]
                        f_name = parts[4]

                        stats['num_bytes'] += f_size
                        if re.match(r"^.f.+", f_pfield ):
                            stats['num_files'] += 1
                        elif re.match(r"^.d.+", f_pfield ):
                            stats['num_dirs'] += 1
                        elif re.match(r"^.l.+", f_pfield ):
                            stats['num_links'] += 1
                        else:
                            stats['num_unknownitem'] += 1

            elif opt['mode'] in ("list"):

                if not target.exists():
                    target.mkdir( parents=True, exist_ok=True )

                print("Listing %s logging to %s" % (site, logfile ))
                for f in rsync_file_list( siteline ):

                    if re.match("^rsync.*", f ):
                        continue
                    
                    stats['num_items'] += 1
                    parts = re.split( r"\s+", f )
                    if len( parts ) == 5:
                        f_pfield = parts[0]
                        f_size = int( re.sub( r",", "", parts[1] ) )
                        f_date = parts[2]
                        f_time = parts[3]
                        f_name = parts[4]

                        stats['num_bytes'] += f_size
                        if re.match(r"^-.+", f_pfield ):
                            stats['num_files'] += 1
                        elif re.match(r"^d.+", f_pfield ):
                            stats['num_dirs'] += 1
                        elif re.match(r"^l.+", f_pfield ):
                            stats['num_links'] += 1
                        else:
                            stats['num_unknownitem'] += 1

            else:
                print("Nothing to do here, unmanaged mode")
                sys.exit(8)

            for k in stats:
                if k not in tot_stats:
                    tot_stats[ k ] = 0
                tot_stats[ k ] += stats[ k ]

            ( n, u ) = byte_unit( stats["num_bytes"] )
            stats['bytes_hum'] = "%.7s %s" % ( n, u )
            stats["site"] = site
            stats["target"] = target.__str__()
            pprint( stats )

    print("-------------------------------------------")
    if 'num_bytes' in tot_stats:
        ( n, u ) = byte_unit( tot_stats["num_bytes"] )
        tot_stats['bytes_hum'] = "%.6s %s" % ( n, u )
    pprint( tot_stats )
    print("-------------------------------------------")
