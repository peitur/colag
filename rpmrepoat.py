#!/usr/bin/env python3

from argparse import ArgumentError
import os, sys, re
import pathlib

import colag.rpmrepo

from pprint import pprint





if __name__  == "__main__":
    
    if len( sys.argv ) < 3:
        raise RuntimeError( "Missing arguments: <config> <destination>" )
    
    filename = pathlib.Path( sys.argv[1] )
    destination = pathlib.Path( sys.argv[2] )
    
    if not destination.exists():
        raise OSError("Missing destination directory %s" % ( destination ) )
    
    s = colag.rpmrepo.config_read( filename  )
    gen = colag.rpmrepo.RepoSyncConfigGen( s['main'], s['repos'], rootdir=destination, debug=True )
    print("##### Full configuration  #####")
    gen.print_all()
    print("###############################")
    s['command'].set_config( gen.mainfile() )
    s['command'].set_base_command( "/usr/bin/dnf" )
    pprint( s['command'].run() )

    gen.cleanup()