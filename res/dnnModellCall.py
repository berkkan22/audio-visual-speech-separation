from multiprocessing import Process

from helperFunctions import *
from global_variables import *

import time


class DnnModelCall(Process):
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam):
        super().__init__()
        print("DnnModelCall: init")
        self.audioBufferInQueueParam = audioBufferInQueueParam
        self.audioBufferDNNOutParam = audioBufferDNNOutParam

    def run(self):
        print("DnnModelCall: run")
        localBuffer = [0] * 40800
        count = 0
        while True:
            if(not self.audioBufferInQueueParam.empty()):
                while(not self.audioBufferInQueueParam.empty() and count < COUNT):
                    localBuffer = removeFirstFrameAndAddNewFrame(localBuffer, self.audioBufferInQueueParam.get())
                    count += 1

            if(count >= COUNT):
                audioBuffer = localBuffer
                time.sleep(0.1) # laufzeit von DNN
                self.audioBufferDNNOutParam.put(audioBuffer[(DNN_AUDIO_FRAME_SIZE*-COUNT)::])
                count = 0
                