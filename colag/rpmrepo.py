#!/usr/bin/env python3

import os, sys, re
import pathlib, shutil, json

import colag.util
import colag.validate

from pprint import pprint

MAIN_OPTIONS={
    "gpgcheck":{"pattern":"^([01]$)", "default":"1" },
    "installonly_limit":{ "pattern":"^([0-9]$)", "default":"3"},
    "clean_requirements_on_remove":{ "pattern":"^([01]$)", "default":"1"},
    "best":{ "pattern":"^([01]$)", "default": "1" },
    "skip_if_unavailable":{ "pattern":"^[01]$)", "default":"0" },
    "reposdir":{"pattern":"^([01])$", "default": "repo.d"}
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


class RepoSyncRPM( object ):
    def __init__( self, **opt ):
        self.__debug = opt.get("debug", False )
        self.__options = opt.copy()
        self.__base_command = self.__detect_repo_mgm()
        self.__config = RepoSyncConfigGen( **opt )
        self.__base_command = "/usr/sbin/dnf"
    

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

class RepoSyncConfigGen( object ):
    
    def __init__( self, **opt ):
        self.__debug = opt.get("debug", False )
        self.__options = opt.copy()
        self.__temp_repo_dir = colag.util.random_tempdir()
        self.__main_config_file = "main.conf"
        self.__repo_config_file = "%s.repo" % ( colag.util.random_string() )
        self.__repo_config_data = dict()
        self.__main_config_data = dict()


    def __main_file( self ):
        pass
    
    
    def __repo_file( self ):
        pass
    
    def cleanup( self ):
        if pathlib.Path( self.__temp_repo_dir ).exists():
            shutil.rmtree( self.__temp_repo_dir )


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

    def configuration( self ):
        return self.__configuration.copy()
    
    def config_format( self ):
        lines = list()
        lines.append( "[%s]" %( self.__id ) )
        for c,v in self.__configuration.items():
            if v:
                lines.append("\t%s=%s" % ( c, v) )

        return lines

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

        return lines


def config_read( filename, **opt ):
    items = json.load( open( filename ) )
    if "main" in items:
        main = items['main']
        mconf = colag.rpmrepo.RepoSyncConfigMain( main )
        print( "\n".join( mconf.config_format() ) )
        
    if "repos" in items:
        repos = items['repos']
        for repo in repos:
            conf = colag.rpmrepo.RepoSyncConfigRepo( repo )
            print(  "\n".join( conf.config_format() ) )
        
        

if __name__ == "__main__":
    import colag.rpmrepo

    s = config_read("samples.d/rpmsync.json")