import cv2
from scipy import signal
import numpy as np

"""
    This is the file where all global variables
    are defined. If your hardware or you DNN 
    model has other requirements you need to change them here
"""

# VisualVoice requirements
DNN_INPUT_LENGTH = 2.55
DNN_SAMPLERATE = 16000
DNN_AUDIO_FRAME_SIZE = 128

# our hardware requirements
SAMPLERATE = 32000
AUDIO_FRAME_SIZE = 256

# resulting var
DOWN_SAMPLING_FACTOR = int(SAMPLERATE/DNN_SAMPLERATE)
ANTI_ALIASING_FILTER_ORDER = 16


def getButterCoeffs(samplingFactor):
    b, a = signal.butter(ANTI_ALIASING_FILTER_ORDER, 1/samplingFactor, 'low')
    return b, a

b, a = getButterCoeffs(DOWN_SAMPLING_FACTOR)
FILTER_STATES_LP_DOWN_SAMPLE = np.zeros(ANTI_ALIASING_FILTER_ORDER)
FILTER_STATES_LP_UP_SAMPLE_CHANNEL0 = np.zeros(ANTI_ALIASING_FILTER_ORDER)

# audioBuffer sizes
AUDIO_BUFFER_IN_SIZE = 40800

# this is the output buffer. The size is also the limitation
# for the process to be in realtime. For more please read the bachelor thesis at # TODO: chapter of this part
AUDIO_BUFFER_OUT_SIZE = 10000


# video capture device and openCV variables
FONT = cv2.FONT_HERSHEY_PLAIN
GAB_BETWEEN_LIP = 20
FPS_RATE= 25 # because it fits perfect to the audio frames?
FRAME_HEIGHT = 1
FRAME_WIDHT = 1
FRAME_CHANNELS = 3
