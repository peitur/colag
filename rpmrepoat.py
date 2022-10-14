#!/usr/bin/env python3

from argparse import ArgumentError
import os, sys, re
import pathlib

import colag.rpmrepo







if __name__  == "__main__":
    
    if len( sys.argv ) <= 1:
        raise ArgumentError()
    
    s = colag.rpmrepo.config_read( filename  )
    gen = RepoSyncConfigGen( s['main'], s['repos'], rootdir="test1", debug=True )
    print("##### Full configuration  #####")
    gen.print_all()
    print("###############################")

    gen.cleanup()
