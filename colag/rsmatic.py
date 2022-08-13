#!/usr/bin/env python


import sys,os,re
import json

from pprint import pprint

class RsmaticConfig( object ):
    
    def __init__( self, filename, **opt ):
        self.__debug = opt.get( "debug", False )
        self.__filename = filename
        self.__data = None
        self.__logfile = opt.get("logfile", None )
        
        self.__static_options = [
            "--no-motd",
            "--recursive",
            "--safe-links",
            "--out-format=\"%'i %'b %t %n\""
        ]
        
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
            "list-only":{"mandatory": False, "pattern": None , "type":"flag" },            
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
            "bandwidth":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "protect-args":{"mandatory": False, "pattern": None , "type":"flag"  },
            "contimeout":{"mandatory": False, "pattern": "^[0-9]+$" , "type":"int"  },
            "numeric-ids":{"mandatory": False, "pattern": None , "type":"flag"  },
            "min-size":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "max-size":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "delay-updates":{"mandatory": False, "pattern": None , "type":"flag"  }
        }
    
        self.__loginfo = {
            "logfile":{ "mandatory": False, "pattern": r"^[a-zA-Z0-9]+$", "type":"str", "option":"--log-file" },
            "logformat":{ "mandatory": False, "pattern": None , "type":"flag", "option":"--log-file-format=\"%t %o %i %b [%l] %M %n\"" }
        }
        
        self.__load_file()
        
    def __load_file( self ):
        cdata = json.load( open(self.__filename, "r" ) )
        for cache in cdata:

            ## temporary until validator works as intended (famous last words)
            for c in cache:
                if c not in self.__valid_config:
                    raise AttributeError("Unsupported configuration option: %s" % ( c ) )
                
            if 'options' in cache and type( cache['options'] ).__name__ in ( "dict" ):
                for o in cache['options']:
                    if o not in self.__valid_options:
                        raise AttributeError("Unsupported rsync option: %s" % ( o ) )

        self.__full_config = cdata.copy()
    
    def filename( self ):
        return self.__filename
    
    def config( self ):
        return self.__full_config.copy()
    


class RsyncCommand( object ):
    
    def __init__( self, **options ):
        self.__debug = options.get("debug", False )
        self.__config = None        
    
    def load_config( self, filename ):
        self.__config = RsmaticConfig( filename )
        
    def set_config( self, conf ):
        if type( conf ).__name__ not in ("RsmaticConfig"):
            raise AttributeError("Bad configuration object for rsmatic")
        self.__config = conf

    def run( self ):
        pass

if __name__ == "__main__":
    filename = "samples.d/rsmatic.test.json"
    c = RsmaticConfig( filename )

    r = RsyncCommand( )
    r.load_config( filename )
    r.run()