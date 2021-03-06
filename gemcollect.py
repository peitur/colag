#!/usr/bin/env python3

import sys,re,os,re, datetime
import requests
import json
import hashlib, random, string
import getopt
import tarfile, zipfile

from pprint import pprint
from pathlib import Path

module_seen = list()

def get_gem_url( module = "" ): return "https://rubygems.org/api/v1/gems/%s.json" % ( module )
def get_gem_latest( module = "" ):return "https://rubygems.org/api/v1/versions/%s/latest.json" % ( module )
def get_gem_versions( module = "" ): return "https://rubygems.org/api/v1/versions/%s.json" % ( module )
def get_gem_download_url( module, version ): return "https://rubygems.org/gems/%s-%s.gem" % ( module, version )
def get_gem_dependencies( module ): return "https://rubygems.org/api/v1/dependencies.json?gems=%s" % (module )

def random_string( length ):
    return ''.join(random.SystemRandom().choice( string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range( length ))

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


def rmdir_tree( path ):
    pth = Path( path )
    for sub in pth.iterdir() :
        if sub.is_dir() :
            rmdir_tree(sub)
        else:
            sub.unlink()
    pth.rmdir()


def mk_temp_dir( root="/tmp" ):
    return "%s/py_%s" % ( root, random_string( 6 ) )

def all_versions( module, **opt ):
    module = module.lstrip().rstrip()

    q = get_request( module, get_gem_versions( module ) )

    return [ { "name": module, "version": x['number'], "sha": x['sha'], "gversion": x['rubygems_version'], "rversion": x['ruby_version'] } for x in q ]


def collect_pkg_versions( module, req, version = None, **opt ):
    module = module.lstrip().rstrip()

    if not version:
        version = get_latest( module )

    versions = all_versions( module )

    return requirement_filter_version( versions, req, version, **opt )


def requirement_filter( vlist, req, version, field="version", **opt ):
    if req in (">="):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] >= version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in ("=","=="):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] == version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in ("~>"):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] >= version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in ("<="):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] <= version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in ("<"):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] < version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in (">"):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] > version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    elif req in ("!="):
        return [ x for x in vlist if x[ field ] and re.split( "\s+", x[ field ] )[-1] != version and not re.search(r"[a-zA-Z]+", re.split( "\s+", x[ field ] )[-1] ) ]
    else:
        raise AttributeError( "Unsupported requirement option %s" % (req) )

def get_version_dependencies( module, version = None, **opt ):
    module = module.lstrip().rstrip()
    if not version:
        version = get_latest( module )

    q = get_request( module, get_gem_dependencies( module ) )
    return [ { "name": module, "version": x['number'], "dependencies": x['dependencies'] } for x in q if x['number'] == version ]



def get_latest( module ):
    module = module.lstrip().rstrip()
    l = get_request( module, get_gem_latest( module ) )
    return l['version']

def requirement_filter_version( vlist, req, version, **opt ):
    return requirement_filter( vlist, req, version, "version", **opt )

def requirement_filter_rversion( vlist, req, version, **opt ):
    return requirement_filter( vlist, req, version, "rversion", **opt )

def requirement_filter_gversion( vlist, req, version, **opt ):
    return requirement_filter( vlist, req, version, "gversion", **opt )


def rversion_latest( module, req, rversion, **opt ):
    module = module.lstrip().rstrip()
    versions = all_versions( module )
    if rversion:
        return requirement_filter_rversion( versions, req, rversion, **opt ).pop(0)
    return versions.pop(0)

def gversion_latest( module, req, gversion, **opt ):
    module = module.lstrip().rstrip()
    versions = all_versions( module )
    if gversion:
        return requirement_filter_gversion( versions, req, gversion, **opt ).pop(0)
    return versions.pop(0)




def collect_latest_for( module, **opt ):
    gversion = None
    rversion = None
    module = module.lstrip().rstrip()
    deps = list()

    if 'rubyversion' in opt:
        rversion = opt['rubyversion']
    if 'gemsversion' in opt:
        gversion = opt['gemsversion']

    print( "module:%s gversion:%s rversion:%s" % (module, gversion, rversion ) )

    versions = all_versions( module )

    # Filter out all versions that match version requirements for any package. They still need to follow the basic deps
    if gversion: versions = list( requirement_filter_gversion( versions, "<=", gversion, **opt ) )
    if rversion: versions = list( requirement_filter_rversion( versions, "<=", rversion, **opt ) )

    ## if req is in opt, for each req, apply filter and then select the one with highest version (0)
    # for ...
    if 'dependencies' in opt and len( opt['dependencies'] ) > 0:
        print("###########################")
        deps = opt['dependencies']
        del  opt['dependencies']
        print("###########################")


    ## If atleast one Version is found ...

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    pprint( versions[0] )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


    if len( versions ) > 0:
        vinfo = versions[0]
        version = vinfo['version']
        if get_gem_download_url( vinfo['name'], vinfo['version'] ) in module_seen:
            return None
        else:
            module_seen.append( get_gem_download_url( vinfo['name'], version ) )

        ## Get the highest versions dependencies
        gdm = get_version_dependencies( vinfo['name'], vinfo['version'])
        if len( gdm ) > 0:
            vinfo['dependencies'] = gdm[0]['dependencies']
            opt['dependencies'] = vinfo['dependencies']
        print("=================================")
        pprint( vinfo )

        dwurl = get_gem_download_url( vinfo['name'], vinfo['version'] )
        pprint( dwurl )
        # for each dependency, try to download and create checksum file, recursivly

        #

