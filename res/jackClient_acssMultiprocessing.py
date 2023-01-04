import sys
import signal
import os
import jack
import threading
import cv2
# import capVideo
import numpy as np
import time
from multiprocessing import Process

# NUMBER_OF_SEGMENTS = 255
# BUFFER_SIZE = 256

DNN_INPUT_LENGTH = 2, 55
DNN_FREQUENT_RATE = 16000
DNN_AUDIO_FRAME_SIZE = 128

AUDIO_BUFFER_IN_SIZE = 40800
AUDIO_BUFFER_OUT_SIZE = 3000


client = jack.Client("AVSS")

event = threading.Event()

# global audioQueue
# global videoQueue
# global audioBufferFromThePast
# global videoBufferFromThePast
# audioBufferFromThePast = np.zeros(NUMBER_OF_SEGMENTS*BUFFER_SIZE)
# videoBufferFromThePast = []


global videoQueue
global audioBufferInQueue
global audioBufferOut
global dnnOutQueue


class AudioCapture(Process):
    def __init__(self, videoQueueParam, audioBufferInQueueParam, dnnOutQueueParam):
        super().__init__()
        print("AudioCapture: init")

        videoQueue = videoQueueParam

        audioBufferOut = [0] * AUDIO_BUFFER_OUT_SIZE
        audioBufferInQueue = audioBufferInQueueParam

        # self.videoBuffer = np.zeros((1, 1))

        dnnOutQueue = dnnOutQueueParam

        # global audioQueue
        # global videoQueue

        # audioQueue = audioFrameQueue
        # videoQueue = videoFrameQueue
        # queue2 = queue
        # check if the server has started
        if client.status.server_started:
            print("JACK server started")
        if client.status.name_not_unique:
            print("unique name {0!r} assigned".format(client.name))

        # cap = cv2.VideoCapture(0)
        # global testBool
        # testBool = True
        # index = 0

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
        assert frames == client.blocksize

        # TODO: downsample to 16kHz

        # fill the audio buffer
        audioFrame = [0] * DNN_AUDIO_FRAME_SIZE
        # remove first 128 element and add new element
        audioBufferIn = audioBufferInQueue.get()
        hintererBuffer = audioBufferIn[128:]
        audioBufferIn = hintererBuffer
        # add new audio frame to buffer
        audioBufferIn.extend(audioFrame)
        audioBufferInQueue.put(audioBufferIn)

        # prints the length of the audio buffer once when the DNN is running
        if(isDnnRunning == False):
            # print("Lenght of in buffer \t\t" + str(len(self.audioBufferInQueue))) # sollte immer gleich 40800 sein
            # print("Lenght of the out buffer after filling (start DNN) \t" + str(len(self.audioBufferOut)))
            # sollte immer gleich 40800 sein
            print("qSize of in buffer \t\t" +
                  str(audioBufferInQueue.qsize()))
            # sollte immer gleich 40800 sein
            print("Lenght of in buffer \t\t" + str(len(audioBufferIn)))
            print("Lenght of the out buffer \t\t" +
                  str(len(audioBufferOut)))
            isDnnRunning = True

        # print("DnnModelCall started")
        if(dnnOutQueue.qsize() > 0):
            isDnnRunning = False
            # hier wird der output buffer gefüllt
            dnnModelResult = dnnOutQueue.get()
            # print("audioBufferOut: ", dnnModelResult)
            audioBufferOut.extend(dnnModelResult)
            print("Lenght of the out buffer after filling \t" +
                  str(len(audioBufferOut)))

        # TODO: read output buffer and play it
        audioBufferOut.pop(0)
        print("Lenght of the out buffer \t\t" + str(len(audioBufferOut)))

        # ! can be removed if it works
        # assert len(client.inports) == len(client.outports)
        # assert frames == client.blocksize
        # for i, o in zip(client.inports, client.outports):
        #     o.get_array()[:] = i.get_buffer()

        # dataCurrent48kHz = client.inports[0].get_array()
        # print(dataCurrent48kHz)

        # ! der output ist gleich mein input
        # client.outports[0].get_array()[:] = client.inports[0].get_array()

        # audioQueue.put(client.inports[0].get_array())

        # buffer wird geflatted gefüllt
        # audioBufferFromThePast[NUMBER_OF_SEGMENTS*BUFFER_SIZE -
        #                        BUFFER_SIZE::] = client.inports[0].get_array().flatten()
        # temp = audioBufferFromThePast[BUFFER_SIZE::]
        # audioBufferFromThePast = np.append(temp, np.zeros(BUFFER_SIZE))
        # print(audioBufferFromThePast)

        # if(len(audioBufferFromThePast) < 1):
        # Add to array to keep the past
        # audioBufferFromThePast.append(client.inports[0].get_array())
        # videoBufferFromThePast.append(videoQueue.get())

        # audioBufferFromThePast

        # print(audioBufferFromThePast)
        # print(videoBufferFromThePast)

        # print(videoQueue.qsize())
        # print(len(audioBufferFromThePast))
        # print(len(videoBufferFromThePast))

        # ML call here
        # Ich rufe aus und gekomme was zurück
        # Wenn das zurückgegebene nicht leer ist
        # setze den output auf das zurückgegebene
        # Oder aufruf mit processen machen das die
        # aufrufe parallel laufen können? aber dann
        # kann es überlastet werden, weil zu viel
        # threads/process laufen

        # client.outports[0].get_array()[:] = dataCurrent48kHz

    @client.set_shutdown_callback
    def shutdown(status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)

        # Stop cv2
        # cap.release()
        cv2.destroyAllWindows()

        event.set()
