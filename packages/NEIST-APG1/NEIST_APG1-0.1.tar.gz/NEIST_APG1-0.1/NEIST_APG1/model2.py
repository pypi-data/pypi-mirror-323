# NEIST_APG1/model2.py
from tensorflow.keras.models import load_model

# Example: loading the second model
def DNN_NEIST_APG1():
    # Load the model (replace with your actual model file path)
    model = load_model('E:/py1/NEIST_APG1/DNN-NEIST-APG1.h5')  # Replace with your model's path
    return model
