"""
PyGlops is a game engine for python. It is "abstract" so in most
cases classes here need to be subclassed to be useful (see KivyGlops).
This module provides simple dependency-free access to OBJ files and
certain 3D math operations.
"""
__author__ = 'Jake Gustafson'

import os
import math
import sys
import random
# from docutils.utils.math.math2html import VerticalSpace
# import traceback
from kivyglops.common import (
    get_verbose_enable,
    get_yaml_from_literal_value,
    get_dict_deepcopy,
    view_traceback,
    is_true,
    debug_dict,
)
# from pyrealtime import *
from datetime import datetime

import timeit
from timeit import default_timer as best_timer
import time
from kivyglops.wobjfile import (
    standard_emit_yaml,
    WObjFile,
)

TAU = math.pi * 2.
NEG_TAU = -TAU

settings = {}
settings['globals'] = {}
settings['globals']['attack_uses'] = \
    ['throw_arc', "throw_linear", 'melee']
settings['globals']['camera_perspective_number'] = 1
# ^ is changed in PyGlops init
settings['world'] = {}
settings['world']['gravity_enable'] = True
# ^ formerly globals world_gravity_enable
settings['world']['gravity'] = 9.8
# ^ formerly globals world_gravity
settings['world']['ground'] = 0.0  # only used if no walkmesh
settings['world']['density'] = 0.0
settings['world']['minimums'] = [0., 0., 0.]
settings['world']['minimums'][0] = sys.float_info.min
settings['world']['minimums'][1] = -15  # such as for when to die
# ^ formerly settings['globals']['world_bottom']
settings['world']['minimums'][2] = sys.float_info.min
settings['world']['maximums'] = [0., 0., 0.]
settings['world']['maximums'][0] = sys.float_info.max
settings['world']['maximums'][1] = sys.float_info.max
settings['world']['maximums'][2] = sys.float_info.max
settings['world']['friction_divisor'] = 1.2
# ^ formerly settings['globals']['world_friction_divisor']
settings['world']['cor'] = 1.2
# ^ coefficient of restitution
#   bounce_max_y_new / bounce_y_max_orig
# settings['world']['gravity_enable'] = None
# ^ None since use_walkmesh_at checks for None
settings['templates'] = {}
# settings['templates']['properties']['hitbox'] = new_hitbox()
# ^ see further down (after hitbox_* functions) for hitbox
settings['templates']['properties'] = {}  # glop.properties
settings['templates']['properties']['hit_radius'] = .5
settings['templates']['properties']['clip_enable'] = False
settings['templates']['properties']['roll_enable'] = True
# ^ roll while touching ground and moving
settings['templates']['properties']['cor'] = 0.0  # see ['world']['cor']
settings['templates']['properties']['expand_min'] = 0.0
settings['templates']['properties']['expand_max'] = 0.0
settings['templates']['properties']['expanded'] = 0.0
# ^ negative for compressed
settings['templates']['properties']['hit_radius'] = 0.1524
# ^ .5' equals .1524m
settings['templates']['properties']['clip_enable'] = False
settings['templates']['properties']['separable_offsets'] = []
# ^ if more than one submesh is in vertices, chunks are saved
#   in here, such as to assist with explosions
settings['templates']['properties']['physics_enable'] = False
settings['templates']['properties']['infinite_inventory_enable'] = True
# settings['templates']['properties']['eye_height'] = 0.0
# ^ or 1.7 since 5'10" person is
#   ~1.77m, and eye down a bit
settings['templates']['properties']['eye_height'] = 1.7
# ^ 1.7 since 5'10" person is ~1.77m,
# ^ and eye down a bit
# settings['templates']['properties']['reach_radius'] = 0.381
# ^ 2.5' .381m
settings['templates']['properties']['reach_radius'] = 2.5
settings['templates']['properties']['bump_enable'] = False
settings['templates']['properties']['hit_radius'] = .2
settings['templates']['properties']['expanded_vec'] = 0.0
# ^ angle from which it is compressed (for bounce etc)
settings['templates']['properties']['bump_sound_paths'] = []
settings['templates']['properties']['damaged_sound_paths'] = []
# ^ even if not an actor
settings['templates']['actor_properties'] = {}
# settings['templates']['actor_properties']['hit_radius'] = .5
settings['templates']['actor_properties']['clip_enable'] = True
settings['templates']['actor_properties']['roll_enable'] = False
settings['templates']['actor_properties']['physics_enable'] = True
settings['templates']['actor_properties']['bump_enable'] = True
settings['templates']['actor'] = {}
settings['templates']['actor']['land_speed'] = 12.
settings['templates']['actor']['land_accel'] = 12.
settings['templates']['actor']['land_degrees_per_second'] = 720.
# ^ unless you're Tara Lipinski 2 rotations per second is pretty good
settings['templates']['actor']['fly_enable'] = False
settings['templates']['actor']['throw_speed'] = 15.
# ^ ignored if item has projectile_speed
settings['templates']['actor']['target_index'] = None
settings['templates']['actor']['moveto_index'] = None
settings['templates']['actor']['target_pos'] = None
settings['templates']['actor']['land_speed'] = 12.5
# ^ since 45 KMh is average (45/60/60*1000)
settings['templates']['actor']['ranges'] = {}
settings['templates']['actor']['ranges']['melee'] = 0.5
settings['templates']['actor']['ranges']['throw_arc'] = 10.
settings['templates']['actor']['inventory_index'] = -1
settings['templates']['actor']['inventory_items'] = []
settings['templates']['actor']['unarmed_melee_enable'] = False
settings['templates']['state'] = {}
settings['templates']['state']['links'] = []
# ^ list of relationship dicts
settings['templates']['state']['constrained_enable'] = False
settings['templates']['state']['on_ground_enable'] = False
settings['templates']['state']['at_rest_event_enable'] = False
settings['templates']['state']['visible_enable'] = True
settings['templates']['state']['in_range_indices'] = []
settings['templates']['state']['velocity'] = [0., 0., 0.]
settings['templates']['state']['velocity'][0] = 0.0
settings['templates']['state']['velocity'][1] = 0.0
settings['templates']['state']['velocity'][2] = 0.0

tab_string = "  "

# verbose_enable = True  # see get_verbose_enable() in common.py instead

# references:
# kivy-trackball objloader (version with no MTL loader) by nskrypnik
# objloader from kivy-rotation3d (version with placeholder mtl loader)
# by nskrypnik

# TODO: remove resource_find but still make able to find mtl file
# under Kivy somehow

dump_enable = False
add_dump_comments_enable = False

V_POS_INDEX = 0
V_TC0_INDEX = 1
V_TC1_INDEX = 2
V_DIFFUSE_INDEX = 3
V_NORMAL_INDEX = 4
# see also pyglopsmesh.vertex_depth below

# indices of tuples inside vertex_format (see PyGlop)
VFORMAT_NAME_INDEX = 0
VFORMAT_VECTOR_LEN_INDEX = 1
VFORMAT_TYPE_INDEX = 2

EMPTY_ITEM = dict()
EMPTY_ITEM['name'] = "Empty"


def new_flag_f():
    return .4444


def is_flag_f(v):
    return v == .4444


kEpsilon = 1.0E-6
# ^ adjust to suit.  If you use floats, you'll
#   probably want something like 1.0E-7 (added
#   by Poikilos [tested: using 1.0E-6 since python 3
#   fails to set 3.1415927 to 3.1415926
#   see delta_theta in KivyGlops]
# kEpsilon = 1.0E-7
# ^ adjust to suit.  If you use floats, you'll
#   probably want something like 1.0E-7 (added
#   by Poikilos)


def fequals(f1, f2):
    '''
    Check if difference is between global kEpsilon and -kEpsilon.
    '''
    if f1 > f2:
        return (f1 - f2) <= kEpsilon
    return (f2 - f1) <= kEpsilon
    # kEpsilon = 1.0E-6 is recommended, since
    # if kEpsilon is 1.0E-7,
    # < FAILS sometimes:
    #     says 2.5911259 not 2.5911258 after '='
    #     and
    # <= FAILS sometimes for negatives:
    #     says -3.0629544 not -3.0629545 after '='


def match_fn_ci(fileNameOrNameOrNone, name):
    '''
    Match a filename or a filename without an extension to name
    (case-insensitive).
    '''
    source_name_lower = fileNameOrNameOrNone.lower()
    name_lower = name.lower()
    if fileNameOrNameOrNone is None:
        return False
    return ((source_name_lower == name_lower)
            or (os.path.splitext(source_name_lower)[0] == name_lower))

    return


def match_fn(fileNameOrNameOrNone, name):
    '''
    Match a filename or a filename without an extension to name
    (case-insensitive).
    '''
    if fileNameOrNameOrNone is None:
        return False
    return ((fileNameOrNameOrNone == name)
            or (os.path.splitext(fileNameOrNameOrNone)[0] == name))
    return


def normalize_3d_by_ref(this_vec3):
    # see <https://stackoverflow.com/questions/23303598
    # /3d-vector-normalization-issue#23303817>
    length = math.sqrt(this_vec3[0] * this_vec3[0]
                       + this_vec3[1] * this_vec3[1]
                       + this_vec3[2] * this_vec3[2])
    if length > 0:
        this_vec3[0] /= length
        this_vec3[1] /= length
        this_vec3[2] /= length
    else:
        this_vec3[0] = 0.0
        this_vec3[1] = -1.0  # give some kind of normal for 0,0,0
        this_vec3[2] = 0.0


def degrees_list(vals):
    result = []
    for val in vals:
        result.append(math.degrees(val))
    return result


def get_fvec4_from_svec3(vals, last_value):
    results = None
    try:
        if len(vals) == 1:
            results = (float(vals[0]),
                       float(vals[0]),
                       float(vals[0]),
                       last_value)
        elif len(vals) == 2:
            print("ERROR in get_fvec4: bad length 2 for " + str(vals))
            results = (float(vals[0]),
                       float(vals[0]),
                       float(vals[0]),
                       last_value)
        elif len(vals) == 3:
            results = (float(vals[0]),
                       float(vals[1]),
                       float(vals[2]),
                       last_value)
        else:
            results = (float(vals[0]),
                       float(vals[1]),
                       float(vals[2]),
                       last_value)
    except ValueError:
        print("ERROR in get_fvec4: bad floats in " + str(vals))
        results = 0.0, 0.0, 0.0, 0.0
    return results


def get_fvec4_from_svec_any_len(vals):
    results = None
    try:
        if len(vals) == 1:
            results = (float(vals[0]),
                       float(vals[0]),
                       float(vals[0]),
                       1.0)
        elif len(vals) == 2:
            print("ERROR in get_fvec4: bad length 2 for " + str(vals))
            results = (float(vals[0]),
                       float(vals[0]),
                       float(vals[0]),
                       float(vals[1]))
        elif len(vals) == 3:
            results = (float(vals[0]),
                       float(vals[1]),
                       float(vals[2]),
                       1.0)
        else:
            results = (float(vals[0]),
                       float(vals[1]),
                       float(vals[2]),
                       float(vals[3]))
    except ValueError:
        print("ERROR in get_fvec4: bad floats in " + str(vals))
        results = 0.0, 0.0, 0.0, 0.0
    return results


def get_vec3_from_point(point):
    return (point.x, point.y, point.z)


def get_rect_from_polar_deg(r, theta):
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x, y


def get_rect_from_polar_rad(r, theta):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y


def angle_trunc(a):
    '''
    angle_trunc and get_angle_between_points edited Jul 19 '15 at 20:12
    answered Sep 28 '11 at 16:10  Peter O. <http://stackoverflow.com
    /questions/7586063/how-to-calculate-the-angle-between-a-line-and
    -the-horizontal-axis>. 29 Apr 2016
    '''
    # while a < 0.0:
    #     a += TAU
    # I'm no longer certain of the merits of this function so return a:
    return a


def get_angle_vec2(src_pos, dest_pos):
    deltaY = dest_pos[1] - src_pos[1]
    deltaX = dest_pos[0] - src_pos[0]
    return angle_trunc(math.atan2(deltaY, deltaX))


def get_angle_between_points(x_orig, y_orig, x_landmark, y_landmark):
    '''
    angle_trunc and get_angle_between_points edited Jul 19 '15 at 20:12
    answered Sep 28 '11 at 16:10  Peter O. <http://stackoverflow.com
    /questions/7586063/how-to-calculate-the-angle-between-a-line-and
    -the-horizontal-axis>. 29 Apr 2016
    '''
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(math.atan2(deltaY, deltaX))


def get_angle_between_two_vec3_xz(a, b):
    '''
    get angle between two points (from a to b), swizzled to 2d on xz
    plane; based on get_angle_between_points
    '''
    deltaY = b[2] - a[2]
    deltaX = b[0] - a[0]
    return angle_trunc(math.atan2(deltaY, deltaX))


def get_angles_vec3(src_pos, dst_pos, default_angles=None):
    '''
    default_angles: only default_angles[2] is used, but if not provided,
    roll (results[2]) angle will be 0 (since roll can't be calculated
    using 2 points)
    '''
    results = [0., 0., 0.]
    if default_angles is not None and default_angles[2] is not None:
        results[2] = default_angles[2]
    # pitch = src_pos[0]
    # yaw = src_pos[1]
    if len(dst_pos) > 2:
        results[0] = get_angle_between_points(src_pos[1], src_pos[2],
                                              dst_pos[1], dst_pos[2])
        results[1] = get_angle_between_points(src_pos[0], src_pos[2],
                                              dst_pos[0], dst_pos[2])
    else:
        results[2] = get_angle_between_points(src_pos[0], src_pos[1],
                                              dst_pos[0], dst_pos[1])
        if default_angles is not None and default_angles[0] is not None:
            results[0] = default_angles[0]
        if get_verbose_enable():
            print("[ pyglops.py ] (verbose message in look_at_pos)"
                  " got 2D coords, so only y angle (results[1]) could"
                  " be calculated. The other angles in results have"
                  " been set to default_angles if present otherwise 0.")
    return results


def get_near_line_info_xz(a, b, c):
    '''
    get nearest vec3 and distance on 3D line defined by line segment bc
    using xz of point a (in other words, get the nearest point on the
    line "under" point a looking downward at the xz plane)
    returns ((x,y,z), distance) tuple where (x,y,z) is closest 3D
    position on line segment
    bc from point a, swizzled to 2d on xz plane (y of return always a[1])
    (formerly PointSegmentDistanceSquared)
    '''

    t = None
    # as per <http://stackoverflow.com/questions/849211
    # /shortest-distance-between-a-point-and-a-line-segment>
    kMinSegmentLenSquared = kEpsilon
    # ^ kEpsilon # adjust to suit. If you use float, you'll probably
    #   want something like 0.000001f

    # Epsilon is the common name for the floating point error constant
    # (needed since some base 10 numbers cannot be stored as IEEE 754
    # with absolute precision)
    # --1E-14 or 1e-14 is same as 1.0 * 10**-14 according to
    # <http://python-reference.readthedocs.io/en/latest/docs/float
    # /scientific.html>
    dx = c[0] - b[0]
    dy = c[2] - b[2]
    db = [a[0] - b[0], 0.0, a[2] - b[2]]
    # ^ 0.0 since swizzling to xz (ignore source y)
    segLenSquared = (dx * dx) + (dy * dy)
    if segLenSquared >= -kMinSegmentLenSquared and \
            segLenSquared <= kMinSegmentLenSquared:
        # segment is a point.
        qx = b[0]
        qy = b[2]
        t = 0.0
        distance = ((db[0] * db[0]) + (db[2] * db[2]))
        return (qx, a[1], qy), distance
    else:
        # Project a line from p to the segment [p1,p2].
        # By considering the line
        # extending the segment, parameterized as p1 + (t * (p2 - p1)),
        # we find projection of point p onto the line.
        # It falls where t = [(p - p1) . (p2 - p1)] / |p2 - p1|^2
        t = ((db[0] * dx) + (db[2] * dy)) / segLenSquared
        if t < kEpsilon:
            # intersects at or to the 'left' of first
            # segment vertex (b[0], b[2]).
            # If it is approximately 0.0, then intersection is at p1.
            # If t is less than that, then there is no intersection
            # (such as p is not within the 'bounds' of the segment)
            if t > -kEpsilon:
                # intersects at 1st segment vertex
                t = 0.0
            # set our 'intersection' point to p1.
            qx = b[0]
            qy = b[2]
        elif t > (1.0 - kEpsilon):
            # Note: If you wanted the ACTUAL intersection point of
            # where the projected lines would intersect if
            # we were doing PointLineDistanceSquared, then qx would be
            # (b[0] + (t * dx)) and qy would be (b[2] + (t * dy)).

            # intersects at or to the 'right' of second segment vertex
            # (c[0], c[2]).  If t is approximately 1.0, then
            # intersection is at p2.  If t is greater than that, then
            # there is no intersection (i.e. p is not within
            # the 'bounds' of the segment)
            if t < (1.0 + kEpsilon):
                # intersects at 2nd segment vertex
                t = 1.0
            # set our 'intersection' point to p2.
            qx = c[0]
            qy = c[2]
        else:
            # Note: If you wanted the ACTUAL intersection point of where
            # the projected lines would intersect if
            # we were doing PointLineDistanceSquared, then qx would be
            # (b[0] + (t * dx)) and qy would be (b[2] + (t * dy)).
            # The projection of the point to the point on the segment
            # that is perpendicular succeeded and the point
            # is 'within' the bounds of the segment.  Set the
            # intersection point as that projected point.
            qx = b[0] + (t * dx)
            qy = b[2] + (t * dy)
        # return the squared distance from p to the intersection point.
        # Note that we return the squared distance
        # as an oaimization because many times you just need to compare
        # relative distances and the squared values
        # works fine for that.  If you want the ACTUAL distance, just
        # take the square root of this value.
        dpqx = a[0] - qx
        dpqy = a[2] - qy
        distance = ((dpqx * dpqx) + (dpqy * dpqy))
        return (qx, a[1], qy), distance


def get_distance_vec2_to_vec2line_xz(a, b, c):
    '''
    Get distance from point a to line bc, swizzled to 2d on xz plane.
    '''
    return (
        math.sin(math.atan2(b[2] - a[2], b[0] - a[0]) -
                 math.atan2(c[2] - a[2], c[0] - a[0])) *
        math.sqrt((b[0] - a[0]) * (b[0] - a[0]) +
                  (b[2] - a[2]) * (b[2] - a[2]))
    )


def get_distance_vec2_to_vec2line(a, b, c):
    '''
    Get distance from point a to line bc
    '''
    # - from ADOConnection on stackoverflow answered Nov 18 '13 at 22:37
    # This commented part is the expanded version of the same answer
    # (both versions are given in answer)
    # normalize points
    # Point cn = new Point(c[0] - a[0], c[1] - a[1])
    # Point bn = new Point(b[0] - a[0], b[1] - a[1])

    # double angle = Math.Atan2(bn[1], bn[0]) - Math.Atan2(cn[1], cn[0])
    # double abLength = Math.Sqrt(bn[0]*bn[0] + bn[1]*bn[1])

    # return math.sin(angle)*abLength;
    return (
        math.sin(math.atan2(b[1] - a[1], b[0] - a[0])
                 - math.atan2(c[1] - a[1], c[0] - a[0]))
        * math.sqrt((b[0] - a[0]) * (b[0] - a[0])
                    + (b[1] - a[1]) * (b[1] - a[1]))
    )


def get_distance_vec3_xz(first_pt, second_pt):
    '''
    swizzle to 2d point on xz plane, then get distance
    '''
    return math.sqrt((second_pt[0]-first_pt[0])**2 +
                     (second_pt[2]-first_pt[2])**2)


def get_distance_vec3(first_pt, second_pt):
    return math.sqrt((second_pt[0] - first_pt[0])**2
                     + (second_pt[1] - first_pt[1])**2
                     + (second_pt[2] - first_pt[2])**2)


def get_distance_vec2(first_pt, second_pt):
    return math.sqrt((second_pt[0]-first_pt[0])**2 +
                     (second_pt[1]-first_pt[1])**2)


def get_halfplane_sign(p1, p2, p3):
    '''
    halfplane check (which half) formerly sign
    from <http://stackoverflow.com/questions/2049582
    /how-to-determine-a-point-in-a-2d-triangle>
    edited Oct 18 '14 at 18:52 by msrd0
    answered Jan 12 '10 at 14:27 by Kornel Kisielewicz
    (based on <http://www.gamedev.net/community/forums
    /topic.asp?topic_id=295943>)
    '''
    # return (p1.x - p3.x) * (p2.y - p3.y) -
    #     (p2.x - p3.x) * (p1.y - p3.y)
    return ((p1[0] - p3[0]) * (p2[1] - p3[1])
            - (p2[0] - p3[0]) * (p1[1] - p3[1]))


def PointInTriangle(pos, v1, v2, v3):
    '''
    from <http://stackoverflow.com/questions/2049582
    /how-to-determine-a-point-in-a-2d-triangle>
    edited Oct 18 '14 at 18:52 by msrd0
    answered Jan 12 '10 at 14:27 by Kornel Kisielewicz
    (based on <http://www.gamedev.net/community/forums
    /topic.asp?topic_id=295943>)
    '''
    b1 = get_halfplane_sign(pos, v1, v2) < 0.0
    b2 = get_halfplane_sign(pos, v2, v3) < 0.0
    b3 = get_halfplane_sign(pos, v3, v1) < 0.0
    # WARNING: returns false sometimes on edge, depending whether
    # triangle is clockwise or counter-clockwise
    return (b1 == b2) and (b2 == b3)


