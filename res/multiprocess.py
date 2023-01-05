# from capVideoMultiprocessing import capVideoFunc
from multiprocessing import Process, Queue, Array
import cv2
from jackClient_acssMultiprocessing import AudioCapture
from syncLoop import SyncLoop
from videoCapture import CaptureVideo
import jack
import numpy
from dnnModellCall import DnnModelCall


if __name__ == '__main__':
    """
    Wir haben nur eine VideoQueue, da wir nur die frames rübergeben wollen
    zu audioCapture
    im audioCapture wird dann eine audioBuffer erstellt und ein videoBuffer
    das was wir besprochen haben
    und dann werden die buffers an den DnnModelCall übergeben
    """

    # initilize queue to share data between processes on frame per 0.04 s
    videoFrameQueue = Queue()

    # init audioFrameQueue
    audioBufferInQueue = Queue()
    # fill the audioBufferInQueue with 0
    audioBufferInQueue.put([0] * 40800)  # numpy geht nicht weil zu groß

    # dnnOutQueue for continous output
    dnnOutQueue = Queue()
    dnnModelCall = DnnModelCall(
        dnnOutQueue, videoFrameQueue, audioBufferInQueue)
    dnnModelCall.start()

    # add VideoCaputure as process
    captureVideo = CaptureVideo(videoFrameQueue, 0)
    captureVideo.start()

    # add AudioCaputure as process
    audioCapture = AudioCapture(audioBufferInQueue, videoFrameQueue, dnnOutQueue)
    audioCapture.start()

    #! Wait for them to finish which will never happen because it is a True loop
    # syncProcess.join()
    # captureVideo.join()
    # audioCapture.join()
