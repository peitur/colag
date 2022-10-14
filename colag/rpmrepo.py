#!/usr/bin/env python3

import os, sys, re
import pathlib, shutil, json

import colag.util
import colag.validate
import colag.command

from pprint import pprint
COMMAND_OPTIONS={
    "source":{"type":"flag", "default": False },
    "newest-only":{"type":"flag", "default": True },
    "urls":{ "type":"flag", "default": False },
    "tempcache":{ "type":"flag", "default": True },
    "download_path":{"mandatory": True, "type":"str" }
}

MAIN_OPTIONS={
    "gpgcheck":{"pattern":"^([01]$)", "default":"1" },
    "installonly_limit":{ "pattern":"^([0-9]$)", "default":"3"},
    "clean_requirements_on_remove":{ "pattern":"^([01]$)", "default":"1"},
    "best":{ "pattern":"^([01]$)", "default": "1" },
    "skip_if_unavailable":{ "pattern":"^[01]$)", "default":"0" },
    "reposdir":{"pattern":"^([01])$", "default": "repo.d", "update": True}
}

REPO_OPTIONS={
    "id":{"mandatory": True, "pattern":"^(.+)$"},
    "name":{"mandatorye": True, "pattern":"^(.+)$"},
    "baseurl":{"mandatory": True, "pattern":"^(.+)$"},
    "mirrorlist":{"pattern":"^(.+)$", "default":None },
    "gpgcheck":{"pattern":"^([01]$)", "default":"1" },
    "gpgcakey":{"pattern":"(.+)", "default": None },
    "gpgkey":{"pattern":"^(/.+)$", "default":None },
    "sslverify":{"pattern":"^([01])$", "default":None },
    "sslcacert":{"pattern":"^(/.+)$", "default":None },
    "sslclientkey":{"pattern":"^(/.+)$", "default":None },
    "sslclientcert":{"pattern":"^(/.+)$", "default":None },
    "sslverifystatus":{"pattern":"^([01])$", "default":None },
    "metadata_expire":{"pattern":"^([0-9]+)$", "default":"86400" },
    "metalink":{"pattern":"^(.+)$", "default": None },
    "repo_gpgcheck":{"pattern":"^(.+)$", "default": None },
    "timeout":{"pattern":"^(.+)$", "default": None },
    "retries":{"pattern":"^(.+)$", "default": None },
    "throttle":{"pattern":"^(.+)$", "default": None },
    "bandwidth":{"pattern":"^(.+)$", "default": None },
    "proxy":{"pattern":"^(.+)$", "default": None },
    "proxy_username":{"pattern":"^(.+)$", "default": None },
    "proxy_password":{"pattern":"^(.+)$", "default": None },
    "username":{"pattern":"^(.+)$", "default": None },
    "password":{"pattern":"^(.+)$", "default": None },
    "cost":{"pattern":"^(.+)$", "default": None },
    "skip_if_unavailable":{"pattern":"^(.+)$", "default": None }
}

REPO_MGM_PATHS={
    "dnf":{ "needs":[] },
    "yum":{ "needs":["reposync"]},
    "reposync": {}
}


