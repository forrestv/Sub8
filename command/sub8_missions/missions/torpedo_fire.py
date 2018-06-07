from txros import util
import rospy
from geometry_msgs.msg import Point
from sensor_msgs.msg import CameraInfo
from mil_msgs.msg import RangeStamped
import tf
from twisted.internet import defer
import sys
from sub8 import SonarObjects
from image_geometry import PinholeCameraModel
import numpy as np

# Current depth constant
CURRENT_DEPTH = 0
# The boolean that tells us if we have accomplished our mission.
TARGET_LOCK = False
# The number of frames we need to deterimine if we have a permenant lock
LOCK_THRESH = 10
# The counter that tells us if we have secured a permenant lock
LOCK_COUNTER = 0


# @util.cancellableInlineCallbacks
def check_depth():
    global CURRENT_DEPTH

    if (CURRENT_DEPTH - .15 < 1):
        return False
    else:
        return True


@util.cancellableInlineCallbacks
def update_point_callback(msg, sub):
    global TARGET_LOCK
    global LOCK_COUNTER
    global LOCK_THRESH

    m = msg

    if m.z == -6:
        print "up left"
        yield sub.move.up(.05).go(blind=true)
        yield sub.move.left(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == -5:
        print "up"
        yield sub.move.up(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == -4:
        print "up right"
        yield sub.move.up(.05).go(blind=true)
        yield sub.move.right(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == -1:
        # print "left"
        yield sub.move.left(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == 1:
        print "right"
        yield sub.move.right(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == 4:
        print "down left"
        if (check_depth()):
            yield sub.move.down(.05).go(blind=true)
        yield sub.move.left(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == 5:
        print "down"
        if (check_depth()):
            yield sub.move.down(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == 6:
        print "down right"
        if (check_depth()):
            yield sub.move.down(.05).go(blind=true)
        yield sub.move.right(.05).go(blind=true)
        if (TARGET_LOCK > 0):
            print "TARGET LOST."
            TARGET_LOCK = 0

    elif m.z == 0:
        print "TARGET LOCK AQUIRED."
        if LOCK_COUNTER < 10:
            LOCK_COUNTER += 1
        else:
            TARGET_LOCK = True
            print "TARGET AQUIRED, FIRING MISSILES."
            cam_info_sub = yield sub.nh.subscribe(
                '/camera/front/right/camera_info', CameraInfo)

            print('Getting cam info')
            cam_info = yield cam_info_sub.get_next_message()
            model = PinholeCameraModel()
            model.fromCameraInfo(cam_info)
            r, p = yield get_transform(sub, model, np.array([m.x, m.y]))
            so = SonarObjects(
                sub, [sub.move.pitch_down_deg(15),
                      sub.move.pitch_up_deg(15)])
            objs = yield so.start_until_found_in_cone(
                p,
                speed=0.2,
                object_count=1,
                ray=r,
                angle_tol=5,
                distance_tol=5)
            ob = objs.objects[0].pose.position
            where = np.array(ob.x, ob.y, ob.z)
            print('Go to: {}'.format(where))
            yield sub.move.look_at(where).go(bline=True)
            yield sub.move.set_position.go(blind=True, speed=0.2).go()
            print('Aligned')
        # continue
        # fire the missiles!
        # We good bois.
    else:
        print("Danger Will Robinson")
        # continue
        # welp.
        # return True


@util.cancellableInlineCallbacks
def depth_callback(sub):
    global CURRENT_DEPTH
    msg = yield sub._dvl_range_sub.get_next_message()
    CURRENT_DEPTH = defer.returnValue(msg.range)


@util.cancellableInlineCallbacks
def run(sub):

    # dive to mission start depth
    # mission_start_depth = float(input(
    #     "Entered the desired depth for the 'set course' mission: "))  # For pool testing
    #  mission_start_depth = 2.15        # meters
    print "descending to set course mission depth"
    # yield sub.move.to_height(1).go(blind=true)
    global TARGET_LOCK

    # rospy.init_node('torpedo_mission', anonymous=True)
    # Subscriber for Depth.

    # range_sub = sub.nh.subscribe("/dvl/range", RangeStamped)

    # Subscriber for my interesting logic system/perception.

    points_sub = yield sub.nh.subscribe("/torp_vision/points", Point)

    while TARGET_LOCK is False:
        print "Attempting to get Range"
        range_msg = range_sub.get_next_message()
        print "depth_callback"
        depth_callback(sub)
        print "Attempting to get Points"
        point_msg = yield points_sub.get_next_message()
        print "update_point_callback"
        update_point_callback(point_msg, sub)
    '''
    Possible Z values and their meanings:
    m.z = 0 --> Victory.

    ### X ### Range of Values: (-5, 5)
    m.z = -5 --> Only X thresh is off and sub is too low.
    m.z = 5 --> Only X thresh is off and sub is too high.

    ### BOTH ### Range of Values: (4, 6, -4, -6)
    m.z = 4 --> Both are off, too high, too far right.
    m.z = 6 --> Both are off, too high, too far left.
    m.z = -4 --> Both are off, too low, too far left.
    m.z = -6 --> Both are off, too low, too far right.

    ### Y ### Range of Values(-1, 1)
    m.z = -1 --> Only Y is off, too far right.
    m.z = 1 --> Only Y is off, too far left.
    '''


@util.cancellableInlineCallbacks
def get_transform(sub, model, point):
    print('Projecting to 3d ray')
    ray = np.array(model.projectPixelTo3dRay(point))
    print('Transform')
    transform = yield sub._tf_listener.get_transform('/map', 'front_right_cam')
    ray = transform._q_mat.dot(ray)
    ray = ray / np.linalg.norm(ray)
    print('ray: {}, origin: {}'.format(ray, transform._p))
    defer.returnValue((ray, transform._p))
