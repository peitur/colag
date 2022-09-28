#!/usr/bin/env python3

import os, sys, re
import pathlib, shutil

import colag.util

from pprint import pprint

MAIN_OPTIONS={
    "gpgcheck":{"pattern":"^([01]$)", "default":"1" },
    "installonly_limit":{ "pattern":"^([0-9]$)", "default":"3"},
    "clean_requirements_on_remove":{ "pattern":"^([01]$)", "default":"1"},
    "best":{ "pattern":"^([01]$)", "default": "1" },
    "skip_if_unavailable":{ "pattern":"^[01]$)", "default":"0" },
    "reposdir":{"pattern":"^([01])$", "default": None}
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

    def __main_file( self ):
        pass
    
    def __repo_file( self ):
        pass

    def cleanup( self ):
        if pathlib.Path( self.__temp_repo_dir ).exists():
            

if __name__ == "__main__":

    s = RepoSyncRPM()