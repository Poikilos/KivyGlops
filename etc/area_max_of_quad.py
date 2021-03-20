#!/usr/bin/env python
# Python3 program to find maximum
# area of a quadrilateral
import math
import sys

def maxArea (a , b , c , d ):
    # This code is contributed by "Sharad_Bhardwaj"
    # to <https://www.geeksforgeeks.org/maximum-area-quadrilateral/>.
    # Calculating the semi-perimeter
    # of the given quadilateral
    semiperimeter = (a + b + c + d) / 2

    # Applying Brahmagupta's formula to
    # get maximum area of quadrilateral
    return math.sqrt((semiperimeter - a) *
                    (semiperimeter - b) *
                    (semiperimeter - c) *
                    (semiperimeter - d))

# Driver code
a = float(sys.argv[1])
b = float(sys.argv[2])
c = float(sys.argv[3])
d = float(sys.argv[4])
print("  Area using sides {}, {}, {} & {}: {}".format(a, b, c, d, maxArea(a, b, c, d)))

