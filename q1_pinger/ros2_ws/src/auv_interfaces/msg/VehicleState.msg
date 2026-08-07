# Vehicle proprioception, published on /auv/state at 60 Hz.
# All of this is known to the vehicle itself. None of it locates the pinger.
std_msgs/Header header
float32 x                 # metres, world frame
float32 y                 # metres, world frame
float32 vx                # m/s, world frame
float32 vy                # m/s, world frame
float32 heading           # radians
float32 sim_time          # seconds since episode start
uint32  step
