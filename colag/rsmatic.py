#!/usr/bin/env python


from functools import cache
import sys,os,re
import json

from pprint import pprint

import colag.util

class RsmaticConfig( object ):
    
    def __init__( self, opt ):
        self.__debug = opt.get( "debug", False )
        self.__data = opt
        self.__full_config = None
        self.__logfile = opt.get("logfile", None )
        
        self.__static_options = [
            "--no-motd",
            "--recursive",
            "--safe-links",
            "--ignore-missing-args",
            "--out-format=\"%'i %'b %t %n\""
        ]
        
        if self.__logfile:
            self.__static_options.append( "--log-file=%s"  % ( self.__logfile ) )
            self.__static_options.append( "--log-file-format=\"%t %o %i %b [%l] %M %n\"" )
        
        self.__valid_config = {
            "debug":{ "type":"bool", "mandatory": False },
            "source":{ "type":"str", "pattern":r".+", "mandatory":True },
            "target":{ "type":"str", "pattern":r".+", "mandatory":True },
            "logfile":{"mandatory": False, "pattern": r".+" , "type": "str"  },
            "options":{"type":"dict", "mandatory": False, "pattern": None,  }
        }
        
        self.__valid_options = {
            "port":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int" },
            "ipv4":{"mandatory": False, "pattern": None , "type":"flag" },
            "ipv6":{"mandatory": False, "pattern": None , "type":"flag" },
            "list-only":{"mandatory": False, "pattern": None , "type":"flag"},            
            "checksum":{"mandatory": False, "pattern": None , "type":"flag" },
            "recursive":{"mandatory": False, "pattern": None , "type":"flag" },
            "archive":{"mandatory": False, "pattern": None , "type":"flag" },
            "links":{"mandatory": False, "pattern": None , "type":"flag" },
            "acls":{"mandatory": False, "pattern": None , "type":"flag" },
            "xattrs":{"mandatory": False, "pattern": None , "type":"flag" },
            "owner":{"mandatory": False, "pattern": None , "type":"flag" },
            "group":{"mandatory": False, "pattern": None , "type":"flag" },
            "times":{"mandatory": False, "pattern": None , "type":"flag" },
            "dry-run":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete-after":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete-before":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete-during":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete-delay":{"mandatory": False, "pattern": None , "type":"flag"  },
            "delete-excluded":{"mandatory": False, "pattern": None , "type":"flag"  },
            "force":{"mandatory": False, "pattern": None , "type":"flag"  },
            "ignore-times":{"mandatory": False, "pattern": None , "type":"flag"  },
            "size-only":{"mandatory": False, "pattern": None , "type":"flag"  },
            "compress":{"mandatory": False, "pattern": None , "type":"flag"  },
            "compress-level":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "skip-compress":{"mandatory": False, "pattern": None , "type":"flag"  },
            "exclude":{"mandatory": False, "pattern": ".+" , "type":"list"  },
            "exclude-from":{"mandatory": False, "pattern": ".+" , "type":"str"  },
            "include":{"mandatory": False, "pattern": ".+" , "type":"list"  },
            "include-from":{"mandatory": False, "pattern": ".+" , "type":"str"  },
            "bwlimit":  {"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "bandwidth":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int", "rename":"bwlimit"  },
            "protect-args":{"mandatory": False, "pattern": None , "type":"flag"  },
            "contimeout":{"mandatory": False, "pattern": "^[0-9]+$" , "type":"int"  },
            "numeric-ids":{"mandatory": False, "pattern": None , "type":"flag"  },
            "min-size":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "max-size":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "delay-updates":{"mandatory": False, "pattern": None , "type":"flag" },
            "ignore-errors":{"mandatory": False, "pattern": None , "type":"flag" },
            "ignore-missing-args":{"mandatory": False, "pattern": None , "type":"flag" }
        }
            
        self.__validate_config()
    
    def __check_conf_value( self, k, v ):

        ## if type is 'flag', ignore pattern
        if self.__valid_options[k]['type'] in ("flag"):
            return True 
        
        ## if type is correct, ignore pattern
        try:
            if self.__valid_options[k]['type'] in ( "int" ):
                v = int( v )

            if self.__valid_options[k]['type'] in ( "float" ):
                v = float( v )

            if self.__valid_options[k]['type'] in ( "list" ):
                if type( v ).__name__ not in ("list"):
                    v = [ v ]
            
            if self.__valid_options[k]['type'] in ("bool"):
                v = colag.util.boolify( v )

            if self.__valid_options[k]['type'] in ("str"):
                if not re.match( self.__valid_options[k]['pattern'], v ):
                    return False
                    
        except Exception as e:        
            return False
        return True
    
    def __validate_config( self ):
        cache  = self.__data
        ## temporary until validator works as intended (famous last words)
        for c in cache:
            if c not in self.__valid_config:
                raise AttributeError("Unsupported configuration option: %s" % ( c ) )
                            
        if 'options' in cache and type( cache['options'] ).__name__ in ( "dict" ):
            for o in cache['options']:
                if o not in self.__valid_options:
                    raise AttributeError("Unsupported rsync option: %s" % ( o ) )

                if not self.__check_conf_value( o, cache['options'][o] ):
                    raise AttributeError("Invalid option type or format for %s found '%s'" % ( c, cache['options'][o] ) )

        self.__full_config = cache.copy()
    
    def debug( self, d=True ):
        self.__debug = colag.util.boolify( d )
    
    def option_is_flag( self, k ):
        if self.__valid_options[k]['type'] == "flag":
            return True
        return False

    def option_is_list( self, k ):
        if self.__valid_options[k]['type'] == "list":
            return True
        return False

    def option_rename( self, o ):
        if 'rename' in self.__valid_options[ o ]:
            o = self.__valid_options[ o ]['rename']
        return o        

    def filename( self ):
        return self.__filename
    
    def config( self ):
        return self.__full_config.copy()

    def static_config( self ):
        return self.__static_options.copy()
    
    def get( self, k, defval=None ):
        return self.__full_config.get( k, defval )

        

