#!/usr/bin/env python3

import pathlib
import sys,re,os,re

# import requests
import json
import hashlib

from pprint import pprint

BOOLIFY_TRUE=( True, "True", "Yes", "yes" )
BOOLIFY_FALSE=(False, "False", "No", "no")

def boolify( s ):
    if s in BOOLIFY_TRUE:
        return True
    elif s in BOOLIFY_FALSE:
        return False
    else:
        raise AttributeError("Bad boolish value" )
    
    
if __name__ == "__main__":
    pprint( BOOLIFY_TRUE + BOOLIFY_FALSE )