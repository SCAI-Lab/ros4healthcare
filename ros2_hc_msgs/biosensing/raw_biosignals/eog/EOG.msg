std_msgs/Header header

float32[]   eog                     # Amplitude of output value in [unit]
float32[]   signal_quality          # Signal quality from 0-1 [%]
float64[]   time_signal_recorded    # The moment in time the signal was recorded, whereas std_header/Header/stamp is the publishing time
