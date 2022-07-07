#!/usr/bin/env python


import sys,os,re
import json
# import colag
# import colag.validate.SimpleDictValidator as Validator

from pprint import pprint

class RsmaticConfig( object ):
    
    def __init__( self, filename, **opt ):
        self._debug = opt.get( "debug", False )
        self._filename = filename
        self._data = None
        
        self._static_options = [
            "--no-motd",
            "--recursive"
        ]
        
        
        self._valid_config = {
            "debug":{"type":"bool", "mandatory": False },
            "source":{ "type":"str", "pattern":r".+", "mandatory":True },
            "target":{ "type":"str", "pattern":r".+", "mandatory":True },
            "options":{"type":"dict", "mandatory": False, "pattern": None,  }
        }
        
        self._valid_options = {
            "port":{"mandatory": False, "pattern": r"^[0-9]+$" , "type":"int"  },
            "ipv4":{"mandatory": False, "pattern": None , "type":"flag"  },
            "ipv6":{"mandatory": False, "pattern": None , "type":"flag"  },
            "list-only":{"mandatory": False, "pattern": None , "type":"flag"  },            
            "checksum":{"mandatory": False, "pattern": None , "type":"flag"  },
            "recursive":{"mandatory": False, "pattern": None , "type":"flag"  },
            "archive":{"mandatory": False, "pattern": None , "type":"flag"  },
            "links":{"mandatory": False, "pattern": None , "type":"flag"  },
            "acls":{"mandatory": False, "pattern": None , "type":"flag"  },
            "xattrs":{"mandatory": False, "pattern": None , "type":"flag"  },
            "owner":{"mandatory": False, "pattern": None , "type":"flag"  },
            "group":{"mandatory": False, "pattern": None , "type":"flag"  },
            "times":{"mandatory": False, "pattern": None , "type":"flag"  },
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
    
        self._load_file()
        
    def _load_file( self ):
        cdata = json.load( open(self._filename, "r" ) )
        for cache in cdata:
            pprint( cache )
            ## temporary until validator works as intended (famous last words)
            for c in cache:
                if c not in self._valid_config:
                    raise AttributeError("Unsupported configuration option: %s" % ( c ) )
                
            if 'options' in cache and type( cache['options'] ).__name__ in ( "dict" ):
                for o in cache['options']:
                    if o not in self._valid_options:
                        raise AttributeError("Unsupported rsync option: %s" % ( o ) )

        self._full_config = cdata.copy()
    
    def config( self ):
        return self._full_config.copy()
    


if __name__ == "__main__":

    c = RsmaticConfig( "samples.d/rsmatic.test.json")
    pprint( c.config() )