from multiprocessing import Queue

from helperFunctions import *

from videoCapture import CaptureVideo
from dnnModellCall import DnnModelCall
from audioCapture import AudioCaptureNew


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
    videoFrameQueue = Queue()

    # DNN call as process
    dnnModelCall = DnnModelCall(audioBufferInQueue, audioBufferDNNOut)
    dnnModelCall.start()


    # VideoCaputure as process
    captureVideo = CaptureVideo(videoFrameQueue, 0)
    captureVideo.start()


    # AudioCaputure as process
    audioCapture = AudioCaptureNew(audioBufferInQueue, audioBufferDNNOut)
    audioCapture.start()
    
    #! Wait for them to finish which will never happen because it is a True loop
    dnnModelCall.join()
    captureVideo.join()
    audioCapture.join()