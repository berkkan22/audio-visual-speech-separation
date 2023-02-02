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
        localBuffer = []
        while True:
            if(not self.audioBufferInQueueParam.empty()):
                # print("get")
                while(not self.audioBufferInQueueParam.empty() and len(localBuffer) <= 40800):
                    localBuffer.extend(self.audioBufferInQueueParam.get())
                    print(f"localBuffer: {len(localBuffer)}")

            if(len(localBuffer) >= 40800):
                print("Start")
                audioBuffer = localBuffer
                k = 0
                for i in range(100000):
                    k += 1
                self.audioBufferDNNOutParam.put(audioBuffer)
                localBuffer = []
                