# World-frame velocity in m/s plus a desired absolute heading in radians.
# (vx, vy) magnitude is clamped to MAX_SPEED by the simulator.
# Heading aims the hydrophone; it does not steer the vehicle.
std_msgs/Header header
float32 vx
float32 vy
float32 heading
