# from capVideoMultiprocessing import capVideoFunc
from multiprocessing import Process, Queue, Array
import cv2
from jackClient_acssMultiprocessing import AudioCapture
from syncLoop import SyncLoop
from videoCapture import CaptureVideo
import jack
import numpy

if __name__ == '__main__':
    # initilize queue to share data between processes on frame per 0.04 s
    videoFrameQueue = Queue()

    # buffer is 8ms time 5 to match 1 video frame
    audioFrameQueue = Queue()

    # sync process 
    # syncProcess = SyncLoop(videoFrameQueue, audioFrameQueue)
    # syncProcess.start()
    
    # add VideoCaputure as process
    captureVideo = CaptureVideo(videoFrameQueue, 0)
    captureVideo.start()
    
    # add AudioCaputure as process
    audioCapture = AudioCapture(audioFrameQueue, videoFrameQueue)
    audioCapture.start()

    
    #! Wait for them to finish which will never happen because it is a True loop
    # syncProcess.join()
    # captureVideo.join()
    # audioCapture.join()

