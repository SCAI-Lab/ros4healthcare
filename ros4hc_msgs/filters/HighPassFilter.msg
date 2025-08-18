std_msgs/Header header

float32 cutoff_frequency     # Hz
uint8 order                  # Filter order (e.g., 2, 4)
float32 sampling_rate        # Hz
bool zero_phase              # True if using forward-backward (e.g., filtfilt)
