# from capVideoMultiprocessing import capVideoFunc
from multiprocessing import Process, Queue, Array
import cv2
# from jackClient_acssMultiprocessing import AudioCapture
from syncLoop import SyncLoop
from videoCapture import CaptureVideo
import jack
import numpy
from dnnModellCall import DnnModelCall
from audioCapture import AudioCaptureNew
import jack
import threading
from multiprocessing import Process, Queue
import numpy as np
import librosa
from helperFunctions import *
import global_variables as gv
from scipy import signal


if __name__ == '__main__':
    """
    Wir haben nur eine VideoQueue, da wir nur die frames rübergeben wollen
    zu audioCapture
    im audioCapture wird dann eine audioBuffer erstellt und ein videoBuffer
    das was wir besprochen haben
    und dann werden die buffers an den DnnModelCall übergeben
    """

    audioBufferInQueue = Queue()
    audioBufferDNNOut = Queue()
    videoQueue = Queue()


    # dnnOutQueue for continous output
    # dnnModelCall = DnnModelCall(
    #     dnnOutQueue, videoFrameQueue, audioBufferInQueue, trigger)
    dnnModelCall = DnnModelCall(audioBufferInQueue, audioBufferDNNOut)
    dnnModelCall.start()


    # # add VideoCaputure as process
    # captureVideo = CaptureVideo(videoFrameQueue, 0)
    # captureVideo.start()



    # add AudioCaputure as process
    audioCapture = AudioCaptureNew(audioBufferInQueue, audioBufferDNNOut) # AudioCapture(audioBufferInQueue, videoFrameQueue, dnnOutQueue)
    audioCapture.start()
    
    #! Wait for them to finish which will never happen because it is a True loop
    dnnModelCall.join()
    # captureVideo.join()
    audioCapture.join()