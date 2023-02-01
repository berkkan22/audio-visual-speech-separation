import jack
import threading
from multiprocessing import Process, Queue
import numpy as np
import librosa
from helperFunctions import *
import global_variables as gv 
from scipy import signal



client = jack.Client("AVSS")

event = threading.Event()

testBufferIn = gv.audioBufferInQueue
testBufferOut = gv.audioBufferOut

class AudioCaptureNew(Process):
    
    def __init__(self, audioBufferInQueue):
        super().__init__()
        print("AudioCapture: init")
        
        global testQueue
        testQueue = audioBufferInQueue
        
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


        samplerate = 48000
        audioPath = r'resources\misc\gerkmannFrintrop.wav' # "/export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Female01.wav" 

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
        
        global testBufferIn
        global testBufferOut
        
        global testQueue
        
        # play virtualSources on the right speaker (headset)
        virtualSource = virtaulSources(soundFile, soundPos, client,  playActive, spkGainAbs)
        client.outports[1].get_array()[:] = virtualSource
        
        # get the input of the mic
        audioFrameCurrent32kHz = client.inports[0].get_array()[:]

        # Downsample from 32 kHz to 16 kHz samplerate
        # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
        audioFrameCurrent32kHz, gv.FILTER_STATES_LP_DOWN_SAMPLE = signal.lfilter(gv.b, gv.a, audioFrameCurrent32kHz, zi=gv.FILTER_STATES_LP_DOWN_SAMPLE)
        audioFrameCurrent16kHz = audioFrameCurrent32kHz[::gv.DOWN_SAMPLING_FACTOR]

        
        # get the new audioFrame at 16kHz
        newAudioFrame = audioFrameCurrent16kHz
        # print("newAudioFrame length: \t" + str(len(newAudioFrame)))
        
        testQueue.put(newAudioFrame)
        
        if(not gv.dnnOutQueue.empty()):
            print("not empty")
            dnnModelResult = gv.dnnOutQueue.get()
            testBufferOut.extend(dnnModelResult)
            # print("audioBufferOut after extend length: \t" + str(len(gv.audioBufferOut)))

        print("audioBufferOut length: \t" + str(len(testBufferOut)))
        # get the first 128 samples
        outputForUpsampling = testBufferOut[:128]
        # print("outputForUpsampling length: \t" + str(len(outputForUpsampling)))

        # remove the first 128 samples
        testBufferOut = testBufferOut[128:]

        # Upsample from 8 kHz 48 kHz
        dataCurrentOut32kHz = np.zeros_like(audioFrameCurrent32kHz)
        # print("data: " + str(dataCurrentOut32kHz.shape))
        dataCurrentOut32kHz[::gv.DOWN_SAMPLING_FACTOR] = outputForUpsampling # outputForUpsampling # newAudioFrame
        dataCurrentOut32kHz, gv.FILTER_STATES_LP_UP_SAMPLE_CHANNEL0 = signal.lfilter(gv.DOWN_SAMPLING_FACTOR*gv.b, gv.a, dataCurrentOut32kHz, zi=gv.FILTER_STATES_LP_UP_SAMPLE_CHANNEL0)


        # output
        client.outports[0].get_array()[:] = dataCurrentOut32kHz # audioFrameCurrent32kHz # client.inports[0].get_array() # dataCurrentOut32kHz # client.inports[0].get_array() # dataCurrentOut32kHz
        
    
    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)


        event.set()