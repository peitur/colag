#!/usr/bin/env python3

import os, sys, re
from pprint import pprint

import colag


if __name__ == "__main__":

    prod = ["1.0.0","1.0.1","1.0.2","1.1.0","1.1.1","1.2.0","1.3.0","1.3.3","1.3.4r","1.6.0","2.0.1","2.2.0","2.5.2",]
    data = ["test","test==1.0.2", "test>=1.0.0", "test<2.0.1", "test>=1.0.1,<=1.3.4r"]

    a1 = colag.Version("1.2.3.4")
    b1 = colag.Version("1.2.3.4")
    b2 = colag.Version("1.2.3.5")
    b3 = colag.Version("1.2.3.3")

    print( type( a1 ).__name__ )
    print("11: %s" % ( a1 == b1 ) )
    print("12: %s" % ( a1 != b2 ) )

    print("21: %s" % ( a1 < b2 ) )
    print("22: %s" % ( a1 <= b2 ) )

    print("31: %s" % ( a1 > b3 ) )
    print("32: %s" % ( a1 >= b3 ) )



    print("----------------------------")
    version1 = colag.Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for pre-%s" % ( version1 ) )
    pprint( colag.versions_under( prod, version1 ) )
    print("----------------------------")
    version2 = colag.Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for post-%s" % ( version2 ) )
    pprint( colag.versions_over( prod, version2 ) )
    print("----------------------------")
    version3 = colag.Version("1.3.3")
    pprint("Versions: %s" % ( ", ".join(prod)) )
    print("looking for post-%s" % ( version3 ) )
    pprint( colag.versions_exact( prod, version3 ) )
    print("----------------------------")

    for x in data:
        print("----------------------------")
        print( x )
        prd = prod
        for e in colag.parse_product( x ):
            pprint( e )
            if len( e ) > 0:
                if e[0] in ("=="):
                    prd = colag.versions_exact( prd, e[1] )
                    pprint( prd[-1] )
                if e[0] in (">", ">="):
                    prd = colag.versions_over( prd, e[1] )
                    pprint( prd[-1] )
                if e[0] in ("<", "<="):
                    prd = colag.versions_under( prd, e[1] )
                    pprint( prd[-1] )

        print("----------------------------")
