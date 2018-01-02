"""
This provides simple dependency-free access to OBJ files and certain 3D math operations.
#Illumination models (as per OBJ format standard) [NOT YET IMPLEMENTED]:
# 0. Color on and Ambient off
# 1. Color on and Ambient on [binary:0001]
# 2. Highlight on [binary:0010]
# 3. Reflection on and Ray trace on [binary:0011]
# 4. Transparency: Glass on, Reflection: Ray trace on [binary:0100]
# 5. Reflection: Fresnel on and Ray trace on [binary:0101]
# 6. Transparency: Refraction on, Reflection: Fresnel off and Ray trace on [binary:0110]
# 7. Transparency: Refraction on, Reflection: Fresnel on and Ray trace on [binary:0111]
# 8. Reflection on and Ray trace off [binary:1000]
# 9. Transparency: Glass on, Reflection: Ray trace off [binary:1001]
# 10. Casts shadows onto invisible surfaces [binary:1010]
"""

import os
import math
#from docutils.utils.math.math2html import VerticalSpace
#import traceback
from common import *
#from pyrealtime import *

import timeit
from timeit import default_timer as best_timer
import time

tab_string = "  "

verbose_enable = True

def get_verbose_enable():
    return verbose_enable

#references:
#kivy-trackball objloader (version with no MTL loader) by nskrypnik
#objloader from kivy-rotation3d (version with placeholder mtl loader) by nskrypnik

#TODO:
#-remove resource_find but still make able to find mtl file under Kivy somehow

from wobjfile import *
dump_enable = False
add_dump_comments_enable = False

V_POS_INDEX = 0
V_TC0_INDEX = 1
V_TC1_INDEX = 2
V_DIFFUSE_INDEX = 3
V_NORMAL_INDEX = 4
#see also pyglopsmesh.vertex_depth below

#indices of tuples inside vertex_format (see PyGlop)
VFORMAT_NAME_INDEX = 0
VFORMAT_VECTOR_LEN_INDEX = 1
VFORMAT_TYPE_INDEX = 2

EMPTY_ITEM = dict()
EMPTY_ITEM["name"] = "Empty"

kEpsilon = 1.0E-14 # adjust to suit.  If you use floats, you'll probably want something like 1E-7f

def normalize_3d_by_ref(this_vec3):
    #see <https://stackoverflow.com/questions/23303598/3d-vector-normalization-issue#23303817>
    length = math.sqrt(this_vec3[0] * this_vec3[0] + this_vec3[1] * this_vec3[1] + this_vec3[2] * this_vec3[2])
    if length > 0:
        this_vec3[0] /= length
        this_vec3[1] /= length
        this_vec3[2] /= length
    else:
        this_vec3[0] = 0.0
        this_vec3[1] = -1.0  # give some kind of normal for 0,0,0
        this_vec3[2] = 0.0

def get_fvec4_from_svec3(vals, last_value):
    results = None
    try:
        if len(vals)==1:
            results = float(vals[0]), float(vals[0]), float(vals[0]), last_value
        elif len(vals)==2:
            print("ERROR in get_fvec4: bad length 2 for " + str(vals))
            results = float(vals[0]), float(vals[0]), float(vals[0]), last_value
        elif len(vals)==3:
            results = float(vals[0]), float(vals[1]), float(vals[2]), last_value
        else:
            results = float(vals[0]), float(vals[1]), float(vals[2]), last_value
    except ValueError:
        print("ERROR in get_fvec4: bad floats in " + str(vals))
        results = 0.0, 0.0, 0.0, 0.0
    return results

def get_fvec4_from_svec_any_len(vals):
    results = None
    try:
        if len(vals)==1:
            results = float(vals[0]), float(vals[0]), float(vals[0]), 1.0
        elif len(vals)==2:
            print("ERROR in get_fvec4: bad length 2 for " + str(vals))
            results = float(vals[0]), float(vals[0]), float(vals[0]), float(vals[1])
        elif len(vals)==3:
            results = float(vals[0]), float(vals[1]), float(vals[2]), 1.0
        else:
            results = float(vals[0]), float(vals[1]), float(vals[2]), float(vals[3])
    except ValueError:
        print("ERROR in get_fvec4: bad floats in " + str(vals))
        results = 0.0, 0.0, 0.0, 0.0
    return results

def get_vec3_from_point(point):
    return (point.x, point.y, point.z)

def get_rect_from_polar_deg(r, theta):
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x,y

def get_rect_from_polar_rad(r, theta):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x,y

def angle_trunc(a):
    while a < 0.0:
        a += math.pi * 2
    return a

# angle_trunc and getAngleBetweenPoints edited Jul 19 '15 at 20:12  answered Sep 28 '11 at 16:10  Peter O. <http://stackoverflow.com/questions/7586063/how-to-calculate-the-angle-between-a-line-and-the-horizontal-axis>. 29 Apr 2016
def getAngleBetweenPoints(x_orig, y_orig, x_landmark, y_landmark):
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(math.atan2(deltaY, deltaX))

#get angle between two points (from a to b), swizzled to 2d on xz plane; based on getAngleBetweenPoints
def get_angle_between_two_vec3_xz(a, b):
    deltaY = b[2] - a[2]
    deltaX = b[0] - a[0]
    return angle_trunc(math.atan2(deltaY, deltaX))

#returns nearest point on line bc from point a, swizzled to 2d on xz plane
def get_nearest_vec3_on_vec3line_using_xz(a, b, c): #formerly PointSegmentDistanceSquared
    t = None
    #as per http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    kMinSegmentLenSquared = 0.00000001 # adjust to suit.  If you use float, you'll probably want something like 0.000001f

    #epsilon is the common name for the floating point error constant (needed since some base 10 numbers cannot be stored as IEEE 754 with absolute precision)
    #same as 1.0 * 10**-14 according to http://python-reference.readthedocs.io/en/latest/docs/float/scientific.html
    dx = c[0] - b[0]
    dy = c[2] - b[2]
    db = [a[0] - b[0], 0.0, a[2] - b[2]]  # 0.0 since swizzling to xz (ignore source y)
    segLenSquared = (dx * dx) + (dy * dy)
    if segLenSquared >= -kMinSegmentLenSquared and segLenSquared <= kMinSegmentLenSquared:
        # segment is a point.
        qx = b[0]
        qy = b[2]
        t = 0.0
        distance = ((db[0] * db[0]) + (db[2] * db[2]))
        return qx, a[1], qy, distance
    else:
        # Project a line from p to the segment [p1,p2].  By considering the line
        # extending the segment, parameterized as p1 + (t * (p2 - p1)),
        # we find projection of point p onto the line.
        # It falls where t = [(p - p1) . (p2 - p1)] / |p2 - p1|^2
        t = ((db[0] * dx) + (db[2] * dy)) / segLenSquared
        if t < kEpsilon:
            # intersects at or to the "left" of first segment vertex (b[0], b[2]).  If t is approximately 0.0, then
            # intersection is at p1.  If t is less than that, then there is no intersection (i.e. p is not within
            # the 'bounds' of the segment)
            if t > -kEpsilon:
                # intersects at 1st segment vertex
                t = 0.0
            # set our 'intersection' point to p1.
            qx = b[0]
            qy = b[2]
        elif t > (1.0 - kEpsilon): # Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
        # we were doing PointLineDistanceSquared, then qx would be (b[0] + (t * dx)) and qy would be (b[2] + (t * dy)).

            # intersects at or to the "right" of second segment vertex (c[0], c[2]).  If t is approximately 1.0, then
            # intersection is at p2.  If t is greater than that, then there is no intersection (i.e. p is not within
            # the 'bounds' of the segment)
            if t < (1.0 + kEpsilon):
                # intersects at 2nd segment vertex
                t = 1.0
            # set our 'intersection' point to p2.
            qx = c[0]
            qy = c[2]
        else:
            # Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
            # we were doing PointLineDistanceSquared, then qx would be (b[0] + (t * dx)) and qy would be (b[2] + (t * dy)).
            # The projection of the point to the point on the segment that is perpendicular succeeded and the point
            # is 'within' the bounds of the segment.  Set the intersection point as that projected point.
            qx = b[0] + (t * dx)
            qy = b[2] + (t * dy)
        # return the squared distance from p to the intersection point.  Note that we return the squared distance
        # as an oaimization because many times you just need to compare relative distances and the squared values
        # works fine for that.  If you want the ACTUAL distance, just take the square root of this value.
        dpqx = a[0] - qx
        dpqy = a[2] - qy
        distance = ((dpqx * dpqx) + (dpqy * dpqy))
        return qx, a[1], qy, distance

#returns distance from point a to line bc, swizzled to 2d on xz plane
def get_distance_vec2_to_vec2line_xz(a, b, c):
    return math.sin(math.atan2(b[2] - a[2], b[0] - a[0]) - math.atan2(c[2] - a[2], c[0] - a[0])) * math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[2] - a[2]) * (b[2] - a[2]))

#returns distance from point a to line bc
def get_distance_vec2_to_vec2line(a, b, c):
    #from ADOConnection on stackoverflow answered Nov 18 '13 at 22:37
    #this commented part is the expanded version of the same answer (both versions are given in answer)
    #// normalize points
    #Point cn = new Point(c[0] - a[0], c[1] - a[1]);
    #Point bn = new Point(b[0] - a[0], b[1] - a[1]);

    #double angle = Math.Atan2(bn[1], bn[0]) - Math.Atan2(cn[1], cn[0]);
    #double abLength = Math.Sqrt(bn[0]*bn[0] + bn[1]*bn[1]);

    #return math.sin(angle)*abLength;
    return math.sin(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(c[1] - a[1], c[0] - a[0])) * math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]))

#swizzle to 2d point on xz plane, then get distance
def get_distance_vec3_xz(first_pt, second_pt):
    return math.sqrt( (second_pt[0]-first_pt[0])**2 + (second_pt[2]-first_pt[2])**2 )

def get_distance_vec3(first_pt, second_pt):
    return math.sqrt((second_pt[0] - first_pt[0])**2 + (second_pt[1] - first_pt[1])**2 + (second_pt[2] - first_pt[2])**2)

def get_distance_vec2(first_pt, second_pt):
    return math.sqrt( (second_pt[0]-first_pt[0])**2 + (second_pt[1]-first_pt[1])**2 )

#halfplane check (which half) formerly sign
def get_halfplane_sign(p1, p2, p3):
    #return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

#PointInTriangle and get_halfplane_sign are from http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle
#edited Oct 18 '14 at 18:52 by msrd0
#answered Jan 12 '10 at 14:27 by Kornel Kisielewicz
#(based on http://www.gamedev.net/community/forums/topic.asp?topic_id=295943)
def PointInTriangle(pt, v1, v2, v3):
    b1 = get_halfplane_sign(pt, v1, v2) < 0.0
    b2 = get_halfplane_sign(pt, v2, v3) < 0.0
    b3 = get_halfplane_sign(pt, v3, v1) < 0.0
    #WARNING: returns false sometimes on edge, depending whether triangle is clockwise or counter-clockwise
    return (b1 == b2) and (b2 == b3)

def get_pushed_vec3_xz_rad(pos, r, theta):
    #push_x, push_y = (0,0)
    #if r != 0:
    push_x, push_y = get_rect_from_polar_rad(r, theta)
    return pos[0]+push_x, pos[1], pos[2]+push_y

#3 vector version of Developer's solution to <http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle> answered Jan 6 '14 at 11:32 by Developer
#uses x and y values
def is_in_triangle_HALFPLANES(check_pt,v0, v1, v2):
    '''checks if point check_pt(2) is inside triangle tri(3x2). @Developer'''
    a = 1/(-v1[1]*v2[0]+v0[1]*(-v1[0]+v2[0])+v0[0]*(v1[1]-v2[1])+v1[0]*v2[1])
    s = a*(v2[0]*v0[1]-v0[0]*v2[1]+(v2[1]-v0[1])*check_pt[0]+(v0[0]-v2[0])*check_pt[1])
    if s<0: return False
    else: t = a*(v0[0]*v1[1]-v1[0]*v0[1]+(v0[1]-v1[1])*check_pt[0]+(v1[0]-v0[0])*check_pt[1])
    return ((t>0) and (1-s-t>0))

def is_in_triangle_HALFPLANES_xz(check_pt,v0, v1, v2):
    '''checks if point check_pt(2) is inside triangle tri(3x2). @Developer'''
    a = 1/(-v1[2]*v2[0]+v0[2]*(-v1[0]+v2[0])+v0[0]*(v1[2]-v2[2])+v1[0]*v2[2])
    s = a*(v2[0]*v0[2]-v0[0]*v2[2]+(v2[2]-v0[2])*check_pt[0]+(v0[0]-v2[0])*check_pt[2])
    if s<0: return False
    else: t = a*(v0[0]*v1[2]-v1[0]*v0[2]+(v0[2]-v1[2])*check_pt[0]+(v1[0]-v0[0])*check_pt[2])
    return ((t>0) and (1-s-t>0))

#float calcY(vec3 p1, vec3 p2, vec3 p3, float x, float z) {
# as per http://stackoverflow.com/questions/5507762/how-to-find-z-by-arbitrary-x-y-coordinates-within-triangle-if-you-have-triangle
#  edited Jan 21 '15 at 15:07 josh2112 answered Apr 1 '11 at 0:02 Martin Beckett
def get_y_from_xz(p1, p2, p3, x, z):
    det = (p2[2] - p3[2]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[2] - p3[2])

    l1 = ((p2[2] - p3[2]) * (x - p3[0]) + (p3[0] - p2[0]) * (z - p3[2])) / det
    l2 = ((p3[2] - p1[2]) * (x - p3[0]) + (p1[0] - p3[0]) * (z - p3[2])) / det
    l3 = 1.0 - l1 - l2

    return l1 * p1[1] + l2 * p2[1] + l3 * p3[1]

#Did not yet read article: http://totologic.blogspot.fr/2014/01/accurate-point-in-triangle-test.html

