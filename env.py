#!/usr/bin/env python3

import sys
import json
import pathlib
import time

CONFIG={
    
}

if __name__ == "__main__":
    conf = CONFIG.copy()
    infiles = list()
    if len( sys.argv ) > 1:
        infiles = sys.argv[ 1: ]

    for f in infiles:
        if pathlib.Path( f ).suffix == ".json":
            print( f )
    
    print( json.dumps( conf ) )
    
        