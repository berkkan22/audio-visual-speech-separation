import jack # ??? why does this need to be on top????

from multiprocessing import Process, Queue
from scipy import signal
import numpy as np
import threading
import librosa

from helperFunctions import *
from global_variables import *



client = jack.Client("AVSS")

event = threading.Event()

class AudioCaptureNew(Process):
    
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam):
        super().__init__()
        print("AudioCapture: init")
        
        global audioBufferInQueue
        global audioBufferDNNOut
        global audioOutputBuffer
        global count

        audioBufferInQueue = audioBufferInQueueParam
        audioBufferDNNOut = audioBufferDNNOutParam
        audioOutputBuffer = [0] * AUDIO_BUFFER_OUT_SIZE
        count = 0

    def run(self):
        global soundFile
        global soundPos
        global spkGainAbs
        global playActive
        
        print("AudioCapture: run")
        
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))


        samplerate = 48000 # audio file samplerate
        audioPath = 'resources/misc/gerkmannFrintrop.wav' # r'resources\misc\gerkmannFrintrop.wav' # "/export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Female01.wav" 

        # Changing to 32000 for the current settings
        soundFile = []
        TMP_samplerate = 32000
        sample_48k = librosa.load(audioPath, sr=samplerate)[0]
        sample = librosa.resample(sample_48k, orig_sr=samplerate, target_sr=TMP_samplerate)
        # print(f'{sample.shape=}')
        soundFile.append(sample)

        soundPos = np.zeros(1, dtype="int32")
        playActive = np.ones(1, dtype=bool)
        spkGainAbs = np.ones(1)


        # create port for the input speech ("mixed_speech") and the both speaker
        client.inports.register("mixed_speech")
        client.outports.register("speaker1")
        client.outports.register("virtualSource")
        
        with client:
            print("AudioCapture: run")
            
            capture = client.get_ports(is_physical=True, is_output=True)
            if not capture:
                raise RuntimeError("No physical capture ports")

            for src, dest in zip(capture, client.inports):
                client.connect(src, dest)

            playback = client.get_ports(is_physical=True, is_input=True)
            if not playback:
                raise RuntimeError("No physical playback ports")

            for src, dest in zip(client.outports, playback):
                client.connect(src, dest)

            print("Press Ctrl+C to stop")
            try:
                event.wait()
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                
                
    @client.set_process_callback
    def process(frame):
        assert frame == client.blocksize

            
        global FILTER_STATES_LP_DOWN_SAMPLE
        global FILTER_STATES_LP_UP_SAMPLE_CHANNEL0

        
        global audioBufferInQueue
        global audioBufferDNNOut
        global audioOutputBuffer
        global count

        
        # play virtualSources on the right speaker (headset)
        virtualSource = virtaulSources(soundFile, soundPos, client,  playActive, spkGainAbs)
        client.outports[1].get_array()[:] = virtualSource

        
        # get the input of the mic
        # audioFrameCurrent32kHz = client.inports[0].get_array()[:]
        # get the input of the virtualSources
        audioFrameCurrent32kHz = client.outports[1].get_array()[:]

        # Downsample from 32kHz to 16kHz samplerate
        # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
        audioFrameCurrent32kHz, FILTER_STATES_LP_DOWN_SAMPLE = signal.lfilter(b, a, audioFrameCurrent32kHz, zi=FILTER_STATES_LP_DOWN_SAMPLE)
        audioFrameCurrent16kHz = audioFrameCurrent32kHz[::DOWN_SAMPLING_FACTOR]

        
        # get the new audioFrame at 16kHz
        audioBufferInQueue.put(audioFrameCurrent16kHz)

        
        if(not audioBufferDNNOut.empty()):
            dnnModelResult = audioBufferDNNOut.get()
            audioOutputBuffer.extend(dnnModelResult)

        # get the first 128 samples
        outputForUpsampling = audioOutputBuffer[:128]

        # remove the first 128 samples
        audioOutputBuffer = audioOutputBuffer[128:]

        # Upsample from 16kHz 32kHz
        dataCurrentOut32kHz = np.zeros_like(audioFrameCurrent32kHz)
        dataCurrentOut32kHz[::DOWN_SAMPLING_FACTOR] = outputForUpsampling
        dataCurrentOut32kHz, FILTER_STATES_LP_UP_SAMPLE_CHANNEL0 = signal.lfilter(DOWN_SAMPLING_FACTOR*b, a, dataCurrentOut32kHz, zi=FILTER_STATES_LP_UP_SAMPLE_CHANNEL0)


        # output
        client.outports[0].get_array()[:] = dataCurrentOut32kHz 

    
    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)


        event.set()