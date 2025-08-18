DeviceInfo   device_info

uint16      wavelengths         # Wavelength of emmitted light in [nm]
float32[]   ac_component        # Pulsatile AC component (cardic synchronous variations in blood volume)
float32[]   dc_component        # Superimposed DC component (shaped by sympathetic nervous system activity, respiration, thermoregulation)
string[] 	ppg_location 	    # Location of sensor that measures the ppg
string  	ppg_measuring_mode  # Measuring method for ppg ("transmissive absorption", "reflection", ect.)
float32[] 	signal_gain 	    # Gain refers to the amount by which the signals amplitude is increased or decreased. (Gain = 1 -> signal unchanged, gain <1 signal is attenuated, gain >1 signal is amplified)