def get_pushed_vec3_xz_rad(pos, r, theta):
    # push_x, push_y = (0,0)
    # if r != 0:
    push_x, push_y = get_rect_from_polar_rad(r, theta)
    return pos[0]+push_x, pos[1], pos[2]+push_y


# 3 vector version of Developer's solution to <http://stackoverflow.com
# /questions/2049582/how-to-determine-a-point-in-a-2d-triangle>
# answered Jan 6 '14 at 11:32 by Developer
# uses x and y values
def is_in_triangle_HALFPLANES(check_pt, v0, v1, v2):
    '''
    Check if point check_pt(2) is inside triangle tri(3x2)
    by @Developer
    '''
    a = 1/(-v1[1]*v2[0]+v0[1]*(-v1[0]+v2[0])+v0[0]*(v1[1]-v2[1])+v1[0]*v2[1])
    s = a*(v2[0]*v0[1]-v0[0]*v2[1]+(v2[1]-v0[1])*check_pt[0]+(v0[0]-v2[0])*check_pt[1])
    if s < 0:
        return False
    else:
        t = a*(v0[0]*v1[1]-v1[0]*v0[1]+(v0[1]-v1[1])*check_pt[0]+(v1[0]-v0[0])*check_pt[1])
    return ((t > 0) and (1-s-t > 0))


def is_in_triangle_HALFPLANES_xz(check_pt, v0, v1, v2):
    '''
    Check if point check_pt(2) is inside triangle tri(3x2)
    by @Developer
    '''
    a = 1/(-v1[2]*v2[0]+v0[2]*(-v1[0]+v2[0])+v0[0]*(v1[2]-v2[2])+v1[0]*v2[2])
    s = a*(v2[0]*v0[2]-v0[0]*v2[2]+(v2[2]-v0[2])*check_pt[0]+(v0[0]-v2[0])*check_pt[2])
    if s < 0:
        return False
    else:
        t = a*(v0[0]*v1[2]-v1[0]*v0[2]+(v0[2]-v1[2])*check_pt[0]+(v1[0]-v0[0])*check_pt[2])
    return ((t > 0) and (1-s-t > 0))


def get_y_from_xz(p1, p2, p3, x, z):
    '''
    float calcY(vec3 p1, vec3 p2, vec3 p3, float x, float z) {
    as per <http://stackoverflow.com/questions/5507762
    /how-to-find-z-by-arbitrary-x-y-coordinates-within
    -triangle-if-you-have-triangle>
    edited Jan 21 '15 at 15:07 josh2112
    answered Apr 1 '11 at 0:02 Martin Beckett
    '''
    det = (p2[2] - p3[2]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[2] - p3[2])

    l1 = ((p2[2] - p3[2]) * (x - p3[0]) + (p3[0] - p2[0]) * (z - p3[2])) / det
    l2 = ((p3[2] - p1[2]) * (x - p3[0]) + (p1[0] - p3[0]) * (z - p3[2])) / det
    l3 = 1.0 - l1 - l2

    return l1 * p1[1] + l2 * p2[1] + l3 * p3[1]


def PointInsideTriangle2_vec2(check_pt, tri):
    '''
    check if point check_pt(2) is inside triangle tri(3x2)
    by @Developer:
    solution to <http://stackoverflow.com/questions/2049582
    /how-to-determine-a-point-in-a-2d-triangle>
    answered Jan 6 '14 at 11:32 by Developer
    '''
    a = 1/(-tri[1, 1]*tri[2, 0]+tri[0, 1]*(-tri[1, 0]+tri[2, 0])+tri[0, 0]*(tri[1, 1]-tri[2, 1])+tri[1, 0]*tri[2, 1])
    s = a*(tri[2, 0]*tri[0, 1]-tri[0, 0]*tri[2, 1]+(tri[2, 1]-tri[0, 1])*check_pt[0]+(tri[0, 0]-tri[2, 0])*check_pt[1])
    if s < 0:
        return False
    else:
        t = a*(tri[0, 0]*tri[1, 1]-tri[1, 0]*tri[0, 1]+(tri[0, 1]-tri[1, 1])*check_pt[0]+(tri[1, 0]-tri[0, 0])*check_pt[1])
    return ((t > 0) and (1-s-t > 0))


def is_in_triangle_coords(px, py, p0x, p0y, p1x, p1y, p2x, p2y):
    '''
    IsInTriangle_Barymetric (accurate to global kEpsilon)
    '''
    Area = 1/2*(-p1y*p2x + p0y*(-p1x + p2x) + p0x*(p1y - p2y) + p1x*p2y)
    s = 1/(2*Area)*(p0y*p2x - p0x*p2y + (p2y - p0y)*px + (p0x - p2x)*py)
    t = 1/(2*Area)*(p0x*p1y - p0y*p1x + (p0y - p1y)*px + (p1x - p0x)*py)
    # TODO: fix situation where it fails when clockwise (see discussion
    # at http://stackoverflow.com/questions/2049582
    # /how-to-determine-a-point-in-a-2d-triangle )
    return (s > kEpsilon) and (t > kEpsilon) and (1-s-t > kEpsilon)


def is_in_triangle_xz(check_vec3, a_vec3, b_vec3, c_vec3):
    '''
    IsInTriangle_Barymetric swizzled to xz (uses index 0 and 2 of vec3),
    accurate to global kEpsilon).
    '''
    # kEpsilon = 1.0E-7
    # ^ Adjust to suit.  If you use floats, you'll
    #   probably want something like 1E-7f (added by Poikilos)
    Area = 1/2*(-b_vec3[2]*c_vec3[0] + a_vec3[2]*(-b_vec3[0] + c_vec3[0]) + a_vec3[0]*(b_vec3[2] - c_vec3[2]) + b_vec3[0]*c_vec3[2])
    s = 1/(2*Area)*(a_vec3[2]*c_vec3[0] - a_vec3[0]*c_vec3[2] + (c_vec3[2] - a_vec3[2])*check_vec3[0] + (a_vec3[0] - c_vec3[0])*check_vec3[2])
    t = 1/(2*Area)*(a_vec3[0]*b_vec3[2] - a_vec3[2]*b_vec3[0] + (a_vec3[2] - b_vec3[2])*check_vec3[0] + (b_vec3[0] - a_vec3[0])*check_vec3[2])
    # TODO: fix situation where it fails when clockwise (see discussion
    # at http://stackoverflow.com/questions/2049582
    # /how-to-determine-a-point-in-a-2d-triangle )
    return (s > kEpsilon) and (t > kEpsilon) and (1-s-t > kEpsilon)


def is_in_triangle_vec2(check_vec2, a_vec2, b_vec2, c_vec2):
    '''
    IsInTriangle_Barymetric swizzled to xz (uses index 0 and 2 of vec3),
    accurate to kEpsilon.
    '''
    Area = 1/2*(-b_vec2[1]*c_vec2[0] + a_vec2[1]*(-b_vec2[0] + c_vec2[0]) + a_vec2[0]*(b_vec2[1] - c_vec2[1]) + b_vec2[0]*c_vec2[1])
    if (Area > kEpsilon) or (Area < -kEpsilon):
        s = 1/(2*Area)*(a_vec2[1]*c_vec2[0] - a_vec2[0]*c_vec2[1] + (c_vec2[1] - a_vec2[1])*check_vec2[0] + (a_vec2[0] - c_vec2[0])*check_vec2[1])
        t = 1/(2*Area)*(a_vec2[0]*b_vec2[1] - a_vec2[1]*b_vec2[0] + (a_vec2[1] - b_vec2[1])*check_vec2[0] + (b_vec2[0] - a_vec2[0])*check_vec2[1])
        # TODO: fix situation where it fails when clockwise (see
        # discussion at http://stackoverflow.com/questions/2049582
        # /how-to-determine-a-point-in-a-2d-triangle )
        return (s > kEpsilon) and (t > kEpsilon) and (1-s-t > kEpsilon)
    else:
        return False


'''
class ItemData:  #changed to dict
    name = None
    passive_bumper_command = None
    health_ratio = None

    def __init__(self, bump="obtain"):
        health_ratio = 1.0
        passive_bumper_command = bump
'''


def new_hitbox():
    ret = {}
    ret['minimums'] = [-0.25, -0.25, -0.25]
    ret['maximums'] = [0.25, 0.25, 0.25]
    return ret


def copy_hitbox(o):
    ret = {}
    ret['minimums'] = copy.deepcopy(o['minimums'])
    ret['maximums'] = copy.deepcopy(o['maximums'])
    return ret


def hitbox_contains_vec2(o, px):
    '''
    See if top view location is inside 3d location
    (map y of px to z of o, in other words, compare px[1] to o[*][2])
    '''
    return (px[0] >= o['minimums'][0] and px[0] <= o['maximums'][0]
            and px[1] >= o['minimums'][2] and px[1] <= o['maximums'][2])


def hitbox_contains_vec3(o, pos):
    return (pos[0] >= o['minimums'][0]
            and pos[0] <= o['maximums'][0]
            and pos[1] >= o['minimums'][1]
            and pos[1] <= o['maximums'][1]
            and pos[2] >= o['minimums'][2]
            and pos[2] <= o['maximums'][2])


settings['templates']['properties']['hitbox'] = new_hitbox()


