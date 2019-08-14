#!/usr/bin/env python3

import os, sys, re
from pprint import pprint

class Version( object ):
    def __init__( self, v ):
        self._split_rx = re.compile( "\." )
        self._raw_version = v
        self._version = re.split( self._split_rx, self._raw_version)


    def __eq__( self, v ):
        va = self._version
        vb =  re.split( self._split_rx, v )

        if len( va ) != len( vb ):
            return False

        for i, j in enumerate( va ):
            if va[i] != vb[i]:
                return False
        return True

    def __ne__( self, v ):
        return not self.__eq__( v )

    def __lt__( self, v ):
        va = self._version
        vb =  re.split( self._split_rx, v )

        one_a = int( "".join( va ) )
        one_b = int( "".join( vb ) )
        if one_a < one_b:
            return True
        return False

    def __le__( self, v ):
        va = self._version
        vb =  re.split( self._split_rx, v )

        if self.__eq__( v ):
            return True

        one_a = int( "".join( va ) )
        one_b = int( "".join( vb ) )
        if one_a < one_b:
            return True
        return False

    def __gt__( self, v ):
        va = self._version
        vb =  re.split( self._split_rx, v )

        one_a = int( "".join( va ) )
        one_b = int( "".join( vb ) )
        if one_a > one_b:
            return True
        return False


    def __ge__( self, v ):
        va = self._version
        vb =  re.split( self._split_rx, v )

        if self.__eq__( v ):
            return True

        one_a = int( "".join( va ) )
        one_b = int( "".join( vb ) )
        if one_a > one_b:
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
    if version not in vlist:
        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = Version( version )
    res = list()
    for x in sorted( vlist ):
        if v > x:
            res.append( x )
    return res


def versions_over( vlist, version ):
    if version not in vlist:
        raise AttributeError("Version %s not in version list!" % ( version ) )

    v = Version( version )
    res = list()
    for x in sorted( vlist ):
        if v < x:
            res.append( x )
    return res




if __name__ == "__main__":

    prod = ["1.0.0","1.0.1","1.0.2","1.1.0","1.1.1","1.2.0","1.3.0","1.3.3","1.3.4","1.6.0","2.0.1","2.2.0","2.5.2",]
    data = ["test","test==1.0.0", "test>=1.0.0", "test<2.0.0", "test>=1.2.1,<=2.0.0"]

    a1 = "1.2.3.4"
    b1 = "1.2.3.4"
    b2 = "1.2.3.5"
    b3 = "1.2.3.3"

    ao1 = Version( a1 )
    print("11: %s" % ( ao1 == b1 ) )
    print("12: %s" % ( ao1 != b2 ) )

    print("21: %s" % ( ao1 < b2 ) )
    print("22: %s" % ( ao1 <= b2 ) )

    print("31: %s" % ( ao1 > b3 ) )
    print("32: %s" % ( ao1 >= b3 ) )


    for x in data:
        print("----------------------------")
        print( x )
        for e in parse_product( x ) :
            if len( e ) > 0:
                pprint( e )

        print("----------------------------")

    print("----------------------------")
    version1 = "1.3.3"
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for pre-%s" % ( version1 ) )
    pprint( versions_under( prod, version1 ) )
    print("----------------------------")
    version2 = "1.3.3"
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for post-%s" % ( version2 ) )
    pprint( versions_over( prod, version2 ) )
    print("----------------------------")