#Developer's solution to <http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle> answered Jan 6 '14 at 11:32 by Developer
def PointInsideTriangle2_vec2(check_pt,tri):
    '''checks if point check_pt(2) is inside triangle tri(3x2). @Developer'''
    a = 1/(-tri[1,1]*tri[2,0]+tri[0,1]*(-tri[1,0]+tri[2,0])+tri[0,0]*(tri[1,1]-tri[2,1])+tri[1,0]*tri[2,1])
    s = a*(tri[2,0]*tri[0,1]-tri[0,0]*tri[2,1]+(tri[2,1]-tri[0,1])*check_pt[0]+(tri[0,0]-tri[2,0])*check_pt[1])
    if s<0: return False
    else: t = a*(tri[0,0]*tri[1,1]-tri[1,0]*tri[0,1]+(tri[0,1]-tri[1,1])*check_pt[0]+(tri[1,0]-tri[0,0])*check_pt[1])
    return ((t>0) and (1-s-t>0))

def is_in_triangle_coords(px, py, p0x, p0y, p1x, p1y, p2x, p2y):
#    IsInTriangle_Barymetric
    kEpsilon = 1.0E-14 # adjust to suit.  If you use floats, you'll probably want something like 1E-7f (added by expertmm)
    Area = 1/2*(-p1y*p2x + p0y*(-p1x + p2x) + p0x*(p1y - p2y) + p1x*p2y)
    s = 1/(2*Area)*(p0y*p2x - p0x*p2y + (p2y - p0y)*px + (p0x - p2x)*py)
    t = 1/(2*Area)*(p0x*p1y - p0y*p1x + (p0y - p1y)*px + (p1x - p0x)*py)
#    #TODO: fix situation where it fails when clockwise (see discussion at http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle )
    return  s>kEpsilon and t>kEpsilon and 1-s-t>kEpsilon

#swizzled to xz (uses index 0 and 2 of vec3)
def is_in_triangle_xz(check_vec3, a_vec3, b_vec3, c_vec3):
#    IsInTriangle_Barymetric
    kEpsilon = 1.0E-14 # adjust to suit.  If you use floats, you'll probably want something like 1E-7f (added by expertmm)
    Area = 1/2*(-b_vec3[2]*c_vec3[0] + a_vec3[2]*(-b_vec3[0] + c_vec3[0]) + a_vec3[0]*(b_vec3[2] - c_vec3[2]) + b_vec3[0]*c_vec3[2])
    s = 1/(2*Area)*(a_vec3[2]*c_vec3[0] - a_vec3[0]*c_vec3[2] + (c_vec3[2] - a_vec3[2])*check_vec3[0] + (a_vec3[0] - c_vec3[0])*check_vec3[2])
    t = 1/(2*Area)*(a_vec3[0]*b_vec3[2] - a_vec3[2]*b_vec3[0] + (a_vec3[2] - b_vec3[2])*check_vec3[0] + (b_vec3[0] - a_vec3[0])*check_vec3[2])
#    #TODO: fix situation where it fails when clockwise (see discussion at http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle )
    return  s>kEpsilon and t>kEpsilon and 1-s-t>kEpsilon

#swizzled to xz (uses index 0 and 2 of vec3)
def is_in_triangle_vec2(check_vec2, a_vec2, b_vec2, c_vec2):
#    IsInTriangle_Barymetric
    kEpsilon = 1.0E-14 # adjust to suit.  If you use floats, you'll probably want something like 1E-7f (added by expertmm)
    Area = 1/2*(-b_vec2[1]*c_vec2[0] + a_vec2[1]*(-b_vec2[0] + c_vec2[0]) + a_vec2[0]*(b_vec2[1] - c_vec2[1]) + b_vec2[0]*c_vec2[1])
    if Area>kEpsilon or Area<-kEpsilon:
        s = 1/(2*Area)*(a_vec2[1]*c_vec2[0] - a_vec2[0]*c_vec2[1] + (c_vec2[1] - a_vec2[1])*check_vec2[0] + (a_vec2[0] - c_vec2[0])*check_vec2[1])
        t = 1/(2*Area)*(a_vec2[0]*b_vec2[1] - a_vec2[1]*b_vec2[0] + (a_vec2[1] - b_vec2[1])*check_vec2[0] + (b_vec2[0] - a_vec2[0])*check_vec2[1])
    #    #TODO: fix situation where it fails when clockwise (see discussion at http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle )
        return  s>kEpsilon and t>kEpsilon and 1-s-t>kEpsilon
    else:
        return False
#class ItemData:  #changed to dict
#    name = None
#    passive_bumper_command = None
#    health_ratio = None

#    def __init__(self, bump="obtain"):
#        health_ratio = 1.0
#        passive_bumper_command = bump

# PyGlop defines a single OpenGL-ready object. PyGlops should be used for importing, since one mesh file (such as obj) can contain several meshes. PyGlops handles the 3D scene.


class PyGlopHitBox:
    minimums = None
    maximums = None

    def __init__(self):
        self.minimums = [-0.25, -0.25, -0.25]
        self.maximums = [0.25, 0.25, 0.25]

    def copy(self):
        target = PyGlopHitBox()
        target.minimums = copy.deepcopy(self.minimums)
        target.maximums = copy.deepcopy(self.maximums)
        return target

    def contains_vec3(self, pos):
        return pos[0]>=self.minimums[0] and pos[0]<=self.maximums[0] \
            and pos[1]>=self.minimums[1] and pos[1]<=self.maximums[1] \
            and pos[2]>=self.minimums[2] and pos[2]<=self.maximums[2]

    def to_string(self):
        return str(self.minimums[0]) + " to " + str(self.maximums[0]) + \
            ",  " + str(self.minimums[1]) + " to " + str(self.maximums[1]) + \
            ",  " + str(self.minimums[2]) + " to " + str(self.maximums[2])

