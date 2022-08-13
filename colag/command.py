#!/usr/bin/env python3

import pathlib
import sys,re,os,re, datetime
import subprocess, shlex

# import requests
import json
import hashlib

from datetime import datetime
from pprint import pprint


import colag.util

class GenericCommand( object ):
    
    def __init__( self, cmd, **opt ):
        self.__debug = colag.util.boolify( opt.get("debug", False ) )
        self.__data = list()        
        self.__cmd  = cmd
        self.__opt = opt
        
        if type( cmd ).__name__ in ( "str" ):
            self.__cmd  = shlex.split( cmd )


    def run_iterator( self ):
        res = list()
        
        if self.__debug: print( "CMD Running:> '%s'" % ( " ".join( self.__cmd ) ) )

        prc = subprocess.Popen( self.__cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd=self.__opt.get( "cwd", None ), universal_newlines=True, shell=False )
        for line in prc.stdout.readlines():
            yield line.rstrip()
            
            if prc.poll():
                break
            
        return ( prc.returncode, res )
        

    def run_command_list( self ):

        res = list()
        
        if self.__debug: print( "CMD Running:> '%s'" % ( " ".join( self.__cmd ) ) )

        prc = subprocess.Popen( self.__cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd=self.__opt.get( "cwd", None ), universal_newlines=True, shell=False )
        for line in prc.stdout.readlines():
            res.append( line.rstrip() )
            
            if prc.poll():
                break
            
        return ( prc.returncode, res )



if __name__ == "__main__":
    c = GenericCommand( "ls -al" )
    [ print( s ) for s in c.run_iterator() ]