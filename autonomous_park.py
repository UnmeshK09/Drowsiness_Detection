#!/usr/bin/env python

from __future__ import print_function
import sys
import math
import numpy as np

# ROS Imports
import rospy
from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped

# PID CONTROL PARAMS
kp = 0.8
ki = 0.0001
kd = 0.5
prev_error = 0.0
integral = 0.0

# WALL FOLLOW PARAMS
DESIRED_DISTANCE_LEFT = 0.6
VELOCITY = 4.5
CAR_LENGTH = 0.50
TIME_INCREMENT = 0.1

class Autonomous_Park:
    def __init__(self):
        rospy.init_node('autonomous_park', anonymous=True)

        lidarscan_topic = '/scan'
        drive_topic = rospy.get_param("~autonomous_park_topic")

        self.lidar_sub = rospy.Subscriber(lidarscan_topic, LaserScan, self.lidar_callback)
        self.drive_pub = rospy.Publisher(drive_topic, AckermannDriveStamped, queue_size=1)
        self.speed = 0.0

    def getRange(self, data, angle):
        ranges = data.ranges
        range_max = data.range_max
        range_min = data.range_min
        valid_ranges = np.clip(ranges, range_min, range_max)
        index = np.arange(valid_ranges.size)
        angle_array = data.angle_min + index * data.angle_increment
        idx = (np.abs(angle_array - angle)).argmin()
        desired_range = valid_ranges[idx]
        desired_angle = angle_array[idx]
        return {"range": desired_range, "angle": desired_angle}

    def pid_control(self, error, velocity):
        global integral, prev_error, kp, ki, kd
        P = kp * error
        I = integral + ki * error * TIME_INCREMENT
        D = kd * (error - prev_error) / TIME_INCREMENT
        angle = P + I + D
        drive_msg = AckermannDriveStamped()
        drive_msg.header.stamp = rospy.Time.now()
        drive_msg.header.frame_id = "laser"
        drive_msg.drive.steering_angle = angle
        drive_msg.drive.speed = velocity - abs(1.5*angle)
        self.drive_pub.publish(drive_msg)
        self.speed = velocity
        prev_error = error
        integral = I

    def followLeft(self, data, leftDist):
        a = self.getRange(data, math.pi/6)  # 30 degrees
        b = self.getRange(data, math.pi/2)  # 90 degrees
        theta = abs(a["angle"]-b["angle"])
        alpha = math.atan((b["range"]-a["range"]*math.cos(theta))/(a["range"]*math.sin(theta)))
        look_ahead_dist = self.speed * TIME_INCREMENT
        pred_dist = b["range"]*math.cos(alpha) - look_ahead_dist*math.sin(alpha)
        error = leftDist - pred_dist
        return -1 * error

    def lidar_callback(self, data):
        error = self.followLeft(data, DESIRED_DISTANCE_LEFT)
        self.pid_control(error, VELOCITY)

if __name__ == '__main__':
    Autonomous_Park()
    rospy.spin()
