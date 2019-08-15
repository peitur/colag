#!/usr/bin/env python3

import os, sys, re
from distutils.version import LooseVersion, StrictVersion

from pprint import pprint

class Version( object ):
    def __init__( self, v ):
        self._split_rx = re.compile( "\." )
        self._raw_version = v
        if type( v ).__name__ == "str":
            self._version = LooseVersion( v )
        elif type( v ).__name__ == "Version":
            self._version = LooseVersion( str(v) )
        elif type( v ).__name__ == "LooseVersion":
            self._version = v
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

        if va == vb:
            return True

        if va < vb:
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

        if va == vb:
            return True

        if va > vb:
            return True
        return False

def parse_product( s ):
    rx = re.compile( r"^([a-zA-Z0-9-_]+)(.*)$" )
    m = rx.findall( s )
    res = list()
    if m:
        if len( m[0] ) > 1:
           parts = re.split( r",", m[0][1] )
           for p in parts:
               n = re.findall( r"([<>=!]+)([0-9\.]+)", p )
               if n:
                   res.append( n[0] )
    return res

def versions_under( vlist, version ):
    if str(version) not in vlist:
        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if v > Version(x):
            res.append( x )
    return res


def versions_over( vlist, version ):
    if str(version) not in vlist:
        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if v < Version(x):
            res.append( x )
    return res

def versions_exact( vlist, version ):
    if str(version) not in vlist:
        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = version
    res = list()
    for x in sorted( vlist ):
        if v == Version(x):
            res.append( x )
    return res

def mycmp(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

if __name__ == "__main__":

    prod = ["1.0.0","1.0.1","1.0.2","1.1.0","1.1.1","1.2.0","1.3.0","1.3.3","1.3.4","1.6.0","2.0.1","2.2.0","2.5.2",]
    data = ["test","test==1.0.0", "test>=1.0.0", "test<2.0.0", "test>=1.2.1,<=2.0.0"]

    a1 = Version("1.2.3.4")
    b1 = Version("1.2.3.4")
    b2 = Version("1.2.3.5")
    b3 = Version("1.2.3.3")

    print( type( a1 ).__name__ )
    print("11: %s" % ( a1 == b1 ) )
    print("12: %s" % ( a1 != b2 ) )

    print("21: %s" % ( a1 < b2 ) )
    print("22: %s" % ( a1 <= b2 ) )

    print("31: %s" % ( a1 > b3 ) )
    print("32: %s" % ( a1 >= b3 ) )



    print("----------------------------")
    version1 = Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for pre-%s" % ( version1 ) )
    pprint( versions_under( prod, version1 ) )
    print("----------------------------")
    version2 = Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for post-%s" % ( version2 ) )
    pprint( versions_over( prod, version2 ) )
    print("----------------------------")
    version3 = Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for post-%s" % ( version3 ) )
    pprint( versions_exact( prod, version3 ) )
    print("----------------------------")

    for x in data:
        print("----------------------------")
        print( x )
        for e in parse_product( x ) :
            if len( e ) > 0:
                pprint( e )
        print("----------------------------")
