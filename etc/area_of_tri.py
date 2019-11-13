#!/usr/bin/env python
# Python Program to find the area of triangle
import sys
a = float(sys.argv[1])
b = float(sys.argv[2])
c = float(sys.argv[3])

# from https://www.programiz.com/python-programming/examples/area-triangle

# calculate the semi-perimeter
s = (a + b + c) / 2

# calculate the area
area = (s*(s-a)*(s-b)*(s-c)) ** 0.5
print('  Area using sides {}, {} & {}: {}'.format(a, b, c, area))
