#!/usr/bin/env python3

import subprocess, shlex

import colag.util

class GenericCommand( object ):
    
    def __init__( self, cmd, **opt ):
        self.__debug = colag.util.boolify( opt.get("debug", False ) )
        self.__just_print = colag.util.boolify( opt.get("just_print", False ) )
        self.__data = list()        
        self.__cmd  = cmd
        self.__opt = opt
        
        if type( cmd ).__name__ in ( "str" ):
            self.__cmd  = shlex.split( cmd )
        else:
            self.__cmd  = [ str( s ) for s in  cmd ]

    def run_iterator( self ):

        if self.__debug: print( "CMD Running:> '%s'" % ( " ".join( self.__cmd ) ) )
        if self.__just_print:
             return ( 0, list() )
         
        prc = subprocess.Popen( self.__cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd=self.__opt.get( "cwd", None ), universal_newlines=True, shell=False )
        for line in prc.stdout.readlines():
            yield line.rstrip()
            
            if prc.poll():
                break
            
        return ( prc.returncode, list() )
        

    def run_list( self ):

        res = list()
        
        if self.__debug: print( "CMD Running:> '%s'" % ( " ".join( self.__cmd ) ) )
        if self.__just_print:
             return ( 0, list() )

        prc = subprocess.Popen( self.__cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, cwd=self.__opt.get( "cwd", None ), universal_newlines=True, shell=False )
        for line in prc.stdout.readlines():
            res.append( line.rstrip() )
            
            if prc.poll():
                break
            
        return ( prc.returncode, res )



if __name__ == "__main__":
    c = GenericCommand( "ls -al" )
    [ print( s ) for s in c.run_iterator() ]
    [ print( s ) for s in c.run_list() ]