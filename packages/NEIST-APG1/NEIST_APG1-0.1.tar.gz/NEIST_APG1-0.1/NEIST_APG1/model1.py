# NEIST_APG1/model1.py
from tensorflow.keras.models import load_model

# Example: loading the first model


def DNN_MS_NEIST_APG1():
    # Load the model (replace with your actual model file path)
    model = load_model('DNN-MS-NEIST-APG1.h5')  # Replace with your model's path
    return model
