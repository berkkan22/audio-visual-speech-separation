import sys
from scipy import signal
import os
import jack
import threading
import cv2
# import capVideo
import numpy as np
import time
from multiprocessing import Process
from global_variables import *
from helperFunctions import *
import librosa


client = jack.Client("AVSS")

event = threading.Event()

global videoQueue
global audioBufferInQueue
global audioBufferOut
global dnnOutQueue
global triggerQueue


global count
count = -1

class AudioCapture(Process):
    def __init__(self, audioBufferInQueueParam, videoQueueParam, dnnOutQueueParam, triggerQueueParam):
        super().__init__()
        print("AudioCapture: init")


        global videoQueue
        global audioBufferInQueue
        global audioBufferOut
        global dnnOutQueue
        global videoBufferFromThePast
        global audioBufferTestTempBerkkan
        global dnnModelCallTest
        global triggerQueue

        triggerQueue = triggerQueueParam


        audioBufferTestTempBerkkan = [0] * (40800 // 8)
        audioBufferOut = [0] * AUDIO_BUFFER_OUT_SIZE
        audioBufferInQueue = audioBufferInQueueParam

        dnnOutQueue = dnnOutQueueParam

        videoQueue = videoQueueParam
        videoFrameSize = np.zeros((FRAME_HEIGHT, FRAME_WIDHT, FRAME_CHANNELS), np.uint8)
        videoBufferFromThePast = [[0]] * 64  # ? wie groß ist der buffer?


    def run(self):
        global soundPos
        global soundFile
        global spkGainAbs
        global playActive

        # check if the server has started
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))

        samplerate = 48000 #TODO use JACK sample rate

        # bash -c 'cd ~/anaconda3/bin;source activate base; python /export/scratch/studio/StudioScripts/Resources/jack-clients/jackClient_multiAudioPlayer.py /export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Female01.wav -80 /export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Male01.wav -80 /export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/Noise_Factory.wav -80 2400 500'
        audioPath = "/export/scratch/studio/StudioScripts/Demos/SpeechEnhancementAndSeparation/AudioInput/48k/Speech_Female01.wav" 

        #Changing to 32000 for the current settings
        soundFile = []
        TMP_samplerate = 32000
        sample_48k = librosa.load(audioPath, sr=samplerate)[0]
        sample = librosa.resample(sample_48k, orig_sr=samplerate, target_sr=TMP_samplerate)
        print(f'{sample.shape=}')
        soundFile.append(sample)

        soundPos = np.zeros(1, dtype="int32")
        playActive = np.ones(1, dtype=bool)
        spkGainAbs = np.ones(1)


        # create port for the input speech ("mixed_speech") and the both speaker
        client.inports.register("mixed_speech")
        client.outports.register("speaker1")
        client.outports.register("speaker2")
        client.outports.register("virtualSource1")

        with client:
            # When entering this with-statement, client.activate() is called.
            # This tells the JACK server that we are ready to roll.
            # Our process() callback will start running now.

            # Connect the ports.  You can't do this before the client is activated,
            # because we can't make connections to clients that aren't running.
            # Note the confusing (but necessary) orientation of the driver backend
            # ports: playback ports are "input" to the backend, and capture ports
            # are "output" from it.
            # print(self.q.get())
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

        # When the above with-statement is left (either because the end of the
        # code block is reached, or because an exception was raised inside),
        # client.deactivate() and client.close() are called automatically.



    # audio process loop
    @client.set_process_callback
    def process(frames):
        # 'global' is requiert because we initiliz them in the init function
        # and because we cant give 'self' in the callback function I work 
        # with 'global'
        global videoBufferFromThePast
        global audioBufferOut
        global audioBufferTestTempBerkkan
        global dnnModelCallTest
        global triggerQueue

        global FILTER_STATES_LP_DOWN_SAMPLE
        global FILTER_STATES_LP_UP_SAMPLE_CHANNEL0

        global count
        global soundPos
        global soundFile
        global spkGainAbs
        global playActive

        assert frames == client.blocksize

        # virtualSoruces
        if soundPos[0]+client.blocksize > soundFile[0].size:
            soundPos[0] = 0
        virtaulSource = soundFile[0][soundPos[0]:soundPos[0]+client.blocksize] * 0.5 #* spkGainAbs[0] * playActive[0]
        # print(f'{len(audioFrameCurrent32kHz)}')
        soundPos[0] += client.blocksize #* playActive[0]

        client.outports[2].get_array()[:] = virtaulSource



        # get the input of the mic
        audioFrameCurrent32kHz = client.inports[0].get_array()[:]

        # # Downsample from 32 kHz to 16 kHz samplerate
        # # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
        audioFrameCurrent32kHz, FILTER_STATES_LP_DOWN_SAMPLE = signal.lfilter(b, a, audioFrameCurrent32kHz, zi=FILTER_STATES_LP_DOWN_SAMPLE)
        audioFrameCurrent16kHz = audioFrameCurrent32kHz[::DOWN_SAMPLING_FACTOR]

        
        # get the new audioFrame at 16kHz
        newAudioFrame = audioFrameCurrent16kHz 

        if(count == 19):
            audioBufferInQueue.put(audioBufferTestTempBerkkan)
            # triggerQueue.put(True)

            # count = 0
        else:
            audioBufferTestTempBerkkan = removeFirstFrameAndAddNewFrame(audioBufferTestTempBerkkan, newAudioFrame)
            count += 1


        # fill the video buffer
        if(not videoQueue.empty()):
            videoBufferFromThePast = videoBufferFromThePast[1:]
            videoBufferFromThePast.append(videoQueue.get())
            # print("video buffer ")

        if(not dnnOutQueue.empty()):
            # print("audioBufferOut before extend length: \t\t\t" + str(len(audioBufferOut)))

            dnnModelResult = dnnOutQueue.get()
            audioBufferOut.extend(dnnModelResult)
            # print("audioBufferOut after extend length: \t" + str(len(audioBufferOut)))

        # get the first 128 samples
        outputForUpsampling = audioBufferOut[:128]

        # remove the first 128 samples
        audioBufferOut = audioBufferOut[128:]

        print(f'audioBufferOut: {len(audioBufferOut)}, count: {count}')


         # Upsample from 8 kHz 48 kHz
        dataCurrentOut32kHz = np.zeros_like(audioFrameCurrent32kHz)
        # print("data: " + str(dataCurrentOut32kHz.shape))
        dataCurrentOut32kHz[::DOWN_SAMPLING_FACTOR] = outputForUpsampling
        dataCurrentOut32kHz, FILTER_STATES_LP_UP_SAMPLE_CHANNEL0 = signal.lfilter(DOWN_SAMPLING_FACTOR*b, a, dataCurrentOut32kHz, zi=FILTER_STATES_LP_UP_SAMPLE_CHANNEL0)


        # output
        client.outports[0].get_array()[:] = dataCurrentOut32kHz # client.inports[0].get_array() # dataCurrentOut32kHz


    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)

        # Stop cv2
        # cap.release()
        cv2.destroyAllWindows()

        event.set()

