string[]    device_serial_number        # Serialnumbers of the devices of signal origin
float32[]   prediction_probablility     # Probability of prediction's according to classifier
string[]    glossary                    # Possibilities linked to the prediction_probability with same index   
uint16      class_amount			    # Amount of Classes (2=supine/nonsupine, 3=supine/nonsupine/nonoccupied, 4, 5)
string[]    model_type                  # Machine learning model type
string[]    model_version               # The version the model is trained with/ From what data was the model created 
