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

#references:
#kivy-trackball objloader (version with no MTL loader) by nskrypnik
#objloader from kivy-rotation3d (version with placeholder mtl loader) by nskrypnik

#TODO:
#-remove resource_find but still make able to find mtl file under Kivy somehow

from kivy.resources import resource_find
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
    return angle_trunc(atan2(deltaY, deltaX))

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
    kEpsilon = 1.0E-14 # adjust to suit.  If you use floats, you'll probably want something like 1E-7f
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
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1]);
#PointInTriangle and sign are from http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle
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
    det = (p2[2] - p3[2]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[2] - p3[2]);

    l1 = ((p2[2] - p3[2]) * (x - p3[0]) + (p3[0] - p2[0]) * (z - p3[2])) / det;
    l2 = ((p3[2] - p1[2]) * (x - p3[0]) + (p1[0] - p3[0]) * (z - p3[2])) / det;
    l3 = 1.0 - l1 - l2;

    return l1 * p1[1] + l2 * p2[1] + l3 * p3[1];

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
    s = 1/(2*Area)*(a_vec2[1]*c_vec2[0] - a_vec2[0]*c_vec2[1] + (c_vec2[1] - a_vec2[1])*check_vec2[0] + (a_vec2[0] - c_vec2[0])*check_vec2[1])
    t = 1/(2*Area)*(a_vec2[0]*b_vec2[1] - a_vec2[1]*b_vec2[0] + (a_vec2[1] - b_vec2[1])*check_vec2[0] + (b_vec2[0] - a_vec2[0])*check_vec2[1])
#    #TODO: fix situation where it fails when clockwise (see discussion at http://stackoverflow.com/questions/2049582/how-to-determine-a-point-in-a-2d-triangle )
    return  s>kEpsilon and t>kEpsilon and 1-s-t>kEpsilon

#class ItemData:  #changed to dict
#    name = None
#    passive_bumper_command = None
#    health_ratio = None
    
#    def __init__(self, bump="obtain"):
#        health_ratio = 1.0
#        passive_bumper_command = bump

