#!/usr/bin/env python3

import sys
import json
import pathlib

CONFIG={
    
}

if __name__ == "__main__":
    infiles = list()
    if len( sys.argv ) > 1:
        infiles = sys.argv[ 1: ]

    
    print( json.dumps( CONFIG ) )