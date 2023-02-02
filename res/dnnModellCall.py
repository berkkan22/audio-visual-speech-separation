from multiprocessing import Process
import time
import global_variables as gv
import audioCapture as ac


class DnnModelCall(Process):
    def __init__(self, audioBufferInQueueParam, audioBufferDNNOutParam):
        super().__init__()
        print("DnnModelCall: init")
        self.audioBufferInQueueParam = audioBufferInQueueParam
        self.audioBufferDNNOutParam = audioBufferDNNOutParam

    def run(self):
        print("DnnModelCall: run")
        while True:
            if(not self.audioBufferInQueueParam.empty()):
                print("Start")
                audioBuffer = self.audioBufferInQueueParam.get()

                self.audioBufferDNNOutParam.put(audioBuffer)
                