# PyGlop defines a single OpenGL-ready object. PyGlops should be used for importing, since one mesh file (such as obj) can contain several meshes. PyGlops handles the 3D scene.
class PyGlop:
    name = None #object name such as from OBJ's 'o' statement
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
    bump_enable = None
    #IF ADDING NEW VARIABLE here, remember to update any copy functions (such as get_kivyglop_from_pyglop) or copy constructors in your subclass or calling program
    vertex_format = None
    vertices = None
    indices = None
    #opacity = None  moved to material.diffuse_color 4th channel

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
        self.hit_radius = 0.1524  # .5' equals .1524m
        self.bump_enable = False
        self.properties = {}
        self.properties["inventory_index"] = -1
        self.properties["inventory_items"] = []
        #formerly in MeshData:
        # order MUST match V_POS_INDEX etc above
        self.vertex_format = [
            (b'a_position', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec3)
            (b'a_texcoord0', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2); vTexCoord0; available if enable_tex[0] is true
            (b'a_texcoord1', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2);  available if enable_tex[1] is true
            (b'a_color', 4, 'float'),  # vColor (diffuse color of vertex)
            (b'a_normal', 3, 'float')  # vNormal; Munshi prefers vec3 (Kivy also prefers vec3)
            ]
        self.vertex_depth = 0
        for i in range(0,len(self.vertex_format)):
            self.vertex_depth += self.vertex_format[i][VFORMAT_VECTOR_LEN_INDEX]

        self.on_vertex_format_change()

        self.indices = []  # list of tris (vertex index, vertex index, vertex index, etc)

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

    def apply_pivot(self):
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        v_offset = 0
        for v_number in range(0, vertex_count):
            self.vertices[v_offset+self._POSITION_OFFSET+0] -= self._pivot_point[0]
            self.vertices[v_offset+self._POSITION_OFFSET+1] -= self._pivot_point[1]
            self.vertices[v_offset+self._POSITION_OFFSET+2] -= self._pivot_point[2]
            v_offset += self.vertex_depth
        self._pivot_point = (0.0, 0.0, 0.0)
    
    def pop_glop_item(self, this_glop_index):
        try:
            self.properties["inventory_items"].pop(this_glop_index)
            if this_glop_index == 0:
                self.select_next_inventory_slot(True)
            else:
                self.select_next_inventory_slot(False)
        except:
            print("Could not finish pop_glop_item:")
            view_traceback()
    
    def push_glop_item(self, this_glop, this_glop_index):
        result = False
        #item_dict = {}
        item_dict = this_glop.item_dict
        
        #item_dict["glop_index"] = this_glop_index  #already done when set as itme
        #item_dict["glop_name"] = this_glop.name  #already done when set as itme
        for i in range(0,len(self.properties["inventory_items"])):
            if self.properties["inventory_items"][i] == None:
                self.properties["inventory_items"][i] = item_dict
                result = True
                print("obtained item in slot "+str(i)+": "+str(item_dict))
                break
        if not result:
            self.properties["inventory_items"].append(item_dict)
            print("obtained item in new slot: "+str(item_dict))
            result = True
        if result:
            if self.properties["inventory_index"] < 0:
                self.properties["inventory_index"] = 0
        return result
    
    def select_next_inventory_slot(self, is_forward):
        delta = 1
        if not is_forward:
            delta = -1
        if len(self.properties["inventory_items"]) > 0:
            self.properties["inventory_index"] += delta
            if self.properties["inventory_index"] < 0:
                self.properties["inventory_index"] = len(self.properties["inventory_items"]) - 1
            elif self.properties["inventory_index"] >= len(self.properties["inventory_items"]):
                self.properties["inventory_index"] = 0
            this_item_dict = self.properties["inventory_items"][self.properties["inventory_index"]]
            proper_name = ""
            if "glop_name" in this_item_dict:
                proper_name = this_item_dict["glop_name"]
            print("Selected "+this_item_dict["name"]+" "+proper_name+" in slot "+str(self.properties["inventory_index"]))
            print("You have "+str(len(self.properties["inventory_items"]))+" item(s).")
        else:
            print("You have 0 items.")

    def _on_change_pivot(self):
        pass

    def transform_pivot_to_geometry(self):
        self._pivot_point = self.get_center_average_of_vertices()
        self._on_change_pivot()
        pass

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
            #pass  #don't care
        if result is None:
            if verbose_enable:
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


    def set_textures_from_mtl_dict(self, mtl_dict):
        #print("")
        #print("set_textures_from_mtl_dict...")
        #print("")
        try:
            self.material.diffuse_color = mtl_dict.get('Kd') or self.material.diffuse_color
            self.material.diffuse_color = [float(v) for v in self.material.diffuse_color]
            self.material.ambient_color = mtl_dict.get('Ka') or self.material.ambient_color
            self.material.ambient_color = [float(v) for v in self.material.ambient_color]
            self.material.specular_color = mtl_dict.get('Ks') or self.material.specular_color
            self.material.specular_color = [float(v) for v in self.material.specular_color]
            self.material.specular_coefficent = float(mtl_dict.get('Ns', self.material.specular_coefficent))
            #TODO: store as diffuse color alpha instead: self.opacity = mtl_dict.get('d')
            #TODO: store as diffuse color alpha instead: if self.opacity is None:
            #TODO: store as diffuse color alpha instead:     self.opacity = 1.0 - float(mtl_dict.get('Tr', 0.0))
            if "map_Kd" in mtl_dict.keys():
                self.material.properties["diffuse_path"] = mtl_dict["map_Kd"]
                #print("  NOTE: diffuse_path: "+self.material.properties["diffuse_path"])
            #else:
                #print("  WARNING: "+str(self.name)+" has no map_Kd among material keys "+','.join(mtl_dict.keys()))

        except:  # Exception:
            print("Could not finish set_textures_from_mtl_dict:")
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

    def append_dump(self, thisList, this_min_tab):
        thisList.append(this_min_tab+"Glop:")
        tabString="  "
        if self.name is not None:
            thisList.append(this_min_tab+tabString+"name: "+self.name)
        if self.vertices is not None:
            if add_dump_comments_enable:
                thisList.append(this_min_tab+tabString+"#len(self.vertices)/self.vertex_depth:")
            thisList.append(this_min_tab+tabString+"vertices_count: "+str(len(self.vertices)/self.vertex_depth))
        if self.indices is not None:
            thisList.append(this_min_tab+tabString+"indices_count:"+str(len(self.indices)))
        thisList.append(this_min_tab+tabString+"vertex_depth: "+str(self.vertex_depth))
        if self.vertices is not None:
            if add_dump_comments_enable:
                thisList.append(this_min_tab+tabString+"#len(self.vertices):")
            thisList.append(this_min_tab+tabString+"vertices_info_len: "+str(len(self.vertices)))
        thisList.append(this_min_tab+tabString+"POSITION_INDEX:"+str(self.POSITION_INDEX))
        thisList.append(this_min_tab+tabString+"NORMAL_INDEX:"+str(self.NORMAL_INDEX))
        thisList.append(this_min_tab+tabString+"COLOR_INDEX:"+str(self.COLOR_INDEX))

        component_index = 0
        component_offset = 0

        while component_index < len(self.vertex_format):
            vertex_format_component = self.vertex_format[component_index]
            component_name_bytestring, component_len, component_type = vertex_format_component
            component_name = component_name_bytestring.decode("utf-8")
            thisList.append(this_min_tab+tabString+component_name+".len:"+str(component_len))
            thisList.append(this_min_tab+tabString+component_name+".type:"+str(component_type))
            thisList.append(this_min_tab+tabString+component_name+".index:"+str(component_index))
            thisList.append(this_min_tab+tabString+component_name+".offset:"+str(component_offset))
            component_index += 1
            component_offset += component_len

        #thisList.append(this_min_tab+tabString+"POSITION_LEN:"+str(self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]))

        if add_dump_comments_enable:
            #thisList.append(this_min_tab+tabString+"#VFORMAT_VECTOR_LEN_INDEX:"+str(VFORMAT_VECTOR_LEN_INDEX))
            thisList.append(this_min_tab+tabString+"#len(self.vertex_format):"+str(len(self.vertex_format)))
            thisList.append(this_min_tab+tabString+"#COLOR_OFFSET:"+str(self.COLOR_OFFSET))
            thisList.append(this_min_tab+tabString+"#len(self.vertex_format[self.COLOR_INDEX]):"+str(len(self.vertex_format[self.COLOR_INDEX])))
        channel_count = self.vertex_format[self.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        if add_dump_comments_enable:
            thisList.append(this_min_tab+tabString+"#vertex_bytes_per_pixel:"+str(channel_count))


        for k,v in sorted(self.properties.items()):
            thisList.append(this_min_tab+tabString+k+": "+v)

        thisTextureFileName=self.get_texture_diffuse_path()
        if thisTextureFileName is not None:
            thisList.append(this_min_tab+tabString+"get_texture_diffuse_path(): "+thisTextureFileName)

        #thisList=append_dump_as_yaml_array(thisList, "vertex_info_1D",self.vertices,this_min_tab+tabString)
        tabString="  "
        if add_dump_comments_enable:
            thisList.append(this_min_tab+tabString+"#1D vertex info array, aka:")
        thisList.append(this_min_tab+tabString+"vertices:")
        component_offset = 0
        vertex_actual_index = 0
        for i in range(0,len(self.vertices)):
            if add_dump_comments_enable:
                if component_offset==0:
                    thisList.append(this_min_tab+tabString+tabString+"#vertex ["+str(vertex_actual_index)+"]:")
                elif component_offset==self.COLOR_OFFSET:
                    thisList.append(this_min_tab+tabString+tabString+"#  color:")
                elif component_offset==self._NORMAL_OFFSET:
                    thisList.append(this_min_tab+tabString+tabString+"#  normal:")
                elif component_offset==self._POSITION_OFFSET:
                    thisList.append(this_min_tab+tabString+tabString+"#  position:")
                elif component_offset==self._TEXCOORD0_OFFSET:
                    thisList.append(this_min_tab+tabString+tabString+"#  texcoords0:")
                elif component_offset==self._TEXCOORD1_OFFSET:
                    thisList.append(this_min_tab+tabString+tabString+"#  texcoords1:")
            thisList.append(this_min_tab+tabString+tabString+"- "+str(self.vertices[i]))
            component_offset += 1
            if component_offset==self.vertex_depth:
                component_offset = 0
                vertex_actual_index += 1

        thisList.append(this_min_tab+tabString+"indices:")
        for i in range(0,len(self.indices)):
            thisList.append(this_min_tab+tabString+tabString+"- "+str(self.indices[i]))


    def on_vertex_format_change(self):
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



class PyGlopsMaterial:
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

    def append_dump(self, thisList, this_min_tab):
        thisList.append(this_min_tab+"GlopsMaterial:")
        tabString="  "
        if self.name is not None:
            thisList.append(this_min_tab+tabString+"name: "+self.name)
        if self.mtlFileName is not None:
            thisList.append(this_min_tab+tabString+"mtlFileName: "+self.mtlFileName)
        for k,v in sorted(self.properties.items()):
            thisList.append(this_min_tab+tabString+k+": "+str(v))

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


#Also in wobjfile.py:
def append_dump_as_yaml_array(thisList, thisName, sourceList, this_min_tab):
    tabString="  "
    thisList.append(this_min_tab+thisName+":")
    for i in range(0,len(sourceList)):
        thisList.append(this_min_tab+tabString+"- "+str(sourceList[i]))


def new_tuple(length, fill_start=0, fill_len=-1, fill_value=1.0):
    result = None
    tmp=list()
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


def get_pyglop_from_wobject(this_wobject):  #formerly set_from_wobject formerly import_wobject; based on _finalize_obj_data
    this_pyglop = None
    if (this_wobject.faces is not None):
        this_pyglop = PyGlop()
        this_pyglop.source_path = this_wobject.source_path
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
        if this_pyglop._POSITION_OFFSET<0:
            IS_SELF_VFORMAT_OK = False
            print("Couldn't find name containing 'pos' or 'position' in any vertex format element (see pyglops.py PyGlop constructor)")
        if this_pyglop._NORMAL_OFFSET<0:
            IS_SELF_VFORMAT_OK = False
            print("Couldn't find name containing 'normal' in any vertex format element (see pyglops.py PyGlop constructor)")
        if this_pyglop._TEXCOORD0_OFFSET<0:
            IS_SELF_VFORMAT_OK = False
            print("Couldn't find name containing 'texcoord' in any vertex format element (see pyglops.py PyGlop constructor)")
        if this_pyglop.COLOR_OFFSET<0:
            IS_SELF_VFORMAT_OK = False
            print("Couldn't find name containing 'color' in any vertex format element (see pyglops.py PyGlop constructor)")

        #vertices_offset = None
        #normals_offset = None
        #texcoords_offset = None
        #vertex_depth = 8
        #based on finish_object
    #         if this_pyglop._current_object == None:
    #             return
    #
        if not IS_SELF_VFORMAT_OK:
            sys.exit(1)
        zero_vertex = list()
        for index in range(0,this_pyglop.vertex_depth):
            zero_vertex.append(0.0)
        if (this_pyglop.vertex_format[this_pyglop.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]>3):
            zero_vertex[3] = 1.0
            #NOTE: this is done since usually if len is 3, simple.glsl included with kivy converts it to vec4 appending 1.0:
            #attribute vec3 v_pos;
            #void main (void) {
            #vec4(v_pos,1.0);
        #this_offset = this_pyglop.COLOR_OFFSET
        channel_count = this_pyglop.vertex_format[this_pyglop.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        for channel_subindex in range(0,channel_count):
            zero_vertex[this_pyglop.COLOR_OFFSET+channel_subindex] = -1.0  # -1.0 for None #TODO: asdf flag a different way (other than negative) to work with fake standard shader


        participle="accessing object from list"
        #this_wobject = this_pyglop.glops[index]
        this_pyglop.name = None
        this_name = ""
        try:
            if this_wobject.name is not None:
                this_pyglop.name = this_wobject.name
                this_name = this_wobject.name
        except:
            pass  #don't care

        try:
            #if this_wobject.wmaterial is None:
            participle="processing material"
            if this_wobject.wmaterial is not None:  # if this_wobject.properties["usemtl"] is not None:
                #this_wobject.material=this_pyglop._getMaterial(this_wobject.properties["usemtl"])
                if this_wobject.wmaterial._map_filename_dict is not None:  # if this_wobject.wmaterial is not None:
                    this_pyglop.set_textures_from_mtl_dict(this_wobject.wmaterial._map_filename_dict)
                    #TODO: so something with _map_params_dict (wobjfile.py makes each entry a list of params if OBJ had map params before map file name)
                else:
                    print("WARNING: this_wobject.wmaterial._map_filename_dict is None")
            else:
                print("WARNING: this_wobject.wmaterial is None")
        except:  # Exception as e:
            #print("Could not finish "+participle+" in get_pyglop_from_wobject: "+str(e))
            print("Could not finish "+participle+" in get_pyglop_from_wobject: ")
            view_traceback()

        if this_pyglop.vertices is None:
            this_pyglop.vertices = []
            vertex_components = zero_vertex[:]
            #obj format stores faces like (quads are allowed such as in following examples):
            #this_wobject_this_face 1399/1619 1373/1593 1376/1596 1400/1620
            #format is:
            #this_wobject_this_face VERTEX_I VERTEX_I VERTEX_I VERTEX_I
            #or
            #this_wobject_this_face VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX
            #or
            #this_wobject_this_face VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX
            #where *I are integers starting at 0 (stored starting at 1)
            #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
            #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 1
            #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 2
            #NOTE: in obj format, TEXCOORDS_INDEX is optional

            #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
            #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 1
            #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 2

            #nskrypnik put them in a different order than obj format (0,1,2) for some reason so do this order instead ONLY if using his obj loader:
            #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
            #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 2
            #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 1

            #use the following globals from wobjfile.py instead of assuming any FACE_VERTEX_COMPONENT values:
            #FACE_V  # index of vertex index in the face (since face is a list)
            #FACE_TC  # index of tc0 index in the face (since face is a list)
            #FACE_VN  # index of normal index in the face (since face is a list)

            source_face_index = 0
            try:
                if (len(this_pyglop.indices)<1):
                    participle = "before detecting vertex component offsets"
                    #detecting vertex component offsets is required since indices in an obj file are sometimes relative to the first index in the FILE not the object
                    if this_wobject.faces is not None:
                        #get offset
                        for faceIndex in range(0,len(this_wobject.faces)):
                            for componentIndex in range(0,len(this_wobject.faces[faceIndex])):
                                #print("found face "+str(faceIndex)+" component "+str(componentIndex)+": "+str(this_wobject.faces[faceIndex][componentIndex]))
                                #print(str(this_wobject.faces[faceIndex][vertexIndex]))
                                #if (len(this_wobject.faces[faceIndex][componentIndex])>=FACE_V):
                                #TODO: audit this code:
                                for vertexIndex in range(0,len(this_wobject.faces[faceIndex][componentIndex])):
                                    #calculate new offsets, in case obj file was botched (for correct obj format, wobjfile.py changes indices so they are relative to wobject ('o' command) instead of file
                                    if componentIndex==FACE_V:
                                        thisVertexIndex = this_wobject.faces[faceIndex][componentIndex][vertexIndex]
                                        #if vertices_offset is None or thisVertexIndex<vertices_offset:
                                            #vertices_offset = thisVertexIndex
                                    #if (len(this_wobject.faces[faceIndex][componentIndex])>=FACE_TC):
                                    elif componentIndex==FACE_TC:
                                        thisTexCoordIndex = this_wobject.faces[faceIndex][componentIndex][vertexIndex]
                                        #if texcoords_offset is None or thisTexCoordIndex<texcoords_offset:
                                            #texcoords_offset = thisTexCoordIndex
                                    #if (len(this_wobject.faces[faceIndex][componentIndex])>=FACE_VN):
                                    elif componentIndex==FACE_VN:
                                        thisNormalIndex = this_wobject.faces[faceIndex][componentIndex][vertexIndex]
                                        #if normals_offset is None or thisNormalIndex<normals_offset:
                                            #normals_offset = thisNormalIndex

                        #if vertices_offset is not None:
                            #print("detected vertices_offset:"+str(vertices_offset))
                        #if texcoords_offset is not None:
                            #print("detected texcoords_offset:"+str(texcoords_offset))
                        #if normals_offset is not None:
                            #print("detected normals_offset:"+str(normals_offset))

                    participle = "before processing faces"
                    dest_vertex_index = 0
                    face_count = 0
                    new_texcoord = new_tuple(this_pyglop.vertex_format[this_pyglop.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX])
                    if this_wobject.faces is not None:
                        for this_wobject_this_face in this_wobject.faces:
                            participle = "getting face components"
                            #print("face["+str(source_face_index)+"]: "+participle)

                            #DOES triangulate of more than 3 vertices in this face (connects each loose point to first vertex and previous vertex)
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
                                    participle = "getting normal components at "+str(normal_index)+"-"+str(normals_offset)  # str(norms[face_index]-normals_offset)
                                    if normal_index is not None:
                                        normal = this_wobject.normals[normal_index-normals_offset]
                                    #if norms[face_index] != -1:
                                        #normal = this_wobject.normals[norms[face_index]-normals_offset]
                                except:  # Exception as e:
                                    print("Could not finish "+participle+" for wobject named '"+this_name+"':")
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
                                        participle = "getting texcoord components at "+str(texcoord_index)+"-"+str(texcoords_offset)  # str(norms[face_index]-normals_offset)

                                        if texcoord_index is not None:
                                            texcoord = this_wobject.texcoords[texcoord_index-texcoords_offset]
                                        #if tcs[face_index] != -1:
                                            #participle = "using texture coordinates at index "+str(tcs[face_index]-texcoords_offset)+" (after applying texcoords_offset:"+str(texcoords_offset)+"; Count:"+str(len(this_wobject.texcoords))+")"
                                            #texcoord = this_wobject.texcoords[tcs[face_index]-texcoords_offset]
                                    else:
                                        if verbose_enable:
                                            print("Warning: no texcoords found in wobject named '"+this_name+"'")
                                except:  # Exception as e:
                                    print("Could not finish "+participle+" for wobject named '"+this_name+"':")
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
                                    print("Could not finish "+participle+" for wobject named '"+this_name+"':")
                                    view_traceback()

                                participle = "combining components"
                                #vertex_components = [v[0], v[1], v[2], normal[0], normal[1], normal[2], texcoord[0], 1 - texcoord[1]] #TODO: why does kivy-rotation3d version have texcoord[1] instead of 1 - texcoord[1]
                                vertex_components = list()
                                for i in range(0,this_pyglop.vertex_depth):
                                    vertex_components.append(0.0)
                                for element_index in range(0,3):
                                    vertex_components[this_pyglop._POSITION_OFFSET+element_index] = v[element_index]
                                if (this_pyglop.vertex_format[this_pyglop.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]>3):
                                    vertex_components[this_pyglop._POSITION_OFFSET+3] = 1.0  # non-position padding value must be 1.0 for matrix math to work correctly
                                for element_index in range(0,3):
                                    vertex_components[this_pyglop._NORMAL_OFFSET+element_index] = normal[element_index]
                                for element_index in range(0,2):

                                    if element_index==1:
                                        vertex_components[this_pyglop._TEXCOORD0_OFFSET+element_index] = 1-texcoord[element_index]
                                    else:
                                        vertex_components[this_pyglop._TEXCOORD0_OFFSET+element_index] = texcoord[element_index]

                                if len(v)>3:
                                    #Handle nonstandard obj file with extended vertex info (color)
                                    abs_index = 0
                                    for element_index in range(4,len(v)):
                                        vertex_components[this_pyglop.COLOR_OFFSET+abs_index] = v[element_index]
                                        abs_index += 1
                                else:
                                    #default to white vertex color
                                    #TODO: asdf change this to black with alpha 0.0 and overlay (using material color as base)
                                    for element_index in range(0,4):
                                        vertex_components[this_pyglop.COLOR_OFFSET+element_index] = 1.0
                                this_pyglop.vertices.extend(vertex_components)
                                source_face_vertex_count += 1
                                vertexinfo_index += 1
                            #end while vertexinfo_index in face

                            participle = "combining triangle indices"
                            vertexinfo_index = 0
                            relative_source_face_vertex_index = 0  #required for tracking faces with less than 3 vertices
                            face_first_vertex_dest_index = dest_vertex_index
                            tesselated_f_count = 0
                            #example obj quad (without Texcoord) vertex_index/texcoord_index/normal_index:
                            #f 61//33 62//33 64//33 63//33
                            #face_vertex_list=list()  # in case verts are out of order, prevent tesselation from connecting wrong verts
                            while vertexinfo_index<len(this_wobject_this_face):
                                #face_vertex_list.append(dest_vertex_index)
                                if vertexinfo_index==2:
                                    #OK to assume dest vertices are in order, since just created them (should work even if source vertices are not in order)
                                    tri = [dest_vertex_index, dest_vertex_index+1, dest_vertex_index+2]
                                    this_pyglop.indices.extend(tri)
                                    dest_vertex_index += 3
                                    relative_source_face_vertex_index += 3
                                    tesselated_f_count += 1
                                elif vertexinfo_index>2:
                                    #TESSELATE MANUALLY for faces with more than 3 vertices (connect loose vertex with first vertex and previous vertex)
                                    tri = [face_first_vertex_dest_index, dest_vertex_index-1, dest_vertex_index]
                                    this_pyglop.indices.extend(tri)
                                    dest_vertex_index += 1
                                    relative_source_face_vertex_index += 1
                                    tesselated_f_count += 1
                                vertexinfo_index += 1

                            if (tesselated_f_count<1):
                                print("WARNING: Face tesselated to 0 faces")
                            elif (tesselated_f_count>1):
                                if verbose_enable:
                                    print("Face tesselated to "+str(tesselated_f_count)+" face(s)")

                            if relative_source_face_vertex_index<source_face_vertex_count:
                                print("WARNING: Face has fewer than 3 vertices (problematic obj file)")
                                dest_vertex_index += source_face_vertex_count - relative_source_face_vertex_index
                            source_face_index += 1
                    else:
                        print("WARNING: this_wobject.faces list is None in object '"+this_name+"'")
                    participle = "generating pivot point"

                    this_pyglop.transform_pivot_to_geometry()
                else:
                    print("ERROR: can't use pyglop since already has vertices (len(this_pyglop.indices)>=1)")

            except:  # Exception as e:
                #print("Could not finish "+participle+" at source_face_index "+str(source_face_index)+" in get_pyglop_from_wobject: "+str(e))
                print("Could not finish "+participle+" at source_face_index "+str(source_face_index)+" in get_pyglop_from_wobject: ")
                view_traceback()

                    #print("vertices after extending: "+str(this_wobject.vertices))
                    #print("indices after extending: "+str(this_wobject.indices))
        #         if this_wobject.mtl is not None:
        #             this_wobject.wmaterial = this_wobject.mtl.get(this_wobject.obj_material)
        #         if this_wobject.wmaterial is not None and this_wobject.wmaterial:
        #             this_wobject.set_textures_from_mtl_dict(this_wobject.wmaterial)
                #self.glops[self._current_object] = mesh
                #mesh.calculate_normals()
                #self.faces = []

        #         if (len(this_wobject.normals)<1):
        #             this_wobject.calculate_normals()  #this does not work. The call to calculate_normals is even commented out at <https://github.com/kivy/kivy/blob/master/examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015.
        else:
            print("ERROR in get_pyglop_from_wobject: existing vertices found {this_pyglop.name:'"+str(this_name)+"'}")
    else:
        print("WARNING in get_pyglop_from_wobject: ignoring wobject where faces list is None.")
    return this_pyglop
#end def get_pyglop_from_wobject



class PyGlops:
    glops = None
    materials = None
    lastUntitledMeshNumber = -1
    lastCreatedMaterial = None
    lastCreatedMesh = None
    _walkmeshes = None
    camera_glop = None
    prev_inbounds_camera_translate = None
    _bumper_indices = None
    _bumpee_indices = None

    def __init__(self):
        self.camera_glop = PyGlop()  #should be remade to subclass of PyGlop in subclass of PyGlops
        self.camera_glop.eye_height = 1.7  # 1.7 since 5'10" person is ~1.77m, and eye down a bit
        self.camera_glop.hit_radius = .1
        self.camera_glop.name = "camera_glop"
        self._walkmeshes = []
        self.glops = []
        self.materials = []
        self._bumper_indices = []
        self._bumpee_indices = []

    def append_dump(self, thisList):
        tabString="  "
        thisList.append("Glops:")
        for i in range(0,len(self.glops)):
            self.glops[i].append_dump(thisList, tabString)
        thisList.append("GlopsMaterials:")
        for i in range(0,len(self.materials)):
            self.materials[i].append_dump(thisList, tabString)

    def create_mesh(self):
        return PyGlop()

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

    def get_pyglops_list_from_obj(self, source_path):  # load_obj(self, source_path): #TODO: ? swapyz=False):
        participle = "(before initializing)"
        linePlus1 = 1
        #firstMeshIndex = len(self.glops)
        results = None
        try:
            #self.lastCreatedMesh = None
            participle = "checking path"
            if os.path.exists(source_path):
                results = list()  # create now, so that if None, that means source_path didn't exist
                participle = "setting up WObjFile"
                this_objfile = WObjFile()
                participle = "loading WObjFile"
                this_objfile.load(source_path)
                if this_objfile.wobjects is not None:
                    if len(this_objfile.wobjects)>0:
                        for i in range(0,len(this_objfile.wobjects)):
                            participle = "getting wobject"
                            this_wobject = this_objfile.wobjects[i]
                            participle = "converting wobject..."
                            this_pyglop = get_pyglop_from_wobject(this_wobject)
                            if this_pyglop is not None:
                                participle = "appending pyglop to scene"
                                #if results is None:
                                #    results = list()
                                results.append(this_pyglop)
                                if verbose_enable:
                                    if this_pyglop.name is not None:
                                        print("appended glop named '"+this_pyglop.name+"'")
                                    else:
                                        print("appended glop {name:None}")
                            else:
                                print("ERROR: this_pyglop is None after converting from wobject")
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


