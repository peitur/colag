#!/usr/bin/env python

import sys, os, re
from unittest.result import failfast


class SimpleDictValidator( object ):
    
    def __init__( self, vmap, **opt ):
        self._debug = opt.get("debug", False )
        self._strict = opt.get( "strict", False )
        self._last_failed = list()
        
        # { 
        #   ""key" : { "pattern":"", "mandatory":False, "type":"" }
        # }
        self._map = None

        if type( vmap ).__name__ not in ("dict"):
            raise AttributeError("Validator map invalid, must be dictionary")

        self.map = vmap.copy()


    def _validate_type( self, want, data ):
        if type( want ).__name__ in ( "str" ):
            want = ( want )

        if type( want ).__name__ not in ( "tupel" ):
            raise AttributeError( "Invalid want format when checking variable type")
        
        if type( data ).__name__ in want:
            return True

        return False
    
    def _validate_str( self, rx, data ):
        if re.match( rx, data ):
            return True
        return False        

    def _validate_bool( self, data ):
        if data in (True, False ):
            return True
        return False

    def _validate_boolish( self, data ):
        if data in (True, False, "true","false","yes","no", "Yes","No" ):
            return True
        return False

    def _type_name( self, data ):
        return type( data ).__name__

    def validate( self, data ):
        failed = []
               
        if type( data ).__name__ not in ("dict"):
            raise AttributeError("Data invalid, must be dictionary")
        
        ## check for mandatory keys, if missing add to failed check
        for m in self._map:
            if 'mandatory' in self._map[ m ]:
                if self._map[ m ]['mandatory'] not in (True, False ):
                    raise AttributeError( "Invalid mandatory value in map, must be bool")
                
                if self._map[ m ]['mandatory'] and m not in data:
                    failed.append( m )
                    
        for k in data:

            if type( k ).__name__ not in ("str"):
                raise AttributeError("Bad key value in data, must be string")

            if k not in self._map[ k ]:
                raise AttributeError("Unknown configuration parameter %s" % ( k ) )
            
            if 'pattern' not in self._map:
                raise AttributeError("Missing mandatory pattern i map")
            
            
            r = re.match( self._map[ k ]['pattern'], data[ k ] )
            if not r:
                failed.append( k )
                    
        self._last_failed = failed

        if len( failed ) > 0:
            return False
        return True

    def last_failed( self ):
        return self._last_failed.copy()

if __name__ == "__main__":
    m1 = {
        "k1":"abc"
    }
    
    d1 = {}