class RepoSyncCommand( object ):
    def __init__( self, opt ):
        self.__debug = opt.get("debug", False )
        self.__options = opt.copy()
        self.__input =  opt.copy()
        self.__config_file = None
        self.__base_command = self.__detect_repo_mgm()
        self.__configuration = dict()
        self.__validator = colag.validate.SimpleDictValidator( COMMAND_OPTIONS )
        
        self.__load_defaults()
        self.__apply_input()

    def __load_defaults( self ):
        for op in COMMAND_OPTIONS:
            vals = COMMAND_OPTIONS[ op ]
            if 'default' in vals:
                self.__configuration[ op ] = vals[ "default" ]

    def __apply_input( self ):
        if type( self.__input ).__name__ != "dict":
            raise ValueError("Invalid configurtation format")
        
        for op in self.__input:
            if op in COMMAND_OPTIONS:
                self.__configuration[ op ] = self.__input[ op ]
                       
    def __detect_repo_mgm( self ):
        det = dict()
        
        for tool in REPO_MGM_PATHS:
            if 'PATH' in os.environ:    
                for p in re.split(":", os.environ['PATH'] ):
                    if self.__debug: print("CHECKING: %s in %s" % ( tool, p ))

                    if pathlib.Path( "%s/%s" % ( p, tool ) ).exists():
                        if self.__debug: print("FOUND: %s in %s" % ( tool, p ))
                        det[ tool ] = pathlib.Path( "%s/%s" % ( p, tool ) )
                        continue

        if 'dnf' in det:
            return det['dnf']
        
        if 'yum' in det:
            if 'reposync' in det:
                return det['reposync']
            else:
                raise EnvironmentError("Missing reposync tool")

        return None
        
    def __command( self, filename=None ):
        if not self.__base_command:
            raise OSError( "Missing rpm repo coammand to use")
        if filename:
            self.set_config( filename )
            
        if not self.__config_file:
            raise RuntimeError( "Missing configuration, please set configuration file first" )
        
        cmd = list()
        cmd.append( self.__base_command  )
        cmd.append( "--config=%s" % ( self.__config_file ) )
        
        for c in self.__configuration:
            if  self.__configuration[ c ] and  COMMAND_OPTIONS[ c ]["type"] == "flag":
                cmd.append( "--%s" % ( c ) )
            if  self.__configuration[ c ] and  COMMAND_OPTIONS[ c ]["type"] == "str":
                cmd.append( "--%s=%s" % ( c, self.__configuration[ c ] ) )
                
        return  cmd
    
    
    
    def  set_config( self, filename ):
        print("Updated main config %s" % ( filename ) )
        self.__config_file = pathlib.Path( filename )
        if not self.__config_file.exists():
            raise FileNotFoundError( "No such file %s" % (filename) )

    def set_base_command( self, cmd ):
        self.__base_command = cmd

    def run( self, filename=None ):
        cmd = self.__command( filename  )
        for line in colag.command.GenericCommand( cmd, debug=self.__debug, just_print=True ).run_iterator():
            line = line.lstrip().rstrip()
            
class RepoSyncConfigGen( object ):
    
    def __init__( self, mconf, rclist, **opt ):
        self.__debug = opt.get("debug", False )
        self.__options = opt.copy()
        self.__temp_repo_dir = None
        self.__main_config = mconf
        self.__repo_configs = rclist
        self.__reposdir = mconf.get("reposdir")
        self.__rootdir = opt.get("rootdir", "/tmp" )
        self.__main_filename = opt.get("mainfile", "main.conf")
        self.__init_environment()
        self.__main_file()
        self.__repo_file()

    def __init_environment( self ):
        self.__temp_repo_dir = colag.util.random_tempdir( rootdir=self.__rootdir ,rlen=16, create=True )
        self.__main_config.set( "reposdir", "%s/%s" % ( self.__temp_repo_dir, self.__reposdir ) )
        pathlib.Path( self.__main_config.get("reposdir" ) ).mkdir( parents=True )

    def __main_file( self ):
        filename = pathlib.Path( "%s/%s" % ( self.__temp_repo_dir, self.__main_filename ) )
        if self.__debug:
            print("Creating main config file %s" % ( filename ) )
            
        with open( filename, "w" ) as fd:
            fd.write( self.__main_config.config_format() )
        
    
    def __repo_file( self ):
        for id, item in self.__repo_configs.items():
            filename = pathlib.Path( "%s/%s/%s.repo" % ( self.__temp_repo_dir, self.__reposdir, id ) )
            if self.__debug:
                print("Creating repo config file %s" % ( filename ) )
            
            with open( filename, "w" ) as fd:
                fd.write( item.config_format() )
    
    def mainfile( self ):
        return pathlib.Path( "%s/%s" % ( self.__temp_repo_dir, self.__main_filename ) )
    
    def environment( self ):
        return pathlib.Path( self.__temp_repo_dir )
    
    def cleanup( self ):
        if self.__debug:
            print("Cleaning up temporary directory %s" % ( self.__temp_repo_dir ) )
        if pathlib.Path( self.__temp_repo_dir ).exists():
            shutil.rmtree( self.__temp_repo_dir )
            
            
    def print_all( self ):
        print( self.__main_config.config_format() )
        for _, r in self.__repo_configs.items():
            print( r.config_format() )

