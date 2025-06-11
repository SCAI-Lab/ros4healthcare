std_msgs/Header header

float32 low_cutoff_frequency     # Lower bound [Hz]
float32 high_cutoff_frequency    # Upper bound [Hz]
uint8 order                      # Filter order
float32 sampling_rate            # Hz
bool zero_phase                  # Optional: phase-preserving filter