class RsyncCommand( object ):
    
    def __init__( self, options ):
        
        if not type( options ).__name__ in ("dict", "RsmaticConfig" ):
            raise AttributeError( "Bad config value type for command builder : %s" % ( type( options ).__name__ ) )
        
        self.__debug = options.get("debug", False )
        self.__logfile = options.get("logfile", None )
        self.__config = options        
        self.__command = list()
                
        self.__command.append("rsync")
        for o in self.__config.static_config():
            self.__command.append( o )

    def __mk_generic_option( self, o, v ):
        o = self.__config.option_rename( o )
        if self.__config.option_is_flag( o ):
            return "--%s" % ( o )
        elif self.__config.option_is_list( o ):
            if type( v ).__name__ not in ("list"):
                v = [ v ]
            return " ".join( ["--%s=%s" % ( o, i ) for i in v ] )
        return "--%s=%s" % ( o, v ) 

        
    def __mk_command( self ):
        item =  self.__config.config()

        options = item['options']
        for c in options:
            val = options[c]
            self.__command.append( self.__mk_generic_option( c, val ) )


        self.__command.append( item['source'] )
        self.__command.append( item['target'] )

        return self.__command
        
    
    def set_config( self, conf ):
        if type( conf ).__name__ not in ("RsmaticConfig"):
            raise AttributeError("Bad configuration object for rsmatic")
        self.__config = conf

    def run( self ):
        return self.__mk_command().copy()

if __name__ == "__main__":
    filename = "samples.d/rsmatic.test.json"
    for conf in json.load( open( filename, "r" ) ):
        c = RsmaticConfig( conf )
        
        c.debug()
        
        r = RsyncCommand( c )
        r.run()