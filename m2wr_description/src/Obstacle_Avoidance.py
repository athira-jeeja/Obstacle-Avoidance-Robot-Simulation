#! /usr/bin/env python

import rospy

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
pub = None

def callback_laser(msg):
  # 720 samples into 3 regions
  regions = {
    'right':  min(min(msg.ranges[0:239]), 10),
    'front':  min(min(msg.ranges[240:479]), 10),
    'left':   min(min(msg.ranges[479:719]), 10),
  }
  
  take_action(regions)
  
def take_action(regions):
  threshold_dist = 1
  linear_speed = 0.6
  angular_speed = 1

  msg = Twist()
  linear_x = 0
  angular_z = 0
  
  state_description = ''
  
  if regions['front'] > threshold_dist and regions['left'] > threshold_dist and regions['right'] > threshold_dist:
    state_description = 'case 1 - no obstacle'
    linear_x = linear_speed
    angular_z = 0
  elif regions['front'] < threshold_dist and regions['left'] < threshold_dist and regions['right'] < threshold_dist: # 2 conditions can be set 
    state_description = 'case 7 - front and left and right'
    # non -stop condition
    linear_x = -linear_speed
    angular_z = angular_speed # Increase this angular speed for avoiding obstacle faster
    # # stop condition
    # linear_x = 0
    # angular_z = 0
  elif regions['front'] < threshold_dist and regions['left'] > threshold_dist and regions['right'] > threshold_dist:
    state_description = 'case 2 - front'
    linear_x = 0
    angular_z = angular_speed
  elif regions['front'] > threshold_dist and regions['left'] > threshold_dist and regions['right'] < threshold_dist:
    state_description = 'case 3 - right'
    linear_x = 0
    angular_z = -angular_speed
  elif regions['front'] > threshold_dist and regions['left'] < threshold_dist and regions['right'] > threshold_dist:
    state_description = 'case 4 - left'
    linear_x = 0
    angular_z = angular_speed
  elif regions['front'] < threshold_dist and regions['left'] > threshold_dist and regions['right'] < threshold_dist:
    state_description = 'case 5 - front and right'
    linear_x = 0
    angular_z = -angular_speed
  elif regions['front'] < threshold_dist and regions['left'] < threshold_dist and regions['right'] > threshold_dist:
    state_description = 'case 6 - front and left'
    linear_x = 0
    angular_z = angular_speed
  elif regions['front'] > threshold_dist and regions['left'] < threshold_dist and regions['right'] < threshold_dist:
    state_description = 'case 8 - left and right'
    linear_x = linear_speed
    angular_z = 0
  else:
    state_description = 'unknown case'
    rospy.loginfo(regions)

  rospy.loginfo(state_description)
  msg.linear.x = linear_x
  msg.angular.z = angular_z
  pub.publish(msg)

def main():
  global pub
  
  rospy.init_node('reading_laser')
  
  pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
  
  sub = rospy.Subscriber('/m2wr/laser/scan', LaserScan, callback_laser)
  
  rospy.spin()

if __name__ == '__main__':
  main()