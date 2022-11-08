#!/usr/bin/python3

import os, re, sys
import pathlib, json
import tarfile
import logging
import shutil
import hashlib
import pkg_resources

import subprocess, shlex
from pprint import pprint


DEFAULT_SOURCE="trailer"
DEFAULT_TARGET="vendor"
CARGO_FILE="Cargo.toml"
CARGO_CHECKSUM_FILE=".cargo-checksum.json"
CARGO_CHECKSUM_ALGO="sha256"

CRAATE_IMPORT_OVERWRITE=True
############

class Version( object ):
    def __init__( self, v ):
        self._split_rx = re.compile( "\." )
        self._raw_version = v

        if type( v ).__name__ == "str":
            self._version = pkg_resources.parse_version( str(v) )
        elif type( v ).__name__ == "Version":
            self._version = pkg_resources.parse_version( str(v) )
        elif type( v ).__name__ == "list":
            self._version = pkg_resources.parse_version( ".".join( [ str(x) for x in v ] ) )
        else:
            raise AttributeError("%s not supported format" % ( type(v).__name__ ) )


    def get( self ):
        return self._version


    def __str__( self ):
        return self._raw_version

    def __eq__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va == vb:
            return True
        return False


    def __ne__( self, v ):
        return not self.__eq__( v )

    def __lt__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va < vb:
            return True
        return False
    def __le__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va <= vb:
            return True
        return False

    def __gt__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va > vb:
            return True
        return False


    def __ge__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va >= vb:
            return True
        return False