class RepoSyncConfigMain( object ):
    
    def __init__( self, conf, **opt ):
        self.__debug = opt.get("debug", False )
        self.__input = conf
        self.__id = conf.get("id", "main" )
        self.__configuration = dict()
        self.__options = opt.copy()
        self.__validator = colag.validate.SimpleDictValidator( MAIN_OPTIONS )
        
        self.__load_defaults()
        self.__apply_input()
        
    ## 1. load defaults
    ## 2. apply settings from input
    def __load_defaults( self ):
        for op in MAIN_OPTIONS:
            vals = MAIN_OPTIONS[ op ]
            if 'default' in vals:
                self.__configuration[ op ] = vals[ "default" ]

    def __apply_input( self ):
        if type( self.__input ).__name__ != "dict":
            raise ValueError("Invalid configurtation format")
        
        for op in self.__input:
            if op in MAIN_OPTIONS:
                self.__configuration[ op ] = self.__input[ op ]

    def id( self, val=None ):
        if val:
            self.__id = val
        return self.__id

    def set( self, key, val ):
        if key in MAIN_OPTIONS:
            if 'update' in MAIN_OPTIONS[ key ] and MAIN_OPTIONS[ key ]['update']:
                self.__configuration[ key ] = val
            else:
                AttributeError( "Key is read only: %s" % ( key ) )
                
    def get( self, key ):
        if key in MAIN_OPTIONS:
            return self.__configuration.get( key, None )
                    
    def configuration( self ):
        return self.__configuration.copy()
    
    def config_format( self ):
        lines = list()
        lines.append( "[%s]" %( self.__id ) )
        for c,v in self.__configuration.items():
            if v:
                lines.append("\t%s=%s" % ( c, v) )

        lines.append("")
        return "\n".join( lines )


class RepoSyncConfigRepo( object ):
    
    def __init__( self, conf, **opt ):
        self.__debug = opt.get("debug", False )
        self.__input = conf
        self.__id = None
        self.__configuration = dict()
        self.__options = opt.copy()
        self.__validator = colag.validate.SimpleDictValidator( REPO_OPTIONS )

        self.__load_defaults()
        self.__apply_input()


    ## 1. load defaults
    ## 2. apply settings from input
    def __load_defaults( self ):
        for op in REPO_OPTIONS:
            vals = REPO_OPTIONS[ op ]
            if 'default' in vals:
                if vals['default']:
                    self.__configuration[ op ] = vals[ "default" ]

    def __apply_input( self ):
        if type( self.__input ).__name__ != "dict":
            raise ValueError("Invalid configurtation format")
        
        for op in self.__input:
            if op in REPO_OPTIONS:
                if op in ('id'):
                    self.__id = self.__input[ op ]
                else:
                    self.__configuration[ op ] = self.__input[ op ]

    def set( self, key, val ):
        if key in REPO_OPTIONS:
            if 'update' in REPO_OPTIONS[ key ] and REPO_OPTIONS[ key ]['update']:
                self.__configuration[ key ] = val
            else:
                AttributeError( "Key is read only: %s" % ( key ) )

    def get( self, key ):
        if key in REPO_OPTIONS:
            return self.__configuration.get( key, None )

    def id( self, val=None ):
        if val:
            self.__id = val
        return self.__id

    def configuration( self ):
        return self.__configuration.copy()

    def config_format( self ):
        lines = list()
        lines.append( "[%s]" %( self.__id ) )
        for c,v in self.__configuration.items():
            if v:
                lines.append("\t%s=%s" % ( c, v) )

        lines.append("")
        return "\n".join( lines )



def config_read( filename, **opt ):
    items = json.load( open( filename ) )
    objects = dict()
    
    if "command" in items:
        objects['command'] = colag.rpmrepo.RepoSyncCommand( items['command'] )
        
    if "main" in items:
        main = items['main']
        mconf = colag.rpmrepo.RepoSyncConfigMain( main )
        objects[ mconf.id() ] = mconf
        
    if "repos" in items:
        repos = items['repos']
        for repo in repos:
            conf = colag.rpmrepo.RepoSyncConfigRepo( repo )
            if 'repos' not in objects:
                objects['repos'] = dict()
                
            if conf.id() in objects['repos']:
                raise AttributeError("Duplicate repo IDs in configuration: %s" % ( conf.id() ))
            objects['repos'][ conf.id() ] = conf

    return objects

if __name__ == "__main__":
    import colag.rpmrepo

    s = config_read("samples.d/rpmsync.json")
    gen = RepoSyncConfigGen( s['main'], s['repos'], rootdir="test1", debug=True )
    print("##### Full configuration  #####")
    gen.print_all()
    print("###############################")
    pprint( s['command'].run() )
    gen.cleanup()
    