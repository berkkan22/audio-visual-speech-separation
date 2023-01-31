import jack
import threading
from multiprocessing import Process
import numpy as np
import librosa
from helperFunctions import *


client = jack.Client("AVSS")

event = threading.Event()

class AudioCaptureNew(Process):
    def __init__(self):
        super().__init__()
        print("AudioCapture: init")
        
        
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
        
        virtualSource = virtaulSources(soundFile, soundPos, client,  playActive, spkGainAbs)
        client.outports[1].get_array()[:] = virtualSource
        
        client.outports[0].get_array()[:] = client.inports[0].get_array()[:]
        
    
    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)


        event.set()