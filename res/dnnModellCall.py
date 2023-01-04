from multiprocessing import Process
import time


class DnnModelCall(Process):
    def __init__(self, queue, videoBuffer, audioBuffer):
        super().__init__()
        print("DnnModelCall: init")
        self.queue = queue
        self.videoBuffer = videoBuffer
        self.audioBuffer = audioBuffer

    def run(self):
        print("DnnModelCall: run")
        while True:
            if(not self.audioBuffer.empty()):
                # getedAudioBuffer = self.audioBuffer.get()
                k = 0
                print("\n**************************************************")
                print("********** Start DNN Model Process here **********")
                print("**************************************************\n")
                for i in range(0, 10000000):
                    k += 1
                # TODO: Call DNN Model here
                print("Calculation done")
                # print("audioBuffer: ", len(self.audioBuffer))
                # print("videoBuffer: ", self.videoBuffer)
                newFrame = [0] * 2560
                self.queue.put(newFrame)
