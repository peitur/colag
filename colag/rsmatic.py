#!/usr/bin/env python


import sys,os,re
import json
import colag
import colag.validate.SimpleDictValidator as Validator

class RsmaticConfig( object ):
    
    def __init__( self, filename, **opt ):
        self._debug = opt.get( "debug", False )
        self._filename = filename
        self._data = None
        
        self._valid_config = {
            "debug":{""},
            "source":{},
            "target":{}
        }
        self._valid_coptions = {}
        
    def _load_file( self ):
        cache = json.load( open(self._filename ), "r" )




if __name__ == "__main__":
    pass