############

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
    elif chksum == "md5":
        hasher = hashlib.md5()
    else:
        hasher = hashlib.sha256()

    with open( filename, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()

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


def cargo_meta_file( filepath, filename=CARGO_FILE ):
    values = list()
    cfile = "%s/%s" % ( filepath, filename )
    with open( cfile, "r" ) as fd:
        for line in fd.readlines():
            line = line.rstrip().lstrip()
            if re.match( r"^\s*#.*" , line ) or len( line ) == 0:
                continue
            values.append( line )
    return values
            
            
def cargo_meta_pkg( pkgfile ):
    try:
        tar = tarfile.open( pkgfile, "r:gz")
        p = re.compile( r"[^/]+/%s" % (CARGO_FILE) )
        for ti in tar.getmembers():
            if p.match( ti.name ):
                return [ x.decode("utf-8").lstrip().rstrip() for x in tar.extractfile( ti.name ).readlines() ]

    except KeyError as e:
        raise IndexError("Invalid crate file")
    finally:
        tar.close()
    raise IndexError("Invalid crate file, no metadata file found")

def cargo_meta_unpack_path( pkgfile ):
    try:
        tar = tarfile.open( pkgfile, "r:gz")
        p = re.compile( r"[^/]+/%s" % (CARGO_FILE) )
        for ti in tar.getmembers():
            if p.match( ti.name ):
                return pathlib.Path( ti.name ).parent

    except KeyError as e:
        raise IndexError("Invalid crate file")
    finally:
        tar.close()
    raise IndexError("Invalid crate file, no metadata file found")


def cargo_meta_parse( data ):
    values = dict()
    ctag = ""
    for line in data:
        line = line.rstrip().lstrip()

        if re.match( r"^\s*#.*" , line ) or len( line ) == 0:
            continue

        c_rx = re.match( r"\[\s*(\S+)\s*\]", line )
        if c_rx:
            ctag = c_rx.group(1)
        
        l_rx = re.match( r"^\s*(\S+)\s*=\s*\"(.+)\"", line )
        if l_rx:
            values[ "%s.%s" % ( ctag, l_rx.group(1)) ] = l_rx.group(2)
                
    return values


def cargo_extract_source( cratefile,  tpath="." ):
    if not cargo_check_source( cratefile ):
        RuntimeError("Dangerous archive file \"%s\", skipping" % ( cratefile ) )
    tar = tarfile.open( cratefile )
    try:
        tar.extractall( tpath )
    except:
        return False
    finally:
        tar.close()
    return True

def cargo_check_source( pkgfile ):
     
    rxl = [ re.compile("^/.+"), re.compile("\.\./") ]
    tar = tarfile.open( pkgfile, "r:gz")     
    try:
        for ti in tar.getmembers():
            
            for rx in rxl:
                if rx.match( ti.name ):
                    return False

    except KeyError as e:
        raise IndexError("Invalid crate file")
    finally:
        tar.close()
    return True

def rmdir_tree( path ):
    pth = pathlib.Path( path )
    for sub in pth.iterdir() :
        if sub.is_dir() :
            rmdir_tree(sub)
        else:
            sub.unlink()
    pth.rmdir()


def get_crates( dir ):
    return [ f for f in pathlib.Path( dir ).iterdir() if re.match( ".+\.crate$", f.name ) ]

def get_imported( dir ):
    return [ f for f in pathlib.Path( dir ).iterdir() if f.is_dir() ]

def highest_version( cratelist ):
    if len( cratelist ) == 0:
        return None
    
    if len( cratelist ) > 1:
        highest =  cratelist[0]
        for item in cratelist:
            if Version( item['version'] ) > Version( highest['version'] ):
                highest = item
        return highest
    else:
        return cratelist[0]

def dirtree( root, path ):
    res = list()
    for item in pathlib.Path( "%s/%s" % (root, path) ).iterdir():

        pathparts = item.parts
        rootparts = pathlib.Path( root ).parts
        ppath = "/".join( pathparts[ len( rootparts ): ] )

        if item.is_dir():
            res = res + dirtree( root, ppath )
        else:
            res.append( ppath )

    return res
    

def directory_content_checksum( root, path, chmsumfile=CARGO_CHECKSUM_FILE ):
    res = dict()

    for item in dirtree( root, path ):
        res[ str( item ) ] = file_hash( "%s/%s" %( root, str( item ) ), CARGO_CHECKSUM_ALGO )
        
    return res

def create_checksum( root, path, cratefile, chmsumfile=CARGO_CHECKSUM_FILE ):

    res = dict()
    
    res['files' ] = directory_content_checksum( root, path, chmsumfile )
    res["package"] = file_hash( cratefile )
    
    sumfile = "%s/%s/%s" %( root, path, chmsumfile )
    if pathlib.Path( sumfile ).exists():
        pathlib.Path( sumfile ).unlink()
    f = open( sumfile, "w" )
    f.write( json.dump( res, f ) )
    f.close()

if __name__ == "__main__":
    
    seen_crates = dict()
    pending_crates_meta = dict()
    imported_crates_meta = dict()
    work_list = dict()
    
    
    try:
        spath = sys.argv[1]
        tpath = sys.argv[2]
        
        crate_list = get_crates( spath )
        imported_list = get_imported( tpath )
        
        print( "Reading crates from \"%s\"" % ( spath ) )
        print( "Importing to \"%s\"" % ( tpath ) )
        print("Found %s crates in \"%s\"" % ( len( crate_list ), spath) )
        print("Found %s crates in \"%s\"" % ( len( imported_list ), tpath) )
        
        for impc in [ cargo_meta_parse( cargo_meta_file( str( i ) ) ) for i in imported_list ]:
            imported_crates_meta[ impc['package.name'] ] = {"name": impc['package.name'], "version":impc['package.version'] }
        
        for pkg in crate_list:
            impc = cargo_meta_parse( cargo_meta_pkg( str( pkg ) ) )
            if impc['package.name'] not in pending_crates_meta:
                pending_crates_meta[ impc['package.name'] ] = list()
            pending_crates_meta[ impc['package.name'] ].append( {"name": impc['package.name'], "version":impc['package.version'], "filename": pkg } )
        
        for p in pending_crates_meta:
            work_list[ p ] = highest_version( pending_crates_meta[ p ] )

        for item in work_list:
            
            crate = str( work_list[ item ]['filename'] )
            crt_meta = work_list[ item ]        
            
            print(" - \"%s\" = \"%s\" # \"%s\"" % ( crt_meta['name'], crt_meta['version'], crate ), end=" " )

            if cargo_extract_source( str( crate ), tpath ):
                crt_unp_name = cargo_meta_unpack_path( str( crate ) )
                crt_unp_path = pathlib.Path( "%s/%s" % ( tpath, crt_unp_name ) )
                crt_target = pathlib.Path( "%s/%s" %( tpath, crt_meta['name'] ) )
                crt_rollback_path = pathlib.Path("%s.old" % ( crt_target ) )
                
                if not crt_unp_path.exists():
                    raise OSError("Could not intended crate directory \"%s\"" % ( crt_unp_path ) )
                
                if crt_target.exists() and CRAATE_IMPORT_OVERWRITE:
                    inst_crt_meta = imported_crates_meta[ crt_meta['name' ] ]
                    print( ": Found crate \"%s\" version \"%s\", overwriting with version \"%s\"" % ( inst_crt_meta['name'], inst_crt_meta['version'], crt_meta['version'] ), end=" " )
                    crt_target.rename( crt_rollback_path )
                
                try:
                    crt_unp_path.rename( crt_target )
                    create_checksum( crt_target, ".", crate )
                    if crt_rollback_path.exists( ) and CRAATE_IMPORT_OVERWRITE:
                        shutil.rmtree( str( crt_rollback_path ) )
                                
                except:
                    if crt_rollback_path.exists():
                        shutil.rmtree( str( crt_target ) )
                        crt_rollback_path.rename( crt_target )
            print()
            
    except Exception as e:
        raise 



    