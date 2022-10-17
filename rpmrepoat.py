#!/usr/bin/env python3

from argparse import ArgumentError
import os, sys, re
import pathlib

import colag.rpmrepo

from pprint import pprint





if __name__  == "__main__":
    
    if len( sys.argv ) < 2:
        raise RuntimeError( "Missing arguments: <config>" )
    
    filename = pathlib.Path( sys.argv[1] )        
    s = colag.rpmrepo.config_read( filename  )        
    gen = colag.rpmrepo.RepoSyncConfigGen( s['main'], s['repos'], debug=True )
    
    print("##### Full configuration  #####")
    gen.print_all()
    print("###############################")
    s['command'].set_config( gen.mainfile() )
    s['command'].set_base_command( "/usr/bin/dnf" )
    pprint( s['command'].run() )

    gen.cleanup()
