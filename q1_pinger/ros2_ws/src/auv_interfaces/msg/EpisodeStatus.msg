# Episode progress, published on /auv/episode at 5 Hz.
# `hold_time` resets to zero whenever the vehicle leaves the capture radius:
# orbiting the pinger is not holding station over it.
std_msgs/Header header
bool   active
bool   success
float32 hold_time         # seconds continuously inside the capture radius
float32 hold_required     # seconds needed for success
float32 elapsed
