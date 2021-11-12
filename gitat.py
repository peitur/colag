#!/usr/bin/env python3

import pathlib
import sys,re,os,re, datetime
import subprocess, shlex
# import requests
import json
import hashlib
import getopt

from datetime import datetime
from pprint import pprint
from pathlib import Path


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


def run_command( cmd, **opt ):
    debug = opt.get("debug", False )
    res = list()
    
    if type( cmd ).__name__ == "str":
        cmd = shlex.split( cmd )

    if debug: print( "CMD Running:> '%s'" % ( " ".join( cmd ) ) )

    prc = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd=opt.get( "cwd", None ), universal_newlines=True, shell=False )
    for line in prc.stdout.readlines():
        res.append( line.rstrip() )
        if prc.poll():
            break
    return ( prc.returncode, res )
    
def git_repo_name( repo_str ):
    repo_url_name = re.split( r"/", repo_str )[-1]
    m =re.match( r"^(\S+)\.git$", repo_url_name )
    if m:
        return m.group(1)
    return repo_url_name
    
def git_repo_sync( item, **opt ):
    debug = opt.get("debug", False )
    targetdir = opt.get( 'target' )

    if 'repo' not in item:
        raise AttributeError("Missing repo")
    
    if 'rename' in item:
        targetdir =  pathlib.Path("%s/%s" % ( targetdir, item['rename']))
    else:
        targetdir = pathlib.Path("%s/%s" % ( targetdir, git_repo_name( item['repo' ] )))
  
    print("[+] Sync of %s in %s ... " % ( item['repo'] , targetdir ), end="" )
    
    cmd = list()
    cmd.append("git")
    if targetdir.exists():
        
        opt['cwd'] = str( targetdir )
        cmd.append( "pull" )
        cmd.append("--ff-only")
        print("update")
        
    else:
        opt['cwd'] = None
        cmd.append("clone")
        cmd.append( item['repo'] )
        cmd.append( str( targetdir ) )
        print("new")

    ret = list()
    try:
        
        ( retcode, result ) = run_command( cmd, **opt )
        if retcode not in ( 0, "0" ):
            print("[!] %s" % ( "!"*32) )
            print("[!] Git operation failed!")
            print("[!] %s" % ( "!"*32) )
            print("[!] ExitCode: %s" % ( retcode ) )
            for line in result:
                print("[!] %s" % ( line ) )
            print("[!] %s" % ( "!"*32) )
            
    except Exception as e:
        raise e
    return cmd






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
    opt['debug'] = False
    opt['config_file'] = "gitat.json"
    
    config =  json.load( open( opt['config_file'], "r" ) ).pop(0)

    if 'target' not in config:
        raise AttributeError("Missing target direcotry")
    
    opt['target'] = config['target']
    
    if 'debug' in config:
        opt['debug'] = boolify( config['debug'] )
        
    for bf in sys.argv[1:]:
        
        sitelist = json.load( open( bf, "r" ) )
        for site in sitelist:
            if opt['debug']:
                pprint( site )
            git_repo_sync( site, **opt )

