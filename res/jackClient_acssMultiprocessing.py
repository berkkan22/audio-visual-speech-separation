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

client = jack.Client("AVSS")

event = threading.Event()

# global videoBufferFromThePast
global videoQueue
global audioBufferInQueue
global audioBufferOut
global dnnOutQueue

global count
count = -1

# global isDnnRunningvideoBufferFromThePast
isDnnRunning = False

class AudioCapture(Process):
    def __init__(self, audioBufferInQueueParam, videoQueueParam, dnnOutQueueParam):
        super().__init__()
        print("AudioCapture: init")


        global videoQueue
        global audioBufferInQueue
        global audioBufferOut
        global dnnOutQueue
        global videoBufferFromThePast
        global audioBufferTestTempBerkkan
        global dnnModelCallTest



        audioBufferTestTempBerkkan = [0] * 40800


        videoQueue = videoQueueParam

        audioBufferOut = [0] * AUDIO_BUFFER_OUT_SIZE
        audioBufferInQueue = audioBufferInQueueParam

        # self.videoBuffer = np.zeros((1, 1))

        dnnOutQueue = dnnOutQueueParam

        videoFrameSize = np.zeros((FRAME_HEIGHT, FRAME_WIDHT, FRAME_CHANNELS), np.uint8)
        videoBufferFromThePast = [[0]] * 64  # ? wie groß ist der buffer?
        # print(len(videoBufferFromThePast))

        # global audioQueue
        # global videoQueue

        # audioQueue = audioFrameQueue
        # videoQueue = videoFrameQueue
        # queue2 = queue

    def run(self):
        # check if the server has started
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))

        # create port for the input speech ("mixed_speech") and the both speaker
        client.inports.register("mixed_speech")
        client.outports.register("speaker1")
        client.outports.register("speaker2")

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
                # print("TEST")
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
        global isDnnRunning
        global videoBufferFromThePast
        global audioBufferOut
        global audioBufferTestTempBerkkan
        global dnnModelCallTest

        global FILTER_STATES_LP_DOWN_SAMPLE
        global FILTER_STATES_LP_UP_SAMPLE_CHANNEL0

        global count

        assert frames == client.blocksize

        # get the input of the mic
        audioFrameCurrent32kHz = client.inports[0].get_array()

        # Downsample from 32 kHz to 16 kHz samplerate
        # ATTENTION: Signal must be prefiltered with low pass at Nyquist (< 4 kHz)
        audioFrameCurrent32kHz, FILTER_STATES_LP_DOWN_SAMPLE = signal.lfilter(b, a, audioFrameCurrent32kHz, zi=FILTER_STATES_LP_DOWN_SAMPLE)
        audioFrameCurrent16kHz = audioFrameCurrent32kHz[::DOWN_SAMPLING_FACTOR]

        
        # get the new audioFrame at 16kHz
        newAudioFrame = audioFrameCurrent16kHz 

        if(count > 20):
            # print("triggert " + str(count))
            # audioBufferInput = audioBufferInQueue.get(block=False) # 40800 aus nullen

            # remove the first frame and add the new frame
            # audioBufferInputModified = removeFirstFrameAndAddNewFrame(audioBufferInput, newAudioFrame)

            # put it again in the queue so it can be used in the DNN process

       	    #  audioBufferTestTempBerkkan = removeFirstFrameAndAddNewFrame(audioBufferTestTempBerkkan, newAudioFrame)

            audioBufferInQueue.put(audioBufferTestTempBerkkan, block=False)

            count = 0

        #     # audioBufferInQueue.get()

        else:
        #     # print("count: " + str(count))

            audioBufferTestTempBerkkan = removeFirstFrameAndAddNewFrame(audioBufferTestTempBerkkan, newAudioFrame)
            count += 1


        # fill the video buffer
        if(not videoQueue.empty()):
            videoBufferFromThePast = videoBufferFromThePast[1:]
            videoBufferFromThePast.append(videoQueue.get(block=False))
            # print("video buffer ")

        if(not dnnOutQueue.empty()):
            # print("audioBufferOut before extend length: \t\t\t" + str(len(audioBufferOut)))

            dnnModelResult = dnnOutQueue.get(block=False)
            audioBufferOut.extend(dnnModelResult)
            # print("audioBufferOut after extend length: \t" + str(len(audioBufferOut)))

        # get the first 128 samples
        outputForUpsampling = audioBufferOut[:128]
        # print("OUTUP " + str(len(outputForUpsampling)))

        # remove the first 128 samples
        audioBufferOut = audioBufferOut[128:]

        # print("AUDIOBUFFER " + str(len(audioBufferOut)))

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

