import numpy # This is needed for jack package!
import numpy as np
from scipy import signal
import scipy.fftpack as fft
import threading
import jack


import keras.backend as K
from keras.models import load_model, model_from_json
import json


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# CAUTION: JACK buffer size must be equal to or smaller than the FFT size

inputSampleRate = 32000 #48000 # Must match JACK configuration
processingSampleRateHz = 8000 # Must match training data
fftSizeMs = 32
downSamplingFactor = int(inputSampleRate/processingSampleRateHz)
nClusters = 2

nFft = int(processingSampleRateHz*fftSizeMs/1000)
nBins = int(nFft/2+1)
fftHopSizeMs = 8
fftHopSizeSamples = int(processingSampleRateHz*fftHopSizeMs/1000)
antiAliasingFilterOrder = 16
bufferSize = nFft
windowScalingFactor = 2 # Due to 75% overlap


currentMonitorOut = "Speakers"



def gui():
    global modesRadioButton

    app = QApplication(["Speech Separation"])
    win = QWidget()
    mainLayout = QVBoxLayout()

    modesRadioButton = [QRadioButton("Speakers"),
                        QRadioButton("Headphones")]
    modesRadioButton[0].setChecked(True)

    mainLayout.addWidget(QLabel("Client running. Cancel with X"))
    win.setLayout(mainLayout)
    win.resize(300, 50)
    win.move(2700, 500)
    win.show()
    sys.exit(app.exec_())


### Keras model related code #####

def dummyLoss(y_true, y_pred):
    return K.sum(K.flatten(y_true)) - K.sum(K.flatten(y_pred))

def backendLog10(x):
    numerator = K.log(x)
    denominator = K.log(K.constant(10, dtype=numerator.dtype))
    return numerator / denominator

def convert_to_inference_model(original_model):
    # "This is need because we need to change the trained recurrent
    # model from 'not stateful' to 'stateful'

    # TODO Delete DPCL layer for performance
    originalModelJson = original_model.to_json()
    inferenceModelDict = json.loads(originalModelJson)

    layers = inferenceModelDict['config']['layers']
    for layer in layers:
        if 'stateful' in layer['config']:
            layer['config']['stateful'] = True

        if 'batch_input_shape' in layer['config']:
            layer['config']['batch_input_shape'][0] = 1
            layer['config']['batch_input_shape'][1] = None

    inferenceModel = model_from_json(json.dumps(inferenceModelDict), custom_objects={'backendLog10': backendLog10, 'dpcl_loss_keras_format': dummyLoss, 'upit_loss_keras_format': dummyLoss, 'dpcl_loss_mse400': dummyLoss})
    inferenceModel.set_weights(original_model.get_weights())
    return inferenceModel

def getModel(modelPath):
    trainModel = load_model(modelPath, custom_objects={'backendLog10': backendLog10, 'dpcl_loss_keras_format': dummyLoss, 'upit_loss_keras_format': dummyLoss, 'dpcl_loss_mse400': dummyLoss})
    return convert_to_inference_model(trainModel)

## ATTENTION: Model is only loaded once per session. Reload can be forced.
modelPath = 'misc/model_2019_02_01__16_36_33_kEpoch_43' # Largest model
modelPath = 'misc/model_2019_02_07__16_01_07_kEpoch_60_2_300'  # Smaller model
forceModelReload = True



if 'globalModel' in globals() and forceModelReload == False:
    print('### Neural network already loaded ###')
else:
    print('### Load neural network ###')
    globalModel = getModel(modelPath)
    globalModel._make_predict_function()

client = jack.Client("SpeechSeparator")

if client.status.server_started:
    print("JACK server started")
if client.status.name_not_unique:
    print("unique name {0!r} assigned".format(client.name))

event = threading.Event()

### DSP functions ####

def getPeriodicHann(M):
    n = np.arange(0, M)
    return 0.5 - 0.5*np.cos(2.0*np.pi*n/(M))

sqrtHannWindow = np.sqrt(getPeriodicHann(nFft))

def getButterCoeffs(samplingFactor):
    b, a = signal.butter(antiAliasingFilterOrder, 1/samplingFactor, 'low')
    return b, a

def getWindowedIFft(spec):
    spec = np.concatenate((spec, spec[-2:0:-1].conj()), 0)
    return sqrtHannWindow * fft.ifft(spec).real

def getWindowedFftForRealInput(signal):
    return fft.fft(sqrtHannWindow*signal)[:nBins]


# Buffers
audioInputBuffer = np.zeros(bufferSize)
olaBufferSpk0 = np.zeros(bufferSize)
olaBufferSpk1 = np.zeros(bufferSize)

