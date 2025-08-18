std_msgs/Header header

float32 process_noise        # Q
float32 measurement_noise    # R
float32 initial_estimate     # Optional
float32 gain                 # Optional Kalman gain if precomputed
