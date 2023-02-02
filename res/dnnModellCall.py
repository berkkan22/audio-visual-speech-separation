from multiprocessing import Process
import time
from helperFunctions import *


class DnnModelCall(Process):
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam):
        super().__init__()
        print("DnnModelCall: init")
        self.audioBufferInQueueParam = audioBufferInQueueParam
        self.audioBufferDNNOutParam = audioBufferDNNOutParam

    def run(self):
        print("DnnModelCall: run")
        # localBuffer = [0] * 40800
        localBuffer = []
        # count = 0
        while True:
            if(not self.audioBufferInQueueParam.empty()):

                while(not self.audioBufferInQueueParam.empty() and len(localBuffer) <= 40800):
                    # localBuffer = removeFirstFrameAndAddNewFrame(localBuffer, self.audioBufferInQueueParam.get())
                    localBuffer.extend(self.audioBufferInQueueParam.get())
                    # print(f"localBuffer: {len(localBuffer)}")

            if(len(localBuffer) >= 40800):
                print("Start")
                audioBuffer = localBuffer
                print(len(localBuffer))
                # print(len(audioBuffer[-2560::]))
                time.sleep(0.16)
                self.audioBufferDNNOutParam.put(audioBuffer)
                localBuffer = []
                