def getSeperatedSpeechWithModel(inputBuffer):
    global globalModel
    global audioInputBuffer
    global olaBufferSpk0
    global olaBufferSpk1

    inputBufSize = inputBuffer.shape[0]
    audioInputBuffer[:-fftHopSizeSamples] = audioInputBuffer[fftHopSizeSamples:]
    audioInputBuffer[-inputBufSize:] = inputBuffer

    # Get Spectrogram data
    complexSectrogram = getWindowedFftForRealInput(np.ascontiguousarray(audioInputBuffer, dtype=np.float32))

    networkInput = np.abs(complexSectrogram[np.newaxis, np.newaxis, :])

    # Do the actual work here
    networkOutput = globalModel.predict(networkInput)
    networkOutput = networkOutput[1] # Use UPIT output
    predictedSpeakerMasks = np.reshape(networkOutput, (nBins, nClusters))
    predictedSpecgram = predictedSpeakerMasks * complexSectrogram[:, np.newaxis]

    ifftSpk0 = getWindowedIFft(predictedSpecgram[:, 0])
    ifftSpk1 = getWindowedIFft(predictedSpecgram[:, 1])

    olaBufferSpk0 = olaBufferSpk0 + ifftSpk0
    speakerSignal0 = olaBufferSpk0[:fftHopSizeSamples]/windowScalingFactor
    olaBufferSpk0[:-fftHopSizeSamples] = olaBufferSpk0[fftHopSizeSamples:]
    olaBufferSpk0[-fftHopSizeSamples:] = 0.0

    olaBufferSpk1 = olaBufferSpk1 + ifftSpk1
    speakerSignal1 = olaBufferSpk1[:fftHopSizeSamples]/windowScalingFactor
    olaBufferSpk1[:-fftHopSizeSamples] = olaBufferSpk1[fftHopSizeSamples:]
    olaBufferSpk1[-fftHopSizeSamples:] = 0.0

    return speakerSignal0, speakerSignal1


# Filter coefficients and filter states
b, a = getButterCoeffs(downSamplingFactor)
filterStatesLpDownSample = np.zeros(antiAliasingFilterOrder)
filterStatesLpUpSampleChannel0 = np.zeros(antiAliasingFilterOrder)
filterStatesLpUpSampleChannel1 = np.zeros(antiAliasingFilterOrder)

@client.set_process_callback
def process(frames):
    global filterStatesLpDownSample
    global filterStatesLpUpSampleChannel0
    global filterStatesLpUpSampleChannel1

    assert frames == client.blocksize

    dataCurrent48kHz = client.inports[0].get_array()

    # Downsample from 48 kHz to 8 kHz samplerate
    # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
    dataCurrent48kHz, filterStatesLpDownSample = signal.lfilter(b, a, dataCurrent48kHz, zi=filterStatesLpDownSample)
    dataCurrent8kHz = dataCurrent48kHz[::downSamplingFactor]

    # Model call 
    speakerSignal0, speakerSignal1 = getSeperatedSpeechWithModel(dataCurrent8kHz)

    # Upsample from 8 kHz 48 kHz
    dataCurrent48kHzChannel0 = np.zeros_like(dataCurrent48kHz)
    dataCurrent48kHzChannel1 = np.zeros_like(dataCurrent48kHz)
    dataCurrent48kHzChannel0[::downSamplingFactor] = speakerSignal0
    dataCurrent48kHzChannel1[::downSamplingFactor] = speakerSignal1
    dataCurrent48kHzChannel0, filterStatesLpUpSampleChannel0 = signal.lfilter(downSamplingFactor*b, a, dataCurrent48kHzChannel0, zi=filterStatesLpUpSampleChannel0)
    dataCurrent48kHzChannel1, filterStatesLpUpSampleChannel1 = signal.lfilter(downSamplingFactor*b, a, dataCurrent48kHzChannel1, zi=filterStatesLpUpSampleChannel1)

    client.outports[0].get_array()[:] = dataCurrent48kHzChannel0
    client.outports[1].get_array()[:] = dataCurrent48kHzChannel1

@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown! status:", status, " reason:", reason )
    event.set()

client.inports.register("mixed_speech")
client.outports.register("speaker1")
client.outports.register("speaker2")


with client:
    print("Client running. (Speech Separation)")
    gui()
    print("Client stopped. (Monitor Controller)")
#
#
#with client:
#    print("Press Ctrl+C to stop")
#    try:
#        event.wait()
#    except KeyboardInterrupt:
#        print("\nInterrupted by user")