class PyGlop:
    '''
    PyGlop defines a single OpenGL-ready object. PyGlops should be used
    for importing, since one mesh file (such as obj) can contain several
    meshes. PyGlops handles the 3D scene.
    '''

    def __init__(self, default_templates=None):
        # update copy constructor if adding/changing copyable members
        self.name = None  # object name such as from OBJ's 'o' statement
        self.source_path = None
        # ^ required so that meshdata objects can be
        #   uniquely identified (where more than one
        #   file has same object name)
        self.properties = None
        # ^ dictionary of properties (keys such as usemtl)
        self.vertex_depth = None
        self.material = None
        self._min_coords = None
        # ^ bounding cube minimums in local coordinates
        self._max_coords = None
        # ^ bounding cube maximums in local coordinates
        self._pivot_point = None
        # TODO: (?) eliminate _pivot_point--instead always use
        # 0,0,0 and move vertices to change pivot;
        # currently calculated from average of vertices
        # if was imported from obj
        self.foot_reach = None
        # ^ distance from center (such as root bone) to floor
        self.eye_height = None  # distance from floor
        self.item_dict = None
        self.projectile_dict = None
        # ^ TEMPORARY, only while in air, but based on
        # item_dict (only uses item_dict[key] for key
        # in item_dict['projectile_keys'])
        self.actor_dict = None
        self.bump_enable = None
        self.reach_radius = None
        self.in_range_indices = None
        # ^ ONLY set if bumpable (not bumper)
        self._cached_floor_y = None
        self.infinite_inventory_enable = None
        self.look_target_glop = None
        self.visible_enable = None
        self.vertex_format = None
        self.vertices = None
        self.indices = None
        # self.opacity = None
        # ^ moved to material['diffuse_color'] 4th channel

        # region runtime variables
        self.glop_index = None  # set by add_glop
        # endregion runtime variables

        # region vars based on OpenGL ES 1.1 MOVED TO material
        # self.ambient_color = None  # vec4
        # self.diffuse_color = None  # vec4
        # self.specular_color = None  # vec4
        # # self.emissive_color = None  # vec4
        # self.specular_exponent = None  # float
        # endregion vars based on OpenGL ES 1.1 MOVED TO material

        # region calculated from vertex_format
        self._POSITION_OFFSET = None
        self._NORMAL_OFFSET = None
        self._TEXCOORD0_OFFSET = None
        self._TEXCOORD1_OFFSET = None
        self.COLOR_OFFSET = None
        self.POSITION_INDEX = None
        self.NORMAL_INDEX = None
        self.TEXCOORD0_INDEX = None
        self.TEXCOORD1_INDEX = None
        self.COLOR_INDEX = None
        # endregion calculated from vertex_format

        self._init_glop(default_templates=default_templates)

    def _init_glop(self, default_templates=None):
        # formerly __init__ but that would interfere with super
        # if subclass has multiple inheritance
        try:
            self.properties = {}
            self.state = {}
            if default_templates is None:
                default_templates = settings['templates']
                if get_verbose_enable():
                    print("[ PyGlop ] (verbose message in _init_glop) "
                          "missing default_templates param. Try setting"
                          " to dict with required"
                          " variables, such as the"
                          " settings['templates'] global"
                          " (using that for now)")
            if default_templates is not None:
                if len(default_templates) > 0:
                    if 'state' in default_templates:
                        for key in default_templates['state']:
                            self.state[key] = \
                                default_templates['state'][key]
                    else:
                        print("[ PyGlop ] WARNING in _init_glop:"
                              "default_templates has no 'state'"
                              " key")
                    if 'properties' in default_templates:
                        for key in default_templates['properties']:
                            self.properties[key] = \
                                default_templates['properties'][key]
                    else:
                        print("[ PyGlop ] WARNING in _init_glop:"
                              "default_templates has no 'properties'"
                              " key")
                else:
                    print("[ PyGlop ] WARNING in _init_glop: "
                          "default_templates has no keys "
                          "Unless you subclassed Pyglops"
                          "and know what you don't need, this"
                          "could cause missing dict crashes")
            # formerly in MeshData:
            # order MUST match V_POS_INDEX etc above

            # a_position: Munshi prefers vec4 (Kivy prefers vec3)
            # a_texcoord0: Munshi prefers vec4 (Kivy prefers vec2);
            #  vTexCoord0; available if enable_tex[0] is true
            # a_texcoord1: Munshi prefers vec4 (Kivy prefers vec2);
            #  available if enable_tex[1] is true
            # a_color: vColor (diffuse color of vertex)
            # a_normal: vNormal; Munshi prefers vec3 (Kivy also
            #  prefers vec3)
            self.vertex_format = [(b'a_position', 4, 'float'),
                                  (b'a_texcoord0', 4, 'float'),
                                  (b'a_texcoord1', 4, 'float'),
                                  (b'a_color', 4, 'float'),
                                  (b'a_normal', 3, 'float')
                                  ]
            # calculate vertex_depth etc:
            self.on_vertex_format_change()

            self.indices = []
            # ^ list of tris (1 big linear list of indices)
            # Default basic material of this glop
            self.material = new_material()
            self.material['diffuse_color'] = (1.0, 1.0, 1.0, 1.0)
            # ^ overlay vertex color onto this using vertex alpha
            self.material['ambient_color'] = (0.0, 0.0, 0.0, 1.0)
            self.material['specular_color'] = (1.0, 1.0, 1.0, 1.0)
            self.material['specular_coefficient'] = 16.0
            # self.material['opacity'] = 1.0

            # TODO: find out where this code goes
            # (was here for unknown reason)
            # if result is None:
            #     print("WARNING: no material for Glop named '" +
            #           str(self.name) + "' (NOT YET IMPLEMENTED)")
            # return result
        except:
            print("[ PyGlop ] ERROR--_init_glop could not finish:")
            view_traceback()

    def __str__(self):
        return (str(type(self)) + " named " + str(self.name) + " at "
                + str(self.get_pos()))

    def get_pos(self):
        print("[ PyGlop ] ERROR: implement get_pos in subclass")
        return None

    def set_pos(self, pos):
        print("[ PyGlop ] ERROR: implement set_pos in subclass")

    def get_angle(self, axis_i):
        print("[ PyGlop ] ERROR: implement get_angle in subclass")
        return None

    def set_angle(self, axis_index, angle):
        print("[ PyGlop ] ERROR: implement set_angle in subclass")

    def get_angles(self):
        print("[ PyGlop ] ERROR: implement get_angles in subclass")
        return None

    def set_angles(self, angles):
        print("[ PyGlop ] ERROR: implement set_angles in subclass")

    def get_is_glop(self, o):
        result = False
        try:
            result = o._get_is_glop()
        except:
            pass
        return result

    def get_class_name(self):
        return "PyGlop"

    def _get_is_glop(self):
        # use this for duck-typing (try, and if exception, not glop)
        return True

    def copy(self, depth=0):
        '''
        copy should have override in subclass that calls copy_as_subclass
        then adds subclass-specific values to that result
        '''
        return self.copy_as_subclass(self.new_glop_method,
                                     depth=depth+1)

    def get_owner_name(self):
        result = None
        if self.item_dict is not None:
            result = self.item_dict.get('owner')
        else:
            print("[ PyGlop ] WARNING: tried to get owner name of"
                  " non-item")
        return result

    def get_owner_key(self):
        result = None
        if self.item_dict is not None:
            result = self.item_dict.get('owner_key')
        else:
            print("[ PyGlop ] WARNING: tried to get owner index of"
                  "non-item")
        return result

    def copy_as_subclass(self, new_glop_method,
                         ref_my_verts_enable=False, ancestors=[],
                         depth=0):
        target = None
        ancestors.append(self)
        if get_verbose_enable():
            print("[ PyGlop ] " + "  " * depth + "copy_as_subclass" +
                  " {'name':" + str(self.name) + "}")
        try:
            target = new_glop_method()
            target.name = self.name
            # ^ object name such as from OBJ's
            #   'o' statement
            target.source_path = self.source_path
            # ^ required so that meshdata objects can be uniquely
            # identified (where more than one file has same
            # object name)
            if self.properties is not None:
                target.properties = copy.deepcopy(self.properties)
                # ^ dictionary of properties (keys such as usemtl)
            target.vertex_depth = self.vertex_depth
            if self.material is not None:
                target.material = copy_material(self.material, depth=depth+1)
            target._min_coords = self._min_coords
            # ^ bounding cube minimums in local coordinates
            target._max_coords = self._max_coords
            # ^ bounding cube maximums in local coordinates
            target._pivot_point = self._pivot_point
            # TODO: (?) eliminate _pivot_point--instead always
            # use 0,0,0 and move vertices to change pivot; currently
            # calculated from average of vertices if was imported
            # from obj
            target.foot_reach = self.foot_reach
            # ^ distance from center (such as root bone) to floor
            target.properties['eye_height'] = \
                self.properties['eye_height']
            # ^ distance from floor
            target.properties['hit_radius'] = \
                self.properties['hit_radius']
            oa_len = len(ancestors)
            target.item_dict = self.deepcopy_with_my_type(
                self.item_dict,
                ancestors=ancestors[:oa_len],
                depth=depth+1
            )  # DOES return None if sent None
            target.projectile_dict = self.deepcopy_with_my_type(
                self.projectile_dict,
                ancestors=ancestors[:oa_len],
                depth=depth+1)
            # ^ NOTE: only exists while in air, and
            #   based on item_dict
            target.actor_dict = self.deepcopy_with_my_type(
                self.actor_dict,
                ancestors=ancestors[:oa_len],
                depth=depth+1)
            target.properties['bump_enable'] = \
                self.properties['bump_enable']
            target.properties['reach_radius'] = \
                self.properties['reach_radius']
            # target.state['in_range_indices'] = []
            # self.state['in_range_indices']
            target.properties['physics_enable'] = \
                self.properties['physics_enable']
            target.state['velocity'][0] = self.state['velocity'][0]
            target.state['velocity'][1] = self.state['velocity'][1]
            target.state['velocity'][2] = self.state['velocity'][2]
            # target._cached_floor_y = self._cached_floor_y
            target.properties['infinite_inventory_enable'] = \
                self.properties['infinite_inventory_enable']
            target.look_target_glop = self.look_target_glop
            # ^ by reference since is a reference to begin with
            if self.properties['hitbox'] is not None:
                target.properties['hitbox'] = \
                    self.properties['hitbox'].deepcopy()
            target.state['visible_enable'] = \
                self.state['visible_enable']
            target.vertex_format = copy.deepcopy(self.vertex_format)
            if ref_my_verts_enable:
                target.vertices = self.vertices
                target.indices = self.indices
            else:
                target.vertices = copy.deepcopy(self.vertices)
                target.indices = copy.deepcopy(self.indices)
        except:
            print("[ PyGlop ] " + "  " * depth + "ERROR--could not"
                  " finish copy_as_subclass:")
            view_traceback()
        return target

    def deepcopy_with_my_type(self, old_dict, ref_my_type_enable=False,
                              ancestors=[], depth=0,
                              skip_my_type_enable=False):
        '''
        prevent pickling failure by using this to copy dicts AND
        lists that contain members that are my type
        '''
        new_dict = None
        # if type(old_dict) is dict:
        new_dict = None
        keys = None
        ancestors.append(old_dict)
        oa_len = len(ancestors)
        od = old_dict
        rmte = ref_my_type_enable
        if od is not None:
            if isinstance(od, list):
                if len(od) > 0:
                    # new_dict = [None]*len(od)
                    # new_dict[0] = "uhoh"
                    # if len(new_dict)>1 and new_dict[1]=="uhoh":
                    #     print(
                    #         "[ PyGlop ] ERROR in "
                    #         "deepcopy_with_my_type: failed to "
                    #         "produce unique list items!")
                    #     sys.exit(1)
                    # new_dict[0] = None
                    new_dict = []
                    keys = range(0, len(od))
                else:
                    new_dict = []
                    keys = []
            elif isinstance(od, dict):
                new_dict = {}
                keys = od.keys()
            if keys is not None:
                # will fail if neither dict nor list (let it fail)
                for this_key in keys:
                    ov = od[this_key]  # old value
                    if self.get_is_glop(ov):
                        if not skip_my_type_enable:
                            # NOTE: the type for both sides of the check
                            # above are always the subclass if running
                            # this from a subclass as demonstrated by:
                            # print("the type of old dict "
                            #       + str(type(ov))
                            #       + " == " + str(type(self)))
                            if rmte:
                                if isinstance(new_dict, dict):
                                    new_dict[this_key] = ov
                                else:
                                    new_dict.append(ov)
                            else:
                                copy_of_var = None
                                if ov not in ancestors:
                                    copy_of_var = ov.copy_as_subclass(
                                        ov.new_glop_method,
                                        ref_my_verts_enable=rmte,
                                        depth=depth+1,
                                        ancestors=ancestors[:oa_len])
                                else:
                                    print("[ PyGlop ] " + "  " * depth +
                                          "WARNING: avoiding infinite" +
                                          " recursion at depth " +
                                          str(depth) +
                                          " by refusing to " +
                                          "copy_as_subclass since" +
                                          " item at '" +
                                          str(this_key) + "' is a " +
                                          "self-reference found in " +
                                          str(len(ancestors)) +
                                          " ancestors: " +
                                          str(ancestors))
                                if isinstance(new_dict, dict):
                                    new_dict[this_key] = copy_of_var
                                else:
                                    new_dict.append(copy_of_var)
                                    # ^ unnecessary since preallocated
                                    #   now
                        # else do nothing, leave None (or not in dict)
                    elif isinstance(ov, list):
                        this_copy = self.deepcopy_with_my_type(
                            ov,
                            ref_my_type_enable=rmte,
                            depth=depth+1,
                            ancestors=ancestors[:oa_len])
                        if isinstance(new_dict, dict):
                            new_dict[this_key] = this_copy
                        else:
                            new_dict.append(this_copy)
                    elif isinstance(ov, dict):
                        this_copy = self.deepcopy_with_my_type(
                            ov,
                            ref_my_type_enable=rmte,
                            depth=depth+1,
                            ancestors=ancestors[:oa_len])
                        if isinstance(new_dict, dict):
                            new_dict[this_key] = this_copy
                        else:
                            new_dict.append(this_copy)
                    else:
                        # NOTE: both value types and unknown classes
                        # end up here
                        try:
                            '''
                            if get_verbose_enable():
                                print("[ PyGlop ] " + "  " * depth +
                                      "Calling copy method for " +
                                      str(type(ov)) +
                                      " object at key " +
                                      str(this_key))
                            '''
                            this_copy = ov.copy()
                            if isinstance(new_dict, dict):
                                new_dict[this_key] = this_copy
                            else:
                                new_dict.append(this_copy)
                        except:
                            '''
                            if get_verbose_enable():
                                print("[ PyGlop ] " + "  " * depth +
                                      "used '=' instead for " +
                                      str(type(ov)) +
                                      " object at key " +
                                      str(this_key))
                            '''
                            this_copy = ov
                            if isinstance(new_dict, dict):
                                new_dict[this_key] = this_copy
                            else:
                                new_dict.append(this_copy)
                        '''
                        try:
                            if get_verbose_enable():
                                print("[ PyGlop ] Calling " +
                                      "copy.deepcopy on " +
                                      str(type(ov)) +
                                      " at key " + str(this_key))
                            new_dict[this_key] = copy.deepcopy(ov)
                        except:
                            try:
                                new_dict[this_key] = ov
                                print("[ PyGlop ] WARNING:" +
                                      " deepcopy_with_my_type " +
                                      "failed to deepcopy " +
                                      type(ov).__name__ + " '" +
                                      str(ov) +
                                      "' at '" +
                                      str(this_key) + "' so using" +
                                      " '=' instead")
                            except:
                                print("[ PyGlop ] ERROR:" +
                                      " deepcopy_with_my_type " +
                                      "failed to deepcopy " +
                                      str(type(ov)) +
                                      " '" + str(ov) + "' at '" +
                                      str(this_key) + "' in " +
                                      str(type(new_dict)) + " but" +
                                      " '=' also failed")
                                view_traceback()
                        '''
            else:  # keys is None
                if isinstance(od, type(self)):
                    print(
                        "[ PyGlop ] " + "  " * depth + "WARNING:"
                        " deepcopy_with_my_type is calling copy on"
                        " old_dict since is " + str(type(od))
                        + " (similar to using .copy instead of"
                        " deepcopy_with_my_type)"
                    )
                    new_dict = od.copy_as_subclass(
                        self.new_glop_method,
                        depth=depth+1,
                        ancestors=ancestors[:oa_len])
                else:
                    try:
                        # print("[ PyGlop ] " + "  " * depth +
                        #       "Calling" + " copy on " + str(type(od)))
                        new_dict = od.copy()
                    except:
                        # if get_verbose_enable():
                        #     print("[ PyGlop ] "+"  " * depth +
                        #           "using" + " '=' for " +
                        #           str(type(od)))
                        new_dict = od
                        # FIXME: Is it ok to assume it is a value type here?
        return new_dict

    def get_has_hit_range(self):
        # print("get_has_hit_range should be implemented by subclass.")
        return (self.properties.get('hitbox') is not None) and \
               (self.properties.get('hit_radius') is not None)

    def calculate_hit_range(self):
        print("calculate_hit_range should be implemented by subclass.")
        print("  (setting hitbox to None to avoid using default)")
        self.properties['hitbox'] = None

    def on_process_ai(self, glop_index):
        '''
        This should be implemented in the subclass. It determines what
        the glop should do.
        '''
        pass

    def apply_vertex_offset(self, this_point):
        sv = self.vertices
        if sv is None:
            print("[ PyGlop ] WARNING in apply_vertex_offset: "
                  " self.vertices is None for " + str(self.name))
            return

        vertex_count = int(len(sv)/self.vertex_depth)
        v_offset = 0
        hb = self.properties.get('hitbox')
        if hb is not None:
            for i in range(0, 3):
                # intentionally set to rediculously far in
                # opposite direction:
                hb['minimums'][i] = sys.maxsize
                hb['maximums'][i] = -sys.maxsize
        phr = self.properties.get('hit_radius')
        hr = 0.0  # use separate var to reduce dict access and if's
        if phr is not None:
            hr = phr
        for v_number in range(0, vertex_count):
            vo = v_offset+self._POSITION_OFFSET
            for i in range(0, 3):
                sv[vo+i] -= this_point[i]
                if hb is not None:
                    if sv[vo+i] < hb['minimums'][i]:
                        hb['minimums'][i] = sv[vo+i]
                    if sv[vo+i] > hb['maximums'][i]:
                        hb['maximums'][i] = sv[vo+i]
            this_vertex_relative_distance = \
                get_distance_vec3(sv[vo:], this_point)
            if this_vertex_relative_distance > hr:
                hr = this_vertex_relative_distance
                # self.properties['hit_radius'] = hr
                # ^ don't change the object--allow blank hr
            # sv[vo+0] -= this_point[0]
            # sv[vo+1] -= this_point[1]
            # sv[vo+2] -= this_point[2]
            v_offset += self.vertex_depth
        if phr is not None:
            phr = hr
            self.properties['hit_radius'] = phr
        else:
            print("[ PyGlop ] WARNING in apply_vertex_offset:"
                  " hit_radius will not change since it isn't present.")

    def apply_pivot(self):
        self.apply_vertex_offset(self._pivot_point)
        self._pivot_point = (0.0, 0.0, 0.0)

    def look_at(self, this_glop):
        print("WARNING: look_at should be implemented by subclass"
              "which has rotation angle(s) or matr(ix/ices)")

    def look_at_pos(self, pos):
        print("WARNING: look_at_pos should be implemented by"
              "subclass which has rotation angle(s) or matr(ix/ices)")

    def is_linked_as(self, this_glop, as_rel):
        return self.get_link_as(this_glop, as_rel)

    def get_link_as(self, this_glop, as_rel):
        '''
        Get index of parent ONLY if r_type (relationship type)==as_rel
        '''
        result = -1
        for i in range(len(self.state['links'])):
            rel = self.state['links'][i]
            if rel['r_type'] == as_rel:
                if rel['state']['parent_glop'] is this_glop:
                    result = i
                    break
        return result

    def get_link_and_type(self, this_glop):
        '''
        Get a tuple with: index (-1 if None) and relationship type
        '''
        result = -1, None
        for i in range(len(self.state['links'])):
            rel = self.state['links'][i]
            if rel['state']['parent_glop'] is this_glop:
                result = i, rel['r_type']
                break
        return result

    def has_item_with_any_use(self, uses):
        result = False
        if self.actor_dict is not None:
            for item_dict in self.actor_dict['inventory_items']:
                if 'uses' in item_dict:
                    for this_use in item_dict['uses']:
                        if this_use in uses:
                            result = True
                            break
        return result

    def find_item_with_any_use(self, uses):
        '''
        Get a tuple containing inventory index in
        actor_dict['inventory_items'] AND use string that is in uses
        '''
        result = -1, None
        if self.actor_dict is not None:
            for item_dict in self.actor_dict['inventory_items']:
                if 'uses' in item_dict:
                    for i in range(len(item_dict['uses'])):
                        if item_dict['uses'][i] in uses:
                            result = i, item_dict['uses'][i]
                            break
        return result

    def push_glop_item(self, item_glop, this_glop_index,
                       sender_name="unknown"):
        '''
        _run_command automatically runs this.
        _internal_bump_glop (which usually occurs via _run_*) usually
        runs _run_command.
        Also, add_actor_weapon adds a non-glop weapon and calls this.
        '''
        item_dict = item_glop.item_dict
        result = self.push_item(
            item_dict,
            sender_name="push_glop_item via "+sender_name
        )
        result['calling_method'] = "push_glop_item"
        if result['fit_enable']:
            i, r_type = item_glop.get_link_and_type(self)
            if i <= -1:  # not is_linked_as(item_glop, "carry"):
                if item_dict.get('cooldown') is not None:
                    if item_dict['state'].get('last_used_time') is None:
                        # make item ready on first pickup:
                        item_dict['state']['last_used_time'] = \
                            time.time() - item_dict['cooldown']
                rel = {}
                rel['state'] = {}
                rel['state']['parent_glop'] = self
                rel['state']['parent_index'] = self.glop_index
                rel['r_type'] = "carry"
                item_glop.properties['physics_enable'] = False
                item_glop.state['links'].append(rel)
            else:
                print(
                    "[ KivyGlop ] WARNING: '{}' {} item '{}' " +
                    ", so not setting '{}' (attempted by {})"
                    "".format(self.name, r_type, item_glop.name,
                              self.name, sender_name)
                )
                if item_dict is not None:
                    if 'owner_key' in item_dict:
                        print("             (owner is ['{}'] {})"
                              "".format(item_dict['owner_key'],
                                        item_dict['owner']))
                    else:
                        print("             (no owner)")
                else:
                    print("             (ERROR: not an item)")
        return result

    def pop_glop_item(self, item_glop_index):
        '''
        Get a select item event dict which includes the item if
        successful.
        '''
        sied = None
        # ^ select item event dict
        # sied['fit_enable'] = False
        try:
            ad = self.actor_dict
            if ad is not None:
                if item_glop_index < \
                        len(ad['inventory_items']) and \
                        item_glop_index >= 0:
                    # sied['fit_enable'] = True
                    # ad['inventory_items'].pop(item_glop_index)
                    ad['inventory_items'][item_glop_index] = \
                        EMPTY_ITEM
                    if item_glop_index == 0:
                        sied = self.sel_next_inv_slot(True)
                    else:
                        sied = self.sel_next_inv_slot(False)
                    if sied is not None:
                        if 'calling_method' in sied:
                            sied['calling_method'] += \
                                " from pop_glop_item"
                        else:
                            sied['calling_method'] = \
                                "from pop_glop_item"
            else:
                print("[ PyGlop ] ERROR: cannot give item to"
                      " non-actor (only add actors to"
                      " self._bumper_indices; add items to"
                      " self._bumpable_indices instead)")
        except:
            print("[ PyGlop ] Could not finish pop_glop_item:")
            view_traceback()
        return sied

    def find_item_inventory_index(self, name):
        result = -1
        ad = self.actor_dict
        if ad is not None:
            for i in range(0, len(ad['inventory_items'])):
                if (ad['inventory_items'][i] is not None) and \
                   (ad['inventory_items'][i]['name'] == name):
                    result = i
                    break
        else:
            print("[ PyGlop ] error in find_item_inventory_index:"
                  " you tried to check for items on a non-actor glop")
        return result

    def has_item(self, name):
        result = False
        ad = self.actor_dict
        if ad is None:
            print("[ PyGlop ] error in has_item: you tried to check"
                  " for items on a non-actor glop")
            return result
        for i in range(0, len(ad['inventory_items'])):
            if (ad['inventory_items'][i] is not None) and \
               (ad['inventory_items'][i]['name'] == name):
                result = True
                break
        return result

    def push_item(self, item_dict, sender_name="unknown"):
        '''
        Your program can override this method for custom inventory
        layout (use
        `self.actor_dict['inventory_items'].append(item_dict)` and you
        must return a dict containing fit_enable boolean for whether
        item was obtained and should be attached).

        Keys in returned select item event dict:
        fit_enable -- stays false if inventory full
        fit_at -- stays -1 if inventory full
        '''
        if get_verbose_enable():
            print('* push_item: {} from '.format(item_dict, sender_name))
        sied = {}
        # ^ select item event dict
        sied['glop_index'] = self.glop_index
        sied['fit_enable'] = False  # stay False only if inventory full
        sied['fit_at'] = -1
        if item_dict is not None:
            if item_dict.get('owner_key') is None:
                pass
            else:
                print("[ PyGlop ] WARNING in push_item: owner_key"
                      " is already " + str(item_dict['owner_key'])
                      + " but I am " + str(self.glop_index))
            for i in range(0, len(self.actor_dict['inventory_items'])):
                if self.actor_dict['inventory_items'][i] is None or \
                   self.actor_dict['inventory_items'][i]['name'] == \
                   EMPTY_ITEM['name']:
                    self.actor_dict['inventory_items'][i] = item_dict
                    sied['fit_enable'] = True
                    sied['fit_at'] = i
                    if get_verbose_enable():
                        print("[ PyGlop ] (verbose message) actor "
                              + str(self.name)
                              + " obtained item in slot "
                              + str(i))  # +": " + str(item_dict))
                    break
            if self.properties['infinite_inventory_enable']:
                if not sied['fit_enable']:
                    self.actor_dict['inventory_items'].append(item_dict)
                    sied['fit_at'] = \
                        len(self.actor_dict['inventory_items']) - 1
                    # print("[ PyGlop ] (verbose message) obtained"
                    #       "item in new slot: "+str(item_dict))
                    if get_verbose_enable():
                        print("[ PyGlop ] (verbose message) actor {}"
                              " obtained {} in new slot {}"
                              "".format(self.name, item_dict['name'],
                                        sied['fit_at']))
                    sied['fit_enable'] = True
            if sied['fit_enable']:
                if self.actor_dict['inventory_index'] < 0:
                    # Auto-select a new item if no slot was selected.
                    self.actor_dict['inventory_index'] = sied['fit_at']
                this_item_dict = \
                    self.actor_dict['inventory_items'][sied['fit_at']]
                name = ""
                proper_name = ""
                sied['selected_index'] = \
                    self.actor_dict['inventory_index']
                if 'name' in this_item_dict:
                    name = this_item_dict['name']
                sied['name'] = name
                if 'glop_name' in this_item_dict:
                    proper_name = this_item_dict['glop_name']
                sied['proper_name'] = proper_name
                sied['calling_method'] = "push_item"
        else:
            print("[ PyGlop ] ERROR in push_item: {} tried to add None"
                  " to inventory"
                  "".format(sender_name))
        return sied

    def sel_next_inv_slot(self, is_forward):
        '''
        Change the slot and get the select item event dict.
        '''
        sied = {}  # select item event dict
        sied['glop_index'] = self.glop_index
        ad = self.actor_dict
        delta = 1
        if not is_forward:
            delta = -1

        if 'Player' not in debug_dict:
            debug_dict['Player'] = {}

        if ad is None:
            sied['error'] = (
                "[ PyGlop ] ERROR in sel_next_inv_slot: "
                " cannot perform function on non-actor"
            )
            print("[ PyGlop ] ERROR in sel_next_inv_slot: "
                  " cannot perform function on non-actor")
            return sied

        if len(ad['inventory_items']) < 1:
            sied['fit_enable'] = False
            debug_dict['Player']['inv scroll msg'] = "0 items."
            return sied

        sied['fit_enable'] = True
        ad['inventory_index'] += delta
        if ad['inventory_index'] < 0:
            ad['inventory_index'] = len(ad['inventory_items']) - 1
        elif ad['inventory_index'] >= len(ad['inventory_items']):
            ad['inventory_index'] = 0
        this_item_dict = ad['inventory_items'][ad['inventory_index']]
        name = ""
        proper_name = ""
        sied['inventory_index'] = ad['inventory_index']
        if 'glop_name' in this_item_dict:
            proper_name = this_item_dict['glop_name']
        sied['proper_name'] = proper_name
        if 'name' in this_item_dict:
            name = this_item_dict['name']
        sied['name'] = name
        # print("item event: "+str(sied))
        sied['calling_method'] = "sel_next_inv_slot"
        # print("Selected " + this_item_dict['name'] + " " +
        #     proper_name + " in slot " +
        #     str(ad['inventory_index']))
        item_count = 0
        for index in range(0, len(ad['inventory_items'])):
            if (ad['inventory_items'][index]['name']
                    != EMPTY_ITEM['name']):
                item_count += 1
        debug_dict['Player']['inv scroll msg'] = \
            str(item_count) + " item(s)."
        sied['item_count'] = item_count
        return sied

    def _on_change_pivot(self, previous_point=(0.0, 0.0, 0.0),
                         class_name="PyGlop"):
        '''
        This should be implemented by a subclass.
        '''
        if class_name == "PyGlop":
            print("[ PyGlop ] WARNING in _on_change_pivot:"
                  " your subclass should implement"
                  " _on_change_pivot")
        pass

    def get_context(self):
        '''
        Implement this in the subclass since it depends on the graphics
        implementation.
        '''
        print("WARNING: get_context should be defined by a subclass")
        return False

    def transform_pivot_to_geometry(self):
        previous_point = self._pivot_point
        self._pivot_point = self.get_center_average_of_vertices()
        self._on_change_pivot(previous_point=previous_point)

    def find_file(self, rel_or_abs_path, what="file"):
        if rel_or_abs_path is None:
            return None
        result = rel_or_abs_path
        if os.path.exists(result):
            return result
        if self.source_path is None:
            print("[ PyGlop ] ERROR in"
                  " find_file:"
                  " \"{}\" is missing (and the glop doesn't"
                  " have a source_path, so no parent folder"
                  "was checked).".format(what))
            return None
        mesh_path = os.path.abspath(self.source_path)
        # ^ Use self.source_path in case the texture is in the
        #   same directory as the mesh!
        if not os.path.isfile(mesh_path):
            print("The {} \"{}\" is missing and the mesh"
                  " \"{}\" doesn't exist for generating a"
                  " relative path for the glop named \"{}\"."
                  "".format(what, result, mesh_path, self.name))
            return None
        try_path = os.path.join(os.path.dirname(mesh_path), result)
        if not os.path.isfile(try_path):
            print("A texture is missing (tried"
                  " \"{}\") for the glop named \"{}\"."
                  "".format(try_path, self.name))
            return None
        result = try_path
        return result

    def get_texture_diffuse_path(self):
        # ^ formerly getTextureFileName(self):
        if self.material is None:
            return None

        properties = self.material.get('properties')
        if properties is None:
            return None
        diffuse_path = properties.get('diffuse_path')
        return self.find_file(diffuse_path, what="diffuse texture")

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
        self._min_coords = [None, None, None]
        self._max_coords = [None, None, None]
        participle = "initializing"
        vd = self.vertex_depth
        vs = self.vertices
        try:
            if (vs is not None):
                participle = "accessing vertices"
                for i in range(0, int(len(vs)/vd)):
                    for axI in range(0, 3):  # axis index
                        if self._min_coords[axI] is None or \
                                vs[i*vd+axI] < self._min_coords[axI]:
                            self._min_coords[axI] = vs[i*vd+axI]
                        if self._max_coords[axI] is None or \
                                vs[i*vd+axI] > self._max_coords[axI]:
                            self._max_coords[axI] = vs[i*vd+axI]
        except:  # Exception as e:
            print("Could not finish " + participle
                  + " in recalculate_bounds: ")
            view_traceback()

    def get_center_average_of_vertices(self):
        # results = (0.0,0.0,0.0)
        totals = list()
        counts = list()
        results = list()
        vd = self.vertex_depth
        vf = self.vertex_format
        vert_len = vf[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        vs = self.vertices
        for i in range(0, vert_len):
            if i < 3:
                results.append(0.0)
            else:
                results.append(1.0)
                # ^ 4th index (index 3) must be
                # 1.0 for matrix math to work
                # correctly
        participle = "before initializing"
        try:
            totals.append(0.0)
            totals.append(0.0)
            totals.append(0.0)
            counts.append(0)
            counts.append(0)
            counts.append(0)
            if (vs is not None):
                participle = "accessing vertices"
                for i in range(0, int(len(vs)/vd)):
                    for axI in range(0, 3):
                        participle = "accessing vertex axis"
                        if (vs[i*vd+axI] < 0):
                            participle = "accessing totals"
                            totals[axI] += vs[i*vd+axI]
                            participle = "accessing vertex count"
                            counts[axI] += 1
                        else:
                            participle = "accessing totals"
                            totals[axI] += vs[i*vd+axI]
                            participle = "accessing vertex count"
                            counts[axI] += 1
            for axI in range(0, 3):
                participle = "accessing final counts"
                if (counts[axI] > 0):
                    participle = "calculating results"
                    results[axI] = \
                        totals[axI] / counts[axI]
        except:  # Exception as e:
            print("Could not finish " + participle
                  + " in get_center_average_of_vertices: ")
            view_traceback()

        return tuple(results)

    def set_textures_from_wmaterial(self, wmaterial):
        # print("")
        # print("set_textures_from_wmaterial...")
        # print("")
        f_name = "set_textures_from_wmaterial"
        try:
            opacity = None
            if 'd' in wmaterial:
                opacity = float(wmaterial['d']['values'][0])
            elif 'Tr' in wmaterial:
                opacity = 1.0 - float(wmaterial['Tr']['values'][0])
            if opacity is not None:
                if 'Kd' in wmaterial:
                    Kd = wmaterial['Kd']['values']
                    self.material['diffuse_color'] = \
                        get_fvec4_from_svec3(Kd, opacity)
            else:
                if 'Kd' in wmaterial:
                    Kd = wmaterial['Kd']['values']
                    self.material['diffuse_color'] = \
                        get_fvec4_from_svec_any_len(Kd)
            # self.material['diffuse_color'] = \
            #     [float(v) for v in self.material['diffuse_color']]
            if 'Ka' in wmaterial:
                Ka = wmaterial['Ka']['values']
                self.material['ambient_color'] = \
                    get_fvec4_from_svec_any_len(Ka)
            if 'Ks' in wmaterial:
                Ks = wmaterial['Ks']['values']
                self.material['specular_color'] = \
                    get_fvec4_from_svec_any_len(Ks)
            if 'Ns' in wmaterial:
                Ns = wmaterial['Ns']['values']
                self.material['specular_coefficient'] = float(Ns[0])
            # TODO: store as diffuse color alpha instead:
            # self.opacity = wmaterial.get('d')
            # TODO: store as diffuse color alpha instead:
            # if self.opacity is None:
            # TODO: store as diffuse color alpha instead:
            # self.opacity = 1.0 - float(wmaterial.get('Tr', 0.0))
            smp = self.material.get('properties')
            if 'map_Ka' in wmaterial:
                smp['ambient_path'] = wmaterial['map_Ka']['values'][0]
            if 'map_Kd' in wmaterial:
                smp['diffuse_path'] = wmaterial['map_Kd']['values'][0]
                # print("  NOTE: diffuse_path: " + smp['diffuse_path'])
            # else:
            #     print("  WARNING: " + str(self.name) + " has no" +
            #           " map_Kd among material keys " +
            #           ','.join(wmaterial.keys()))
            if 'map_Ks' in wmaterial:
                smp['specular_path'] = wmaterial['map_Ks']['values'][0]
            if 'map_Ns' in wmaterial:
                smp['specular_coefficient_path'] = \
                    wmaterial['map_Ns']['values'][0]
            if 'map_d' in wmaterial:
                smp['opacity_path'] = wmaterial['map_d']['values'][0]
            if 'map_Tr' in wmaterial:
                smp['transparency_path'] = \
                    wmaterial['map_Tr']['values'][0]
                print("[ PyGlop ] Non-standard map_Tr command found"
                      "--inverted opacity map is not yet implemented.")
            if 'bump' in wmaterial:
                smp['bump_path'] = wmaterial['bump']['values'][0]
            if 'disp' in wmaterial:
                smp['displacement_path'] = \
                    wmaterial['disp']['values'][0]
        except:  # Exception:
            print("[ PyGlop ] ERROR: Could not finish " + f_name + ":")
            view_traceback()

    '''
    def calculate_normals(self):
        ## this does not work. The call to calculate_normals is even
        # commented out at <https://github.com/kivy/kivy/blob/master
        # /examples/3Drendering/objloader.py> 20 Mar 2014. 16 Apr 2015.
        vd = self.vertex_depth
        for i in range(int(len(self.indices) / (vd))):
            fi = i * vd
            v1i = self.indices[fi]
            v2i = self.indices[fi + 1]
            v3i = self.indices[fi + 2]

            vs = self.vertices
            p1 = [vs[v1i + c] for c in range(3)]
            p2 = [vs[v2i + c] for c in range(3)]
            p3 = [vs[v3i + c] for c in range(3)]

            u,v  = [0,0,0], [0,0,0]
            for j in range(3):
                v[j] = p2[j] - p1[j]
                u[j] = p3[j] - p1[j]

            n = [0,0,0]
            n[0] = u[1] * v[2] - u[2] * v[1]
            n[1] = u[2] * v[0] - u[0] * v[2]
            n[2] = u[0] * v[1] - u[1] * v[0]

            for k in range(3):
                self.vertices[v1i + 3 + k] = n[k]
                self.vertices[v2i + 3 + k] = n[k]
                self.vertices[v3i + 3 + k] = n[k]
    '''

    def emit_yaml(self, lines, min_tab_string):
        # lines.append(min_tab_string+this_name+":")
        if self.name is not None:
            lines.append(min_tab_string + "name: " +
                         get_yaml_from_literal_value(self.name))
        if self.actor_dict is not None:
            lines.append(min_tab_string + "actor:")
            standard_emit_yaml(lines, min_tab_string*2+"",
                               self.actor_dict)
            # ^ +"" to ensure type
            # ^ DOES use emit_yaml when present for a member
        if self.vertices is not None:
            if add_dump_comments_enable:
                lines.append(min_tab_string
                             + "#len(self.vertices)/self.vertex_depth:")
            lines.append(
                min_tab_string + "vertices_count: " +
                get_yaml_from_literal_value(len(self.vertices)
                                            / self.vertex_depth)
            )
        if self.indices is not None:
            lines.append(
                min_tab_string + "indices_count:" +
                get_yaml_from_literal_value(len(self.indices)))
        lines.append(
            min_tab_string + "vertex_depth: " +
            get_yaml_from_literal_value(self.vertex_depth))
        if self.vertices is not None:
            if add_dump_comments_enable:
                lines.append(min_tab_string +
                             "#len(self.vertices):")
            lines.append(
                min_tab_string + "vertices_info_len: " +
                get_yaml_from_literal_value(len(self.vertices)))
        lines.append(min_tab_string + "POSITION_INDEX:" +
                     get_yaml_from_literal_value(self.POSITION_INDEX))
        lines.append(min_tab_string + "NORMAL_INDEX:" +
                     get_yaml_from_literal_value(self.NORMAL_INDEX))
        lines.append(min_tab_string + "COLOR_INDEX:" +
                     get_yaml_from_literal_value(self.COLOR_INDEX))

        c_i = 0  # component_index
        c_o = 0  # component_offset

        lines.append("vertex_format:")
        vf = self.vertex_format
        standard_emit_yaml(lines, "  ", vf)
        '''
        while c_i < len(vf):
            vertex_format_component = vf[c_i]
            cnbs, c_len, ct = vertex_format_component
            # ^ component_name_bytestring,component_len,component_type
            component_name = cnbs.decode("utf-8")
            lines.append(min_tab_string + component_name + ".len:"
                         + get_yaml_from_literal_value(c_len))
            lines.append(min_tab_string + component_name + ".type:"
                         + get_yaml_from_literal_value(ct))
            lines.append(min_tab_string + component_name + ".index:"
                         + get_yaml_from_literal_value(c_i))
            lines.append(min_tab_string + component_name + ".offset:"
                         + get_yaml_from_literal_value(c_o))
            c_i += 1
            c_o += c_len

        lines.append(
            min_tab_string + "POSITION_LEN:"
            + str(vf[self.POSITION_INDEX][
                  VFORMAT_VECTOR_LEN_INDEX]))
        '''
        if add_dump_comments_enable:
            # lines.append(
            #     min_tab_string + "#VFORMAT_VECTOR_LEN_INDEX:" +
            #     str(VFORMAT_VECTOR_LEN_INDEX))
            lines.append(min_tab_string + "#len(self.vertex_format):"
                         + str(len(vf)))
            lines.append(min_tab_string + "#COLOR_OFFSET:" +
                         str(self.COLOR_OFFSET))
            lines.append(
                min_tab_string + "#len(self.vertex_format[" +
                "self.COLOR_INDEX]):" +
                str(len(vf[self.COLOR_INDEX])))
        channel_count = vf[self.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        if add_dump_comments_enable:
            lines.append(min_tab_string + "#vertex_bytes_per_pixel:"
                         + str(channel_count))

        for k, v in sorted(self.properties.items()):
            lines.append(min_tab_string + str(k) + ": " + str(v))

        thisTextureFileName = self.get_texture_diffuse_path()
        if thisTextureFileName is not None:
            lines.append(min_tab_string
                         + "get_texture_diffuse_path(): "
                         + thisTextureFileName)

        # standard_emit_yaml(lines, min_tab_string, "vertex_info_1D",
        #                    self.vertices)
        if add_dump_comments_enable:
            lines.append(min_tab_string + "#1D vertex info array, aka:")
        c_o = 0
        vertex_actual_index = 0
        if self.vertices is not None:
            lines.append(min_tab_string + "vertices:")
            for i in range(0, len(self.vertices)):
                if add_dump_comments_enable:
                    if c_o == 0:
                        lines.append(
                            min_tab_string + tab_string + "#vertex [" +
                            str(vertex_actual_index) + "]:")
                    elif c_o == self.COLOR_OFFSET:
                        lines.append(
                            min_tab_string + tab_string + "#  color:")
                    elif c_o == self._NORMAL_OFFSET:
                        lines.append(
                            min_tab_string + tab_string + "#  normal:")
                    elif c_o == self._POSITION_OFFSET:
                        lines.append(
                            min_tab_string + tab_string +
                            "#  position:")
                    elif c_o == self._TEXCOORD0_OFFSET:
                        lines.append(
                            min_tab_string + tab_string +
                            "#  texcoords0:")
                    elif c_o == self._TEXCOORD1_OFFSET:
                        lines.append(
                            min_tab_string + tab_string +
                            "#  texcoords1:")
                lines.append(
                    min_tab_string + tab_string + "- " +
                    str(self.vertices[i]))
                c_o += 1
                if c_o == self.vertex_depth:
                    c_o = 0
                    vertex_actual_index += 1
        if self.indices is not None:
            lines.append(min_tab_string + "indices:")
            for i in range(0, len(self.indices)):
                lines.append(min_tab_string + tab_string + "- " +
                             str(self.indices[i]))

    def on_vertex_format_change(self):
        self.vertex_depth = 0
        vf = self.vertex_format
        try:
            for i in range(0, len(vf)):
                self.vertex_depth += vf[i][VFORMAT_VECTOR_LEN_INDEX]
        except TypeError as ex:
            if "NoneType" in str(ex):
                print("[PyGlop on_vertex_format_change] ERROR:"
                      "self.vertex_depth is {}; "
                      "self.vertex_format is {}"
                      "".format(self.vertex_depth, vf))
                return None
            else:
                raise ex
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

        # this_pyglop.vertex_depth = 0
        offset = 0
        temp_vertex = list()
        for i in range(0, len(vf)):
            # first convert from bytestring to str
            vformat_name_lower = \
                str(vf[i][VFORMAT_NAME_INDEX]).lower()
            if 'pos' in vformat_name_lower:
                self._POSITION_OFFSET = offset
                self.POSITION_INDEX = i
            elif 'normal' in vformat_name_lower:
                self._NORMAL_OFFSET = offset
                self.NORMAL_INDEX = i
            elif (('texcoord' in vformat_name_lower)
                  or ('tc0' in vformat_name_lower)):
                if self._TEXCOORD0_OFFSET < 0:
                    self._TEXCOORD0_OFFSET = offset
                    self.TEXCOORD0_INDEX = i
                elif ((self._TEXCOORD1_OFFSET < 0)
                       and ('tc0' not in vformat_name_lower)):
                    self._TEXCOORD1_OFFSET = offset
                    self.TEXCOORD1_INDEX = i
                # else ignore since is probably the second index
                # such as a_texcoord1
            elif "color" in vformat_name_lower:
                self.COLOR_OFFSET = offset
                self.COLOR_INDEX = i
            offset += vf[i][VFORMAT_VECTOR_LEN_INDEX]
        if offset > self.vertex_depth:
            print("ERROR: The count of values in vertex format chunks"
                  " (chunk_count:" + str(len(vf))
                  + "; value_count:" + str(offset) + ") is greater"
                  " than the vertex depth " + str(self.vertex_depth))
        elif offset != self.vertex_depth:
            print("WARNING: The count of values in vertex format"
                  " chunks (chunk_count:"
                  + str(len(vf))
                  + "; value_count:" + str(offset)
                  + ") does not total to vertex depth "
                  + str(self.vertex_depth))
        participle = "(before initializing)"
        # Now you can access any vars you want (not just ones cached
        # above) like:
        # vf[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX]

    def append_wobject(self, this_wobject, pivot_to_g_enable=True):
        # formerly get_glops_from_wobject formerly set_from_wobject
        # formerly import_wobject; based on _finalize_obj_data
        f_name = "append_wobject"
        if this_wobject.face_dicts is None:
            print("WARNING in " + f_name + ": ignoring wobject where" +
                  " face_groups is None (a default face group is" +
                  " made on load if did not exist).")
            return

        self.source_path = this_wobject.source_path
        vf = self.vertex_format
        # from vertex_format above:
        # self.vertex_format = [
        #    (b'a_position', , 'float'),
        #     # ^ Munshi prefers vec4 (Kivy prefers vec3)
        #    (b'a_texcoord0', , 'float'),
        #     # ^ Munshi prefers vec4 (Kivy prefers vec2);
        #     #   vTexCoord0; available if enable_tex[0] is true
        #    (b'a_texcoord1', , 'float'),
        #     # ^ Munshi prefers vec4 (Kivy prefers vec2);
        #     # ^ available if enable_tex[1] is true
        #    (b'a_color', 4, 'float'),
        #     # ^ vColor (diffuse color of vertex)
        #    (b'a_normal', 3, 'float')
        #     # ^ vNormal; Munshi prefers vec3 (Kivy also prefers vec3)
        #    ]
        # self.on_vertex_format_change()
        IS_SELF_VFORMAT_OK = True
        if self._POSITION_OFFSET < 0:
            IS_SELF_VFORMAT_OK = False
            print("[ PyGlop ] Couldn't find name containing 'pos'"
                  " or 'position' in any vertex format element"
                  " (see pyglops.py PyGlop constructor)")
        if self._NORMAL_OFFSET < 0:
            IS_SELF_VFORMAT_OK = False
            print("[ PyGlop ] Couldn't find name containing 'normal'"
                  " in any vertex format element"
                  " (see pyglops.py PyGlop constructor)")
        if self._TEXCOORD0_OFFSET < 0:
            IS_SELF_VFORMAT_OK = False
            print("[ PyGlop ] Couldn't find name containing 'texcoord'"
                  " in any vertex format element"
                  " (see pyglops.py PyGlop constructor)")
        if self.COLOR_OFFSET < 0:
            IS_SELF_VFORMAT_OK = False
            print("[ PyGlop ] Couldn't find name containing 'color'"
                  " in any vertex format element"
                  " (see pyglops.py PyGlop constructor)")

        # vertices_offset = None
        # normals_offset = None
        # texcoords_offset = None
        # vertex_depth = 8
        # based on finish_object
        #     if self._current_object is None:
        #         return
        #
        if not IS_SELF_VFORMAT_OK:
            print("ERROR in " + f_name + ": bad vertex format " +
                  "specified in glop, no vertices could be added")
            return
        p_i = self.POSITION_INDEX
        zero_vertex = list()
        for index in range(0, self.vertex_depth):
            zero_vertex.append(0.0)
        if (vf[p_i][VFORMAT_VECTOR_LEN_INDEX] > 3):
            zero_vertex[3] = 1.0
            # NOTE: this is done since usually if len is 3,
            # simple.glsl included with kivy converts it to
            # vec4 appending 1.0:
            # attribute vec3 v_pos;
            # void main (void) {
            # vec4(v_pos,1.0);
        else:
            print("[ PyGlop ] WARNING in append_wobject: vertex"
                  " depth is 3 where should probably be 4 (index [3]"
                  " should be 1.0 in order for certain matrix math"
                  " to work")
        # this_offset = self.COLOR_OFFSET
        channel_count = vf[self.COLOR_INDEX][VFORMAT_VECTOR_LEN_INDEX]
        for channel_subindex in range(0, channel_count):
            zero_vertex[self.COLOR_OFFSET+channel_subindex] = -1.0
            # ^ -1.0 for None # TODO: asdf flag a different way (other
            #   than negative) to work with a unified shader

        participle = "accessing object from list"
        # this_wobject = self.glops[index]
        # self.name = None
        this_name = ""
        try:
            if this_wobject.name is not None:
                this_name = this_wobject.name
                if self.name is None:
                    self.name = this_name
        except:
            pass  # don't care

        try:
            participle = "processing material"
            if this_wobject.wmaterial is not None:
                # if this_wobject.properties["usemtl"] is not None:
                self.set_textures_from_wmaterial(this_wobject.wmaterial)
            else:
                print("WARNING: this_wobject.wmaterial is None")
        except:
            print("Could not finish " + participle + " in " + f_name
                  + ": ")
            view_traceback()

        glop_vertex_offset = 0
        vd = self.vertex_depth
        if self.vertices is None:
            self.vertices = []
        else:
            if len(self.vertices) > 0:
                glop_vertex_offset = len(self.vertices)
                # NOTE: len(self.vertices) is len(vertices)*vd
                self.properties['separable_offsets'].append(
                    glop_vertex_offset
                )
                print("[ PyGlop ] appending wobject vertices to " +
                      "glop (" + str(self.name) + ")'s existing " +
                      str(glop_vertex_offset) + " vertices")
            else:
                print("[ PyGlop ] appending wobject vertices to " +
                      "glop (" + str(self.name) +
                      ")'s existing list of 0 vertices")
            # print("[ PyGlop ] ERROR in " + f_name + ": existing"
            #       " vertices found {self.name:'"+str(this_name)+"'}")
        vertex_components = zero_vertex[:]

        source_face_index = 0
        # try:
        # if len(self.indices) < 1:
        participle = "before detecting vertex component offsets"
        # Detecting vertex component offsets is required since
        # indices in an obj file are sometimes relative to the
        # first index in the FILE not the object.
        TCO = self._TEXCOORD0_OFFSET
        PO = self._POSITION_OFFSET
        NO = self._NORMAL_OFFSET
        FACE_V = WObjFile.FACE_V
        FACE_TC = WObjFile.FACE_TC
        FACE_VN = WObjFile.FACE_VN
        for key in this_wobject.face_dicts:
            this_face_list = this_wobject.face_dicts[key]['faces']
            # TODO: implement this_wobject.face_dicts[key]['s']
            # which can be "on" or "off" or None
            participle = "before processing faces"
            dest_vertex_index = 0
            face_count = 0
            new_texcoord = new_tuple(
                vf[self.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX]
            )
            if this_face_list is None:
                print("[ PyGlop ] WARNING in append_wobject: "
                      + "faces list in this_wobject.face_groups["
                      + key + "] is None in object '" + this_name
                      + "'")
                continue
            if get_verbose_enable():
                # debug only
                print(
                    "[ PyGlop ] adding " +
                    str(len(this_face_list)) + " face(s) from " +
                    str(type(this_face_list)) + " " + key)
            for this_wobject_this_face in this_face_list:
                # print("  -  # in " + key)  # debug only
                participle = "getting face components"
                # print("face["+str(source_face_index)+"]: "+participle)

                # DOES triangulate faces of more than 3 vertices
                # (connects each loose point to first vertex and
                # previous vertex)
                # (vertex_done_flags are no longer needed since
                # that method is used)
                # vertex_done_flags = list()
                # for vertexinfo_index in range(0,
                #         len(this_wobject_this_face)):
                #     vertex_done_flags.append(False)
                # vertices_done_count = 0

                # with wobjfile.py, each face is an arbitrary-length
                # list of vertex_infos, where each vertex_info is a
                # list containing vertex_index, texcoord_index,
                # then normal_index, so ignore the following
                # commented deprecated lines of code:
                # verts =  this_wobject_this_face[0]
                # norms = this_wobject_this_face[1]
                # tcs = this_wobject_this_face[2]
                # for vertexinfo_index in range(3):
                vertexinfo_index = 0
                source_face_vertex_count = 0
                while vertexinfo_index < len(this_wobject_this_face):
                    # print("vertex[" + str(vertexinfo_index) + "]")
                    vertex_info = \
                        this_wobject_this_face[vertexinfo_index]

                    vertex_index = vertex_info[FACE_V]
                    texcoord_index = vertex_info[FACE_TC]
                    normal_index = vertex_info[FACE_VN]

                    vertex = None
                    texcoord = None
                    normal = None

                    participle = "getting normal components"

                    # get normal components
                    normal = (0.0, 0.0, 1.0)
                    # if normals_offset is None:
                    #     normals_offset = 1
                    normals_offset = 0
                    # ^ since wobjfile.py makes
                    #   indices relative to object
                    try:
                        # if (normal_index is not None) and \
                        #         (normals_offset is not None):
                        #     participle = (
                        #         "getting normal components at " +
                        #         str(normal_index-normals_offset)
                        #          # str(norms[face_index] -
                        #              # normals_offset)
                        # else:
                        participle = (
                            "getting normal components at " +
                            str(normal_index) + "-" +
                            str(normals_offset)
                        )
                        # str(norms[face_index]-normals_offset)
                        wn = this_wobject.normals
                        if normal_index is not None:
                            normal = wn[normal_index-normals_offset]
                        # if norms[face_index] != -1:
                        #     normal = this_wobject.normals[
                        #         norms[face_index]-normals_offset]
                    except:  # Exception as e:
                        print("Could not finish " + participle +
                              " for wobject named '" + this_name +
                              "':")
                        view_traceback()

                    participle = (
                        "getting texture coord components"
                    )
                    participle = (
                        "getting texture coord components" +
                        " at " + str(face_count)
                    )
                    participle = (
                        "getting texture coord components" +
                        " using index " + str(face_count)
                    )
                    # get texture coordinate components
                    # texcoord = (0.0, 0.0)
                    texcoord = new_texcoord[:]
                    # if texcoords_offset is None:
                    #     texcoords_offset = 1
                    texcoords_offset = 0
                    # ^ since wobjfile.py makes indices relative
                    #   to object
                    try:
                        if this_wobject.texcoords is not None:
                            # if (texcoord_index is not None) and \
                            #         (texcoords_offset \
                            #          is not None:
                            #     participle = (
                            #         "getting texcoord" +
                            #         "components at " +
                            #         str(texcoord_index -
                            #             texcoords_offset) +
                            #         # str(norms[face_index] -
                            #         # normals_offset)
                            #     )
                            # else:
                            participle = (
                                "getting texcoord"
                                " components at "
                                + str(texcoord_index) + "-"
                                + str(texcoords_offset)
                            )
                            # str(norms[face_index] -
                            #     normals_offset)

                            if texcoord_index is not None:
                                texcoord = this_wobject.texcoords[
                                    texcoord_index-texcoords_offset
                                ]
                            # if tcs[face_index] != -1:
                            #     tc_len = len(
                            #         this_wobject.texcoords)
                            #     participle = (
                            #         "using texture" +
                            #         coordinates at index " +
                            #         str(tcs[face_index] -
                            #             texcoords_offset) +
                            #         " (after applying" +
                            #         " texcoords_offset:" +
                            #         str(texcoords_offset) +
                            #         "; Count:" +
                            #         str(tc_len)+")"
                            #     )
                            #     texcoord = (
                            #         this_wobject.texcoords[ \
                            #             tcs[face_index] - \
                            #             texcoords_offset]
                            #     )
                        else:
                            if get_verbose_enable():
                                print("Warning: no texcoords "
                                      "found in wobject named '"
                                      + this_name + "'")
                    except:  # Exception as e:
                        print("Could not finish " + participle
                              + " for wobject named '" + this_name
                              + "':")
                        view_traceback()

                    participle = "getting vertex components"
                    # if vertices_offset is None:
                    #     vertices_offset = 1
                    vertices_offset = 0
                    # ^ since wobjfile.py makes indices relative to
                    #   object
                    vs_len = len(this_wobject.vertices)
                    # participle = (
                    #    "accessing face vertex " +
                    #     str(verts[face_index] -
                    #         vertices_offset) +
                    #     " (after applying vertices_offset:" +
                    #     str(vertices_offset) +
                    #     "; Count:" + str(vs_len) + ")"
                    # )
                    participle = (
                        "accessing face vertex "
                        + str(vertex_index) + "-"
                        + str(vertices_offset) + " (after"
                        " applying vertices_offset:"
                        + str(vertices_offset)
                    )
                    if (this_wobject.vertices is not None):
                        participle += "; Count:" + str(vs_len) + ")"
                    else:
                        participle += \
                            "; this_wobject.vertices: None)"
                    try:
                        this_vi = vertex_index-vertices_offset
                        # v = this_wobject.vertices[\
                        #     verts[face_index]-vertices_offset]
                        v = this_wobject.vertices[this_vi]
                    except:  # Exception as e:
                        print("[ PyGlop ] (ERROR) could not "
                              "finish " + participle + " for "
                              "wobject named '" + this_name + "':")
                        view_traceback()

                    participle = "combining components"

                    # TODO: why does kivy-rotation3d version have
                    # texcoord[1] instead of 1 - texcoord[1] in:
                    # vertex_components = [
                    #     v[0], v[1], v[2],
                    #     normal[0], normal[1], normal[2],
                    #     texcoord[0], 1 - texcoord[1]]
                    # ]
                    vertex_components = list()
                    for i in range(0, vd):
                        vertex_components.append(0.0)
                    for element_index in range(0, 3):
                        vertex_components[PO+element_index] = \
                            v[element_index]
                    if (vf[p_i][VFORMAT_VECTOR_LEN_INDEX] > 3):
                        vertex_components[PO+3] = 1.0
                        # ^ non-position padding value must be 1.0
                        #   for matrix math to work correctly
                    for element_index in range(0, 3):
                        vertex_components[NO+element_index] = \
                            normal[element_index]
                    for element_index in range(0, 2):
                        if element_index == 1:
                            vertex_components[TCO+element_index] = \
                                1-texcoord[element_index]
                        else:
                            vertex_components[TCO+element_index] = \
                                texcoord[element_index]

                    CO = self.COLOR_OFFSET
                    if len(v) > 3:
                        # Use extended vertex info (color)
                        # from a nonstandard obj file.
                        abs_index = 0
                        for element_index in range(4, len(v)):
                            vertex_components[CO+abs_index] = \
                                v[element_index]
                            abs_index += 1
                    else:
                        # default to transparent vertex color
                        # TODO: overlay vertex color using material
                        # color as base
                        for element_index in range(0, 4):
                            vertex_components[CO+element_index] = 0.0
                    # print("    - " + str(vertex_components))  # debug only
                    self.vertices.extend(vertex_components)
                    source_face_vertex_count += 1
                    vertexinfo_index += 1
                # end while vertexinfo_index in face

                participle = "combining triangle indices"
                vertexinfo_index = 0
                sFaceVI = 0
                # ^ relative_source_face_vertex_index
                #   required for tracking faces with less than
                #   3 vertices
                face_first_vertex_dest_index = dest_vertex_index
                # ^ store first face (used for tesselation)
                tesselated_f_count = 0
                # example obj quad (without Texcoord) vertex_index/
                # texcoord_index/normal_index:
                # f 61//33 62//33 64//33 63//33
                # face_vertex_list = list()
                # ^ in case verts are out of order,
                #   prevent tesselation from connecting wrong verts
                while vertexinfo_index < len(this_wobject_this_face):
                    # face_vertex_list.append(dest_vertex_index)
                    if vertexinfo_index == 2:
                        # OK to assume dest vertices are in order,
                        # since just created them (should work
                        # even if source vertices are not in order)
                        tri = [
                            glop_vertex_offset+dest_vertex_index,
                            glop_vertex_offset+dest_vertex_index+1,
                            glop_vertex_offset+dest_vertex_index+2
                        ]
                        self.indices.extend(tri)
                        dest_vertex_index += 3
                        sFaceVI += 3
                        tesselated_f_count += 1
                    elif vertexinfo_index > 2:
                        # TESSELATE MANUALLY for faces with more
                        # than 3 vertices (connect loose vertex with
                        # first vertex and previous vertex)
                        tri = [
                            glop_vertex_offset
                            + face_first_vertex_dest_index,
                            glop_vertex_offset+dest_vertex_index-1,
                            glop_vertex_offset+dest_vertex_index
                        ]
                        self.indices.extend(tri)
                        dest_vertex_index += 1
                        sFaceVI += 1
                        tesselated_f_count += 1
                    vertexinfo_index += 1

                if (tesselated_f_count < 1):
                    print("WARNING: Face tesselated to 0 faces")
                # elif tesselated_f_count > 1:
                #     if get_verbose_enable():
                #         print("Face tesselated to "
                #               + str(tesselated_f_count)
                #               + " face(s)")

                if sFaceVI < source_face_vertex_count:
                    print("WARNING: Face has fewer than 3 vertices"
                          " (problematic obj file "
                          + str(this_wobject.source_path) + ")")
                    dest_vertex_index += (source_face_vertex_count
                                          - sFaceVI)
                source_face_index += 1
        participle = "generating pivot point"
        # if self.properties['hitbox'] is not None:
        #     print("[ PyGlop ] WARNING: self."
        #           "properties['hitbox'] is not None"
        #           " already during append_wobject")
        if pivot_to_g_enable:
            self.transform_pivot_to_geometry()
        # else:
        #     print("ERROR: can't use pyglop since already has"
        #           " vertices (len(self.indices)>=1)")
        '''
        except:  # Exception as e:
            # print("[ PyGlop ] ERROR in append_wobject"
            #       + "--Could not finish " + participle
            #       + " at source_face_index "
            #       + str(source_face_index)
            #       + " in " + f_name + ": " + str(e))
            print("[ PyGlop ] ERROR--could not finish " +
                  participle + " at source_face_index " +
                  str(source_face_index) + " in " + f_name + ": ")
            view_traceback()

            # print("vertices after extending: "
            #       + str(this_wobject.vertices))
            # print("indices after extending: "
            #       + str(this_wobject.indices))
            # if this_wobject.mtl is not None:
            #     this_wobject.wmaterial = \
            #         this_wobject.mtl.get(this_wobject.obj_material)
            # if ((this_wobject.wmaterial is not None) and
            #         this_wobject.wmaterial):
            #     this_wobject.set_textures_from_wmaterial(
            #         this_wobject.wmaterial
            #     )
            # self.glops[self._current_object] = mesh
            # mesh.calculate_normals()
            # self.faces = []
        '''
        # if (len(this_wobject.normals)<1):
        #     this_wobject.calculate_normals()
        #         # this does not work.
        #         # The call to calculate_normals is even commented
        #         # out at <https://github.com/kivy/kivy/blob/master
        #         # /examples/3Drendering/objloader.py>
        #         # accessed 20 Mar 2014. 16 Apr 2015.
        # end def append_wobject
# end class PyGlop


def new_material():
    ret = {}
    ret['properties'] = {}
    ret['name'] = None
    ret['mtl_path'] = None
    # region vars based on OpenGL ES 1.1
    ret['ambient_color'] = (0.0, 0.0, 0.0, 1.0)
    ret['diffuse_color'] = (1.0, 1.0, 1.0, 1.0)
    ret['specular_color'] = (1.0, 1.0, 1.0, 1.0)
    ret['emissive_color'] = (0.0, 0.0, 0.0, 1.0)
    ret['specular_exponent'] = 1.0
    # endregion vars based on OpenGL ES 1.1
    return ret


def copy_material(o, depth=0):
    ret = new_material()
    if o['properties'] is not None:
        ret['properties'] = get_dict_deepcopy(o['properties'],
                                              depth=depth+1)
    ret['name'] = o['name']
    ret['mtl_path'] = o['mtl_path']
    ret['ambient_color'] = o['ambient_color']
    ret['diffuse_color'] = o['diffuse_color']
    ret['specular_color'] = o['specular_color']
    ret['emissive_color'] = o['emissive_color']
    ret['specular_exponent'] = o['specular_exponent']
    return ret


def angles_to_angle_and_matrix(angles_list_xyz):
    '''
    Convert a list of angles to a Kivy angle matrix.

    Sequential arguments:
    angles_list_xyz -- The variable name ends in xyz so it must be ready
                       to be swizzled.
    '''
    result_angle_matrix = [0.0, 0.0, 0.0, 0.0]
    for axI in range(len(angles_list_xyz)):
        while angles_list_xyz[axI] < 0:
            angles_list_xyz[axI] += 360.0
        if angles_list_xyz[axI] > result_angle_matrix[0]:
            result_angle_matrix[0] = angles_list_xyz[axI]
    if result_angle_matrix[0] > 0:
        for axI in range(len(angles_list_xyz)):
            result_angle_matrix[1+axI] = (
                angles_list_xyz[axI] / result_angle_matrix[0]
            )
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


# already imported from wobjfile.py:
# def standard_emit_yaml(lines, min_tab_string, sourceList):
#     lines.append(min_tab_string+this_name+":")
#     for i in range(0,len(sourceList)):
#         lines.append(min_tab_string+"- "+str(sourceList[i]))


def new_tuple(length, fill_start=0, fill_len=-1, fill_value=1.0):
    result = None
    tmp = []
    fill_count = 0
    for i in range(0, length):
        if (i >= fill_start) and (fill_count < fill_len):
            tmp.append(fill_value)
            fill_count += 1
        else:
            tmp.append(0.0)
    # if length == 1:
    #     result = tuple(0.0)
    # elif length == 2:
    #     result = (0.0, 0.0)
    # elif length == 3:
    #     result = (0.0, 0.0, 0.0)
    # elif length == 4:
    #     result = (0.0, 0.0, 0.0, 0.0)
    # elif length == 5:
    #     result = (0.0, 0.0, 0.0, 0.0, 0.0)
    # elif length == 6:
    #     result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    # elif length == 7:
    #     result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    # elif length == 8:
    #     result = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return tuple(tmp)  # result


def new_light():
    ret = {}
    # region vars based on OpenGL ES 1.1
    ret['position'] = (0.0, 0.0, 0.0, 0.0)
    ret['ambient_color'] = (0.0, 0.0, 0.0, 0.0)
    ret['diffuse_color'] = (0.0, 0.0, 0.0, 0.0)
    ret['specular_color'] = (0.0, 0.0, 0.0, 0.0)
    ret['spot_direction'] = (0.0, 0.0, 0.0)
    ret['attenuation_factors'] = (0.0, 0.0, 0.0)
    ret['spot_exponent'] = 1.0
    ret['spot_cutoff_angle'] = 45.0
    ret['compute_distance_attenuation'] = False
    # endregion vars based on OpenGL ES 1.1
    return ret


class PyGlops:

    def __init__(self, new_glop_method):
        self.showNextHashWarning = True
        self.glops = None
        self.materials = None
        self.lastUntitledMeshNumber = -1
        self.lastCreatedMaterial = None
        self.lastCreatedMesh = None
        self._walkmeshes = None
        self._visual_debug_enable = None
        if not hasattr(self, 'ui'):
            # ui may exist now if subclass calls super() late
            self.ui = None
        self.camera_glop = None
        self.player_glop = None
        self._player_glop_index = None
        self.prev_inbounds_camera_translate = None
        self._bumper_indices = None
        self._bumpable_indices = None
        self._world_min_y = None
        self._world_grav_acceleration = None
        self.last_update_s = None

        self.fired_count = None

        global settings
        self.settings = settings
        self.settings['globals']['camera_perspective_number'] = \
            self.CAMERA_FIRST_PERSON()
        if not isinstance(self.settings, dict):
            print("[ PyGlops ] FATAL ERROR: missing settings dict")
            sys.exit(1)
        self._delay_is_available_enable = False
        self._player_indices = []  # player number 1 is 0
        self._visual_debug_enable = False
        self.fired_count = 0
        self.settings['globals']['fly_enables'] = {}
        try:
            self.camera_glop = new_glop_method()
        except:
            print("[ PyGlops ] uh oh, new_glop_method failed"
                  " (this should never happen). Try updating Kivy 1.9.0"
                  " to a later version.")
            view_traceback()
            try:
                new_glop_method = self.ui.dummy_glop.new_glop_method
                self.camera_glop = new_glop_method()
            except:
                print("[ PyGlops ] uh oh, call via type failed too:")
                view_traceback()
        self.camera_glop.name = "Camera"
        self._walkmeshes = []
        self.glops = []
        self.materials = []
        self._bumper_indices = []
        self._bumpable_indices = []
        self._actor_indices = []

    def __str__(self):
        return "PyGlops engine"

    def get_has_gravity(self):
        return self.settings['world']['gravity_enable'] is True

    def get_class_name(self):
        return "PyGlops"

    def set_fly(self, enable):
        print("[ PyGlops ] WARNING: set_fly is deprecated. Use "
              "set_gravity_enable or set_player_fly instead ("
              "calling set_gravity_enable(" + str(not enable) + ")")
        self.set_gravity_enable(not enable)
        # self.settings['templates']['actor']['fly_enable'] = enable

    def get_fly_by_name(self, glop_name):
        result = is_true(
            self.settings['globals']['fly_enables'].get(glop_name)
        )

    def set_gravity(self, gravity_mss):
        '''
        Set the world gravity.

        Sequential arguments:
        gravity_mss -- Set the gravitational acceleration
                       in meters per second squared.
        '''
        if (gravity_mss is True) or (gravity_mss is False):
            self.set_gravity_enable(gravity_mss)
            print("[ PyGlops ] ERROR in set_gravity: you said "
                  + str(gravity_mss) + " but should have sent a "
                  "number. Try set_gravity_enable instead "
                  "(called automatically for now)")
        else:
            self.settings['world']['gravity'] = gravity_mss

    def set_gravity_enable(self, enable):
        self.settings['world']['gravity_enable'] = enable

    def CAMERA_FREE(self):
        '''
        The camera does not move automatically (you may move it yourself)
        '''
        return 0

    def CAMERA_FIRST_PERSON(self):
        '''
        The camera set to same position as player's pivot point
        '''
        return 1

    def CAMERA_SECOND_PERSON(self):
        '''
        The camera is from the perspective of random enemy
        '''
        return 2

    def CAMERA_THIRD_PERSON(self):
        '''
        The camera is behind and above player (in world axes), not rotating
        '''
        return 3

    '''
    def _run_command(self, command, bumpable_index, bumper_index,
                     bypass_handlers_enable=False):
         print("WARNING: _run_command should be implemented by a"
               "subclass since it requires using the graphics"
               " implementation")
         return False
    '''

    def update(self):
        print("WARNING: update should be implemented by a subclass"
              " otherwise it assumes there is a realtime game and/or"
              " graphical output")

    def get_verbose_enable(self):
        return get_verbose_enable()

    def spawn_pex_particles(self, path, pos, radius=1.0,
                            duration_seconds=None):
        if self.ui is not None:
            self.ui.spawn_pex_particles(path, pos, radius, duration_seconds)
        else:
            print("[ PyGlops ] ERROR in spawn_pex_particles:"
                  " self.ui is None")

    def give_item_by_keyword_to_player_number(self, player_number,
                                              keyword,
                                              allow_owned_enable=False):
        '''
        This method overrides object bump code, and gives the item to
        the player (mimics "obtain" event).
        Cause the unit controlled by the player to obtain the item
        found first by keyword, then hide the item (overrides object
        bump code).
        '''
        indices = get_indices_of_similar_names(
            keyword,
            allow_owned_enable=allow_owned_enable
        )
        result = False
        if indices is not None and len(indices) > 0:
            item_glop_index = indices[0]
            result = self.give_item_index_to_player_number(
                player_number,
                item_glop_index,
                "hide"
            )
        return result

    def give_item_index_to_player_number(self, player_number,
                                         item_glop_index,
                                         pre_commands=None,
                                         bypass_handlers_enable=True):
        '''
        This method overrides object bump code, and gives the item to
        the player (mimics "obtain" command).

        Keyword arguments:
        pre_commands -- can be either None (to imply default "hide") or
                        a string containing semicolon-separated
                        commands that will occur before obtain does.
        '''
        result = False
        bumpable_index = item_glop_index
        bumper_index = self.get_player_glop_index(player_number)
        if get_verbose_enable():
            print("give_item_index_to_player_number; item_name:"
                  + self.glops[bumpable_index].name + "; player_name:"
                  + self.glops[bumper_index].name)
        if pre_commands is None:
            pre_commands = "hide"
            # ^ default behavior is to hold item in inventory invisibly
        if pre_commands is not None:
            command_list = pre_commands.split(";")
            for command_original in command_list:
                command = command_original.strip()
                if command != "obtain":
                    self._run_command(
                        command,
                        bumpable_index,
                        bumper_index,
                        bypass_handlers_enable=bypass_handlers_enable
                    )
                else:
                    print("[ PyGlops ] warning: skipped redundant"
                          " 'obtain' command in post_commands param"
                          " given to give_item_index_to_player_number")
                    # "obtain" command is ONLY run below (or
                    # automatically by _internal_bump_glop),
                    # via _run_command

        self._run_command(
            "obtain",
            bumpable_index,
            bumper_index,
            bypass_handlers_enable=bypass_handlers_enable
        )
        result = True
        return result

    def _run_semicolon_separated_commands(self,
                                          semicolon_separated_commands,
                                          bumpable_index, bumper_index,
                                          bypass_handlers_enable=False):
        if semicolon_separated_commands is not None:
            command_list = semicolon_separated_commands.split(";")
            if get_verbose_enable():
                print("[ PyGlops ] (verbose message) command_list: {}"
                      "".format(command_list))
            self._run_commands(
                command_list,
                bumpable_index,
                bumper_index,
                bypass_handlers_enable=bypass_handlers_enable
            )

    def _run_commands(self, command_list, bumpable_index, bumper_index,
                      bypass_handlers_enable=False):
        for command_original in command_list:
            command = command_original.strip()
            self._run_command(
                command,
                bumpable_index,
                bumper_index,
                bypass_handlers_enable=bypass_handlers_enable
            )

    def _run_command(self, command, bumpable_index, bumper_index,
                     bypass_handlers_enable=False):
        '''
        This is normally run by _internal_bump_glop (such as via _run_* above).
        '''
        # if get_verbose_enable():
        #     print("[ PyGlops ] (verbose message) _run_command(" +
        #           command + ", ...)")
        if command == "hide":
            self.hide_glop(self.glops[bumpable_index])
            self.glops[bumpable_index].properties['bump_enable'] = False
        elif command == "obtain":
            # first, fire the (blank) overridable event handlers:
            dgn = self.glops[bumpable_index].name
            # ^ detectable glop name formerly bumpable_name
            bgn = self.glops[bumper_index].name
            # ^ formerly bumper _name
            # self._deprecated_on_obtain_glop_by_name(dgn, bgn)  # handler
            self.on_obtain_glop(bumpable_index, bumper_index)  # handler
            for j in range(len(self._bumpable_indices)):
                if self._bumpable_indices[j] == bumpable_index:
                    self._bumpable_indices[j] = None
                    # can't delete until bump loop is done in update

            # Add it to player's item list if "fits" in inventory:
            if self.glops[bumper_index].actor_dict is not None:
                bumper = self.glops[bumper_index]
                bumped = self.glops[bumpable_index]
                item_event = bumper.push_glop_item(bumped, bumpable_index)
                # Then manually transfer the glop to the player if it
                # fit (a game can override `push_item` to control
                # fit_enable):
                if item_event['fit_enable']:
                    bumped.item_dict['owner'] = bumper.name
                    bumped.item_dict['owner_key'] = bumper_index
                    item_event['calling_method'] = "_run_command"
                    # process item event so selected inventory slot gets
                    # updated in case that is the found slot for the
                    # item:
                    self.after_selected_item(item_event)
                if get_verbose_enable():
                    print(command + " " + bumped.name + " {fit:"
                          + str(item_event['fit_enable']) + "}")
            else:
                print("[ PyGlops ] ERROR in _run_command: tried to"
                      " give item to non-actor (only add actors to"
                      " self._bumper_indices; add items to"
                      " self._bumpable_indices instead)")
                view_traceback()
        else:
            print("Glop named {} attempted an unknown glop command"
                  " (in bump event): {}"
                  "".format(self.glops[bumpable_index].name, command))

    def hide_glop(self, this_glop):
        print("ERROR: hide_glop should be implemented by a sub-class"
              " since implementation is specific"
              " to the target platform")
        return False

    def show_glop(self, this_glop_index):
        print("ERROR: show_glop should be implemented by a sub-class"
              " since implementation is specific"
              " to the target platform")
        return False

    def after_selected_item(self, select_item_event_dict):
        name = None
        # proper_name = None
        selected_index = None
        sied = select_item_event_dict
        pgi = self.get_player_glop_index(1)
        if sied is not None:
            if sied.get('glop_index') is not None:
                if sied.get('inventory_index') is not None and \
                   sied['inventory_index'] > -1:
                    calling_method_string = ""
                    if 'calling_method' in sied:
                        calling_method_string = sied['calling_method']
                    if 'name' in sied:
                        name = sied['name']
                    else:
                        print("ERROR in after_selected_item: missing"
                              " name in select_item_event_dict "
                              + calling_method_string)
                    # if 'proper_name' in sied:
                    #     proper_name = sied['proper_name']
                    # else:
                    #     print("ERROR in after_selected_item ("
                    #           + calling_method_string + "): missing"
                    #           " proper_name in"
                    #           " select_item_event_dict")
                    if 'selected_index' in sied:
                        selected_index = sied['selected_index']
                    else:
                        print("[ PyGlops ] ERROR in "
                              "after_selected_item"
                              " (" + calling_method_string + "):"
                              " missing selected_index in"
                              " select_item_event_dict")
                    if sied.get('glop_index') == pgi:
                        if 'Player' not in debug_dict:
                            debug_dict['Player'] = {}
                        ddp = debug_dict['Player']
                        ddp['inventory selected'] = str(name)
                else:
                    if sied.get('glop_index') == pgi:
                        if 'Player' not in debug_dict:
                            debug_dict['Player'] = {}
                        ddp = debug_dict['Player']
                        ddp['inventory selected'] = "<no slot>"
            else:
                print("[ PyGlops ] ERROR in after_selected_item: "
                      "missing glop_index in select_item_event_dict")
        self.ui.set_primary_item_caption(str(selected_index) + ": "
                                         + str(name))
        self.update_item_visual_debug()

    def load_obj(self, source_path, swapyz_enable=False, centered=False,
                 pivot_to_g_enable=True):
        results = None  # new glop indices
        print("[ PyGlops ] ERROR: If you are not using KivyGlops, make "
              "your own PyGlops subclass and implement the load_obj("
              "self, source_path, swapyz_enable=False, centered=False,"
              " pivot_to_g_enable=True)  method")
        return results

    def add_actor_weapon(self, glop_index, item_dict):
        '''
        Add a non-glop item where item_dict['fires_glops'] is a list of
        glop objects.
        (push_item is called, which DOES auto-select IF no slot selected
        --if actor_dict['inventory_index'] < 0 before calling this method)
        '''
        result = False
        # item_event = self.glops[glop_index].push_glop_item(
        #     self.glops[bumpable_index], bumpable_index)
        # Process item event so selected inventory slot gets updated
        # in case obtained item ends up in it:
        # self.after_selected_item(item_event)
        # if get_verbose_enable():
        #     print(command+" "+self.glops[bumpable_index].name)
        self.preprocess_item(item_dict, sender_name="add_actor_weapon")
        if 'fired_sprite_path' in item_dict:
            indices = self.load_obj(
                "meshes/sprite-square.obj",
                pivot_to_g_enable=True
            )
        else:
            w_glop = self.new_glop_method()
            self.glops.append(w_glop)
            w_glop.glop_index = len(self.glops) - 1
            w_glop.state['glop_index'] = w_glop.glop_index
            indices = [len(self.glops)-1]
            if self.glops[indices[0]] is not w_glop:
                # then address multithreading paranoia
                indices = None
                for try_i in range(len(self.glops)):
                    if self.glops[try_i] is w_glop:
                        indices = [try_i]
                        break
            if indices is not None:
                print("WARNING: added invisible " + str(type(w_glop))
                      + " weapon (no 'fired_sprite_path' in item_dict")
            else:
                print("WARNING: failed to find new invisible "
                      + str(type(w_glop))
                      + " weapon (no 'fired_sprite_path' in item_dict")
        item_dict['fires_glops'] = list()
        # TODO: remove redundancy by using set_as_item
        # (which now checks for fires_glops)
        if item_dict.get('name') is None:
            item_dict['name'] = "Primary Weapon"
        if indices is not None:
            for i in range(0, len(indices)):
                fired = self.glops[indices[i]]
                item_dict['fires_glops'].append(fired)
                fired.set_texture_diffuse(item_dict['fired_sprite_path'])
                fired.look_target_glop = self.camera_glop
                for j in range(len(self._bumpable_indices)):
                    if self._bumpable_indices[j] == indices[i]:
                        self._bumpable_indices[j] = None
                        # can't delete until bump loop is done
                        # in update

                if get_verbose_enable():
                    print("[ PyGlops ] (verbose message)"
                          " add_actor_weapon is calling push_item"
                          " manually")
                item_event = self.glops[glop_index].push_item(
                    item_dict,
                    sender_name="add_actor_weapon"
                )
                if ((item_event is not None)
                        and ('fit_enable' in item_event)
                        and (item_event['fit_enable'])):
                    result = True
                    item_event['calling_method'] = "add_actor_weapon"
                    # process item event so selected inventory slot gets
                    # updated in case obtained item ends up in it:
                    self.after_selected_item(item_event)
                else:
                    if item_event is not None:
                        if 'fit_enable' in item_event:
                            print("NOTICE: Nothing done for item_push"
                                  " since presumably, "
                                  "{}'s inventory was full"
                                  " (fit_enable={})"
                                  "".format(self.glops[glop_index].name,
                                            item_event['fit_enable']))
                        else:
                            print("ERROR in add_actor_weapon"
                                  ": Nothing done (fit_enable is None)")
                    else:
                        print("WARNING in add_actor_weapon" +
                              ": item_event returned" +
                              " by push_item was None")
                # print("add_actor_weapon: using " +
                #       str(fired.name) + " as sprite.")
            for i in range(0, len(indices)):
                self.hide_glop(self.glops[indices[i]])
        else:
            if 'fired_sprite_path' in item_dict:
                print("[ PyGlops ] ERROR in add_actor_weapon"
                      ": got 0 objects from"
                      " fired_sprite_path '{}'"
                      "".format(item_dict['fired_sprite_path']))
            else:
                print("[ PyGlops ] ERROR in add_actor_weapon"
                      ": could not add invisible weapon to"
                      " self.glops")

        # print("add_actor_weapon OK")
        return result

    def _internal_bump_glop(self, bumpable_index, bumper_index):
        '''
        Normally called by update (every frame for every bump)
        in your subclass (in subclass only since locations are
        dependent on graphics implementation).

        Sequential arguments:
        bumpable_index -- Provide the glop index of the detectable
                          (bumpable) glop.
        bumper_index -- Provide the glop index of the glop that bumped
                        it, otherwise set to None.
        '''
        bumper = None
        bgn = None
        # ^ formerly bumper_name
        if bumper_index is not None:
            bumper = self.glops[bumper_index]
            bgn = bumper.name
        bumped = None
        dgn = None
        dgItD = None
        if bumpable_index is not None:
            bumped = self.glops[bumpable_index]
            dgn = bumped.name
            dgItD = bumped.item_dict
        # Prevent repeated bumping until out of range again:
        if bumper_index is not None:
            if bumper_index not in bumped.state['in_range_indices']:
                bumped.state['in_range_indices'].append(bumper_index)
            else:
                print("[ PyGlops ] WARNING in _internal_bump_glop: '"
                      + bumped.name + "' is already being bumped by '"
                      + str(bgn))

        # result =
        # NOTE: on_at_rest should already have been called
        # if result is not None:
        #     if 'detectable_name' in result:
        #         dgn = result['bumpable_name']  # ['dgn']
        #     if 'bumper_name' in result:
        #         bgn = result['bumper_name']  # ['bgn']

        # if dgn is not None and bgn is not None:
        dgPjD = bumped.projectile_dict
        if dgPjD is not None:
            if bumper is not None:
                if len(bumper.properties['damaged_sound_paths']) > 0:
                    rand_i = random.randrange(
                        0, len(bumper.properties['damaged_sound_paths']))
                    self.play_sound(
                        bumper.properties['damaged_sound_paths'][rand_i])
            if get_verbose_enable():
                print("[ PyGlops ] (debug only in _internal_bump_glop"
                      " PROJECTILE HIT _internal_bump_glop"
                      " found projectile_dictbump")  # debug only
            if bumper_index is not None:
                self.on_attacked_glop(bumper_index, dgPjD['owner_key'],
                                      dgPjD)
            if len(bumped.properties['bump_sound_paths']) > 0:
                rand_i = random.randrange(
                    0,
                    len(bumped.properties['bump_sound_paths'])
                )
                self.play_sound(
                    bumped.properties['bump_sound_paths'][rand_i]
                )
            if bumper is not None:
                if len(bumper.properties['bump_sound_paths']) > 0:
                    rand_i = random.randrange(
                        0,
                        len(bumper.properties['bump_sound_paths'])
                    )
                    self.play_sound(
                        bumper.properties['bump_sound_paths'][rand_i]
                    )
            bumped.projectile_dict = None
            # ^ End the projectile behavior.
            bumped.properties['bump_enable'] = True
            # TODO: ^ elmininate `['bump_enable'] = True` here ??
            if bumper_index is not None:
                if bumper_index not in bumped.state['in_range_indices']:
                    # prevent picking up item after it hits you,
                    # unless you move away afterward
                    bumped.state['in_range_indices'].append(bumper_index)
            # else:
            #     pass
            #     if bumper is not None:
            #         print("bumper:" + str(bumper._t_ins.xyz) +
            #               "; bumped:" + str(bumped._t_ins.xyz))
            # if 'bump' in dgItD:
            # NOTE ignore bumped.state['in_range_indices'] list
            # since firing at point blank range is ok.
            # if bumper is not None:
            #     print("[ debug only ] projectile bumped by object " +
            #           str(bgn))
            #     print("[ debug only ]    hit_radius:" +
            #           str(bumper.properties['hit_radius']))
            #     if bumper.properties['hitbox'] is not None:
            #         print("[ debug only ]   hitbox: " +
            #               str(bumper.properties['hitbox']))
            #     else:
            #         print("bumpable glop item_dict does"
            #               " not contain 'bump'")
        elif dgItD is not None:
            bad_flag = "(projectile_dict)"
            this_flag = "<unexpected scenario>"
            if dgItD.get('bump') is None:
                if get_verbose_enable():
                    print("[ PyGlops ] bumpable glop item_dict does"
                          " not contain 'bump' (semicolon-separated"
                          " actions)")
                return

            if bumped.properties['bump_enable']:
                if bumped.projectile_dict is not None:
                    this_flag = bad_flag
                elif dgItD is not None and 'as_projectile' in dgItD:
                    print("[ PyGlops ] _internal_bump_glop is"
                          " ignoring DEPRECATED as_projectile"
                          " key--place your projectile values"
                          " in item_dict directly instead")
                    this_flag = ("(ignoring DEPRECATED"
                                 " as_projectile key)")
                else:
                    this_flag = "(standard item)"
                if get_verbose_enable():
                    print("[ PyGlops ] _internal_bump_glop " +
                          dgn + " processing " +
                          this_flag)
                if bumper is None:
                    if get_verbose_enable():
                        print("[ PyGlops ] (verbose message in"
                              " _internal_bump_glop: owner check"
                              " and command string list was skipped"
                              "since bumped world.")
                    return
                if (dgItD is None) or (dgItD.get('owner_key') is None):
                    if dgItD['bump'] is None:
                        # verbose message already shown above
                        return
                    # self._run_semicolon_separated_
                    # commands(dgItD['bump'],
                    # bumpable_index, bumper_index);
                    commands = dgItD['bump'].split(";")
                    for command in commands:
                        command = command.strip()
                        if get_verbose_enable():
                            bumper_name_msg = "'" + bgn + "'"
                            if bgn is None:
                                bumper_name_msg = 'world'
                            print("[ PyGlops ] bump " +
                                  bumped.name +
                                  ": " + command + " '" +
                                  dgn + "' by " +
                                  bumper_name_msg)
                        if command == "obtain":
                            if bumper.actor_dict is None:
                                print(
                                    "[ PyGlops ] ERROR in " +
                                    "_internal_bump_glop: tried to " +
                                    "run obtain for bumper '" +
                                    str(bumper.name) +
                                    "' that is not an actor")

                            if this_flag == bad_flag:
                                print("[ PyGlops ] ERROR:"
                                      " _internal_bump_glop: obtained"
                                      " projectile while airborne")
                        self._run_command(command, bumpable_index,
                                          bumper_index)
                else:
                    if get_verbose_enable():
                        bumper_name_msg = "'" + str(bgn) + "'"
                        if bgn is None:
                            bumper_name_msg = 'world'
                        print("[ PyGlops ] " + bumper_name_msg
                              + " is not bumping into '" + bumped.name
                              + "' since it was already obtained by ["
                              + str(dgItD['owner_key']) + "] "
                              + str(self.glops[dgItD['owner_key']].name))
        else:
            if get_verbose_enable():
                # This is not actually a problem (non-damaging non-item
                # glop bumped something).
                print("[ PyGlops] {}"
                      " (verbose message in "
                      "_internal_bump_glop) bumped object '{}'"
                      " is not an item nor projectile"
                      " (maybe it was set to bump_enable manually"
                      " or _internal_bump_glop was called manually)"
                      "".format(datetime.now().time(), bumped.name))

    def get_player_glop_index(self, player_number):
        result = None
        if self._player_glop_index is not None:
            # TODO: check player_number instead
            result = self._player_glop_index
        else:
            if self.player_glop is not None:
                for i in range(0, len(self.glops)):
                    # TODO: check player_number instead
                    if self.glops[i] is self.player_glop:
                        result = i
                        self._player_glop_index = i
                        print("[ PyGlops ] WARNING:" +
                              " player_glop_index was not set (but"
                              " player_glop found in glops) so now"
                              " is.")
                        break
        return result

    def emit_yaml(self, lines, min_tab_string):
        # lines.append(min_tab_string+this_name+":")
        lines.append(min_tab_string+"glops:")
        for i in range(0, len(self.glops)):
            lines.append(min_tab_string+tab_string+"-")
            self.glops[i].emit_yaml(
                lines,
                min_tab_string+tab_string+tab_string
            )
        lines.append(min_tab_string
                     + "materials:"
                     " \"material to YAML is not implemented\"")

    def on_explode_glop(self, pos, radius, attacked_index,
                        projectile_dict):
        print("[ PyGlops ] subclass of subclass may implement"
              " on_explode_glop (and check for None before using"
              " variables other than pos)")

    def explode_glop_at(self, index, projectile_dict=None):
        print("[ PyGlops ] subclass should implement on_explode_glop"
              " (and check for None before using variables other than"
              " pos)")

    def set_camera_mode(self, perspective_number):
        self.settings['globals']['camera_perspective_number'] = \
            perspective_number

    def set_as_actor_at(self, index, template_dict):
        # result = False
        if index is None:
            print("[ PyGlops ] ERROR in set_as_actor_at: index is None")
            return False
        if index < 0:
            print("[ PyGlops ] ERROR in set_as_actor_at: index is "+str(index))
            return False
        if index >= len(self.glops):
            print("[ PyGlops ] ERROR in set_as_actor_at: index "+str(index)+" is out of range")
            return False
        if template_dict is None:
            template_dict = {}
        a_glop = self.glops[index]
        new_a_d = a_glop.deepcopy_with_my_type(template_dict)
        a_glop.actor_dict = {}
        d_properties = a_glop.deepcopy_with_my_type(
            self.settings['templates']['actor_properties'])
        d_actor_dict = a_glop.deepcopy_with_my_type(
            self.settings['templates']['actor'])
        a_glop.state['glop_index'] = index
        # NOTE: already has ['templates']['properties'] via
        # glop __init__
        for key in d_properties:
            a_glop.properties[key] = d_properties[key]
        for key in d_actor_dict:
            a_glop.actor_dict[key] = d_actor_dict[key]
        for key in template_dict:
            if key not in new_a_d:
                print("[ PyGlops ] ERROR in set_as_actor_at:"
                      "deepcopy_* failed to copy '" + key + "'")
        for key in new_a_d:
            if key not in \
                    self.settings['templates']['actor_properties']:
                a_glop.actor_dict[key] = new_a_d[key]
            else:
                a_glop.properties[key] = new_a_d[key]
                if get_verbose_enable():
                    print("[ PyGlops ] (verbose message in"
                          " set_as_actor_at) "
                          " used key '" + key + "' for"
                          "properties since in "
                          "self.settings['defaults']"
                          "['actor_properties']")

        a_glop.calculate_hit_range()
        self._bumper_indices.append(index)
        self._actor_indices.append(index)
        if get_verbose_enable():
            print("[ PyGlops ] Set [" + str(index) + "] '"
                  + str(a_glop.name) + "' as bumper")
            if a_glop.properties.get('hitbox') is None:
                print("  hitbox: None")
            else:
                print("  hitbox: {}"
                      "".format(a_glop.properties['hitbox']))
        # return result

    def new_glop_method(self):
        '''
        Always reimplement this so the camera is correct subclass.
        '''
        print("[ PyGlops ] ERROR: new_glop_method for PyGlop"
              " should never be used")
        return PyGlop()

    def set_player_fly(self, player_number, fly_enable):
        sg = self.settings['globals']
        # TODO: Get the player's unit
        if fly_enable is True:
            sg['fly_enables'][self.player_glop.name] = True
        else:
            sg['fly_enables'][self.player_glop.name] = False

    def set_fly_by_name(self, glop_name, fly_enable):
        self.settings['globals']['fly_enables'][glop_name] = \
            is_true(fly_enable)

    def get_mesh_by_name(self, name):
        result = None
        if name is not None:
            if len(self.glops) > 0:
                for index in range(0, len(self.glops)):
                    if name == self.glops[index].name:
                        result = self.glops[index]
        return result

    def get_glop_list_from_obj(self, source_path, new_glop_method,
                               pivot_to_g_enable=True):
        # load_obj(self, source_path): # TODO: ? swapyz=False):
        participle = "(before initializing)"
        linePlus1 = 1
        # firstMeshIndex = len(self.glops)
        results = None
        # self.lastCreatedMesh = None
        participle = "checking path"
        if not os.path.exists(source_path):
            print("ERROR: file '"+str(source_path)+"' not found")
            return None

        results = []
        # ^ create now, so that if None,
        # that means source_path didn't exist
        participle = "setting up WObjFile"
        this_objfile = WObjFile()
        participle = "loading WObjFile"
        this_objfile.load(source_path)
        if this_objfile.wobjects is None:
            print("ERROR: wobjects is None after loading '"
                  + source_path + "'")
            return None
        if len(this_objfile.wobjects) < 1:
            print("ERROR: 0 wobjects could be read from '" +
                  source_path + "'")
            return None
        # for i in range(0, len(this_objfile.wobjects)):
        for key in this_objfile.wobjects:
            participle = "getting wobject"
            this_wobject = this_objfile.wobjects[key]
            if this_wobject is not None:
                participle = "converting wobject..."
                this_pyglop = new_glop_method()
                this_pyglop.append_wobject(
                    this_wobject,
                    pivot_to_g_enable=pivot_to_g_enable)
                if this_pyglop is not None:
                    participle = "appending pyglop to scene"
                    # if results is None:
                    #     results = list()
                    results.append(this_pyglop)
                    if get_verbose_enable():
                        if this_pyglop.name is not None:
                            print("appended glop named '"
                                  + this_pyglop.name + "'")
                        else:
                            print("appended glop {name:None}")
                else:
                    print("ERROR: this_pyglop is None after"
                          + " converting from wobject")
            else:
                print("ERROR: this_wobject is None (object "
                      + str(i) + " from '" + source_path + "'")
        '''
        except:  # Exception as e:
            print("Could not finish a wobject in load_obj"
                  " while " + participle + " on line "
                  + str(linePlus1) + ":")
            view_traceback()
        '''
        return results

    def axis_index_to_string(self, index):
        result = "unknown axis"
        if (index == 0):
            result = "x"
        elif (index == 1):
            result = "y"
        elif (index == 2):
            result = "z"
        return result

    def set_as_item(self, glop_name, template_dict,
                    pivot_to_g_enable=False):
        result = False
        if glop_name is not None:
            for i in range(0, len(self.glops)):
                if self.glops[i].name == glop_name:
                    return self.set_as_item_at(
                        i,
                        template_dict,
                        pivot_to_g_enable=pivot_to_g_enable
                    )
                    break

    def _append_to_list_property(self, i, property_name, v):
        p = self.glops[i].properties.get(property_name)
        if p is None:
            p = []
            self.glops[i].properties[property_name] = p
            print("WARNING: _append_to_list_property"
                  " had to create list '{}' for glop \"{}\""
                  "".format(property_name, i))
        if v not in p:
            p.append(v)

    def add_damaged_sound_at(self, i, path):
        self._append_to_list_property(i, 'damaged_sound_paths', path)

    def add_bump_sound_at(self, i, path):
        self._append_to_list_property(i, 'bump_sound_paths', path)

    def preprocess_item(self, item_dict, sender_name="unknown"):
        f_name = "preprocess_item via " + sender_name
        if item_dict is None:
            print("[ PyGlops ] ERROR in preprocess_item: "
                  "item_dict is None so item will probably glitch!")
            return False
        if 'use' in item_dict:  # found deprecated use key
            if 'uses' not in item_dict:
                item_dict['uses'] = []
            if item_dict['use'] not in item_dict['uses']:
                item_dict['uses'].append(item_dict['use'])
            else:
                print("[ PyGlops ] WARNING in " + f_name + ": "
                      "item_dict['uses'] already contains "
                      + str(item_dict['use']))
            print("[ PyGlops ] WARNING in " + f_name + ": use is "
                  "deprecated--do item['uses'] = ['"
                  + str(item_dict['use']) + "'] instead")
            del item_dict['use']
        if 'uses' in item_dict:
            throw_enable = False
            for use in item_dict['uses']:
                if ('throw' in use) or ('shoot' in use):
                    # del item_dict['use']['throw_arc']
                    # item_dict['use']['attack']
                    if 'projectile_keys' not in item_dict:
                        print("[ PyGlops ] WARNING in "
                              + f_name + ": no ['projectile_keys'] in"
                              " item, so if thrown, projectile_dict"
                              " will have all you gave "
                              + str(item_dict) + " available to "
                              "on_attacked_glop so hopefully you"
                              " didn't put anything big in there ("
                              " it gets deepcopied if"
                              " drop_enable=False)!")
                        item_dict['projectile_keys'] = []
                        projectile_dict_template = \
                            self.ui.dummy_glop.deepcopy_with_my_type(
                                item_dict)
                        for copy_key in projectile_dict_template:
                            item_dict['projectile_keys'].append(
                                projectile_dict_template[copy_key])

                    # else:
                    #     if 'hit_damage' not in \
                    #             item_dict['as_projectile']:
                    #         print("[ PyGlops ] WARNING: no "
                    #               "['hit_damage'] "
                    #               "in ['as_projectile']"
                    #               "in item--so won't do damage")
        else:
            # It is an item with no use.
            pass
        if 'droppable' in item_dict:
            print("[ PyGlops ] WARNING in " + f_name
                  + ": droppable is not"
                  " implemented yet--you may have meant drop_enable"
                  " instead")
            if not is_true(item_dict['droppable']):
                item_dict['drop_enable'] = False
            print("            droppable: "
                  + str(is_true(item_dict['droppable'])))
        if 'drop_enable' in item_dict:
            if (not (item_dict['drop_enable'] is False)) and \
               (not (item_dict['drop_enable'] is True)):
                prevVal = item_dict['drop_enable']
                item_dict['drop_enable'] = is_true(prevVal)
                print("[ PyGlops ] NOTE in " + f_name +
                      ": converting drop_enable to boolean: "
                      " {} (was {})"
                      "".format(is_true(item_dict['drop_enable']),
                                prevVal))
            elif get_verbose_enable():
                print("[ PyGlops ] (verbose message in {}"
                      ") drop_enable: {}"
                      "".format(f_name,
                                is_true(item_dict['drop_enable'])))
        if 'state' in item_dict:
            print("[ PyGlops ] WARNING in " + f_name + ": state is "
                  "a reserved key used for situational data--"
                  "it will be overwritten with a dict "
                  "containing internals")
        if 'name' not in item_dict:
            print("[ PyGlops ] WARNING in " + f_name + ": no 'name'"
                  " in given item dict")
        item_dict['state'] = {}

    def set_as_item_at(self, i, template_dict, pivot_to_g_enable=False):
        result = False
        item_dict = self.glops[i].deepcopy_with_my_type(template_dict)
        # ^ Deepcopy to prevent every instance from being the same dict
        #   and from being modified later if template is modified
        self.glops[i].item_dict = item_dict
        self.preprocess_item(item_dict, sender_name="set_as_item_at")
        self.glops[i].item_dict['glop_name'] = self.glops[i].name
        self.glops[i].item_dict['state']['glop_index'] = i
        self.glops[i].state['glop_index'] = i
        drop_enable = True
        if 'drop_enable' in item_dict:
            if not is_true(item_dict['drop_enable']):
                drop_enable = False
        if not drop_enable:
            item_dict['fires_glops'] = list()
            # TODO: check for fired_sprite_path and fired_sprite_size
            item_dict['fires_glops'].append(self.glops[i])
            if get_verbose_enable():
                print("[ PyGlops ] (verbose message in set_as_item_at)"
                      " appending self to fires_glops since is not"
                      " droppable")

        self.glops[i].properties['bump_enable'] = True
        self.glops[i].state['in_range_indices'] = []
        # ^ allows to be obtained at start of main event
        #   loop since considered not in range already
        self.glops[i].properties['hit_radius'] = 0.1
        if pivot_to_g_enable:
            self.glops[i].transform_pivot_to_geometry()

        this_glop = self.glops[i]
        tgp = self.glops[i].properties
        tgv = this_glop.vertices
        self._bumpable_indices.append(i)
        if tgv is None:
            print("[ PyGlops ] WARNING: new item has no vertices"
                  " (setting hit_radius to 0)")
            tgp['hit_radius'] = 0.
            return result
        try:
            vertex_count = int(len(tgv)/this_glop.vertex_depth)
            v_offset = 0
            min_y = None
            po_1 = this_glop._POSITION_OFFSET+1
            for v_number in range(0, vertex_count):
                if min_y is None or tgv[v_offset+po_1] < min_y:
                    min_y = tgv[v_offset+po_1]
                v_offset += this_glop.vertex_depth
            if min_y is not None:
                tgp['hit_radius'] = min_y
                if tgp['hit_radius'] < 0.0:
                    tgp['hit_radius'] = 0.0 - tgp['hit_radius']
            else:
                print("[ PyGlops] ERROR in set_as_item_at:" +
                      " could not read any y values" +
                      " from glop named " +
                      str(this_glop.name))
        except:
            print("[ PyGlops ] WARNING: new item '"
                  + self.glops[i].name + "' (name='"
                  + str(template_dict.get('name')) + "') at " + str(i)
                  + " has insufficient mesh data to calculate"
                  " hit_radius automatically (this exception is"
                  " not a problem unless you meant to make a"
                  " visible item):")
            view_traceback(indent="            ")
        # tgp['hit_radius'] = 1.0
        return result

    def use_item_at(self, user_glop, inventory_index, this_use=None):
        '''
        Returns:
        Get a string for how it was used from self.on_item_use,
        otherwise return None if not used for any reason.
        '''
        f_name = "use_item_at"
        VMSG = " (verbose message in use_item_at)"
        try:
            if user_glop is None:
                print(
                    "[ PyGlops] ERROR in use_item_at: user_glop is None"
                )
                return None

            if user_glop.name is None:
                user_glop.name = str(uuid.uuid4())
                print("[ PyGlops ] ERROR in use_item_at: "
                      "user_glop.name was None (set to '"
                      + user_glop.name + "'"
                      " for safety)")
            if user_glop.name not in debug_dict:
                debug_dict[user_glop.name] = {}
            ddu = debug_dict[user_glop.name]
            ugad = user_glop.actor_dict
            item_dict = ugad['inventory_items'][inventory_index]
            ids = item_dict['state']
            item_glop = None
            this_glop_index = None
            if 'glop_index' in ids:
                this_glop_index = ids['glop_index']
                if this_glop_index is not None:
                    item_glop = self.glops[this_glop_index]
                # else not a glop--continue anyway

            item_glop_name = None
            if item_glop is not None:
                item_glop_name = item_glop.name
                if item_glop.item_dict is None:
                    if get_verbose_enable():
                        print("[ PyGlops ]{}"
                              " using item_glop with glop_index"
                              " where glop is not an item (maybe"
                              " should not be in {}'s"
                              " slot's item_dict)"
                              "".format(VMSG, user_glop.name))
                    # if item_glop.item_dict is not None:
                    #     item_dict = item_glop.item_dict
                    # else:
                    #     print("[ PyGlops ] ERROR in use_item_at:"
                    #           " could not find item_dict in"
                    #           " inventory OR item_glop")
            # else:
            #     print("[ PyGlops ] ERROR: use_item_at"
            #           " could not find item_dict in inventory"
            #           " slot {} of glop named {} and therefore"
            #           " could not get item_glop"
            #           "".format(inventory_index,
            #                     user_glop.name))
            #     return None
            if item_dict is None:
                print("[ PyGlops ] ERROR in use_item_at: "
                      "could not get item_dict from .")
                # if get_verbose_enable():
                #     msg = "[ PyGlops ]" + VMSG + " item is not ready"
                #     if 'cooldown' in item_dict:
                #         msg += (
                #             " (cooldown in " +
                #             str(item_dict['cooldown'] -
                #                 (time.time() -
                #                  ids['last_used_time']))
                #     print(msg)
                return None
            if item_glop_name is None:
                item_glop_name = item_dict.get('glop_name')
            elif item_glop_name != item_dict.get('glop_name'):
                print("[ PyGlops ] ERROR in use_item_at: " +
                      "glop_name '" +
                      str(item_dict.get('glop_name')) +
                      "' differs from actual item_glop.name '" +
                      str(item_glop_name))
            if item_dict.get('name') == "Empty":
                # Still let programmer handle the Empty item:
                return self.on_item_use(user_glop, item_dict, None)

            if 'fire_type' in item_dict:
                print("[ PyGlops ] WARNING in use_item_at"
                      ": fire_type is deprecated. Add the"
                      " use to the item dict's"
                      " 'uses' list instead")
                # If item_glop is None, try fires_glops key in dict
                # (see throw_glop):
                # if item_glop is None:
                #     if item_dict['fire_type'] != \
                #             "throw_linear":
                #         print("[ PyGlops ] WARNING: " +
                #               item_dict['fire_type'] +
                #               " not implemented, so" +
                #               " using throw_linear")
                #     self.throw_glop(
                #         user_glop, item_dict,
                #         original_glop_or_None=None,
                #         inventory_index=inventory_index)
            is_ready = True
            if 'cooldown' in item_dict:
                is_ready = False
                cooled_time = time.time() - ids['last_used_time']
                if (ids.get('last_used_time') is None) or \
                   (cooled_time >= item_dict['cooldown']):
                    if ids.get('last_used_time') is not None:
                        is_ready = True
                        ddu['item_dict.cooldown'] = "0.0 #ready"
                    # else Don't assume cooled down when obtained,
                    # otherwise rapid firing items will be allowed
                    ids['last_used_time'] = time.time()
            else:
                ddu['item_dict.cooldown'] = "None"
            if not is_ready:
                if 'cooldown' in item_dict:
                    ddu['item_dict.cooldown'] = item_dict['cooldown']
                return None
            this_use = None
            if 'uses' in item_dict:
                if get_verbose_enable():
                    print("[ PyGlops ]" + VMSG
                          + "'" + str(user_glop.name)
                          + "' using item in slot " +
                          str(ugad['inventory_index']))

                if 'use_sound' in item_dict:
                    self.play_sound(item_dict['use_sound'])
                if this_use is None:
                    this_use = item_dict['uses'][0]
                if get_verbose_enable():
                    if item_glop_name is None:
                        # ERROR: item_glop.name is None
                        item_glop_name = (
                            "<ERROR: item_glop.name is None>"
                        )
                        print("[ PyGlop ]" + VMSG +
                              " item has no glop_name:" +
                              str(item_dict))
                    print("[ PyGlops ]" + VMSG + " uses:" +
                          str(item_dict['uses']) +
                          "; item_glop.name:" +
                          str(item_glop_name))
                if get_verbose_enable():
                    print("[ PyGlops ]" + VMSG + " " + this_use + " "
                          + item_glop_name)
                if ('throw' in this_use) or ('shoot' in this_use):
                    if (('drop_enable' not in item_dict)
                            or is_true(item_dict['drop_enable'])):
                        print("[ PyGlops ] using throw_glop"
                              " with drop since"
                              " drop_enable not"
                              " present/False")
                        self.throw_glop(
                            user_glop,
                            item_dict,
                            item_glop,
                            this_use=this_use,
                            duplicate_enable=False,
                            inventory_index=inventory_index
                        )
                    else:
                        if get_verbose_enable():
                            print("[ PyGlops ]" + VMSG
                                  + "using throw_glop"
                                  " with duplicate_enable since"
                                  " not drop_enable")
                        self.throw_glop(user_glop,
                                        item_dict,
                                        item_glop,
                                        this_use=this_use,
                                        inventory_index=inventory_index)
                else:
                    if get_verbose_enable():
                        print("[ PyGlops ]" + VMSG
                              + " use is unknown: '" + str(this_use)
                              + "' (triggering on_item_use anyway)")
            else:
                name_msg = "<no name item>"
                if item_dict['name'] in item_dict:
                    name_msg = str(item_dict['name'])
                print("[ PyGlops ] ERROR in use_item_at: "
                      + name_msg + " has no uses "
                      "item:" + str(item_dict)
                      + "(triggering on_item_use anyway).")
            self.on_item_use(user_glop, item_dict, this_use)
        except Exception as ex:
            print("[ PyGlops ] ERROR: Could not finish use_selected:")
            if user_glop is not None:
                print("  user_glop.name: " + str(user_glop.name))
                print("  item_dict: {}".format(item_dict))
                print(
                    "  len(user_glop.actor_dict['inventory_items']):"
                    + str(len(user_glop.actor_dict['inventory_items']))
                )
            else:
                print("  user_glop: None")
            print('  inventory_index:' + str(inventory_index))
            print("  traceback: '''")
            view_traceback()
            print("  '''")
            raise ex

    def throw_glop(self, user_glop, item_dict, original_glop_or_None,
                   this_use=None, remove_item_dict=True,
                   set_projectile=True, duplicate_enable=True,
                   inventory_index=None):
        '''
        Keyword arguments:
        this_use -- State which mode in which to use the item from
                    among the possible uses. If None, the user didn't
                    try to use it in a certain way, so the first use
                    available will be used.

        throw_copy -- if did not provide original_glop, item_dict must
                      have fires_glops key that is list of *Glop objects
        duplicate_enable -- if True, copies the object (by instance);
                            if False, the SAME item will be used and it
                            will leave player's inventory
        inventory_index -- if None, and droppable (or droppable boolean
                           is not in item_dict), item will not be dropped
                           and warning will be logged to console
        '''
        VMSG = " (verbose message in throw_glop)"
        og = original_glop_or_None
        favorite_pivot = None
        fires_glops = None
        if user_glop is None:
            print("[pyglops.py] user_glop is None in throw_glop")
            return False
        if og is not None:
            fires_glops = [og]
        elif ((item_dict is not None)
                and ('fires_glops' in item_dict)):
            fires_glops = item_dict['fires_glops']
        else:
            print("[ PyGlops ] ERROR in throw_copy: nothing"
                  " done since cannot get glop to throw from"
                  " 'fires_glops' key of item_dict nor was"
                  " original_glop param set")
        if fires_glops is None:
            print("[ PyGlops ] ERROR in throw_glop: user_glop None")
            return False
        for fires_glop in fires_glops:
            # formerly in item_dict['fires_glops']
            if this_use is None:
                if 'uses' in item_dict:
                    for try_use in item_dict['uses']:
                        if ('throw' in try_use) or \
                                ('shoot' in try_use):
                            this_use = try_use
                            print(
                                "[ PyGlops ] WARNING in " +
                                "throw_glop: this_use was" +
                                " not specified, so " +
                                "using " + str(try_use) +
                                " (found in " +
                                "item_dict['uses'])"
                            )
                            break
                    if this_use is None:
                        print("[ PyGlops ] WARNING in "
                              "throw_glop: this_use was not"
                              " specified, and uses did not"
                              " contain a string containing"
                              " 'throw_', so using default"
                              " throw (linear)")
                else:
                    print("[ PyGlops ] WARNING in "
                          "throw_glop: this_use was not"
                          " specified, and uses was not"
                          " in item_dict, so using default"
                          " throw (linear)")
            # if get_verbose_enable():
            #     print("[ PyGlops ]" + VMSG +
            #           " calling copy_as_mesh_instance for"
            #           "fires_glop")
            if duplicate_enable:
                fired_glop = fires_glop.copy_as_mesh_instance()
            else:
                fired_glop = fires_glop
            if (og is None) or (fired_glop is not og):
                fired_glop.name = \
                    "fired_glop[" + str(self.fired_count) + "]"
                self.fired_count += 1
            item = fired_glop.item_dict

            if 'as_projectile' in item_dict:
                print("[ PyGlops ] WARNING in throw_glop: "
                      "as_projectile is deprecated. use "
                      "'hit_damage' directly in item_dict"
                      " and set "
                      "item_dict['projectile_keys']"
                      "=['hit_damage'] instead")
            if fired_glop.projectile_dict is not None:
                print("[ PyGlops ] ERROR in throw_glop: "
                      "projectile_dict was already present"
                      "before thrown (this should never"
                      " happen)--will be reset")
            fired_glop.projectile_dict = {}
            # ^ should only exist while airborne
            projectile = fired_glop.projectile_dict
            projectile['owner'] = user_glop.name
            projectile['owner_key'] = user_glop.glop_index
            if user_glop.glop_index is None:
                print("[ PyGlops ] ERROR in throw_glop:"
                      " user_glop.glop_index is None")
            if 'projectile_keys' in item_dict:
                for projectile_var_name in \
                        item_dict['projectile_keys']:
                    projectile[projectile_var_name] = \
                        item_dict[projectile_var_name]
            # projectile = \
            #     get_dict_deepcopy(item_dict['as_projectile'])
            fired_glop.properties['bump_enable'] = True
            fired_glop.state['in_range_indices'] = \
                [user_glop.glop_index]

            if fired_glop.properties.get('hitbox') is None:
                fired_glop.calculate_hit_range()
            if get_verbose_enable():
                print("[ PyGlops ]{}"
                      " set projectile_dict"
                      " and bump_enable for '{}'"
                      " and added to _bumpable_indices"
                      "".format(VMSG, fired_glop.name))
                print("            for item used by"
                      " user_glop.glop_index:"
                      + str(user_glop.glop_index) + "; ")

            fired_glop._t_ins.x = user_glop._t_ins.x
            ugp = user_glop.properties
            if ugp.get('hitbox') is not None:
                fired_glop._t_ins.y = (
                    ugp['hitbox']['minimums'][1] +
                    ugp['eye_height']
                )
            else:
                fired_glop._t_ins.y = (
                    ugp['hit_radius'] +
                    ugp['eye_height']
                )
            fired_glop._t_ins.z = user_glop._t_ins.z

            this_speed = 15.  # meters/sec
            custom_speed_name = None  # for debugging
            if user_glop.actor_dict is not None:
                if 'throw_speed' in user_glop.actor_dict:
                    this_speed = \
                        user_glop.actor_dict['throw_speed']
                    custom_speed_name = 'throw_speed'
            if 'projectile_speed' in item_dict:
                this_speed = item_dict['projectile_speed']
                custom_speed_name = 'projectile_speed'
            if get_verbose_enable():
                if custom_speed_name is None:
                    custom_speed_name = "default"
                print("[ PyGlops ]" + VMSG
                      + " throw_glop is using"
                      " speed " + str(this_speed) + " from "
                      + custom_speed_name + " for "
                      + fired_glop.name)

            x_angle = None
            y_angle = None
            z_angle = None
            try:
                x_angle = user_glop._r_ins_x.angle
                if this_use == 'throw_arc':
                    x_angle += math.radians(30)
                if x_angle > math.radians(90):
                    x_angle = math.radians(90)
                fired_glop.state['velocity'][1] = \
                    this_speed * math.sin(x_angle)
                this_h_speed = this_speed * math.cos(x_angle)
                # horizontal speed is affected by pitch
                # (this is correct since x is cos(y.angle) and
                # z is sin(y.angle))
                fired_glop.state['velocity'][0] = (
                    this_h_speed *
                    math.cos(user_glop._r_ins_y.angle)
                )
                fired_glop.state['velocity'][2] = (
                    this_h_speed *
                    math.sin(user_glop._r_ins_y.angle)
                )
            except:
                fired_glop.state['velocity'][0] = 0
                fired_glop.state['velocity'][2] = 0
                print(
                    "[ PyGlop ] ERROR--"
                    "throw_glop could not finish getting throw"
                    " x,,z values"
                )
                view_traceback()

            fired_glop.state['visible_enable'] = True

            if fired_glop.glop_index is None:
                self.glops.append(fired_glop)
                fired_glop_index = None
                # Check identity for multithreading paranoia:
                if self.glops[len(self.glops) - 1] is \
                        fired_glop:
                    fired_glop_index = len(self.glops) - 1
                else:
                    print("[ PyGlops ] INFO in throw_glop: "
                          "correcting an incorrect glop index"
                          " directly after adding to glops")
                    fired_glop_index = \
                        self.index_of_mesh(fired_glop.name)
                fired_glop.glop_index = fired_glop_index
                fired_glop.state['glop_index'] = \
                    fired_glop_index
                # NOTE: show_glop is done below in all cases
            else:
                if duplicate_enable:
                    print("[ PyGlop ] WARNING in throw_glop:"
                          " not adding to glop list"
                          " fired_glop.glop_index already set"
                          " (you should use"
                          " duplicate_enable=True param if you"
                          " want an instance)")
            if (item is not None) and ('inventory_index' in item):
                del item['inventory_index']
                print("[ PyGlop ] WARNING: inventory_index"
                      " in item_dict is deprecated (so deleted)"
                      "--should only be in actor_dict and"
                      " item_event")
            if duplicate_enable:
                # Only remove links from the copy.
                # (NOTE: owner and owner_key
                # [and projectile_dict] are removed by
                # ui.update* such as update_glsl when hits)
                if fired_glop.state is not None:
                    if 'links' in fired_glop.state:
                        fired_glop.state['links'] = []
                if item is not None:
                    pass
                    # if 'inventory_index' in item:
                    #     del item['inventory_index']
            else:
                # If not duplicate_enable, remove links
                # (necessary since made no copy).
                if inventory_index is not None:
                    event_dict = user_glop.pop_glop_item(
                        inventory_index
                    )
                    event_dict['calling_method'] = "throw_glop"
                    self.after_selected_item(event_dict)
                else:
                    print("[ PyGlop ] ERROR in throw_glop: "
                          "item is drop_enable on use, but "
                          "inventory_index param is missing, so"
                          " item will not be dropped (item will"
                          " be severely glitched)")

                if og is not None:
                    if len(og.state['links']) > 0:
                        og.state['links'] = []
                    if get_verbose_enable():
                        print("[ PyGlops ]" + VMSG + " removed"
                              " relations from item_glop"
                              " since left inventory.")
                else:
                    print("[ PyGlops ] WARNING in throw_glop: "
                          "did not remove relations from"
                          " original item glop since"
                          " original_glop_or_None param was"
                          " None (though left inventory)."
                          " Pass that param when using"
                          " duplicate_enable=False for this to"
                          " work.")

            self.show_glop(fired_glop.glop_index)
            # ^ adds to display, such as adding mesh to canvas
            fired_glop.properties['physics_enable'] = True
            fired_glop.state['on_ground_enable'] = False
            fired_glop.properties['bump_enable'] = True
            # item is bumpable (but only actor can be bumper)
            self._bumpable_indices.append(fired_glop.glop_index)

            # TODO: why was this nonsense here:
            # if favorite_pivot is None:
            #     favorite_pivot = fired_glop._t_ins.xyz
            # fired_glop._t_ins.x += \
            #     fired_glop._t_ins.x - favorite_pivot[0]
            # fired_glop._t_ins.y += \
            #     fired_glop._t_ins.y - favorite_pivot[1]
            # fired_glop._t_ins.z += \
            #     fired_glop._t_ins.z - favorite_pivot[2]

            # x_off, z_off = get_rect_from_polar_rad(
            #     this_speed, user_glop._r_ins_y.angle)
            # this_h_speed = (
            #     this_speed *
            #     math.cos(user_glop._r_ins_x.angle)
            # )
            # fired_glop.state['velocity'][0] = x_off
            # fired_glop.state['velocity'][2] = z_off
            # x_off, y_off = \
            #     get_rect_from_polar_rad(
            #         this_speed,
            #         user_glop._r_ins_x.angle)
            # fired_glop.state['velocity'][1] = y_off
            # print("projectile velocity x,y,z:"
            #       + str((fired_glop.state['velocity'][0],
            #              fired_glop.state['velocity'][1],
            #              fired_glop.state['velocity'][2])))

            # print("FIRED self._bumpable_indices: "
            #       + str(self._bumpable_indices))

            # start off a ways away:
            # fired_glop._t_ins.x += \
            #     fired_glop.state['velocity'][0]*2
            # fired_glop._t_ins.y += \
            #     fired_glop.state['velocity'][1]*2
            # fired_glop._t_ins.z += \
            #     fired_glop.state['velocity'][2]*2
            # fired_glop._t_ins.y += \
            #     ugp['eye_height']/2


    def update_item_visual_debug(self):
        if self.player_glop is None:
            return
        if self.player_glop.actor_dict is None:
            return
        pgad = self.player_glop.actor_dict
        if 'Player' not in debug_dict:
            debug_dict['Player'] = {}
        ddp = debug_dict['Player']
        if pgad['inventory_index'] < 0:
            ddp['selected_item'] = "<no slot selected>"
            return
        try:
            pgadii = pgad['inventory_items']
            if 'glop_name' in pgadii[pgad['inventory_index']]:
                ddp['selected_item.glop_name'] = \
                    pgadii[pgad['inventory_index']]['glop_name']
            else:
                ddp['selected_item.glop_name'] = "<unnamed item>"
        except:
            ddp['selected_item'] = ("<bad inventory_index=\"" +
                                    str(pgad['inventory_index']) + ">")

    def set_coord(self, index, value):
        print("[ PyGlop ] ERROR: set_coord should be implemented"
              "in your subclass")

    def get_coord(self, index):
        print("[ PyGlop ] ERROR: get_coord should be implemented"
              "in your subclass")

    def use_selected(self, user_glop):
        '''
        Returns:
        See use_item_at's return (except None if user is not actor,
            has no inventory, has no selected inventory slot, selected
            inventory slot is bad, or the item at the given slot
            of the actor dict's inventory_items is None).
        '''
        f_name = "use_selected"
        ugad = None
        if user_glop is None:
            print("[ PyGlops ] ERROR in " + f_name
                  + ": user_glop is None")
            return
        ugad = user_glop.actor_dict
        if ugad is None:
            print("[ PyGlops ] ERROR in " + f_name
                  + ": user_glop.actor_dict is None"
                  " (non-actor tried to use item)")
            return
        if ugad.get('inventory_items') is None:
            print("[ PyGlops ] ERROR in " + f_name
                  + ": user_glop.actor_dict['inventory_items']"
                  " is None (actor without inventory tried"
                  " to use item)")
            return
        if ugad.get('inventory_index') is None:
            print("[ PyGlops ] ERROR in " + f_name
                  + ": user_glop."
                  "actor_dict['inventory_index'] is not present"
                  " (actor tried to use item before inventory"
                  " was ready)")
            return

        if int(ugad['inventory_index']) < 0:
            if get_verbose_enable():
                print("[ PyGlops ] (verbose message in " + f_name
                      + ") no inventory slot is selected ("
                      "user_glop.actor_dict['inventory_index']"
                      " is < 0 for " + str(user_glop.name) + ")")
            return
        if ugad['inventory_index'] >= len(ugad['inventory_items']):
            print("[ PyGlops ] ERROR in " + f_name
                  + ": inventory_index " + str(ugad['inventory_index'])
                  + " is not within inventory list range "
                  + str(len(ugad['inventory_items'])))
            return
        if ugad['inventory_items'][ugad['inventory_index']] is None:
            if get_verbose_enable():
                print("[ PyGlops ] (verbose message in " + f_name
                      + ": nothing to do since selected inventory"
                      " slot is None")
            return
        return self.use_item_at(user_glop, ugad['inventory_index'])

    def on_load_glops(self):
        '''
        Your subclass of KivyGlopsWindow should usually implement
        on_load_glops to initialize your variables when the window
        loads.
        '''
        print("[ PyGlops ] WARNING: program-specific subclass of a"
              "framework-specific subclass of PyGlops should implement"
              " on_load_glops (and usually on_update_glops which will"
              " be called before each frame is drawn)")

    def on_update_glops(self):
        '''
        subclass of PyGlops can implement on_update_glops
        '''
        pass

    def on_killed_glop(self, index, projectile_dict):
        pass
        if get_verbose_enable():
            print("[ PyGlops ] (verbose message in on_killed_glop)"
                  " subclass can implement on_killed_glop")

    def kill_glop_at(self, index, projectile_dict=None):
        self.hide_glop(self.glops[index])
        self.on_killed_glop(index, projectile_dict)
        # self.glops[index].properties['bump_enable'] = False
        if self.glops[index].actor_dict is not None:
            self.glops[index].actor_dict['alive_enable'] = False
        else:
            print("[ PyGlop ] WARNING in kill_glop_at: '"
                  + self.glops[index].name + "' is not an actor")

    # def bump_glop(self, detectable_name, bumper_name):
    #     return None

    def on_item_use(self, user_glop, item_dict, this_use):
        '''
        Sequential arguments:
        this_use -- either is None. or is a string for how the item was used
        '''
        return None

    def on_bump(self, glop_index, bumper_index):
        return None

    def on_bump_world(self, glop_index, description):
        '''
        bumped into world (normally 'ground'--though that
        could be edge of walkmesh too)
        '''
        return None

    def on_attacked_glop(self, attacked_index, attacker_index,
                         projectile_dict):
        '''
        Implement this in your subclass if you want something to happen
        in this case.

        # trivial example:
        self.glops[attacked_index].actor_dict['hp'] -= \
            projectile_dict['hit_damage']
        if self.glops[attacked_index].actor_dict['hp'] <= 0:
            self.explode_glop_at(attacked_index)
        '''
        print("[ PyGlops ] on_attacked_glop should be implemented by"
              " the subclass which would know how to damage or"
              " calculate defense or other properties")
        return None

    def _deprecated_on_obtain_glop_by_name(self, bumpable_name,
                                           bumper_name):
        '''
        This still works but makes your handler slow if you, as
        expected, have to search for the glop index by name in order to
        make use of the name. Recommended replacement event handler:
        on_obtain_glop bumpable_glop provides you with bumpable glop's
        name (usually has item_dict) bgn provides you with bumper
        glop's name (usually has actor_dict)
        '''
        raise NotImplementedError("_deprecated_on_obtain_glop_by_name")
        return None

    def on_obtain_glop(self, bumpable_index, bumper_index):
        return None

    def get_nearest_walkmesh_vec3_using_xz(self, pos):
        '''
        returns modified position (except y)
        '''
        result = None
        closest_distance = None
        poly_sides_count = 3
        # corners = list()
        # for i in range(0,poly_sides_count):
        #     corners.append( (0.0, 0.0, 0.0) )
        for this_glop in self._walkmeshes:
            face_i = 0
            indices_count = len(this_glop.indices)
            # assumes tris (see also poly_side_count locals)

            while (face_i < indices_count):
                wrpo0 = v_offset+this_glop._POSITION_OFFSET+0
                wrpo1 = v_offset+this_glop._POSITION_OFFSET+1
                wrpo2 = v_offset+this_glop._POSITION_OFFSET+2
                gvd = this_glop.vertex_depth
                verts = this_glop.vertices
                v_offset = this_glop.indices[face_i]*gvd
                a_vertex = verts[wrpo0], verts[wrpo1], verts[wrpo2]
                v_offset = this_glop.indices[face_i+1]*gvd
                b_vertex = verts[wrpo0], verts[wrpo1], verts[wrpo2]
                v_offset = this_glop.indices[face_i+2]*gvd
                c_vertex = verts[wrpo0], verts[wrpo1], verts[wrpo2]
                # side_a_distance = \
                #     get_distance_vec3_xz(pos, a_vertex, b_vertex)
                # side_b_distance = \
                #     get_distance_vec3_xz(pos, b_vertex, c_vertex)
                # side_c_distance = \
                #     get_distance_vec3_xz(pos, c_vertex, a_vertex)
                this_point, this_distance = get_near_line_info_xz(
                    pos, a_vertex, b_vertex)
                tri_distance = this_distance
                tri_point = this_point

                this_point, this_distance = get_near_line_info_xz(
                    pos, b_vertex, c_vertex)
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                this_point, this_distance = get_near_line_info_xz(
                    pos, c_vertex, a_vertex)
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                if ((closest_distance is None)
                        or (tri_distance < closest_distance)):
                    result = tri_point[0], tri_point[1], tri_point[2]
                    # ok to return y since already swizzled
                    # (get_near_line_info_xz copies source's y
                    # to return's y)
                    closest_distance = tri_distance
                face_i += poly_sides_count
        return result

    def get_nearest_walkmesh_vertex_using_xz(self, pos):
        result = None
        second_nearest_pt = None
        for w_glop in self._walkmeshes:
            X_i = w_glop._POSITION_OFFSET + 0
            Y_i = w_glop._POSITION_OFFSET + 1
            Z_i = w_glop._POSITION_OFFSET + 2
            X_abs_i = X_i
            Y_abs_i = Y_i
            Z_abs_i = Z_i
            wgv = w_glop.vertices
            v_len = len(wgv)
            distance_min = None
            while X_abs_i < v_len:
                distance = math.sqrt((pos[0]-wgv[X_abs_i+0])**2
                                     + (pos[2]-wgv[X_abs_i+2])**2)
                if ((result is None) or (distance_min is None)
                        or (distance < distance_min)):
                    # if result is not None:
                    #     second_nearest_pt = \
                    #         result[0],result[1],result[2]
                    result = (wgv[X_abs_i+0],
                              wgv[X_abs_i+1],
                              wgv[X_abs_i+2])
                    distance_min = distance
                X_abs_i += w_glop.vertex_depth

            # DOESN'T WORK since second_nearest_pt may not be on edge:
            # if second_nearest_pt is not None:
            #     distance1 = get_distance_vec3_xz(pos, result)
            #     distance2 = \
            #         get_distance_vec3_xz(pos, second_nearest_pt)
            #     distance_total=distance1+distance2
            #     distance1_weight = distance1/distance_total
            #     distance2_weight = distance2/distance_total
            #     result = ((result[0] * distance1_weight
            #                + second_nearest_pt[0] * distance2_weight),
            #               (result[1] * distance1_weight
            #                + second_nearest_pt[1] * distance2_weight),
            #               (result[2] * distance1_weight
            #                + second_nearest_pt[2] * distance2_weight))
            #     # TODO: use second_nearest_pt to get nearest location
            #     # along the edge instead of warping to a vertex
        return result

    def is_in_any_walkmesh_xz(self, check_vec3):
        return get_walkmesh_info_xz(check_vec3) is not None

    def get_walkmesh_info_xz(self, check_vec3):
        '''
        get container walkmesh and poly index that is closest on xz plane
        returns: (walkmesh, polygon_index) tuple
        '''
        result = None
        X_i = 0
        flat_second_i = 2  # actually z since ignoring y
        check_vec2 = check_vec3[X_i], check_vec3[flat_second_i]
        walkmesh_i = 0
        while walkmesh_i < len(self._walkmeshes):
            w_glop = self._walkmeshes[walkmesh_i]
            wgv = w_glop.vertices
            wgi = w_glop.indices
            X_i = w_glop._POSITION_OFFSET + 0
            si = w_glop._POSITION_OFFSET + flat_second_i
            vd = w_glop.vertex_depth
            poly_side_count = 3  # assumes tris
            poly_count = int(len(wgi)/poly_side_count)
            po = 0  # polygon offset
            for poly_index in range(0, poly_count):
                if is_in_triangle_vec2(
                        check_vec2,
                        (wgv[wgi[po]*vd+X_i], wgv[wgi[po]*vd+si]),
                        (wgv[wgi[po+1]*vd+X_i], wgv[wgi[po+1]*vd+si]),
                        (wgv[wgi[po+2]*vd+X_i], wgv[wgi[po+2]*vd+si])):
                    result = dict()
                    result['walkmesh_index'] = walkmesh_i
                    result['polygon_offset'] = po
                    break
                po += poly_side_count
            walkmesh_i += 1
        return result

    def use_walkmesh(self, name, hide=True):
        print("[ PyGlops ] ERROR: You must implement use_walkmesh"
              " since implementation depends on the target platform.")
        return False

    def get_similar_names(self, partial_name):
        results = None
        checked_count = 0
        if (partial_name is not None) and (len(partial_name) > 0):
            partial_name_lower = partial_name.lower()
            results = list()
            for this_glop in self.glops:
                checked_count += 1
                if this_glop.name is not None:
                    if partial_name_lower in this_glop.name.lower():
                        results.append(this_glop.name)
                else:
                    print("ERROR in get_similar_names: a glop was None")
        else:
            print("ERROR in get_similar_names: tried to search for"
                  " blank partial_name")
        # print("checked " + str(checked_count))
        return results

    def get_indices_by_source_path(self, source_path):
        results = None
        checked_count = 0
        if source_path is not None and len(source_path) > 0:
            results = list()
            for index in range(0, len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                # print("checked "+this_glop.name.lower())
                if this_glop.source_path is not None:
                    if source_path == this_glop.source_path or \
                       source_path == this_glop.original_path:
                        results.append(index)
        # print("checked " + str(checked_count))
        return results

    def get_indices_of_similar_names(self, partial_name,
                                     allow_owned_enable=True):
        results = None
        checked_count = 0
        if (partial_name is not None) and (len(partial_name) > 0):
            partial_name_lower = partial_name.lower()
            results = list()
            for index in range(0, len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                # print("checked "+this_glop.name.lower())
                if ((this_glop.name is not None)
                        and (allow_owned_enable
                             or (this_glop.item_dict is None)
                             or ('owner' not in this_glop.item_dict))):
                    if partial_name_lower in this_glop.name.lower():
                        results.append(index)
        # print("checked " + str(checked_count))
        return results

    def get_index_lists_by_similar_names(self, partial_names,
                                         allow_owned_enable=True):
        '''
        Find list of similar names slightly faster than multiple calls
        to get_indices_of_similar_names: the more matches earlier in
        the given partial_names array, the faster this method returns
        (therefore overlapping sets are sacrificed).

        Returns: list that is always the length of partial_names + 1,
        as each item is a list of indices where name contains the
        corresponding partial name, except last index which is all others.
        '''
        results = None
        checked_count = 0
        if len(partial_names) > 0:
            results_len = len(partial_names)
            results = {}  # [list() for i in range(results_len + 1)]
            for index in range(0, len(self.glops)):
                this_glop = self.glops[index]
                checked_count += 1
                # print("checked "+this_glop.name.lower())
                # match_indices = [None]*results_len
                match = False
                for i in range(0, results_len):
                    partial_name_lower = partial_names[i].lower()
                    if ((this_glop.name is not None)
                        and (allow_owned_enable
                             or (this_glop.item_dict is None)
                             or ('owner' not in this_glop.item_dict))):
                        if partial_name_lower in this_glop.name.lower():
                            if not partial_names[i] in results:
                                results[partial_names[i]] = []
                            results[partial_names[i]].append(index)
                            match = True
                            # break
                # if not match:
                #     results[results_len].append(index)
        # print("checked "+str(checked_count))
        return results

    def set_world_boundary_by_object(self, thisGlopsMesh,
                                     use_x, use_y, use_z):
        self._world_cube = thisGlopsMesh
        if (self._world_cube is not None):
            self.world_boundary_min = [self._world_cube.get_min_x(),
                                       None,
                                       self._world_cube.get_min_z()]
            self.world_boundary_max = [self._world_cube.get_max_x(),
                                       None,
                                       self._world_cube.get_max_z()]

            for axis_index in range(0, 3):
                if self.world_boundary_min[axis_index] is not None:
                    self.world_boundary_min[axis_index] += \
                        self.projection_near + 0.1
                if self.world_boundary_max[axis_index] is not None:
                    self.world_boundary_max[axis_index] -= \
                        self.projection_near + 0.1
        else:
            self.world_boundary_min = [None, None, None]
            self.world_boundary_max = [None, None, None]

    # def get_keycode(self, key_name):
    #     print("ERROR: get_keycode must be implemented by the"
    #           " framework-specific subclass")
    #     return None

    # def _get_key_state_at(self, key_name):
    #     return self.player1_controller._get_key_state_at(
    #         self.ui.get_keycode(key_name)
    #     )

    def select_mesh_at(self, index):
        glops_count = len(self.glops)
        if index >= glops_count:
            index = 0
        if get_verbose_enable():
            print("trying to select index " + str(index)
                  + " (count is " + str(glops_count) + ")...")
        if (glops_count > 0):
            self.selected_glop_index = index
            self.selected_glop = self.glops[index]
        else:
            self.selected_glop = None
            self.selected_glop_index = None

    def index_of_mesh(self, name):
        result = -1
        name_lower = name.lower()
        for i in range(0, len(self.glops)):
            source_name = None
            source_name_lower = None
            if self.glops[i].source_path is not None:
                source_name = os.path.basename(
                    os.path.normpath(self.glops[i].source_path))
                source_name_lower = source_name.lower()
            if self.glops[i].name == name:
                result = i
                break
            elif self.glops[i].name.lower() == name_lower:
                print("WARNING: object with different capitalization" +
                      " was not considered a match: " +
                      self.glops[i].name)
            elif match_fn(source_name_lower, name_lower):
                result = i
                name_msg = "filename: '" + source_name + "'"
                if os.path.splitext(source_name_lower)[0] == name_lower:
                    name_msg = ("part of filename: '"
                                + os.path.splitext(source_name)[0]
                                + "'")
                print("WARNING: mesh was named '" +
                      str(self.glops[i].name) + "' but found using " +
                      name_msg)
                if (i + 1 < len(self.glops)):
                    for j in range(i+1, len(self.glops)):
                        sub_source_name_lower = None
                        if self.glops[j].source_path is not None:
                            sub_source_name_lower = os.path.basename(
                                os.path.normpath(
                                    self.glops[i].source_path)
                                ).lower()
                        if match_fn(source_name_lower, name_lower):
                            print("  * could also be mesh named '"
                                  + self.glops[j].name + "'")
                break
        return result

    def select_mesh_by_name(self, name):
        found = False
        index = self.index_of_mesh(name)
        if index > -1:
            self.select_mesh_at(index)
            found = True
        return found