class PyGlop:
    #update copy constructor if adding/changing copyable members
    name = None #object name such as from OBJ's 'o' statement
    dat = None
    source_path = None  #required so that meshdata objects can be uniquely identified (where more than one file has same object name)
    properties = None #dictionary of properties--has indices such as usemtl
    vertex_depth = None
    material = None
    _min_coords = None  #bounding cube minimums in local coordinates
    _max_coords = None  #bounding cube maximums in local coordinates
    _pivot_point = None  #TODO: asdf eliminate this--instead always use 0,0,0 and move vertices to change pivot; currently calculated from average of vertices if was imported from obj
    foot_reach = None  # distance from center (such as root bone) to floor
    eye_height = None  # distance from floor
    hit_radius = None
    item_dict = None
    projectile_dict = None
    actor_dict = None
    bump_enable = None
    reach_radius = None
    is_out_of_range = None
    physics_enable = None
    x_velocity = None
    y_velocity = None
    z_velocity = None
    _cached_floor_y = None
    infinite_inventory_enable = None
    bump_sound_paths = None
    look_target_glop = None
    hitbox = None
    visible_enable = None
    vertex_format = None
    vertices = None
    indices = None
    #opacity = None  moved to material.diffuse_color 4th channel

    #region runtime variables
    index = None  # set by add_glop
    #endregion runtime variables

    #region vars based on OpenGL ES 1.1 MOVED TO material
    #ambient_color = None  # vec4
    #diffuse_color = None  # vec4
    #specular_color = None  # vec4
    ##emissive_color = None  # vec4
    #specular_exponent = None  # float
    #endregion vars based on OpenGL ES 1.1 MOVED TO material

    #region calculated from vertex_format
    _POSITION_OFFSET = None
    _NORMAL_OFFSET = None
    _TEXCOORD0_OFFSET = None
    _TEXCOORD1_OFFSET = None
    COLOR_OFFSET = None
    POSITION_INDEX = None
    NORMAL_INDEX = None
    TEXCOORD0_INDEX = None
    TEXCOORD1_INDEX = None
    COLOR_INDEX = None
    #endregion calculated from vertex_format
    
    def __init__(self):
        self._init_glop()

    def _init_glop(self):  # formerly __init__ but that would interfere with super if subclass has multiple inheritance
        self.dat = {}
        self.dat["links"] = []  # list of relationship dicts
        self.separable_offsets = []  # if more than one submesh is in vertices, chunks are saved in here, such as to assist with explosions
        self.visible_enable = True
        self.hitbox = PyGlopHitBox()
        self.physics_enable = False
        self.infinite_inventory_enable = True
        self.is_out_of_range = True
        self.eye_height = 0.0  # or 1.7 since 5'10" person is ~1.77m, and eye down a bit
        self.hit_radius = 0.1524  # .5' equals .1524m
        self.reach_radius = 0.381  # 2.5' .381m
        self.bump_enable = False
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.z_velocity = 0.0
        self.bump_sound_paths = []
        self.properties = {}
        self.properties["inventory_index"] = -1
        self.properties["inventory_items"] = []
        #formerly in MeshData:
        # order MUST match V_POS_INDEX etc above
        self.vertex_format = [(b'a_position', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec3)
                              (b'a_texcoord0', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2); vTexCoord0; available if enable_tex[0] is true
                              (b'a_texcoord1', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2);  available if enable_tex[1] is true
                              (b'a_color', 4, 'float'),  # vColor (diffuse color of vertex)
                              (b'a_normal', 3, 'float')  # vNormal; Munshi prefers vec3 (Kivy also prefers vec3)
                              ]

        self.on_vertex_format_change()

        self.indices = []  # list of tris (1 big linear list of indices)

        self.eye_height = 1.7  # 1.7 since 5'10" person is ~1.77m, and eye down a bit
        self.hit_radius = .2
        self.reach_radius = 2.5

        # Default basic material of this glop
        self.material = PyGlopsMaterial()
        self.material.diffuse_color = (1.0, 1.0, 1.0, 1.0)  # overlay vertex color onto this using vertex alpha
        self.material.ambient_color = (0.0, 0.0, 0.0, 1.0)
        self.material.specular_color = (1.0, 1.0, 1.0, 1.0)
        self.material.specular_coefficent = 16.0
        #self.material.opacity = 1.0

        #TODO: find out where this code goes (was here for unknown reason)
        #if result is None:
        #    print("WARNING: no material for Glop named '"+str(self.name)+"' (NOT YET IMPLEMENTED)")
        #return result

    #copy should have override in subclass that calls copy_as_subclass then adds subclass-specific values to that result
    def copy(self):
        new_material_method = None
        if self.material is not None:
            new_material_method = self.material.new_material
        return self.copy_as_subclass(self.new_glop, new_material_method)
    
    def copy_as_subclass(self, new_glop_method, new_material_method, copy_verts_by_ref_enable=False):
        target = new_glop_method()
        target.name = self.name #object name such as from OBJ's 'o' statement
        target.source_path = self.source_path  #required so that meshdata objects can be uniquely identified (where more than one file has same object name)
        if self.properties is not None:
            target.properties = copy.deepcopy(self.properties) #dictionary of properties--has indices such as usemtl
        target.vertex_depth = self.vertex_depth
        if self.material is not None:
            if new_material_method is not None:
                target.material = self.material.copy_as_subclass(new_material_method)
            else:
                print("WARNING in PyGlop copy: skipped material during copy since no new_material_method was specified")
        target._min_coords = self._min_coords  #bounding cube minimums in local coordinates
        target._max_coords = self._max_coords  #bounding cube maximums in local coordinates
        target._pivot_point = self._pivot_point  #TODO: asdf eliminate this--instead always use 0,0,0 and move vertices to change pivot; currently calculated from average of vertices if was imported from obj
        target.foot_reach = self.foot_reach  # distance from center (such as root bone) to floor
        target.eye_height = self.eye_height  # distance from floor
        target.hit_radius = self.hit_radius
        target.item_dict = self.deepcopy_with_my_type(self.item_dict)  # DOES return None if sent None
        target.projectile_dict = self.deepcopy_with_my_type(self.projectile_dict)
        target.actor_dict = self.deepcopy_with_my_type(self.actor_dict)
        target.bump_enable = self.bump_enable
        target.reach_radius = self.reach_radius
        #target.is_out_of_range = self.is_out_of_range
        target.physics_enable = self.physics_enable
        target.x_velocity = self.x_velocity
        target.y_velocity = self.y_velocity
        target.z_velocity = self.z_velocity
        #target._cached_floor_y = self._cached_floor_y
        target.infinite_inventory_enable = self.infinite_inventory_enable
        target.bump_sound_paths = copy.deepcopy(self.bump_sound_paths)
        target.look_target_glop = self.look_target_glop # by reference since is a reference to begin with
        target.hitbox = self.hitbox.copy()
        target.visible_enable = self.visible_enable
        target.vertex_format = copy.deepcopy(self.vertex_format)
        if copy_verts_by_ref_enable:
            target.vertices = self.vertices
            target.indices = self.indices
        else:
            target.vertices = copy.deepcopy(self.vertices)
            target.indices = copy.deepcopy(self.indices)
        return target

    #prevent pickling failure by using this to copy dicts AND lists that contain members that are my type
    def deepcopy_with_my_type(self, old_dict, copy_my_type_by_reference_enable=False):
        new_dict = None
        #if type(old_dict) is dict:
        new_dict = None
        keys = None
        if old_dict is not None:
            if isinstance(old_dict, list):
                new_dict = []
                keys = range(0, len(old_dict))
            elif isinstance(old_dict, dict):
                new_dict = {}
                keys = old_dict.keys()
            #if keys is not None:
            #will fail if neither dict nor list (let it fail)
            for this_key in keys:
                if type(old_dict[this_key]) == type(self):
                    #NOTE: the type for both sides of the check above are always the subclass if running this from a subclass as demonstrated by: print("the type of old dict " + str(type(old_dict[this_key])) + " == " + str(type(self)))
                    if copy_my_type_by_reference_enable:
                        if isinstance(new_dict, dict):
                            new_dict[this_key] = old_dict[this_key]
                        else:
                            new_dict.append(old_dict[this_key])
                    else:
                        copy_of_var = None
                        #NOTE: self.material would always be a PyGlopsMaterial, not subclass, in the case below
                        new_material_method = None
                        if old_dict[this_key].material is not None:
                            new_material_method = old_dict[this_key].material.new_material
                        copy_of_var = old_dict[this_key].copy_as_subclass(old_dict[this_key].new_glop, new_material_method)
                        if isinstance(new_dict, dict):
                            new_dict[this_key] = copy_of_var
                        else:
                            new_dict.append(copy_of_var)
                #TODO?: elif isinstance(old_dict[this_key], type(self.material))
                elif isinstance(old_dict[this_key], list):
                    new_dict[this_key] = self.deepcopy_with_my_type(old_dict[this_key], copy_my_type_by_reference_enable=copy_my_type_by_reference_enable)
                elif isinstance(old_dict[this_key], dict):
                    new_dict[this_key] = self.deepcopy_with_my_type(old_dict[this_key], copy_my_type_by_reference_enable=copy_my_type_by_reference_enable)
                else:
                    new_dict[this_key] = copy.deepcopy(old_dict[this_key])
        return new_dict

    def calculate_hit_range(self):
        print("Calculate hit range should be implemented by subclass.")
        print("  (setting hitbox to None to avoid using default hitbox)")
        self.hitbox = None
    
    def process_ai(self, glop_index):
        #this should be implemented in the subclass
        pass

    def apply_vertex_offset(self, this_point):
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        v_offset = 0
        for i in range(0,3):
            #intentionally set to rediculously far in opposite direction:
            self.hitbox.minimums[i] = sys.maxsize
            self.hitbox.maximums[i] = -sys.maxsize
        for v_number in range(0, vertex_count):
            for i in range(0,3):
                self.vertices[v_offset+self._POSITION_OFFSET+i] -= this_point[i]
                if self.vertices[v_offset+self._POSITION_OFFSET+i] < self.hitbox.minimums[i]:
                    self.hitbox.minimums[i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
                if self.vertices[v_offset+self._POSITION_OFFSET+i] > self.hitbox.maximums[i]:
                    self.hitbox.maximums[i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
            this_vertex_relative_distance = get_distance_vec3(self.vertices[v_offset+self._POSITION_OFFSET:], this_point)
            if this_vertex_relative_distance > self.hit_radius:
                self.hit_radius = this_vertex_relative_distance
            #self.vertices[v_offset+self._POSITION_OFFSET+0] -= this_point[0]
            #self.vertices[v_offset+self._POSITION_OFFSET+1] -= this_point[1]
            #self.vertices[v_offset+self._POSITION_OFFSET+2] -= this_point[2]

            v_offset += self.vertex_depth
        
    def apply_pivot(self):
        self.apply_vertex_offset(self._pivot_point)
        self._pivot_point = (0.0, 0.0, 0.0)        

    def look_at(self, this_glop):
        print("WARNING: look_at should be implemented by subclass which has rotation angle(s) or matr(ix/ices)")
        
    def has_item(self, name):
        result = False
        for i in range(0,len(self.properties["inventory_items"])):
            if (self.properties["inventory_items"][i] is not None) and \
               (self.properties["inventory_items"][i]["name"] == name):
                result = True
                break
        return result
    
    #your program can override this method for custom inventory layout
    def push_item(self, item_dict):
        select_item_event_dict = dict()
        select_item_event_dict["fit_enable"] = False  # stays false if inventory was full
        for i in range(0,len(self.properties["inventory_items"])):
            if self.properties["inventory_items"][i] is None or self.properties["inventory_items"][i]["name"] == EMPTY_ITEM["name"]:
                self.properties["inventory_items"][i] = item_dict
                select_item_event_dict["fit_enable"] = True
                print("[ PyGlops ] (verbose message) obtained item in slot "+str(i)+": "+str(item_dict))
                break
        if self.infinite_inventory_enable:
            if not select_item_event_dict["fit_enable"]:
                self.properties["inventory_items"].append(item_dict)
                #print("[ PyGlops ] (verbose message) obtained item in new slot: "+str(item_dict))
                print("[ PyGlops ] (verbose message) obtained " + item_dict["name"] + " in new slot " + \
                      str(len(self.properties["inventory_items"])-1))
                select_item_event_dict["fit_enable"] = True
        if select_item_event_dict["fit_enable"]:
            if self.properties["inventory_index"] < 0:
                self.properties["inventory_index"] = 0
            this_item_dict = self.properties["inventory_items"][self.properties["inventory_index"]]
            name = ""
            proper_name = ""
            select_item_event_dict["inventory_index"] = self.properties["inventory_index"]
            if "name" in this_item_dict:
                name = this_item_dict["name"]
            select_item_event_dict["name"] = name
            if "glop_name" in this_item_dict:
                proper_name = this_item_dict["glop_name"]
            select_item_event_dict["proper_name"] = proper_name
            select_item_event_dict["calling method"] = "push_glop_item"
        return select_item_event_dict


    def select_next_inventory_slot(self, is_forward):
        select_item_event_dict = dict()
        delta = 1
        if not is_forward:
            delta = -1
        if len(self.properties["inventory_items"]) > 0:
            select_item_event_dict["fit_enable"] = True
            self.properties["inventory_index"] += delta
            if self.properties["inventory_index"] < 0:
                self.properties["inventory_index"] = len(self.properties["inventory_items"]) - 1
            elif self.properties["inventory_index"] >= len(self.properties["inventory_items"]):
                self.properties["inventory_index"] = 0
            this_item_dict = self.properties["inventory_items"][self.properties["inventory_index"]]
            name = ""
            proper_name = ""
            select_item_event_dict["inventory_index"] = self.properties["inventory_index"]
            if "glop_name" in this_item_dict:
                proper_name = this_item_dict["glop_name"]
            select_item_event_dict["proper_name"] = proper_name
            if "name" in this_item_dict:
                name = this_item_dict["name"]
            select_item_event_dict["name"] = name
            #print("item event: "+str(select_item_event_dict))
            select_item_event_dict["calling method"] = "select_next_inventory_slot"
            #print("Selected "+this_item_dict["name"]+" "+proper_name+" in slot "+str(self.properties["inventory_index"]))
            item_count = 0
            for index in range(0, len(self.properties["inventory_items"])):
                if self.properties["inventory_items"][index]["name"] != EMPTY_ITEM["name"]:
                    item_count += 1
            print("[ PyGlops ] (verbose message) You have " + str(item_count) + " item(s).")
            select_item_event_dict["item_count"] = item_count
        else:
            select_item_event_dict["fit_enable"] = False
            print("[ PyGlops ] You have 0 items.")
        return select_item_event_dict

    def _on_change_pivot(self, previous_point=(0.0,0.0,0.0)):
        # should be implemented by subclass
        # print("[ PyGlops ] your _on_change_pivot should override this")
        pass
    
    def get_context(self):
        # implement in subclass since involves graphics implementation
        print("WARNING: get_context should be defined by a subclass")
        return False
    
    def transform_pivot_to_geometry(self):
        previous_point = self._pivot_point
        self._pivot_point = self.get_center_average_of_vertices()
        self._on_change_pivot(previous_point=previous_point)

    def get_texture_diffuse_path(self):  #formerly getTextureFileName(self):
        result = None
        try:
            if self.material is not None:
                if self.material.properties is not None:
                    if "diffuse_path" in self.material.properties:
                        result = self.material.properties["diffuse_path"]
                        if not os.path.exists(result):
                            try_path = os.path.join(os.path.dirname(os.path.abspath(self.source_path)), result)  #
                            if os.path.exists(try_path):
                                result = try_path
                            else:
                                print("Could not find texture (tried '"+str(try_path)+"'")
        except:
            print("Could not finish get_texture_diffuse_path:")
            view_traceback()
        if result is None:
            if get_verbose_enable():
                print("NOTE: no diffuse texture specified in Glop named '"+str(self.name)+"'")
        return result

    def get_min_x(self):
        val = 0.0
        try:
            val = self._min_coords[0]
        except:
            pass
        return val

    def get_max_x(self):
        val = 0.0
        try:
            val = self._max_coords[0]
        except:
            pass
        return val

    def get_min_y(self):
        val = 0.0
        try:
            val = self._min_coords[1]
        except:
            pass
        return val

    def get_max_y(self):
        val = 0.0
        try:
            val = self._max_coords[1]
        except:
            pass
        return val

    def get_min_z(self):
        val = 0.0
        try:
            val = self._min_coords[2]
        except:
            pass
        return val

    def get_max_z(self):
        val = 0.0
        try:
            val = self._max_coords[2]
        except:
            pass
        return val

    def recalculate_bounds(self):
        self._min_coords = [None,None,None]
        self._max_coords = [None,None,None]
        participle = "initializing"
        try:
            if (self.vertices is not None):
                participle = "accessing vertices"
                for i in range(0,int(len(self.vertices)/self.vertex_depth)):
                    for axisIndex in range(0,3):
                        if self._min_coords[axisIndex] is None or self.vertices[i*self.vertex_depth+axisIndex] < self._min_coords[axisIndex]:
                            self._min_coords[axisIndex] = self.vertices[i*self.vertex_depth+axisIndex]
                        if self._max_coords[axisIndex] is None or self.vertices[i*self.vertex_depth+axisIndex] > self._max_coords[axisIndex]:
                            self._max_coords[axisIndex] = self.vertices[i*self.vertex_depth+axisIndex]
        except:  # Exception as e:
            print("Could not finish "+participle+" in recalculate_bounds: ")
            view_traceback()

    def get_center_average_of_vertices(self):
        #results = (0.0,0.0,0.0)
        totals = list()
        counts = list()
        results = list()
        for i in range(0,self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]):
            if i<3:
                results.append(0.0)
            else:
                results.append(1.0)  #4th index (index 3) must be 1.0 for matrix math to work correctly
        participle = "before initializing"
        try:
            totals.append(0.0)
            totals.append(0.0)
            totals.append(0.0)
            counts.append(0)
            counts.append(0)
            counts.append(0)
            if (self.vertices is not None):
                participle = "accessing vertices"
                for i in range(0,int(len(self.vertices)/self.vertex_depth)):
                    for axisIndex in range(0,3):
                        participle = "accessing vertex axis"
                        if (self.vertices[i*self.vertex_depth+axisIndex]<0):
                            participle = "accessing totals"
                            totals[axisIndex] += self.vertices[i*self.vertex_depth+axisIndex]
                            participle = "accessing vertex count"
                            counts[axisIndex] += 1
                        else:
                            participle = "accessing totals"
                            totals[axisIndex] += self.vertices[i*self.vertex_depth+axisIndex]
                            participle = "accessing vertex count"
                            counts[axisIndex] += 1
            for axisIndex in range(0,3):
                participle = "accessing final counts"
                if (counts[axisIndex]>0):
                    participle = "calculating results"
                    results[axisIndex] = totals[axisIndex] / counts[axisIndex]
        except:  # Exception as e:
            print("Could not finish "+participle+" in get_center_average_of_vertices: ")
            view_traceback()

        return tuple(results)

    def set_textures_from_wmaterial(self, wmaterial):
        #print("")
        #print("set_textures_from_wmaterial...")
        #print("")
        f_name = "set_textures_from_wmaterial"
        try:
            opacity = None
            if "d" in wmaterial:
                opacity = float(wmaterial["d"]["values"][0])
            elif "Tr" in wmaterial:
                opacity = 1.0 - float(wmaterial["Tr"]["values"][0])
            if opacity is not None:
                self.material.diffuse_color = get_fvec4_from_svec3(wmaterial["Kd"]["values"], opacity) if ("Kd" in wmaterial) else self.material.diffuse_color 
            else:
                self.material.diffuse_color = get_fvec4_from_svec_any_len(wmaterial["Kd"]["values"]) if ("Kd" in wmaterial) else self.material.diffuse_color
            #self.material.diffuse_color = [float(v) for v in self.material.diffuse_color]
            self.material.ambient_color = get_fvec4_from_svec_any_len(wmaterial["Ka"]["values"]) if ("Ka" in wmaterial) else self.material.ambient_color
            self.material.specular_color = get_fvec4_from_svec_any_len(wmaterial["Ks"]["values"]) if ("Ks" in wmaterial) else self.material.specular_color
            if "Ns" in wmaterial:
                self.material.specular_coefficent = float(wmaterial["Ns"]["values"][0])
            #TODO: store as diffuse color alpha instead: self.opacity = wmaterial.get('d')
            #TODO: store as diffuse color alpha instead: if self.opacity is None:
            #TODO: store as diffuse color alpha instead:     self.opacity = 1.0 - float(wmaterial.get('Tr', 0.0))
            if "map_Ka" in wmaterial:
                self.material.properties["ambient_path"] = wmaterial["map_Ka"]["values"][0]
            if "map_Kd" in wmaterial:
                self.material.properties["diffuse_path"] = wmaterial["map_Kd"]["values"][0]
                #print("  NOTE: diffuse_path: "+self.material.properties["diffuse_path"])
            #else:
                #print("  WARNING: "+str(self.name)+" has no map_Kd among material keys "+','.join(wmaterial.keys()))
            if "map_Ks" in wmaterial:
                self.material.properties["specular_path"] = wmaterial["map_Ks"]["values"][0]
            if "map_Ns" in wmaterial:
                self.material.properties["specular_coefficient_path"] = wmaterial["map_Ns"]["values"][0]
            if "map_d" in wmaterial:
                self.material.properties["opacity_path"] = wmaterial["map_d"]["values"][0]
            if "map_Tr" in wmaterial:
                self.material.properties["transparency_path"] = wmaterial["map_Tr"]["values"][0]
                print("[ PyGlops ] Non-standard map_Tr command found--inverted opacity map is not yet implemented.")
            if "bump" in wmaterial:
                self.material.properties["bump_path"] = wmaterial["bump"]["values"][0]
            if "disp" in wmaterial:
                self.material.properties["displacement_path"] = wmaterial["disp"]["values"][0]
        except:  # Exception:
            print("[ PyGlops ] ERROR: Could not finish " + f_name + ":")
            view_traceback()

    #def calculate_normals(self):
        ##this does not work. The call to calculate_normals is even commented out at <https://github.com/kivy/kivy/blob/master/examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015.
        #for i in range(int(len(self.indices) / (self.vertex_depth))):
            #fi = i * self.vertex_depth
            #v1i = self.indices[fi]
            #v2i = self.indices[fi + 1]
            #v3i = self.indices[fi + 2]

            #vs = self.vertices
            #p1 = [vs[v1i + c] for c in range(3)]
            #p2 = [vs[v2i + c] for c in range(3)]
            #p3 = [vs[v3i + c] for c in range(3)]

            #u,v  = [0,0,0], [0,0,0]
            #for j in range(3):
                #v[j] = p2[j] - p1[j]
                #u[j] = p3[j] - p1[j]

            #n = [0,0,0]
            #n[0] = u[1] * v[2] - u[2] * v[1]
            #n[1] = u[2] * v[0] - u[0] * v[2]
            #n[2] = u[0] * v[1] - u[1] * v[0]

            #for k in range(3):
                #self.vertices[v1i + 3 + k] = n[k]
                #self.vertices[v2i + 3 + k] = n[k]
                #self.vertices[v3i + 3 + k] = n[k]

    def emit_yaml(self, lines, min_tab_string):
        #lines.append(min_tab_string+this_name+":")
        if self.name is not None:
            lines.append(min_tab_string + "name: " + self.name)
        if self.vertices is not None:
            if add_dump_comments_enable:
                lines.append(min_tab_string+"#len(self.vertices)/self.vertex_depth:")
            lines.append(min_tab_string + "vertices_count: " + str(len(self.vertices)/self.vertex_depth))
        if self.indices is not None:
            lines.append(min_tab_string + "indices_count:" + str(len(self.indices)))
        lines.append(min_tab_string + "vertex_depth: " + str(self.vertex_depth))
        if self.vertices is not None:
            if add_dump_comments_enable:
                lines.append(min_tab_string + "#len(self.vertices):")
            lines.append(min_tab_string + "vertices_info_len: " + str(len(self.vertices)))
        lines.append(min_tab_string + "POSITION_INDEX:" + str(self.POSITION_INDEX))
        lines.append(min_tab_string + "NORMAL_INDEX:" + str(self.NORMAL_INDEX))
        lines.append(min_tab_string + "COLOR_INDEX:" + str(self.COLOR_INDEX))

        component_index = 0
        component_offset = 0

        while component_index < len(self.vertex_format):
            vertex_format_component = self.vertex_format[component_index]
            component_name_bytestring, component_len, component_type = vertex_format_component
            component_name = component_name_bytestring.decode("utf-8")
            lines.append(min_tab_string+component_name + ".len:" + str(component_len))
            lines.append(min_tab_string+component_name + ".type:" + str(component_type))
            lines.append(min_tab_string+component_name + ".index:" + str(component_index))
            lines.append(min_tab_string+component_name + ".offset:" + str(component_offset))
            component_index += 1
            component_offset += component_len

        #lines.append(min_tab_string+"POSITION_LEN:"+str(self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]))

        if add_dump_comments_enable:
            #lines.append(min_tab_string+"#VFORMAT_VECTOR_LEN_INDEX:"+str(VFORMAT_VECTOR_LEN_INDEX))
            lines.append(min_tab_string + "#len(self.vertex_format):" + str(len(self.vertex_format)))
            lines.append(min_tab_string + "#COLOR_OFFSET:" + str(self.COLOR_OFFSET))
            lines.append(min_tab_string + "#len(self.vertex_format[self.COLOR_INDEX]):" + str(len(self.vertex_format[self.COLOR_INDEX])))
        channel_count = self.vertex_format[self.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        if add_dump_comments_enable:
            lines.append(min_tab_string + "#vertex_bytes_per_pixel:" + str(channel_count))


        for k,v in sorted(self.properties.items()):
            lines.append(min_tab_string+k+": "+v)

        thisTextureFileName=self.get_texture_diffuse_path()
        if thisTextureFileName is not None:
            lines.append(min_tab_string + "get_texture_diffuse_path(): " + thisTextureFileName)

        #standard_emit_yaml(lines, min_tab_string, "vertex_info_1D", self.vertices)
        if add_dump_comments_enable:
            lines.append(min_tab_string + "#1D vertex info array, aka:")
        lines.append(min_tab_string + "vertices:")
        component_offset = 0
        vertex_actual_index = 0
        for i in range(0,len(self.vertices)):
            if add_dump_comments_enable:
                if component_offset==0:
                    lines.append(min_tab_string + tab_string + "#vertex [" + str(vertex_actual_index) + "]:")
                elif component_offset==self.COLOR_OFFSET:
                    lines.append(min_tab_string + tab_string + "#  color:")
                elif component_offset==self._NORMAL_OFFSET:
                    lines.append(min_tab_string + tab_string + "#  normal:")
                elif component_offset==self._POSITION_OFFSET:
                    lines.append(min_tab_string + tab_string + "#  position:")
                elif component_offset==self._TEXCOORD0_OFFSET:
                    lines.append(min_tab_string + tab_string + "#  texcoords0:")
                elif component_offset==self._TEXCOORD1_OFFSET:
                    lines.append(min_tab_string + tab_string + "#  texcoords1:")
            lines.append(min_tab_string + tab_string + "- " + str(self.vertices[i]))
            component_offset += 1
            if component_offset==self.vertex_depth:
                component_offset = 0
                vertex_actual_index += 1

        lines.append(min_tab_string + "indices:")
        for i in range(0,len(self.indices)):
            lines.append(min_tab_string + tab_string + "- " + str(self.indices[i]))


    def on_vertex_format_change(self):
        self.vertex_depth = 0
        for i in range(0,len(self.vertex_format)):
            self.vertex_depth += self.vertex_format[i][VFORMAT_VECTOR_LEN_INDEX]
        
        self._POSITION_OFFSET = -1
        self._NORMAL_OFFSET = -1
        self._TEXCOORD0_OFFSET = -1
        self._TEXCOORD1_OFFSET = -1
        self.COLOR_OFFSET = -1

        self.POSITION_INDEX = -1
        self.NORMAL_INDEX = -1
        self.TEXCOORD0_INDEX = -1
        self.TEXCOORD1_INDEX = -1
        self.COLOR_INDEX = -1

        #this_pyglop.vertex_depth = 0
        offset = 0
        temp_vertex = list()
        for i in range(0,len(self.vertex_format)):
            #first convert from bytestring to str
            vformat_name_lower = str(self.vertex_format[i][VFORMAT_NAME_INDEX]).lower()
            if "pos" in vformat_name_lower:
                self._POSITION_OFFSET = offset
                self.POSITION_INDEX = i
            elif "normal" in vformat_name_lower:
                self._NORMAL_OFFSET = offset
                self.NORMAL_INDEX = i
            elif ("texcoord" in vformat_name_lower) or ("tc0" in vformat_name_lower):
                if self._TEXCOORD0_OFFSET<0:
                    self._TEXCOORD0_OFFSET = offset
                    self.TEXCOORD0_INDEX = i
                elif self._TEXCOORD1_OFFSET<0 and ("tc0" not in vformat_name_lower):
                    self._TEXCOORD1_OFFSET = offset
                    self.TEXCOORD1_INDEX = i
                #else ignore since is probably the second index such as a_texcoord1
            elif "color" in vformat_name_lower:
                self.COLOR_OFFSET = offset
                self.COLOR_INDEX = i
            offset += self.vertex_format[i][VFORMAT_VECTOR_LEN_INDEX]
        if offset > self.vertex_depth:
            print("ERROR: The count of values in vertex format chunks (chunk_count:"+str(len(self.vertex_format))+"; value_count:"+str(offset)+") is greater than the vertex depth "+str(self.vertex_depth))
        elif offset != self.vertex_depth:
            print("WARNING: The count of values in vertex format chunks (chunk_count:"+str(len(self.vertex_format))+"; value_count:"+str(offset)+") does not total to vertex depth "+str(self.vertex_depth))
        participle = "(before initializing)"
        # Now you can access any vars you want (not just ones cached
        # above) like:
        # self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]

    def append_wobject(self, this_wobject, pivot_to_geometry_enable=True):
        # formerly get_glops_from_wobject formerly set_from_wobject
        # formerly import_wobject; based on _finalize_obj_data
        f_name = "append_wobject"
        if this_wobject.face_dicts is not None:
            self.source_path = this_wobject.source_path
            #from vertex_format above:
            #self.vertex_format = [
                #(b'a_position', , 'float'),  # Munshi prefers vec4 (Kivy prefers vec3)
                #(b'a_texcoord0', , 'float'),  # Munshi prefers vec4 (Kivy prefers vec2); vTexCoord0; available if enable_tex[0] is true
                #(b'a_texcoord1', , 'float'),  # Munshi prefers vec4 (Kivy prefers vec2);  available if enable_tex[1] is true
                #(b'a_color', 4, 'float'),  # vColor (diffuse color of vertex)
                #(b'a_normal', 3, 'float')  # vNormal; Munshi prefers vec3 (Kivy also prefers vec3)
                #]
            #self.on_vertex_format_change()
            IS_SELF_VFORMAT_OK = True
            if self._POSITION_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("Couldn't find name containing 'pos' or 'position' in any vertex format element (see pyglops.py PyGlop constructor)")
            if self._NORMAL_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("Couldn't find name containing 'normal' in any vertex format element (see pyglops.py PyGlop constructor)")
            if self._TEXCOORD0_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("Couldn't find name containing 'texcoord' in any vertex format element (see pyglops.py PyGlop constructor)")
            if self.COLOR_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("Couldn't find name containing 'color' in any vertex format element (see pyglops.py PyGlop constructor)")

            #vertices_offset = None
            #normals_offset = None
            #texcoords_offset = None
            #vertex_depth = 8
            #based on finish_object
        #         if self._current_object == None:
        #             return
        #
            if IS_SELF_VFORMAT_OK:
                zero_vertex = list()
                for index in range(0,self.vertex_depth):
                    zero_vertex.append(0.0)
                if (self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]>3):
                    zero_vertex[3] = 1.0
                    #NOTE: this is done since usually if len is 3, simple.glsl included with kivy converts it to vec4 appending 1.0:
                    #attribute vec3 v_pos;
                    #void main (void) {
                    #vec4(v_pos,1.0);
                #this_offset = self.COLOR_OFFSET
                channel_count = self.vertex_format[self.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
                for channel_subindex in range(0,channel_count):
                    zero_vertex[self.COLOR_OFFSET+channel_subindex] = -1.0  # -1.0 for None #TODO: asdf flag a different way (other than negative) to work with fake standard shader


                participle="accessing object from list"
                #this_wobject = self.glops[index]
                #self.name = None
                this_name = ""
                try:
                    if this_wobject.name is not None:
                        this_name = this_wobject.name
                        if self.name is None:
                            self.name = this_name
                except:
                    pass  #don't care

                try:
                    participle="processing material"
                    if this_wobject.wmaterial is not None:  # if this_wobject.properties["usemtl"] is not None:
                        self.set_textures_from_wmaterial(this_wobject.wmaterial)
                    else:
                        print("WARNING: this_wobject.wmaterial is None")
                except:
                    print("Could not finish " + participle + " in " + f_name + ": ")
                    view_traceback()

                glop_vertex_offset = 0
                if self.vertices is None:
                    self.vertices = []
                else:
                    if len(self.vertices) > 0:
                        glop_vertex_offset = len(self.vertices)  # NOTE: len(self.vertices) is #of vertices TIMES vertex depth
                        self.separable_offsets.append(glop_vertex_offset)
                        print("[ PyGlops ] appending wobject vertices to glop (" + str(self.name) + ")'s existing " + str(glop_vertex_offset) + " vertices")
                    else:
                        print("[ PyGlops ] appending wobject vertices to glop ("+str(self.name)+")'s existing list of 0 vertices")
                    #print("ERROR in " + f_name + ": existing vertices found {self.name:'"+str(this_name)+"'}")
                vertex_components = zero_vertex[:]


                source_face_index = 0
                try:
                    #if (len(self.indices)<1):
                    participle = "before detecting vertex component offsets"
                    #detecting vertex component offsets is required since indices in an obj file are sometimes relative to the first index in the FILE not the object
                    for key in this_wobject.face_dicts:
                        this_face_list = this_wobject.face_dicts[key]["faces"]
                        #TODO: implement this_wobject.face_dicts[key]["s"] which can be "on" or "off" or None
                        participle = "before processing faces"
                        dest_vertex_index = 0
                        face_count = 0
                        new_texcoord = new_tuple(self.vertex_format[self.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX])
                        if this_face_list is not None:
                            if get_verbose_enable():
                                print("[ PyGlops ] adding " + str(len(this_face_list)) + " face(s) from " + str(type(this_face_list)) + " " + key)  # debug only
                            for this_wobject_this_face in this_face_list:
                                #print("  -  # in " + key)  # debug only
                                participle = "getting face components"
                                #print("face["+str(source_face_index)+"]: "+participle)

                                #DOES triangulate faces of more than 3 vertices (connects each loose point to first vertex and previous vertex)
                                # (vertex_done_flags are no longer needed since that method is used)
                                #vertex_done_flags = list()
                                #for vertexinfo_index in range(0,len(this_wobject_this_face)):
                                #    vertex_done_flags.append(False)
                                #vertices_done_count = 0

                                #with wobjfile.py, each face is an arbitrary-length list of vertex_infos, where each vertex_info is a list containing vertex_index, texcoord_index, then normal_index, so ignore the following commented deprecated lines of code:
                                #verts =  this_wobject_this_face[0]
                                #norms = this_wobject_this_face[1]
                                #tcs = this_wobject_this_face[2]
                                #for vertexinfo_index in range(3):
                                vertexinfo_index = 0
                                source_face_vertex_count = 0
                                while vertexinfo_index<len(this_wobject_this_face):
                                    #print("vertex["+str(vertexinfo_index)+"]")
                                    vertex_info = this_wobject_this_face[vertexinfo_index]

                                    vertex_index = vertex_info[FACE_V]
                                    texcoord_index = vertex_info[FACE_TC]
                                    normal_index = vertex_info[FACE_VN]

                                    vertex = None
                                    texcoord = None
                                    normal = None


                                    participle = "getting normal components"

                                    #get normal components
                                    normal = (0.0, 0.0, 1.0)
                                    #if normals_offset is None:
                                    #    normals_offset = 1
                                    normals_offset = 0  # since wobjfile.py makes indices relative to object
                                    try:
                                        #if (normal_index is not None) and (normals_offset is not None):
                                        #    participle = "getting normal components at "+str(normal_index-normals_offset)  # str(norms[face_index]-normals_offset)
                                        #else:
                                        participle = "getting normal components at " + str(normal_index) + "-" + str(normals_offset)  # str(norms[face_index]-normals_offset)
                                        if normal_index is not None:
                                            normal = this_wobject.normals[normal_index-normals_offset]
                                        #if norms[face_index] != -1:
                                            #normal = this_wobject.normals[norms[face_index]-normals_offset]
                                    except:  # Exception as e:
                                        print("Could not finish " + participle + " for wobject named '" + this_name + "':")
                                        view_traceback()

                                    participle = "getting texture coordinate components"
                                    participle = "getting texture coordinate components at "+str(face_count)
                                    participle = "getting texture coordinate components using index "+str(face_count)
                                    #get texture coordinate components
                                    #texcoord = (0.0, 0.0)
                                    texcoord = new_texcoord[:]
                                    #if texcoords_offset is None:
                                    #    texcoords_offset = 1
                                    texcoords_offset = 0  # since wobjfile.py makes indices relative to object
                                    try:
                                        if this_wobject.texcoords is not None:
                                            #if (texcoord_index is not None) and (texcoords_offset is not None):
                                            #    participle = "getting texcoord components at "+str(texcoord_index-texcoords_offset)  # str(norms[face_index]-normals_offset)
                                            #else:
                                            participle = "getting texcoord components at " + str(texcoord_index) + "-" + str(texcoords_offset)  # str(norms[face_index]-normals_offset)

                                            if texcoord_index is not None:
                                                texcoord = this_wobject.texcoords[texcoord_index-texcoords_offset]
                                            #if tcs[face_index] != -1:
                                                #participle = "using texture coordinates at index "+str(tcs[face_index]-texcoords_offset)+" (after applying texcoords_offset:"+str(texcoords_offset)+"; Count:"+str(len(this_wobject.texcoords))+")"
                                                #texcoord = this_wobject.texcoords[tcs[face_index]-texcoords_offset]
                                        else:
                                            if get_verbose_enable():
                                                print("Warning: no texcoords found in wobject named '" + this_name + "'")
                                    except:  # Exception as e:
                                        print("Could not finish " + participle + " for wobject named '" + this_name + "':")
                                        view_traceback()

                                    participle = "getting vertex components"
                                    #if vertices_offset is None:
                                    #    vertices_offset = 1
                                    vertices_offset = 0  # since wobjfile.py makes indices relative to object
                                    #participle = "accessing face vertex "+str(verts[face_index]-vertices_offset)+" (after applying vertices_offset:"+str(vertices_offset)+"; Count:"+str(len(this_wobject.vertices))+")"
                                    participle = "accessing face vertex "+str(vertex_index)+"-"+str(vertices_offset)+" (after applying vertices_offset:"+str(vertices_offset)
                                    if (this_wobject.vertices is not None):
                                        participle += "; Count:"+str(len(this_wobject.vertices))+")"
                                    else:
                                        participle += "; this_wobject.vertices:None)"
                                    try:
                                        #v = this_wobject.vertices[verts[face_index]-vertices_offset]
                                        v = this_wobject.vertices[vertex_index-vertices_offset]
                                    except:  # Exception as e:
                                        print("[ PyGlops ] (ERROR) could not finish "+participle+" for wobject named '"+this_name+"':")
                                        view_traceback()

                                    participle = "combining components"
                                    #vertex_components = [v[0], v[1], v[2], normal[0], normal[1], normal[2], texcoord[0], 1 - texcoord[1]] #TODO: why does kivy-rotation3d version have texcoord[1] instead of 1 - texcoord[1]
                                    vertex_components = list()
                                    for i in range(0,self.vertex_depth):
                                        vertex_components.append(0.0)
                                    for element_index in range(0,3):
                                        vertex_components[self._POSITION_OFFSET+element_index] = v[element_index]
                                    if (self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]>3):
                                        vertex_components[self._POSITION_OFFSET+3] = 1.0  # non-position padding value must be 1.0 for matrix math to work correctly
                                    for element_index in range(0,3):
                                        vertex_components[self._NORMAL_OFFSET+element_index] = normal[element_index]
                                    for element_index in range(0,2):

                                        if element_index==1:
                                            vertex_components[self._TEXCOORD0_OFFSET+element_index] = 1-texcoord[element_index]
                                        else:
                                            vertex_components[self._TEXCOORD0_OFFSET+element_index] = texcoord[element_index]

                                    if len(v)>3:
                                        #use extended vertex info (color) from nonstandard obj file
                                        abs_index = 0
                                        for element_index in range(4,len(v)):
                                            vertex_components[self.COLOR_OFFSET+abs_index] = v[element_index]
                                            abs_index += 1
                                    else:
                                        #default to transparent vertex color
                                        #TODO: overlay vertex color using material color as base
                                        for element_index in range(0,4):
                                            vertex_components[self.COLOR_OFFSET+element_index] = 0.0
                                    #print("    - " + str(vertex_components))  # debug only
                                    self.vertices.extend(vertex_components)
                                    source_face_vertex_count += 1
                                    vertexinfo_index += 1
                                #end while vertexinfo_index in face

                                participle = "combining triangle indices"
                                vertexinfo_index = 0
                                relative_source_face_vertex_index = 0  #required for tracking faces with less than 3 vertices
                                face_first_vertex_dest_index = dest_vertex_index  # store first face (used for tesselation)
                                tesselated_f_count = 0
                                #example obj quad (without Texcoord) vertex_index/texcoord_index/normal_index:
                                #f 61//33 62//33 64//33 63//33
                                #face_vertex_list = list()  # in case verts are out of order, prevent tesselation from connecting wrong verts
                                while vertexinfo_index < len(this_wobject_this_face):
                                    #face_vertex_list.append(dest_vertex_index)
                                    if vertexinfo_index==2:
                                        #OK to assume dest vertices are in order, since just created them (should work even if source vertices are not in order)
                                        tri = [glop_vertex_offset+dest_vertex_index, glop_vertex_offset+dest_vertex_index+1, glop_vertex_offset+dest_vertex_index+2]
                                        self.indices.extend(tri)
                                        dest_vertex_index += 3
                                        relative_source_face_vertex_index += 3
                                        tesselated_f_count += 1
                                    elif vertexinfo_index>2:
                                        #TESSELATE MANUALLY for faces with more than 3 vertices (connect loose vertex with first vertex and previous vertex)
                                        tri = [glop_vertex_offset+face_first_vertex_dest_index, glop_vertex_offset+dest_vertex_index-1, glop_vertex_offset+dest_vertex_index]
                                        self.indices.extend(tri)
                                        dest_vertex_index += 1
                                        relative_source_face_vertex_index += 1
                                        tesselated_f_count += 1
                                    vertexinfo_index += 1

                                if (tesselated_f_count<1):
                                    print("WARNING: Face tesselated to 0 faces")
                                elif (tesselated_f_count>1):
                                    if get_verbose_enable():
                                        print("Face tesselated to " + str(tesselated_f_count) + " face(s)")

                                if relative_source_face_vertex_index<source_face_vertex_count:
                                    print("WARNING: Face has fewer than 3 vertices (problematic obj file " + str(this_wobject.source_path) + ")")
                                    dest_vertex_index += source_face_vertex_count - relative_source_face_vertex_index
                                source_face_index += 1
                        else:
                            print("WARNING: faces list in this_wobject.face_groups[" + key + "] is None in object '" + this_name + "'")
                    participle = "generating pivot point"
                    if pivot_to_geometry_enable:
                        self.transform_pivot_to_geometry()
                    #else:
                    #    print("ERROR: can't use pyglop since already has vertices (len(self.indices)>=1)")

                except:  # Exception as e:
                    #print("Could not finish "+participle+" at source_face_index "+str(source_face_index)+" in " + f_name + ": "+str(e))
                    print("Could not finish "+participle+" at source_face_index "+str(source_face_index)+" in " + f_name + ": ")
                    view_traceback()

                        #print("vertices after extending: "+str(this_wobject.vertices))
                        #print("indices after extending: "+str(this_wobject.indices))
            #         if this_wobject.mtl is not None:
            #             this_wobject.wmaterial = this_wobject.mtl.get(this_wobject.obj_material)
            #         if this_wobject.wmaterial is not None and this_wobject.wmaterial:
            #             this_wobject.set_textures_from_wmaterial(this_wobject.wmaterial)
                    #self.glops[self._current_object] = mesh
                    #mesh.calculate_normals()
                    #self.faces = []

            #         if (len(this_wobject.normals)<1):
            #             this_wobject.calculate_normals()  #this does not work. The call to calculate_normals is even commented out at <https://github.com/kivy/kivy/blob/master/examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015.
            else:
                print("ERROR in " + f_name + ": bad vertex format specified in glop, no vertices could be added")
        else:
            print("WARNING in " + f_name + ": ignoring wobject where face_groups is None (a default face group is made on load if did not exist).")
    #end def append_wobject

class PyGlopsMaterial:
    #update copy constructor if adding/changing copyable members
    properties = None
    name = None
    mtlFileName = None  # mtl file path (only if based on WMaterial of WObject)

    #region vars based on OpenGL ES 1.1
    ambient_color = None  # vec4
    diffuse_color = None  # vec4
    specular_color = None  # vec4
    emissive_color = None  # vec4
    specular_exponent = None  # float
    #endregion vars based on OpenGL ES 1.1

    def __init__(self):
        self.properties = {}
        self.ambient_color = (0.0, 0.0, 0.0, 1.0)
        self.diffuse_color = (1.0, 1.0, 1.0, 1.0)
        self.specular_color = (1.0, 1.0, 1.0, 1.0)
        self.emissive_color = (0.0, 0.0, 0.0, 1.0)
        self.specular_exponent = 1.0
        
    def new_material(self):
        return PyGlopsMaterial()

    #copy should have override in subclass that calls copy_as_subclass then adds subclass-specific values to that result
    def copy(self):
        return copy_as_subclass(self.new_material)
    
    def copy_as_subclass(self, new_material_method):
        target = new_material_method()
        
        if self.properties is not None:
            target.properties = copy.deepcopy(self.properties)
        target.name = self.name
        target.mtlFileName = self.mtlFileName
        
        target.ambient_color = self.ambient_color
        target.diffuse_color = self.diffuse_color
        target.specular_color = self.specular_color
        target.emissive_color = self.emissive_color
        target.specular_exponent = self.specular_exponent
        return target

    def emit_yaml(self, lines, min_tab_string):
        #lines.append(min_tab_string+this_name+":")
        if self.name is not None:
            lines.append(min_tab_string+"name: "+self.name)
        if self.mtlFileName is not None:
            lines.append(min_tab_string+"mtlFileName: "+self.mtlFileName)
        for k,v in sorted(self.properties.items()):
            lines.append(min_tab_string+k+": "+str(v))

#variable name ends in xyz so must be ready to be swizzled
def angles_to_angle_and_matrix(angles_list_xyz):
    result_angle_matrix = [0.0, 0.0, 0.0, 0.0]
    for axisIndex in range(len(angles_list_xyz)):
        while angles_list_xyz[axisIndex]<0:
            angles_list_xyz[axisIndex] += 360.0
        if angles_list_xyz[axisIndex] > result_angle_matrix[0]:
            result_angle_matrix[0] = angles_list_xyz[axisIndex]
    if result_angle_matrix[0] > 0:
        for axisIndex in range(len(angles_list_xyz)):
            result_angle_matrix[1+axisIndex] = angles_list_xyz[axisIndex] / result_angle_matrix[0]
    else:
        result_angle_matrix[3] = .000001
    return result_angle_matrix


def theta_radians_from_rectangular(x, y):
    theta = 0.0
    if (y != 0.0) or (x != 0.0):
        # if x == 0:
        #     if y < 0:
        #         theta = math.radians(-90)
        #     elif y > 0:
        #         theta = math.radians(90.0)
        # elif y == 0:
        #     if x < 0:
        #         theta = math.radians(180.0)
        #     elif x > 0:
        #         theta = math.radians(0.0)
        # else:
        #     theta = math.atan(y/x)
        theta = math.atan2(y, x)
    return theta


#already imported from wobjfile.py:
#def standard_emit_yaml(lines, min_tab_string, sourceList):
#    lines.append(min_tab_string+this_name+":")
#    for i in range(0,len(sourceList)):
#        lines.append(min_tab_string+"- "+str(sourceList[i]))


def new_tuple(length, fill_start=0, fill_len=-1, fill_value=1.0):
    result = None
    tmp = []
    fill_count = 0
    for i in range(0,length):
        if i>=fill_start and fill_count<fill_len:
            tmp.append(fill_value)
            fill_count += 1
        else:
            tmp.append(0.0)
    #if length==1:
        #result = tuple(0.0)
    #elif length==2:
        #result = (0.0, 0.0)
    #elif length==3:
        #result = (0.0, 0.0, 0.0)
    #elif length==4:
        #result = (0.0, 0.0, 0.0, 0.0)
    #elif length==5:
        #result = (0.0, 0.0, 0.0, 0.0, 0.0)
    #elif length==6:
        #result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    #elif length==7:
        #result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    #elif length==8:
        #result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return tuple(tmp)  # result


class PyGlopsLight:
    #region vars based on OpenGL ES 1.1
    position = None  # vec4 light position for a point/spot light or normalized dir. for a directional light
    ambient_color = None  # vec4
    diffuse_color = None  # vec4
    specular_color = None  # vec4
    spot_direction = None  # vec3
    attenuation_factors = None  # vec3
    spot_exponent = None  # float
    spot_cutoff_angle = None  # float
    compute_distance_attenuation = None  # bool
    #endregion vars based on OpenGL ES 1.1

    def __init__(self):
       self.position = (0.0, 0.0, 0.0, 0.0)
       self.ambient_color = (0.0, 0.0, 0.0, 0.0)
       self.diffuse_color = (0.0, 0.0, 0.0, 0.0)
       self.specular_color = (0.0, 0.0, 0.0, 0.0)
       self.spot_direction = (0.0, 0.0, 0.0)
       self.attenuation_factors = (0.0, 0.0, 0.0)
       self.spot_exponent = 1.0
       self.spot_cutoff_angle = 45.0
       self.compute_distance_attenuation = False



class PyGlops:
    glops = None
    materials = None
    lastUntitledMeshNumber = -1
    lastCreatedMaterial = None
    lastCreatedMesh = None
    _walkmeshes = None
    _visual_debug_enable = None
    ui = None
    camera_glop = None
    player_glop = None
    _player_glop_index = None
    prev_inbounds_camera_translate = None
    _bumper_indices = None
    _bumpable_indices = None
    _world_min_y = None
    _world_grav_acceleration = None
    last_update_s = None
    _fly_enable = None
    _camera_person_number = None
    
    
    fired_count = None

    def __init__(self, new_glop_method):
        self._visual_debug_enable = False
        self._camera_person_number = self.CAMERA_FIRST_PERSON()
        self.fired_count = 0
        self._fly_enable = False
        self._world_grav_acceleration = 9.8
        self.camera_glop = new_glop_method()
        self.camera_glop.name = "Camera"
        self._walkmeshes = []
        self.glops = []
        self.materials = []
        self._bumper_indices = []
        self._bumpable_indices = []
        
    def __str__(self):
        return str(type(self))+" named "+str(self.name)+" at "+str(self.get_location)
        
    # camera does not move automatically (you may move it yourself)
    def CAMERA_FREE(self):
        return 0
        
    # camera set to same position as player's pivot point
    def CAMERA_FIRST_PERSON(self):
        return 1
    
    # camera is from the perspective of random enemy
    def CAMERA_SECOND_PERSON(self):
        return 2
    
    # camera is behind and above player (in world axes), not rotating
    def CAMERA_THIRD_PERSON(self):
        return 3

    def _run_command(self, command, bumpable_index, bumper_index, bypass_handlers_enable=False):
        print("WARNING: _run_command should be implemented by a subclass since it requires using the graphics implementation") 
        return False
        
    def update(self):
        print("WARNING: update should be implemented by a subclass since it assumes there is a realtime game or graphics implementation") 
    #end update
    
    def get_verbose_enable(self):
        return get_verbose_enable() 
        
   # This method overrides object bump code, and gives the item to the player (mimics "obtain" event)
    # cause player to obtain the item found first by keyword, then hide the item (overrides object bump code)
    def give_item_by_keyword_to_player_number(self, player_number, keyword, allow_owned_enable=False):
        indices = get_indices_of_similar_names(keyword, allow_owned_enable=allow_owned_enable)
        result = False
        if indices is not None and len(indices)>0:
            item_glop_index = indices[0]
            result = self.give_item_by_index_to_player_number(player_number, item_glop_index, "hide")
        return result

    # This method overrides object bump code, and gives the item to the player (mimics "obtain" command).
    # pre_commands can be either None (to imply default "hide") or a string containing semicolon-separated commands that will occur before obtain
    def give_item_by_index_to_player_number(self, player_number, item_glop_index, pre_commands=None, bypass_handlers_enable=True):
        result = False
        bumpable_index = item_glop_index
        bumper_index = self.get_player_glop_index(player_number)
        if get_verbose_enable():
            print("give_item_by_index_to_player_number; item_name:"+self.glops[bumpable_index]+"; player_name:"+self.glops[bumper_index].name+"")
        if pre_commands is None:
            pre_commands = "hide"  # default behavior is to hold item in inventory invisibly
        if pre_commands is not None:
            command_list = pre_commands.split(";")
            for command_original in command_list:
                command = command_original.strip()
                if command != "obtain":
                    self._run_command(command, bumpable_index, bumper_index, bypass_handlers_enable=bypass_handlers_enable)
                else:
                    print("  warning: skipped redundant 'obtain' command in post_commands param given to give_item_by_index_to_player_number")

        self._run_command("obtain", bumpable_index, bumper_index, bypass_handlers_enable=bypass_handlers_enable)
        result = True
        return result
        
    def _run_semicolon_separated_commands(self, semicolon_separated_commands, bumpable_index, bumper_index, bypass_handlers_enable=False):
        if semicolon_separated_commands is not None:
            command_list = semicolon_separated_commands.split(";")
            self._run_commands(command_list, bumpable_index, bumper_index, bypass_handlers_enable=bypass_handlers_enable)
    
    def _run_commands(self, command_list, bumpable_index, bumper_index, bypass_handlers_enable=False):
        for command_original in command_list:
            command = command_original.strip()
            self._run_command(command, bumpable_index, bumper_index, bypass_handlers_enable=bypass_handlers_enable)

    def _run_command(self, command, bumpable_index, bumper_index, bypass_handlers_enable=False):
        if command=="hide":
            self.hide_glop(self.glops[bumpable_index])
            self.glops[bumpable_index].bump_enable = False
        elif command=="obtain":
            #first, fire the (blank) overridable event handlers:
            bumpable_name = self.glops[bumpable_index].name
            bumper_name = self.glops[bumper_index].name
            self.obtain_glop(bumpable_name, bumper_name)  # handler
            self.obtain_glop_by_index(bumpable_index, bumper_index)  # handler
            #then manually transfer the glop to the player:
            self.glops[bumpable_index].item_dict["owner"] = self.glops[bumper_index].name            
            item_event = self.glops[bumper_index].push_glop_item(self.glops[bumpable_index], bumpable_index)
            
            #process item event so selected inventory slot gets updated in case that is the found slot for the item:
            self.after_selected_item(item_event)
            if get_verbose_enable():
                print(command+" "+self.glops[bumpable_index].name)
        else:
            print("Glop named "+str(self.glops[bumpable_index].name)+" attempted an unknown glop command (in bump event): "+str(command))

    def hide_glop(self, this_glop):
        print("WARNING: hide_glop should be implemented by a sub-class since it is specific to graphics implementation")
        return False
        
    def show_glop(self, this_glop_index):
        print("WARNING: show_glop should be implemented by a sub-class since it is specific to graphics implementation")
        return False

    def after_selected_item(self, select_item_event_dict):
        name = None
        #proper_name = None
        inventory_index = None
        if select_item_event_dict is not None:
            calling_method_string = ""
            if "calling_method" in select_item_event_dict:
                calling_method_string = select_item_event_dict["calling_method"]
            if "name" in select_item_event_dict:
                name = select_item_event_dict["name"]
            else:
                print("ERROR in after_selected_item: missing name in select_item_event_dict " + calling_method_string)
            #if "proper_name" in select_item_event_dict:
            #    proper_name = select_item_event_dict["proper_name"]
            #else:
            #    print("ERROR in after_selected_item ("+calling_method_string+"): missing proper_name in select_item_event_dict")
            if "inventory_index" in select_item_event_dict:
                inventory_index = select_item_event_dict["inventory_index"]
            else:
                print("ERROR in after_selected_item ("+calling_method_string+"): missing inventory_index in select_item_event_dict")
        self.ui.set_primary_item_caption(str(inventory_index)+": "+str(name))

    def add_actor_weapon(self, glop_index, weapon_dict):
        result = False
        #item_event = self.glops[glop_index].push_glop_item(self.glops[bumpable_index], bumpable_index)
        #process item event so selected inventory slot gets updated in case obtained item ends up in it:
        #self.after_selected_item(item_event)
        #if get_verbose_enable():
        #    print(command+" "+self.glops[bumpable_index].name)
        
        if "fired_sprite_path" in weapon_dict:
            indices = self.load_obj("meshes/sprite-square.obj", pivot_to_geometry_enable=True)
        else:
            w_glop = self.new_glop()
            self.glops.append(w_glop)
            indices = [len(self.glops)-1]
            if self.glops[indices[0]] is not w_glop:
                #then address multithreading paranoia
                indices = None
                for try_i in range(len(self.glops)):
                    if self.glops[try_i] is w_glop:
                        indices = [try_i]
                        break
            if indices is not None:
                print("WARNING: added invisible " + str(type(w_glop)) + " weapon (no 'fired_sprite_path' in weapon_dict")
            else:
                print("WARNING: failed to find new invisible " + str(type(w_glop)) + " weapon (no 'fired_sprite_path' in weapon_dict")
        weapon_dict["fires_glops"] = list()
        if "name" not in weapon_dict or weapon_dict["name"] is None:
            weapon_dict["name"] = "Primary Weapon"
        if indices is not None:
            for i in range(0,len(indices)):
                weapon_dict["fires_glops"].append(self.glops[indices[i]])
                self.glops[indices[i]].set_texture_diffuse(weapon_dict["fired_sprite_path"])
                self.glops[indices[i]].look_target_glop = self.camera_glop
                item_event = self.glops[glop_index].push_item(weapon_dict)
                if (item_event is not None) and ("fit_enable" in item_event) and (item_event["fit_enable"]):
                    result = True
                    #process item event so selected inventory slot gets updated in case obtained item ends up in it:
                    self.after_selected_item(item_event)
                else:
                    if item_event is not None:
                        if "fit_enable" in item_event:
                            print("NOTICE: Nothing done for item_push since presumably, "+str(self.glops[glop_index].name)+"'s inventory was full {fit_enable: " + str(item_event["fit_enable"]+"}"))
                        else:
                            print("ERROR: Nothing done in add_actor_weapon {fit_enable: None}")
                    else:
                        print("WARNING: item_event returned by push_item was None")
                #print("add_actor_weapon: using "+str(self.glops[indices[i]].name)+" as sprite.")
            for i in range(0,len(indices)):
                self.hide_glop(self.glops[indices[i]])
        else:
            if "fired_sprite_path" in weapon_dict:
                print("ERROR: got 0 objects from fired_sprite_path '"+str(weapon_dict["fired_sprite_path"]+"'"))
            else:
                print("ERROR: could not add invisible weapon to self.glops")
            
            
        #print("add_actor_weapon OK")
        return result

    def _internal_bump_glop(self, bumpable_index, bumper_index):
        bumpable_name = self.glops[bumpable_index].name
        bumper_name = self.glops[bumper_index].name
        #result =
        self.bump_glop(bumpable_name, bumper_name)
        #if result is not None:
            #if "bumpable_name" in result:
            #    bumpable_name = result["bumpable_name"]
            #if "bumper_name" in result:
            #    bumper_name = result["bumper_name"]

        #if bumpable_name is not None and bumper_name is not None:
        if self.glops[bumpable_index].item_dict is not None:
            if "bump" in self.glops[bumpable_index].item_dict:
                self.glops[bumpable_index].is_out_of_range = False  #prevents repeated bumping until out of range again
                if self.glops[bumpable_index].bump_enable:
                    if self.glops[bumpable_index].item_dict["bump"] is not None:
                        self._run_semicolon_separated_commands(self.glops[bumpable_index].item_dict["bump"], bumpable_index, bumper_index);
                        commands = self.glops[bumpable_index].item_dict["bump"].split(";")
                        for command in commands:
                            command = command.strip()
                            print("  bump "+self.glops[bumpable_index].name+": "+command+" by "+self.glops[bumper_index].name)
                            self._run_command(command, bumpable_index, bumper_index)
                    else:
                        print("[ PyGlops ] self.glops[bumpable_index].item_dict['bump'] is None")
            else:
                print("[ PyGlops ] self.glops[bumpable_index].item_dict does not contain 'bump'")
        elif self.glops[bumpable_index].projectile_dict is not None:
            #print("  this_distance: "+str(distance))
            if self.glops[bumpable_index].projectile_dict is not None:
                self.attacked_glop(bumper_index, self.glops[bumpable_index].projectile_dict["owner_index"], self.glops[bumpable_index].projectile_dict)
                self.glops[bumpable_index].bump_enable = False
            else:
                pass
                #print("bumper:"+str( (self.glops[bumper_index]._translate_instruction.x, self.glops[bumper_index]._translate_instruction.y, self.glops[bumper_index]._translate_instruction.z) ) +
                #      "; bumped:"+str( (self.glops[bumpable_index]._translate_instruction.x, self.glops[bumpable_index]._translate_instruction.y, self.glops[bumpable_index]._translate_instruction.z) ))
            #if "bump" in self.glops[bumpable_index].item_dict:
            #NOTE ignore self.glops[bumpable_index].is_out_of_range
            # since firing at point blank range is ok.
            #print("[ debug only ] projectile bumped by object " + str(bumper_name))
            #print("[ debug only ]    hit_radius:" + str(self.glops[bumper_index].hit_radius))
            #if self.glops[bumper_index].hitbox is not None:
            #    print("[ debug only ]   hitbox: " + self.glops[bumper_index].hitbox.to_string())
            #else:
            #    print("self.glops[bumpable_index].item_dict does not contain 'bump'")
        else:
            print("[ PyGlops] bumped object '" + \
                  str(self.glops[bumpable_index].name) + \
                  "' is not an item")
    
    def get_player_glop_index(self, player_number):
        result = None
        if self._player_glop_index is not None:
            #TODO: check player_number instead
            result = self._player_glop_index
        else:
            if self.player_glop is not None:
                for i in range(0, len(self.glops)):
                    #TODO: check player_number instead
                    if self.glops[i] is self.player_glop:
                        result = i
                        self._player_glop_index = i
                        print("[ PyGlops ] WARNING: " + \
                              "player_glop_index was not set (but" + \
                              "player_glop found in glops) so now is.")
                        break
        return result

    def emit_yaml(self, lines, min_tab_string):
        #lines.append(min_tab_string+this_name+":")
        lines.append(min_tab_string+"glops:")
        for i in range(0,len(self.glops)):
            lines.append(min_tab_string+tab_string+"-")
            self.glops[i].emit_yaml(lines, min_tab_string+tab_string+tab_string)
        lines.append(min_tab_string+"materials:")
        for i in range(0,len(self.materials)):
            lines.append(min_tab_string+tab_string+"-")
            self.materials[i].emit_yaml(lines, min_tab_string+tab_string+tab_string)

    def display_explosion(self, pos, radius, attacked_index, weapon_dict):
        print("[ PyGlops ] subclass of subclass may implement display_explosion" + \
            " (and check for None before using variables other than pos)")

    def explode_glop_by_index(self, index, weapon_dict=None):
        print("[ PyGlops ] subclass should implement display_explosion" + \
            " (and check for None before using variables other than pos)")

    def set_camera_mode(self, person_number):
        self._camera_person_number = person_number

    def set_as_actor_by_index(self, index, template_dict):
        #result = False
        if index is not None:
            if index>=0:
                if index<len(self.glops):
                    actor_dict = self.glops[index].deepcopy_with_my_type(template_dict)
                    self.glops[index].actor_dict = actor_dict
                    if self.glops[index].hit_radius is None:
                        if "hit_radius" in actor_dict:
                            self.glops[index].hit_radius = actor_dict["hit_radius"]
                        else:
                            self.glops[index].hit_radius = .5
                    if "target_index" not in self.glops[index].actor_dict:
                        self.glops[index].actor_dict["target_index"] = None
                    if "moveto_index" not in self.glops[index].actor_dict:
                        self.glops[index].actor_dict["moveto_index"] = None
                    if "target_pos" not in self.glops[index].actor_dict:
                        self.glops[index].actor_dict["target_pos"] = None
                    if "walk_units_per_second" not in self.glops[index].actor_dict:
                        self.glops[index].actor_dict["walk_units_per_second"] = 1.0
                            
                    self.glops[index].calculate_hit_range()
                    self._bumper_indices.append(index)
                    self.glops[index].bump_enable = True
                    print("[ PyGlops ] Set "+str(index)+" as bumper")
                    if self.glops[index].hitbox is None:
                        print("  hitbox: None")
                    else:
                        print("  hitbox: "+self.glops[index].hitbox.to_string())
                else:
                    print("[ PyGlops ] ERROR in set_as_actor_by_index: index "+str(index)+" is out of range")
            else:
                print("[ PyGlops ] ERROR in set_as_actor_by_index: index is "+str(index))
        else:
            print("[ PyGlops ] ERROR in set_as_actor_by_index: index is None")
        #return result

    #always reimplement this so the camera is correct subclass 
    def new_glop(self):
        print("[ PyGlops ] ERROR: new_glop for PyGlop should never be used")
        return PyGlop()

    def set_fly(self, fly_enable):
        if fly_enable==True:
            self._fly_enable = True
        else:
            self._fly_enable = False

    def create_material(self):
        return PyGlopsMaterial()

    def getMeshByName(self, name):
        result = None
        if name is not None:
            if len(self.glops)>0:
                for index in range(0,len(self.glops)):
                    if name==self.glops[index].name:
                        result=self.glops[index]
        return result

    def get_glop_list_from_obj(self, source_path, new_glop_method, pivot_to_geometry_enable=True):  # load_obj(self, source_path): #TODO: ? swapyz=False):
        participle = "(before initializing)"
        linePlus1 = 1
        #firstMeshIndex = len(self.glops)
        results = None
        try:
            #self.lastCreatedMesh = None
            participle = "checking path"
            if os.path.exists(source_path):
                results = []  # create now, so that if None, that means source_path didn't exist
                participle = "setting up WObjFile"
                this_objfile = WObjFile()
                participle = "loading WObjFile"
                this_objfile.load(source_path)
                if this_objfile.wobjects is not None:
                    if len(this_objfile.wobjects)>0:
                        #for i in range(0,len(this_objfile.wobjects)):
                        for key in this_objfile.wobjects:
                            participle = "getting wobject"
                            this_wobject = this_objfile.wobjects[key]
                            if this_wobject is not None:
                                participle = "converting wobject..."
                                this_pyglop = new_glop_method()
                                this_pyglop.append_wobject(this_wobject, pivot_to_geometry_enable=pivot_to_geometry_enable)
                                if this_pyglop is not None:
                                    participle = "appending pyglop to scene"
                                    #if results is None:
                                    #    results = list()
                                    results.append(this_pyglop)
                                    if get_verbose_enable():
                                        if this_pyglop.name is not None:
                                            print("appended glop named '"+this_pyglop.name+"'")
                                        else:
                                            print("appended glop {name:None}")
                                else:
                                    print("ERROR: this_pyglop is None after converting from wobject")
                            else:
                                print("ERROR: this_wobject is None (object " + str(i) + " from '" + source_path + "'")
                                
                    else:
                        print("ERROR: 0 wobjects could be read from '"+source_path+"'")
                else:
                    print("ERROR: 0 wobjects could be read from '"+source_path+"'")
            else:
                print("ERROR: file '"+str(source_path)+"' not found")
        except:  # Exception as e:
            #print("Could not finish a wobject in load_obj while "+participle+" on line "+str(linePlus1)+": "+str(e))
            print("Could not finish a wobject in load_obj while "+participle+" on line "+str(linePlus1)+":")
            view_traceback()
        return results

    def axis_index_to_string(self,index):
        result = "unknown axis"
        if (index==0):
            result = "x"
        elif (index==1):
            result = "y"
        elif (index==2):
            result = "z"
        return result

    def set_as_item(self, glop_name, template_dict, pivot_to_geometry_enable=False):
        result = False
        if glop_name is not None:
            for i in range(0,len(self.glops)):
                if self.glops[i].name == glop_name:
                    return self.set_as_item_by_index(i, template_dict, pivot_to_geometry_enable=pivot_to_geometry_enable)
                    break

    def add_bump_sound_by_index(self, i, path):
        if path not in self.glops[i].bump_sound_paths:
            self.glops[i].bump_sound_paths.append(path)

    def set_as_item_by_index(self, i, template_dict, pivot_to_geometry_enable=False):
        result = False
        item_dict = self.glops[i].deepcopy_with_my_type(template_dict)  #prevents every item template from being the one
        self.glops[i].item_dict = item_dict
        self.glops[i].item_dict["glop_name"] = self.glops[i].name
        self.glops[i].item_dict["glop_index"] = i
        self.glops[i].bump_enable = True
        self.glops[i].is_out_of_range = True  # allows item to be obtained instantly at start of main event loop
        self.glops[i].hit_radius = 0.1
        if pivot_to_geometry_enable:
            self.glops[i].transform_pivot_to_geometry()

        this_glop = self.glops[i]
        vertex_count = int(len(this_glop.vertices)/this_glop.vertex_depth)
        v_offset = 0
        min_y = None
        for v_number in range(0, vertex_count):
            if min_y is None or this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1] < min_y:
                min_y = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1]
            v_offset += this_glop.vertex_depth
        if min_y is not None:
            self.glops[i].hit_radius = min_y
            if self.glops[i].hit_radius < 0.0:
                self.glops[i].hit_radius = 0.0 - self.glops[i].hit_radius
        else:
            print("ERROR: could not read any y values from glop named "+str(this_glop.name))
        #self.glops[i].hit_radius = 1.0
        self._bumpable_indices.append(i)
        return result

    def use_selected(self, user_glop):
        f_name = "use_selected"
        if user_glop is not None:
            if user_glop.properties is not None:
                if "inventory_items" in user_glop.properties:
                    if "inventory_index" in user_glop.properties:
                        if user_glop.properties["inventory_index"] > -1:
                            try:
                                if get_verbose_enable():
                                    print("[ PyGlops ] (verbose message) " + f_name + ": using item in slot " + str(user_glop.properties['inventory_index']))
                                user_glop.properties["inventory_items"][user_glop.properties["inventory_index"]]
                                this_item = user_glop.properties["inventory_items"][user_glop.properties["inventory_index"]]
                                glop_index = None
                                item_glop = None
                                if "glop_index" in this_item:
                                    glop_index = this_item["glop_index"]
                                    if glop_index is not None:
                                        item_glop = self.glops[glop_index]
                                if item_glop is not None:
                                    if item_glop.item_dict is not None:
                                        if "use" in item_glop.item_dict:
                                            is_ready = True
                                            if "cooldown" in item_glop.item_dict:
                                                is_ready = False
                                                if ("RUNTIME_last_used_time" not in item_glop.item_dict) or (time.time() - item_glop.item_dict["RUNTIME_last_used_time"] >= item_glop.item_dict["cooldown"]):
                                                    if ("RUNTIME_last_used_time" in item_glop.item_dict):
                                                        is_ready = True
                                                    #else Don't assume cooled down when obtained, otherwise rapid firing items will be allowed
                                                    item_glop.item_dict["RUNTIME_last_used_time"] = time.time()
                                            if is_ready:
                                                if "use_sound" in item_glop.item_dict:
                                                    self.play_sound(item_glop.item_dict["use_sound"])
                                                print(item_glop.item_dict["use"]+" "+item_glop.name)
                                                if "throw_" in item_glop.item_dict["use"]:  # such as item_dict["throw_arc"]
                                                    if "as_projectile" in item_glop.item_dict:
                                                        item_glop.projectile_dict = item_glop.item_dict["as_projectile"]
                                                        item_glop.projectile_dict["owner"] = user_glop.name
                                                        item_glop.projectile_dict["owner_index"] = user_glop.index
                                                    if "owner" in item_glop.item_dict:
                                                        del item_glop.item_dict["owner"]  # ok since still in projectile_dict if matters
                                                    #or useless_string = my_dict.pop('key', None)  # where None causes to return None instead of throwing KeyError if not found
                                                    self.glops[item_glop.item_dict["glop_index"]].physics_enable = True
                                                    throw_speed = 1.0 # meters/sec
                                                    try:
                                                        x_angle = user_glop._rotate_instruction_x.angle + math.radians(30)
                                                        if x_angle > math.radians(90):
                                                            x_angle = math.radians(90)
                                                        self.glops[item_glop.item_dict["glop_index"]].y_velocity = throw_speed * math.sin(x_angle)
                                                        horizontal_throw_speed = throw_speed * math.cos(x_angle)
                                                        self.glops[item_glop.item_dict["glop_index"]].x_velocity = horizontal_throw_speed * math.cos(user_glop._rotate_instruction_y.angle)
                                                        self.glops[item_glop.item_dict["glop_index"]].z_velocity = horizontal_throw_speed * math.sin(user_glop._rotate_instruction_y.angle)

                                                    except:
                                                        self.glops[item_glop.item_dict["glop_index"]].x_velocity = 0
                                                        self.glops[item_glop.item_dict["glop_index"]].z_velocity = 0
                                                        print("Could not finish getting throw x,,z values")
                                                        view_traceback()

                                                    self.glops[item_glop.item_dict["glop_index"]].is_out_of_range = False
                                                    self.glops[item_glop.item_dict["glop_index"]].bump_enable = True
                                                    event_dict = user_glop.pop_glop_item(user_glop.properties["inventory_index"])
                                                    self.after_selected_item(event_dict)
                                                    item_glop.visible_enable = True
                                                    item_glop._translate_instruction.x = user_glop._translate_instruction.x
                                                    item_glop._translate_instruction.y = user_glop._translate_instruction.y + user_glop.eye_height
                                                    item_glop._translate_instruction.z = user_glop._translate_instruction.z
                                                    self.show_glop(glop_index)  # formerly added mesh manually (when this method was in KivyGlops)
                                            else:
                                                msg = "[ PyGlops ] item is not ready"
                                                if "cooldown" in item_glop.item_dict:
                                                    msg += " (cooldown in " + str(item_glop.item_dict["cooldown"] - (time.time() - item_glop.item_dict["RUNTIME_last_used_time"]))
                                                print(msg)
                                        else:
                                            print(item_glop.name+" has no use.")
                                    else:
                                        print("[ PyGlops ] ERROR: tried to use a glop that is not an item (this should not be in "+str(user_glop.name)+"'s inventory)")
                                elif "fire_type" in this_item:
                                    if this_item["fire_type"] != "throw_linear":
                                        print("[ PyGlops ] WARNING: "+this_item["fire_type"]+" not implemented, so using throw_linear")
                                    weapon_dict = this_item
                                    favorite_pivot = None
                                    
                                    for fires_glop in weapon_dict["fires_glops"]:
                                        if "subscript" not in weapon_dict:
                                            weapon_dict["subscript"] = 0
                                        fired_glop = fires_glop.copy_as_mesh_instance()
                                        fired_glop.name = "fired[" + str(self.fired_count) + "]"
                                        fired_glop.bump_enable = True
                                        fired_glop.projectile_dict = fired_glop.deepcopy_with_my_type(weapon_dict)
                                        fired_glop.projectile_dict["owner"] = user_glop.name
                                        fired_glop.projectile_dict["owner_index"] = user_glop.index
                                        if favorite_pivot is None:
                                            #favorite_pivot = [0.0, 0.0, 0.0]
                                            favorite_pivot = (fired_glop._translate_instruction.x, fired_glop._translate_instruction.y, fired_glop._translate_instruction.z)
                                        fired_glop._translate_instruction.x += fired_glop._translate_instruction.x - favorite_pivot[0]
                                        fired_glop._translate_instruction.y += fired_glop._translate_instruction.y - favorite_pivot[1]
                                        fired_glop._translate_instruction.z += fired_glop._translate_instruction.z - favorite_pivot[2]
                                        fired_glop._translate_instruction.x = user_glop._translate_instruction.x
                                        fired_glop._translate_instruction.y = user_glop._translate_instruction.y
                                        fired_glop._translate_instruction.z = user_glop._translate_instruction.z
                                        fired_glop.name = fires_glop.name + "." + str(weapon_dict["subscript"])
                                        projectile_speed = 1.0
                                        if "projectile_speed" in weapon_dict:
                                            projectile_speed = weapon_dict["projectile_speed"]
                                        x_off, z_off = get_rect_from_polar_rad(projectile_speed, user_glop._rotate_instruction_y.angle)
                                        fired_glop.x_velocity = x_off
                                        fired_glop.z_velocity = z_off
                                        x_off, y_off = get_rect_from_polar_rad(projectile_speed, user_glop._rotate_instruction_x.angle)
                                        fired_glop.y_velocity = y_off
                                        #print("projectile velocity x,y,z:"+str((fired_glop.x_velocity, fired_glop.y_velocity, fired_glop.z_velocity)))
                                        fired_glop.visible_enable = True
                                        self.glops.append(fired_glop)
                                        fired_glop_index = None
                                        # Check identity for multithreading paranoia:
                                        if self.glops[len(self.glops) - 1] is fired_glop:
                                            fired_glop_index = len(self.glops) - 1
                                        else:
                                            fired_glop_index = self.index_of_mesh(fired_glop.name)
                                        fired_glop.index = fired_glop_index
                                        fired_glop.physics_enable = True
                                        fired_glop.bump_enable = True
                                        self.show_glop(fired_glop_index)  # formerly added mesh to scene in framework-specific way (when this method was in KivyGlops)
                                        weapon_dict["subscript"] += 1
                                        #print("FIRED self._bumpable_indices: " + str(self._bumpable_indices))
                                        self._bumpable_indices.append(len(self.glops)-1)
                                        #start off a ways away:
                                        fired_glop._translate_instruction.x += fired_glop.x_velocity*2
                                        fired_glop._translate_instruction.y += fired_glop.y_velocity*2
                                        fired_glop._translate_instruction.z += fired_glop.z_velocity*2
                                        fired_glop._translate_instruction.y -= user_glop.eye_height/2
                                        self.fired_count += 1
                                        #print("[ debug only ] bumpers:")
                                        #for b_i in self._bumper_indices:  # debug only
                                        #    print("[ debug only ]   - ")
                                        #    print("[ debug only ]     name: " + str(self.glops[b_i].name))
                                        #    print("[ debug only ]     _translate_instruction: " + str(self.glops[b_i]._translate_instruction.xyz))
                            except:
                                print("[ PyGlops ] ERROR: Could not finish use_selected:")
                                print("  user_glop.name:"+str(user_glop.name))
                                print('  user_glop.properties["inventory_index"]:'+str(user_glop.properties["inventory_index"]))
                                print('  len(user_glop.properties["inventory_items"]):'+str(len(user_glop.properties["inventory_items"])))
                                print("  traceback: '''")
                                view_traceback()
                                print("  '''")
                        else:
                            print("[ PyGlops ] ERROR in " + f_name + ": user_glop.properties['inventory_index'] is < 0")
                    else:
                        print("[ PyGlops ] ERROR in " + f_name + ": user_glop.properties['inventory_index'] is not present (actor tried to use item before inventory was ready)")
                else:
                    print("[ PyGlops ] ERROR in " + f_name + ": user_glop.properties['inventory_items'] is None (actor without inventory tried to use item)")
            else:
                print("[ PyGlops ] ERROR in " + f_name + ": user_glop.properties is None (non-actor tried to use item)")
        else:
            print("[ PyGlops ] ERROR in " + f_name + ": user_glop is None")


    def load_glops(self):
        print("[ PyGlops ] WARNING: program-specific subclass of a framework-specific subclass of PyGlops should implement load_glops (and usually update_glops which will be called before each frame is drawn)")

    def update_glops(self):
        # subclass of KivyGlopsWindow can implement load_glops
        #print("NOTICE: subclass of PyGlops can implement update_glops")
        pass

    #def get_player_glop_index(self, player_number):
    #    result = self.get_player_glop_index(self, player_number)

    def killed_glop(self, index, weapon_dict):
        pass
        #print("[ PyGlops ] subclass can implement killed_glop")

    def kill_glop_by_index(self, index, weapon_dict=None):
        self.killed_glop(index, weapon_dict)
        self.hide_glop(self.glops[index])
        self.glops[index].bump_enable = False
        
    def bump_glop(self, bumpable_name, bumper_name):
        return None

    def attacked_glop(self, attacked_index, attacker_index, weapon_dict):
        print("[ PyGlops ] attacked_glop should be implemented by " + \
              "the subclass which would know how to damage or " + \
              "calculate defense or other properties")
        #trivial example:
        #self.glops[attacked_index].actor_dict["hp"] -= weapon_dict["hit_damage"]
        #if self.glops[attacked_index].actor_dict["hp"] <= 0:
        #    self.explode_glop_by_index(attacked_index)
        return None

    def obtain_glop(self, bumpable_name, bumper_name):
        return None

    def obtain_glop_by_index(self, bumpable_index, bumper_index):
        return None

    def get_nearest_walkmesh_vec3_using_xz(self, pt):
        result = None
        closest_distance = None
        poly_sides_count = 3
        #corners = list()
        #for i in range(0,poly_sides_count):
        #    corners.append( (0.0, 0.0, 0.0) )
        for this_glop in self._walkmeshes:
            face_i = 0
            indices_count = len(this_glop.indices)
            while (face_i<indices_count):
                v_offset = this_glop.indices[face_i]*this_glop.vertex_depth
                a_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                v_offset = this_glop.indices[face_i+1]*this_glop.vertex_depth
                b_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                v_offset = this_glop.indices[face_i+2]*this_glop.vertex_depth
                c_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                #side_a_distance = get_distance_vec3_xz(pt, a_vertex, b_vertex)
                #side_b_distance = get_distance_vec3_xz(pt, b_vertex, c_vertex)
                #side_c_distance = get_distance_vec3_xz(pt, c_vertex, a_vertex)
                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, a_vertex, b_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                tri_distance = this_distance
                tri_point = this_point

                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, b_vertex, c_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, c_vertex, a_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                if (closest_distance is None) or (tri_distance<closest_distance):
                    result = tri_point[0], tri_point[1], tri_point[2]  # ok to return y since already swizzled (get_nearest_vec3_on_vec3line_using_xz copies source's y to return's y)
                    closest_distance = tri_distance
                face_i += poly_sides_count
        return result

    def get_nearest_walkmesh_vertex_using_xz(self, pt):
        result = None
        second_nearest_pt = None
        for this_glop in self._walkmeshes:
            X_i = this_glop._POSITION_OFFSET + 0
            Y_i = this_glop._POSITION_OFFSET + 1
            Z_i = this_glop._POSITION_OFFSET + 2
            X_abs_i = X_i
            Y_abs_i = Y_i
            Z_abs_i = Z_i
            v_len = len(this_glop.vertices)
            distance_min = None
            while X_abs_i < v_len:
                distance = math.sqrt( (pt[0]-this_glop.vertices[X_abs_i+0])**2 + (pt[2]-this_glop.vertices[X_abs_i+2])**2 )
                if (result is None) or (distance_min) is None or (distance<distance_min):
                    #if result is not None:
                        #second_nearest_pt = result[0],result[1],result[2]
                    result = this_glop.vertices[X_abs_i+0], this_glop.vertices[X_abs_i+1], this_glop.vertices[X_abs_i+2]
                    distance_min = distance
                X_abs_i += this_glop.vertex_depth

            #DOESN'T WORK since second_nearest_pt may not be on edge
            #if second_nearest_pt is not None:
            #    distance1 = get_distance_vec3_xz(pt, result)
            #    distance2 = get_distance_vec3_xz(pt, second_nearest_pt)
            #    distance_total=distance1+distance2
            #    distance1_weight = distance1/distance_total
            #    distance2_weight = distance2/distance_total
            #    result = result[0]*distance1_weight+second_nearest_pt[0]*distance2_weight, result[1]*distance1_weight+second_nearest_pt[1]*distance2_weight, result[2]*distance1_weight+second_nearest_pt[2]*distance2_weight
                #TODO: use second_nearest_pt to get nearest location along the edge instead of warping to a vertex
        return result

    def is_in_any_walkmesh_xz(self, check_vec3):
        return get_container_walkmesh_and_poly_index_xz(check_vec3) is not None

    def get_container_walkmesh_and_poly_index_xz(self, check_vec3):
        result = None
        X_i = 0
        second_i = 2  # actually z since ignoring y
        check_vec2 = check_vec3[X_i], check_vec3[second_i]
        walkmesh_i = 0
        while walkmesh_i < len(self._walkmeshes):
            this_glop = self._walkmeshes[walkmesh_i]
            X_i = this_glop._POSITION_OFFSET + 0
            second_i = this_glop._POSITION_OFFSET + 2
            poly_side_count = 3
            poly_count = int(len(this_glop.indices)/poly_side_count)
            poly_offset = 0
            for poly_index in range(0,poly_count):
                if (  is_in_triangle_vec2( check_vec2, (this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+second_i]), (this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+second_i]), (this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+second_i]) )  ):
                    result = dict()
                    result["walkmesh_index"] = walkmesh_i
                    result["polygon_offset"] = poly_offset
                    break
                poly_offset += poly_side_count
            walkmesh_i += 1
        return result

    def use_walkmesh(self, name, hide=True):
        print("[ PyGlops ] ERROR: use_walkmesh should be implemented in a subclass since it is dependent on display method")
        return False

    def get_similar_names(self, partial_name):
        results = None
        checked_count = 0
        if partial_name is not None and len(partial_name)>0:
            partial_name_lower = partial_name.lower()
            results = list()
            for this_glop in self.glops:
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.name is not None:
                    if partial_name_lower in this_glop.name.lower():
                        results.append(this_glop.name)
                    #else:
                        #print("[ PyGlops ] (debug only in get_similar_names): name "+str(this_glop.name)+" does not contain "+partial_name)
                else:
                    print("ERROR in get_similar_names: a glop was None")
        else:
            print("ERROR in get_similar_names: tried to search for blank partial_name")
        #print("checked "+str(checked_count))
        return results

    def get_indices_by_source_path(self, source_path):
        results = None
        checked_count = 0
        if source_path is not None and len(source_path)>0:
            results = list()
            for index in range(0,len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.source_path is not None:
                    if source_path == this_glop.source_path or \
                       source_path == this_glop.original_path:
                        results.append(index)
        #print("checked "+str(checked_count))
        return results


    def get_indices_of_similar_names(self, partial_name,
                                     allow_owned_enable=True):
        results = None
        checked_count = 0
        if partial_name is not None and len(partial_name)>0:
            partial_name_lower = partial_name.lower()
            results = list()
            for index in range(0,len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.name is not None and \
                   ( allow_owned_enable or \
                     this_glop.item_dict is None or \
                     "owner" not in this_glop.item_dict ):
                    if partial_name_lower in this_glop.name.lower():
                        results.append(index)
        #print("checked "+str(checked_count))
        return results

    #Find list of similar names slightly faster than multiple calls
    # to get_indices_of_similar_names: the more matches earlier in
    # the given partial_names array, the faster this method returns
    # (therefore overlapping sets are sacrificed).
    #Returns: list that is always the length of partial_names + 1,
    # as each item is a list of indicies where name contains the
    # corresponding partial name, except last index which is all others.
    def get_index_lists_by_similar_names(self, partial_names, allow_owned_enable=True):
        results = None
        checked_count = 0
        if len(partial_names)>0:
            results_len = len(partial_names)
            results = [list() for i in range(results_len + 1)]
            for index in range(0,len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                match_indices = [None]*results_len
                match = False
                for i in range(0, results_len):
                    partial_name_lower = partial_names[i].lower()
                    if this_glop.name is not None and \
                       ( allow_owned_enable or \
                         this_glop.item_dict is None or \
                         "owner" not in this_glop.item_dict ):
                        if partial_name_lower in this_glop.name.lower():
                            results[i].append(index)
                            match = True
                            break
                if not match:
                    results[results_len].append(index)
        #print("checked "+str(checked_count))
        return results


    def set_world_boundary_by_object(self, thisGlopsMesh, use_x, use_y, use_z):
        self._world_cube = thisGlopsMesh
        if (self._world_cube is not None):
            self.world_boundary_min = [self._world_cube.get_min_x(), None, self._world_cube.get_min_z()]
            self.world_boundary_max = [self._world_cube.get_max_x(), None, self._world_cube.get_max_z()]

            for axis_index in range(0,3):
                if self.world_boundary_min[axis_index] is not None:
                    self.world_boundary_min[axis_index] += self.projection_near + 0.1
                if self.world_boundary_max[axis_index] is not None:
                    self.world_boundary_max[axis_index] -= self.projection_near + 0.1
        else:
            self.world_boundary_min = [None,None,None]
            self.world_boundary_max = [None,None,None]



    def print_location(self):
        if get_verbose_enable():
            Logger.debug("self.camera_walk_units_per_second:"+str(self.camera_walk_units_per_second)+"; location:"+str( (self.camera_glop._translate_instruction.x, self.camera_glop._translate_instruction.y, self.camera_glop._translate_instruction.z) ))

    #def get_keycode(self, key_name):
    #    print("ERROR: get_keycode must be implemented by the framework-specific subclass")
    #    return None

    #def get_pressed(self, key_name):
    #    return self.player1_controller.get_pressed(self.ui.get_keycode(key_name))

    def select_mesh_by_index(self, index):
        glops_count = len(self.glops)
        if (index>=glops_count):
            index=0
        if get_verbose_enable():
            Logger.debug("trying to select index "+str(index)+" (count is "+str(glops_count)+")...")
        if (glops_count > 0):
            self.selected_glop_index = index
            self.selected_glop = self.glops[index]
        else:
            self.selected_glop = None
            self.selected_glop_index = None
    
    def index_of_mesh(self, name):
        result = -1
        name_lower = name.lower()
        for i in range(0,len(self.glops)):
            source_name = None
            source_name_lower = None
            if self.glops[i].source_path is not None:
                source_name = os.path.basename(os.path.normpath(self.glops[i].source_path))
                source_name_lower = source_name.lower()
            if self.glops[i].name==name:
                result = i
                break
            elif self.glops[i].name.lower()==name_lower:
                print("WARNING: object with different capitalization was not considered a match: " + self.glops[i].name)
            elif (source_name_lower is not None) and (source_name_lower==name_lower
                  or os.path.splitext(source_name_lower)[0]==name_lower):
                result = i
                name_msg = "filename: '" + source_name + "'"
                if os.path.splitext(source_name_lower)[0]==name_lower:
                    name_msg = "part of filename: '" + os.path.splitext(source_name)[0] + "'"
                print("WARNING: mesh was named '" + self.glops[i].name + "' but found using " + name_msg)
                if (i+1<len(self.glops)):
                    for j in range(i+1,len(self.glops)):
                        sub_source_name_lower = None
                        if self.glops[j].source_path is not None:
                            sub_source_name_lower = os.path.basename(os.path.normpath(self.glops[i].source_path)).lower()
                        if (source_name_lower is not None) and (source_name_lower==name_lower
                            or os.path.splitext(source_name_lower)[0]==name_lower):
                            print("  * could also be mesh named '" + self.glops[j].name+"'")
                break
        return result
    
    def select_mesh_by_name(self, name):
        found = False
        index = self.index_of_mesh(name)
        if index > -1:
            self.select_mesh_by_index(index)
            found = True
        return found