#    if len( versions ) > 0:
#        return collect_pkg_full( module, "==",  versions[0]['version'], **opt )
        print("=================================")
        collect_latest_for( vinfo['name'], **opt )

    return True





def collect_pkg_full( module, req, version, **opt ):
    module = module.lstrip().rstrip()
#    print(">>>> %s %s %s" % ( module, req, version ) )
    if get_gem_download_url( module, version ) in module_seen:
        return None
    else:
        module_seen.append( get_gem_download_url( module, version ) )


    q = get_request( module, get_gem_url( module ) )
    if not q:
        return None

    deps = q['dependencies']
    url = q['gem_uri']
    sha = q['sha']

    dev_dep = deps['development']
    run_dep = deps['runtime']

    if not version:
        version = q['version']

    print( "# [ %s ] [ checking ] Version: %s  => %s" % ( module, version, url ) )
    filename = re.split( r"\/", url)[-1]
    fullfilename = "%s/%s" %( opt['target'] , filename )

    vlist = collect_pkg_versions( module, req, version )
    glist = [ get_gem_download_url( x['name'], x['version'] ) for x in vlist ]

    if not Path( fullfilename ).exists():
        if not download_file( module, url, fullfilename ):
            return None

        hd = get_checksum_info( opt['target'], filename, url, q, opt['checksum'] )

        if not write_checksum_info( module, opt['target'], filename, hd, opt['checksum'] ):
            print("ERROR: Could not write checksum file %s" % ( chkfile ))

        reqlist = list( dev_dep + run_dep )

        if len( reqlist ) > 0:
            for req in reqlist:
                if len( req ) == 0: continue
                if req == module: continue
                r = re.split( r"\s", req['requirements'] )
                collect_pkg_full( req['name'], r[0], r[1] , **opt )

    return True

def write_checksum_info( module, target, filename, hd, checksum ):
    fullfilename = "%s/%s" %( target, filename )
    chkfile = "%s.%s.json" % ( fullfilename, checksum )

    if not Path( chkfile ).exists():
        print( "# [ %s ] [ checksum ] %s -> %s  " % ( module, fullfilename, chkfile ) )
        write_file( chkfile, [ hd ] )
        return True
    return False

def get_checksum_info( target, filename, url, requet, checksum ):
    fullfilename = "%s/%s" %( target , filename )
    chkfile = "%s.%s.json" % ( fullfilename, checksum )

    hd = dict()
    fst = Path( fullfilename ).stat()
    hd['01.filename'] = filename
    hd['02.source'] = url
    hd['03.size'] = int( fst.st_size )
    hd['04.ctime'] = datetime.datetime.fromtimestamp( fst.st_ctime ).isoformat()
    hd['05.mtime'] = datetime.datetime.fromtimestamp( fst.st_mtime ).isoformat()
    hd['06.atime'] = datetime.datetime.fromtimestamp( fst.st_atime ).isoformat()
    hd['07.checksum'] = "%s:%s" % ( checksum, file_hash( fullfilename, checksum ) )
    hd['10.release'] = requet
    return hd

def print_help( scripts ):
    print("> -c|--config <config>")
    print("> -f|--file <gemfile>")
    print("> -g|--gversion <version>")
    print("> -r|--rversion <version>")
    print("> -h|--help")



if __name__ == "__main__":
    opt = dict()

    opt['script'] = sys.argv.pop(0)
    opt['filename'] = "Gemsfile.txt"
    opt['target'] = "gems"
    opt['config'] = None
    opt['gemsversion'] = None
    opt['rubyversion'] = None
    opt['checksum'] = "sha256"

    try:
        opts, args = getopt.getopt(sys.argv, "hc:f:r:g:s:", ["help", "checksum=", "config=", "file=", "rversion=","gversion=" ])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ( "-h", "--help" ):
            print_help( opt['script'] )
            sys.exit(0)
        elif o in ("-c", "--config"):
            opt['config'] = a
        elif o in ("-s", "--checksum"):
            opt['checksum'] = a
        elif o in ("-f", "--file"):
            opt['filename'] = a
        elif o in ("-r", "--rversion"):
            opt['rubyversion'] = a
        elif o in ("-g", "--gversion"):
            opt['gemsversion'] = a


    if Path( "gemcollect.json" ).exists():
        cfg = load_file( "gemcollect.json" )[0]
        opt['target'] = cfg['target']
        if not opt['rubyversion'] and 'rubyversion' in cfg:
            opt['rubyversion'] = cfg['rubyversion']
        if not opt['gemsversion'] and 'gemsversion' in cfg:
            opt['gemsversion'] = cfg['gemsversion']
        if 'checksum' in cfg:
            opt['checksum'] = cfg['checksum']



    target = Path( opt['target'] )
    if not target.exists():
        target.mkdir()


    modules = load_file( opt['filename'] )

    for line in modules:
        if re.match(r"\s*#.*", line): continue
        res = re.split( r"\s", line )
        module = res[0]
        req = "="
        version = None

        if len( res ) > 1:
            if res[1]: req = res[1]
            if res[2]: version = res[2]

        opt['mversion'] = version
        if opt['gemsversion'] or opt['rubyversion']:
            pprint( collect_latest_for( module, **opt ) )
        else:
            collect_pkg_full( module, req, version, **opt )
