#!/usr/bin/env python3

import os, sys, re
import pkg_resources

from pprint import pprint

class Version( object ):
    def __init__( self, v ):
        self._split_rx = re.compile( "\." )
        self._raw_version = v

        if type( v ).__name__ == "str":
            self._version = pkg_resources.parse_version( str(v) )
        elif type( v ).__name__ == "Version":
            self._version = pkg_resources.parse_version( str(v) )
        elif type( v ).__name__ == "list":
            self._version = pkg_resources.parse_version( ".".join( [ str(x) for x in v ] ) )
        else:
            raise AttributeError("%s not supported format" % ( type(v).__name__ ) )


    def get( self ):
        return self._version


    def __str__( self ):
        return self._raw_version

    def __eq__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va == vb:
            return True
        return False


    def __ne__( self, v ):
        return not self.__eq__( v )

    def __lt__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va < vb:
            return True
        return False
    def __le__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va <= vb:
            return True
        return False

    def __gt__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va > vb:
            return True
        return False


    def __ge__( self, v ):
        va = self._version
        vb = Version( v ).get()

        if va >= vb:
            return True
        return False

def parse_product( s ):
    rx = re.compile( r"^([a-zA-Z0-9\-_\.]+)(.*)$" )
    m = rx.findall( s )
    res = list()
    if m:
        if len( m[0] ) > 1:
            parts = re.split( r",", m[0][1] )
            for p in parts:
                n = re.findall( r"([<>=!]+)([0-9\.a-zA-Z]+)", p )
                if n:
                    res.append( n[0] )
        else:
            return (m[0][0], res)
    if len( m ) > 0:
        return (m[0][0], res)
    else:
        return (s, res)

def versions_under( vlist, version, eq = False ):
#    if str(version) not in vlist:
#        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if eq:
            if v >= Version(x):
                res.append( x )
        else:
            if v > Version(x):
                res.append( x )

    return res


def versions_over( vlist, version, eq = False ):
#    if str(version) not in vlist:
#        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if eq:
            if v <= Version( x ):
                res.append( x )
        else:
            if v < Version( x ):
                res.append( x )

    return res

def versions_exact( vlist, version ):
#    if str(version) not in vlist:
#        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if v == Version(x):
            res.append( x )
    return res


def versions_stable( vlist ):
    res = list()
    for x in sorted( vlist ):
        if not re.match( r"(.*rc[0-9]*)|(.*[ab]+[0-9]+)", x ):
            res.append( x )
    return res

if __name__ == "__main__":
    pass
